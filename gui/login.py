from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush

class LoginPage(QWidget):
    def __init__(self, switch_callback):
        super().__init__()
        self.switch_callback = switch_callback

        # Container Utama (Putih Tulang / Putih)
        self.container = QFrame()
        self.container.setObjectName("LoginCard")
        self.container.setFixedWidth(550)
        
        # Stylesheet untuk Container dan Isinya
        self.container.setStyleSheet("""
            QFrame#LoginCard {
                background-color: #FFFFFF;
                border-radius: 20px;
                border: 1px solid #D4C5A9; /* Sedikit sentuhan coklat di border */
            }
            QLabel#Title {
                color: #8B5E3C; 
                font-family: 'Segoe UI', sans-serif;
                font-size: 28px;
                font-weight: bold;
                margin-bottom: 20px;
            }
            QLineEdit {
                border: 2px solid #E5E7EB;
                border-radius: 10px;
                padding: 14px;
                font-size: 15px;
                background-color: #F9FAFB;
                color: #374151;
            }
            QLineEdit:focus {
                border: 2px solid #8B5E3C;
                background-color: #FFFFFF;
            }
            QPushButton {
                background-color: #8B5E3C;
                color: white;
                border-radius: 10px;
                padding: 14px;
                font-size: 17px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #6F4B30;
            }
            QPushButton:pressed {
                background-color: #543824;
            }
        """)

        # Layout Card
        card_layout = QVBoxLayout()
        card_layout.setSpacing(20)
        card_layout.setContentsMargins(50, 50, 50, 50)

        # Judul
        title = QLabel("MemoryLens")
        title.setObjectName("Title")
        title.setAlignment(Qt.AlignCenter)
        
        # Input email
        self.email = QLineEdit()
        self.email.setPlaceholderText("Email Address")
        
        # Input password
        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)
        self.password.returnPressed.connect(self.login)

        # Tombol login
        login_btn = QPushButton("Log In")
        login_btn.clicked.connect(self.login)
        login_btn.setCursor(Qt.PointingHandCursor)

        # Susun Widget ke Card
        card_layout.addWidget(title)
        card_layout.addWidget(self.email)
        card_layout.addWidget(self.password)
        card_layout.addWidget(login_btn)
        
        self.container.setLayout(card_layout)

        # Layout Halaman (Center Alignment)
        main_layout = QVBoxLayout()
        main_layout.addStretch()
        main_layout.addWidget(self.container, 0, Qt.AlignCenter)
        main_layout.addStretch()

        self.setLayout(main_layout)

    def paintEvent(self, event):
        # Latar Belakang Coklat Muda Lembut
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Solid Background #F3ECDC
        painter.fillRect(self.rect(), QColor("#F3ECDC"))
        
        # Ornamen Dekoratif (Lingkaran Coklat Muda Transparan)
        painter.setPen(Qt.NoPen)
        
        # Lingkaran Kiri Atas
        painter.setBrush(QColor(139, 94, 60, 20)) # #8B5E3C transparan
        painter.drawEllipse(-100, -100, 400, 400)
        
        # Lingkaran Kanan Bawah
        painter.setBrush(QColor(139, 94, 60, 15))
        painter.drawEllipse(self.width() - 300, self.height() - 300, 500, 500)
        
        # Lingkaran Dekoratif Tambahan
        painter.setBrush(QColor(255, 255, 255, 100))
        painter.drawEllipse(100, self.height() // 2, 60, 60)

    def login(self):
        # LOGIN DUMMY (sementara)
        if self.email.text() == "admin" and self.password.text() == "123":
            self.switch_callback()
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid email or password.\nUse 'admin' and '123'.")
