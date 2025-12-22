from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PIL import Image, ImageEnhance, ImageFilter  # Untuk pemrosesan gambar
import os
import os

# Import modul dari folder lain (pastikan path benar)
from processing.brightness import adjust_brightness
from processing.contrast import adjust_contrast
from processing.saturation import adjust_saturation
from processing.monochrome import apply_monochrome
from processing.sharpen import apply_sharpen
from storage.save_image import save_to_album
from storage.compress import compress_image
from processing.geometry import apply_rotate, apply_flip
from processing.filters import (
    apply_neutral_filter, apply_warm_filter, apply_cold_filter,
    apply_vintage_filter, apply_bw_filter
)


# Custom Label for Selection and Swipe
class SelectableLabel(QLabel):
    selection_made = pyqtSignal(QRect)
    swipe_left = pyqtSignal()
    swipe_right = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.start_pos = None
        self.end_pos = None
        self.is_selecting = False
        self.crop_mode = False
        self.swipe_threshold = 50  # Minimum pixels for swipe detection

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_pos = event.pos()
            self.end_pos = self.start_pos
            if self.crop_mode:
                self.is_selecting = True
                self.update()

    def mouseMoveEvent(self, event):
        if self.is_selecting:
            self.end_pos = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.start_pos:
            self.end_pos = event.pos()
            
            # Calculate horizontal distance
            dx = self.end_pos.x() - self.start_pos.x()
            dy = self.end_pos.y() - self.start_pos.y()
            
            # Check if it's a horizontal swipe (not crop)
            if not self.crop_mode and abs(dx) > self.swipe_threshold and abs(dx) > abs(dy) * 2:
                # Horizontal swipe detected
                if dx > 0:
                    self.swipe_right.emit()
                else:
                    self.swipe_left.emit()
            elif self.is_selecting:
                # Crop mode - emit selection
                self.update()
                rect = QRect(self.start_pos, self.end_pos).normalized()
                if rect.width() > 10 and rect.height() > 10:
                    self.selection_made.emit(rect)
            
            self.is_selecting = False
            self.start_pos = None
            self.end_pos = None
            self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.is_selecting and self.start_pos and self.end_pos:
            painter = QPainter(self)
            painter.setPen(QPen(Qt.red, 2, Qt.DashLine))
            rect = QRect(self.start_pos, self.end_pos).normalized()
            painter.drawRect(rect)



class MemoryLensGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("MemoryLens")
        
        # Atribut initialized EARLY to prevent resizeEvent crash
        self.original_image = None 
        self.current_image = None
        self.current_pixmap = None
        
        # --- GLOBAL STYLESHEET ---
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F7F3EE;
            }
            QWidget {
                font-family: 'Segoe UI', sans-serif;
                color: #4B4B4B;
            }
            QPushButton {
                background-color: #D6CFC4;
                color: #4B4B4B;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #C2B8AD;
            }
            QPushButton:pressed {
                background-color: #B0A69B;
            }
            QPushButton:checked {
                background-color: #8B5E3C;
                color: white;
            }
            /* Red Reset Button Override */
            QPushButton#ResetAllBtn {
                background-color: #D9534F; 
                color: white;
            }
            QPushButton#ResetAllBtn:hover {
                background-color: #C9302C;
            }
            
            /* Image Panel Style */
            QLabel {
                background-color: #FFFFFF;
                border-radius: 15px;
                border: 1px solid #E5E7EB;
            }
        """)

        # Geometry State
        self.rotation = 0
        self.flip_h = False
        self.flip_v = False
        
        # Filter State
        self.filters = [
            ("Neutral", apply_neutral_filter),
            ("Warm", apply_warm_filter),
            ("Cold", apply_cold_filter),
            ("Vintage", apply_vintage_filter),
            ("Black & White", apply_bw_filter)
        ]
        self.current_filter_index = 0  # Start with Neutral
        
        # Crop State
        self.crop_box = None # (left, top, right, bottom) normalized to current geometry
        
        # Undo/Redo Stacks
        self.undo_stack = []
        self.redo_stack = []

        # Start maximized
        self.showMaximized()

        # Label untuk menampilkan gambar - CHANGED to SelectableLabel
        self.image_label = SelectableLabel("Upload a photo to start")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        # Style handles by Global Stylesheet (QLabel)
        self.image_label.selection_made.connect(self.handle_crop_selection)
        self.image_label.swipe_left.connect(self.next_filter)
        self.image_label.swipe_right.connect(self.prev_filter)


        # Tombol Upload - will be added to layout below image
        self.upload_btn = QPushButton("Upload Photo")
        self.upload_btn.clicked.connect(self.upload_photo)
        self.upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #8B5E3C;
                color: white;
                border: none;
                border-radius: 12px;
                padding: 15px 30px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #6D4A2E;
            }
        """)
        self.upload_btn.setCursor(Qt.PointingHandCursor)
        self.upload_btn.setVisible(True)  # Explicitly show initially

        # --- Filter Navigation UI (overlaid on image) ---
        # Left Arrow Button
        self.filter_left_btn = QPushButton("◄", self.image_label)
        self.filter_left_btn.clicked.connect(self.prev_filter)
        self.filter_left_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(139, 94, 60, 180);
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 20px;
                font-weight: bold;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: rgba(109, 74, 46, 220);
            }
        """)
        self.filter_left_btn.setFixedSize(50, 50)
        self.filter_left_btn.setCursor(Qt.PointingHandCursor)
        self.filter_left_btn.hide()  # Hidden until image loaded
        
        # Right Arrow Button
        self.filter_right_btn = QPushButton("►", self.image_label)
        self.filter_right_btn.clicked.connect(self.next_filter)
        self.filter_right_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(139, 94, 60, 180);
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 20px;
                font-weight: bold;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: rgba(109, 74, 46, 220);
            }
        """)
        self.filter_right_btn.setFixedSize(50, 50)
        self.filter_right_btn.setCursor(Qt.PointingHandCursor)
        self.filter_right_btn.hide()  # Hidden until image loaded
        
        # Filter Name Label
        self.filter_name_label = QLabel("Neutral", self.image_label)
        self.filter_name_label.setAlignment(Qt.AlignCenter)
        self.filter_name_label.setStyleSheet("""
            QLabel {
                background-color: rgba(139, 94, 60, 180);
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 14px;
                font-weight: bold;
                padding: 8px 20px;
            }
        """)
        self.filter_name_label.adjustSize()
        self.filter_name_label.hide()  # Hidden until image loaded


        # --- Sliders ---
        # Helper to create sliders
        def create_slider(label_text, min_v, max_v, init_v):
            wrapper = QWidget()
            l = QVBoxLayout()
            l.setContentsMargins(5,5,5,5) # Add margin
            
            lbl = QLabel(label_text)
            lbl.setAlignment(Qt.AlignCenter)
            
            sld = QSlider(Qt.Horizontal)
            sld.setMinimum(min_v)
            sld.setMaximum(max_v)
            sld.setValue(init_v)
            
            # CHANGED: Apply stylesheet for Round Handles (Brown Theme)
            sld.setStyleSheet("""
                QSlider::groove:horizontal {
                    border: 1px solid #D6CFC4;
                    background: #FFFFFF;
                    height: 8px;
                    border-radius: 4px;
                }
                QSlider::sub-page:horizontal {
                    background: #8B5E3C; /* Brown Accent */
                    border: 1px solid #8B5E3C;
                    height: 8px;
                    border-radius: 4px;
                }
                QSlider::add-page:horizontal {
                    background: #E5E7EB;
                    border: 1px solid #D6CFC4;
                    height: 8px;
                    border-radius: 4px;
                }
                QSlider::handle:horizontal {
                    background: #8B5E3C; /* Brown Handle */
                    border: 2px solid #FFFFFF;
                    width: 18px;
                    height: 18px;
                    margin: -6px 0;
                    border-radius: 9px;
                    /* box-shadow removed */
                }
            """)
            
            spin = QDoubleSpinBox()
            spin.setRange(min_v / 100.0, max_v / 100.0)
            spin.setSingleStep(0.01)
            spin.setValue(init_v / 100.0)
            spin.setAlignment(Qt.AlignCenter)

            def on_slider_change(val):
                spin.blockSignals(True)
                spin.setValue(val / 100.0)
                spin.blockSignals(False)
                self.apply_filters()
                
            def on_spin_change(val):
                # Save state before modification via spinbox logic (tricky, but let's assume Slider Pressed covers manual drags)
                # For Spinbox, we should technically save state. But usually users drag sliders. 
                pass
                
                sld.blockSignals(True)
                sld.setValue(int(val * 100))
                sld.blockSignals(False)
                self.apply_filters()
            
            # Undo Logic: Save state when user starts dragging
            sld.sliderPressed.connect(self.save_undo_state)
            
            sld.valueChanged.connect(on_slider_change)
            spin.valueChanged.connect(on_spin_change)
            
            l.addWidget(lbl)
            l.addWidget(sld)
            l.addWidget(spin)
            wrapper.setLayout(l)
            return wrapper, sld

        self.bright_widget, self.bright_slider = create_slider("Brightness", 0, 200, 100)
        self.contrast_widget, self.contrast_slider = create_slider("Contrast", 0, 200, 100)
        self.sat_widget, self.sat_slider = create_slider("Saturation", 0, 200, 100)
        self.mono_widget, self.mono_slider = create_slider("Monochrome", 0, 100, 0)
        self.sharp_widget, self.sharp_slider = create_slider("Sharpen", 0, 200, 0)

        save_btn = QPushButton("Save to Album")
        save_btn.clicked.connect(self.save_to_album)

        sliders_layout = QHBoxLayout()
        sliders_layout.addWidget(self.bright_widget)
        sliders_layout.addWidget(self.contrast_widget)
        sliders_layout.addWidget(self.sat_widget)
        sliders_layout.addWidget(self.mono_widget)
        sliders_layout.addWidget(self.sharp_widget)

        # --- Geometry & Tools ---
        geo_layout = QHBoxLayout()
        
        btn_rot_left = QPushButton("Rotate Left")
        btn_rot_left.clicked.connect(lambda: self.rotate_image(-90))
        
        btn_rot_right = QPushButton("Rotate Right")
        btn_rot_right.clicked.connect(lambda: self.rotate_image(90))
        
        btn_flip_h = QPushButton("Flip Horizontal")
        btn_flip_h.clicked.connect(lambda: self.flip_image('horizontal'))
        
        btn_flip_v = QPushButton("Flip Vertical")
        btn_flip_v.clicked.connect(lambda: self.flip_image('vertical'))
        
        # CROP TOOLS
        self.btn_crop_mode = QPushButton("Enable Crop")
        self.btn_crop_mode.setCheckable(True)
        self.btn_crop_mode.clicked.connect(self.toggle_crop_mode)
        
        geo_layout.addWidget(btn_rot_left)
        geo_layout.addWidget(btn_rot_right)
        geo_layout.addWidget(btn_flip_h)
        geo_layout.addWidget(btn_flip_v)
        geo_layout.addWidget(self.btn_crop_mode)
        
        # RESET / UNDO LAYOUT
        reset_layout = QHBoxLayout()
        reset_layout.setSpacing(15) # More spacing
        
        self.btn_undo = QPushButton("Undo (Step Back)")
        self.btn_undo.setShortcut(QKeySequence.Undo)
        self.btn_undo.clicked.connect(self.undo)
        self.btn_undo.setEnabled(False)
        
        self.btn_redo = QPushButton("Redo")
        self.btn_redo.setShortcut(QKeySequence.Redo)
        self.btn_redo.clicked.connect(self.redo)
        self.btn_redo.setEnabled(False)
        
        btn_reset_all = QPushButton("Reset All Settings")
        btn_reset_all.setObjectName("ResetAllBtn") # For specific styling
        btn_reset_all.clicked.connect(self.reset_all)

        reset_layout.addWidget(self.btn_undo)
        reset_layout.addWidget(self.btn_redo)
        reset_layout.addWidget(btn_reset_all)

        action_layout = QHBoxLayout()
        action_layout.setSpacing(15)
        
        btn_export = QPushButton("Export Image")
        btn_export.clicked.connect(self.export_image)
        btn_export.setStyleSheet("""
            QPushButton {
                background-color: #5B8C5A;
                color: white;
            }
            QPushButton:hover {
                background-color: #4A7249;
            }
        """)
        
        action_layout.addWidget(save_btn)
        action_layout.addWidget(btn_export)
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15) # Reduced spacing
        main_layout.setContentsMargins(15, 15, 15, 15) # Reduced margins
        
        # Add Shadow to Image Label
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 30)) # Soft shadow
        shadow.setOffset(0, 5)
        self.image_label.setGraphicsEffect(shadow)
        
        main_layout.addWidget(self.image_label, 10) # Increased stretch factor
        
        # Upload button layout - centered between image and sliders
        upload_layout = QHBoxLayout()
        upload_layout.addStretch()
        upload_layout.addWidget(self.upload_btn)
        upload_layout.addStretch()
        main_layout.addLayout(upload_layout)
        
        main_layout.addLayout(sliders_layout)
        main_layout.addLayout(geo_layout)
        main_layout.addLayout(reset_layout) 
        main_layout.addLayout(action_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)


    # --- UNDO / REDO SYSTEM ---
    def get_current_state(self):
        return {
            'bright': self.bright_slider.value(),
            'contrast': self.contrast_slider.value(),
            'sat': self.sat_slider.value(),
            'mono': self.mono_slider.value(),
            'sharp': self.sharp_slider.value(),
            'rotation': self.rotation,
            'flip_h': self.flip_h,
            'flip_v': self.flip_v,
            'crop_box': self.crop_box,
            'filter_index': self.current_filter_index
        }

    def restore_state(self, state):
        self.block_signals(True)
        self.bright_slider.setValue(state['bright'])
        self.contrast_slider.setValue(state['contrast'])
        self.sat_slider.setValue(state['sat'])
        self.mono_slider.setValue(state['mono'])
        self.sharp_slider.setValue(state['sharp'])
        self.block_signals(False)
        
        self.rotation = state['rotation']
        self.flip_h = state['flip_h']
        self.flip_v = state['flip_v']
        self.crop_box = state['crop_box']
        
        # Restore filter
        self.current_filter_index = state.get('filter_index', 0)
        filter_name = self.filters[self.current_filter_index][0]
        self.filter_name_label.setText(filter_name)
        self.filter_name_label.adjustSize()
        self.position_filter_ui()
        
        self.apply_filters()
        self.update_undo_buttons()

    def save_undo_state(self):
        # Push current state to undo stack
        self.undo_stack.append(self.get_current_state())
        # Clear redo stack on new action
        self.redo_stack.clear()
        self.update_undo_buttons()

    def undo(self):
        if not self.undo_stack: return
        
        # Save current state to redo
        current = self.get_current_state()
        self.redo_stack.append(current)
        
        # Pop previous state and restore
        prev_state = self.undo_stack.pop()
        self.restore_state(prev_state)

    def redo(self):
        if not self.redo_stack: return
        
        # Save current state to undo
        current = self.get_current_state()
        self.undo_stack.append(current)
        
        # Pop next state and restore
        next_state = self.redo_stack.pop()
        self.restore_state(next_state)
        
    def update_undo_buttons(self):
        self.btn_undo.setEnabled(len(self.undo_stack) > 0)
        self.btn_redo.setEnabled(len(self.redo_stack) > 0)


    def toggle_crop_mode(self, checked):
        self.image_label.crop_mode = checked
        if checked:
            self.btn_crop_mode.setText("Crop Pattern: Draw Box")
            self.image_label.setCursor(Qt.CrossCursor)
        else:
            self.btn_crop_mode.setText("Enable Crop")
            self.image_label.setCursor(Qt.ArrowCursor)

    def reset_all(self):
        if not self.original_image: return
        
        self.save_undo_state() # Save before reset all
        
        # Reset all states to default
        self.block_signals(True)
        self.bright_slider.setValue(100)
        self.contrast_slider.setValue(100)
        self.sat_slider.setValue(100)
        self.mono_slider.setValue(0)
        self.sharp_slider.setValue(0)
        self.block_signals(False)
        
        self.rotation = 0
        self.flip_h = False
        self.flip_v = False
        self.crop_box = None
        
        # Reset crop button UI
        self.btn_crop_mode.setChecked(False)
        self.toggle_crop_mode(False)
        
        self.apply_filters()
        
    def handle_crop_selection(self, rect):
        if not self.current_image: return
        
        # Save state before crop applied
        self.save_undo_state()
        
        # Get the actual displayed pixmap to calculate the scale
        displayed_pixmap = self.image_label.pixmap()
        if not displayed_pixmap: return
        
        # Coordinate Mapping
        label_w = self.image_label.width()
        label_h = self.image_label.height()
        
        # Use the displayed pixmap size (which is scaled)
        displayed_w = displayed_pixmap.width()
        displayed_h = displayed_pixmap.height()
        
        # Get the actual current image size (before display scaling)
        img_w, img_h = self.current_image.size
        
        if displayed_w == 0 or displayed_h == 0: return

        # Calculate offsets (image is centered in label)
        offset_x = (label_w - displayed_w) / 2
        offset_y = (label_h - displayed_h) / 2
        
        # Calculate scale from displayed to actual image
        scale_x = img_w / displayed_w
        scale_y = img_h / displayed_h
        
        # Map rect to actual image coordinates
        x_start = (rect.x() - offset_x) * scale_x
        y_start = (rect.y() - offset_y) * scale_y
        w_sel = rect.width() * scale_x
        h_sel = rect.height() * scale_y
        
        # Bound/Clamp to image boundaries
        x = max(0, int(x_start))
        y = max(0, int(y_start))
        w = min(img_w - x, int(w_sel))
        h = min(img_h - y, int(h_sel))
        
        if w > 10 and h > 10:
            self.crop_box = (x, y, x+w, y+h)
            self.apply_filters()
            
            # Turn off crop mode after successful crop
            self.btn_crop_mode.setChecked(False)
            self.toggle_crop_mode(False)

    # ADDED: Implement resizeEvent to re-scale image when window size changes
    def resizeEvent(self, event):
        self.update_display()
        self.position_filter_ui()
        super().resizeEvent(event)
    
    def position_filter_ui(self):
        """Position filter navigation buttons and label on image"""
        if not hasattr(self, 'filter_left_btn'):
            return
            
        label_w = self.image_label.width()
        label_h = self.image_label.height()
        
        # Position left arrow (left side, vertically centered)
        self.filter_left_btn.move(20, (label_h - 50) // 2)
        
        # Position right arrow (right side, vertically centered)
        self.filter_right_btn.move(label_w - 70, (label_h - 50) // 2)
        
        # Position filter name label (top center)
        self.filter_name_label.adjustSize()
        label_x = (label_w - self.filter_name_label.width()) // 2
        self.filter_name_label.move(label_x, 20)
        
        # Raise to ensure they're on top
        self.filter_left_btn.raise_()
        self.filter_right_btn.raise_()
        self.filter_name_label.raise_()


    def upload_photo(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.jpg *.png *.jpeg)")
        if file:
            try:
                self.original_image = Image.open(file)
                self.current_image = self.original_image.copy()
                self.current_pixmap = QPixmap(file)
                
                # Reset sliders and states
                self.undo_stack.clear() # Clear undo on new image
                self.redo_stack.clear()
                self.update_undo_buttons()
                
                self.block_signals(True)
                self.bright_slider.setValue(100)
                self.contrast_slider.setValue(100)
                self.sat_slider.setValue(100)
                self.mono_slider.setValue(0)
                self.sharp_slider.setValue(0)
                self.block_signals(False)
                
                self.rotation = 0
                self.flip_h = False
                self.flip_v = False
                self.crop_box = None
                self.current_filter_index = 0  # Reset to Neutral filter

                # Show filter UI elements
                self.filter_left_btn.show()
                self.filter_right_btn.show()
                self.filter_name_label.setText(self.filters[0][0])  # "Neutral"
                self.filter_name_label.show()
                self.position_filter_ui()

                # Keep upload button visible so user can upload new photos anytime
                # self.upload_btn.setVisible(False)  # Commented out - button stays visible
                
                self.update_display()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to load image: {str(e)}")

    def block_signals(self, block):
        self.bright_slider.blockSignals(block)
        self.contrast_slider.blockSignals(block)
        self.sat_slider.blockSignals(block)
        self.mono_slider.blockSignals(block)
        self.sharp_slider.blockSignals(block)

    def update_display(self, pixmap=None):
        target = pixmap if pixmap else self.current_pixmap
        if target:
            # Scale to available label size
            scaled_pixmap = target.scaled(self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(scaled_pixmap)
            
    # Removed duplicate pil_to_pixmap
    def pil_to_pixmap(self, pil_image):
        pil_image.save("temp.png")
        pixmap = QPixmap("temp.png")
        os.remove("temp.png")
        return pixmap

    def rotate_image(self, angle):
        self.save_undo_state()
        self.rotation = (self.rotation + angle) % 360
        self.apply_filters()
        
    def flip_image(self, mode):
        self.save_undo_state()
        if mode == 'horizontal':
            self.flip_h = not self.flip_h
        elif mode == 'vertical':
            self.flip_v = not self.flip_v
        self.apply_filters()
    
    def next_filter(self):
        """Cycle to next filter (swipe left or right arrow)"""
        if not self.original_image:
            return
        
        self.save_undo_state()
        self.current_filter_index = (self.current_filter_index + 1) % len(self.filters)
        filter_name = self.filters[self.current_filter_index][0]
        self.filter_name_label.setText(filter_name)
        self.filter_name_label.adjustSize()
        self.position_filter_ui()
        self.apply_filters()
    
    def prev_filter(self):
        """Cycle to previous filter (swipe right or left arrow)"""
        if not self.original_image:
            return
        
        self.save_undo_state()
        self.current_filter_index = (self.current_filter_index - 1) % len(self.filters)
        filter_name = self.filters[self.current_filter_index][0]
        self.filter_name_label.setText(filter_name)
        self.filter_name_label.adjustSize()
        self.position_filter_ui()
        self.apply_filters()


    def apply_filters(self):
        if not self.original_image: 
            return

        try:
            # 1. Start from Original
            img = self.original_image.copy()
            
            # --- Geometry Transforms (First) ---
            if self.rotation != 0:
                img = apply_rotate(img, self.rotation)
            
            if self.flip_h:
                img = apply_flip(img, 'horizontal')
                
            if self.flip_v:
                img = apply_flip(img, 'vertical')
            
            # --- CROP (Second) ---
            if self.crop_box:
                img = img.crop(self.crop_box)
            
            # --- FILTER (Third) ---
            # Apply selected filter
            filter_func = self.filters[self.current_filter_index][1]
            img = filter_func(img)

            # 2. Get all values
            bright_factor = self.bright_slider.value() / 100.0
            contrast_factor = self.contrast_slider.value() / 100.0
            sat_factor = self.sat_slider.value() / 100.0
            mono_factor = self.mono_slider.value() / 100.0
            sharp_factor = self.sharp_slider.value() / 100.0

            # 3. Apply Filters Sequentially
            
            # Brightness
            if bright_factor != 1.0:
                img = adjust_brightness(img, bright_factor)
            
            # Contrast
            if contrast_factor != 1.0:
                img = adjust_contrast(img, contrast_factor)
                
            # Saturation
            if sat_factor != 1.0:
                img = adjust_saturation(img, sat_factor)

            # Monochrome
            if mono_factor > 0:
                img = apply_monochrome(img, mono_factor)

            # Sharpen
            if sharp_factor > 0:
                img = apply_sharpen(img, sharp_factor)

            # 4. Update Result
            self.current_image = img
            self.update_display(self.pil_to_pixmap(self.current_image))
            
        except Exception as e:
            # Optional: print error to console, but don't spam popups during slide
            print(f"Error applying filters: {e}")

    def save_to_album(self):
        if self.current_image:
            album_path = "user_data/albums/"
            try:
                save_to_album(self.current_image, album_path)
                QMessageBox.information(self, "Success", "Image saved to album!")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to save image: {str(e)}")

    def export_image(self):
        if not self.current_image:
            QMessageBox.warning(self, "Warning", "No image to export!")
            return

        # Simple Dialog for Format and Quality
        dialog = QDialog(self)
        dialog.setWindowTitle("Export Image")
        layout = QVBoxLayout()

        # Format Selection
        format_label = QLabel("Select Format:")
        format_combo = QComboBox()
        format_combo.addItems(["JPEG", "PNG", "BMP"])
        layout.addWidget(format_label)
        layout.addWidget(format_combo)

        # Quality Selection (only for JPEG)
        quality_group = QGroupBox("Compression (JPEG Only)")
        quality_layout = QVBoxLayout()
        quality_label = QLabel("Quality: 95%")
        quality_slider = QSlider(Qt.Horizontal)
        quality_slider.setRange(1, 100)
        quality_slider.setValue(95)
        quality_slider.valueChanged.connect(lambda v: quality_label.setText(f"Quality: {v}%"))
        
        quality_layout.addWidget(quality_label)
        quality_layout.addWidget(quality_slider)
        quality_group.setLayout(quality_layout)
        layout.addWidget(quality_group)

        # Toggle quality slider visibility based on format
        format_combo.currentTextChanged.connect(lambda t: quality_group.setEnabled(t == "JPEG"))

        # Buttons
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(dialog.accept)
        btns.rejected.connect(dialog.reject)
        layout.addWidget(btns)

        dialog.setLayout(layout)

        if dialog.exec_() == QDialog.Accepted:
            selected_format = format_combo.currentText()
            selected_quality = quality_slider.value()
            
            ext_filter = f"{selected_format} Files (*.{selected_format.lower()})"
            file_path, _ = QFileDialog.getSaveFileName(self, "Export Image", "", ext_filter)
            
            if file_path:
                try:
                    if selected_format == "JPEG":
                        self.current_image.convert("RGB").save(file_path, format=selected_format, quality=selected_quality, optimize=True)
                    else:
                        self.current_image.save(file_path, format=selected_format)
                    QMessageBox.information(self, "Success", f"Image exported to {file_path}")
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Failed to export image: {str(e)}")

class MainPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.window = MemoryLensGUI()
        layout.addWidget(self.window)
        self.setLayout(layout)

