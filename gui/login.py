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
                border: 1px solid #FAD9E6; /* Soft pink border */
            }
            QLabel#Title {
                color: #F2A7C3; 
                font-family: 'Segoe UI', sans-serif;
                font-size: 28px;
                font-weight: bold;
                margin-bottom: 20px;
            }
            QLineEdit {
                border: 2px solid #FCEDF2;
                border-radius: 10px;
                padding: 14px;
                font-size: 15px;
                background-color: #FFF9FA;
                color: #4B4B4B;
            }
            QLineEdit:focus {
                border: 2px solid #F2A7C3;
                background-color: #FFFFFF;
            }
            QPushButton {
                background-color: #F2A7C3;
                color: white;
                border-radius: 10px;
                padding: 14px;
                font-size: 17px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #E68EAF;
            }
            QPushButton:pressed {
                background-color: #D67A9C;
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
        
        # Solid Background #FFF5F8
        painter.fillRect(self.rect(), QColor("#FFF5F8"))
        
        # Ornamen Dekoratif (Lingkaran Pink Muda Transparan)
        painter.setPen(Qt.NoPen)
        
        # Lingkaran Kiri Atas
        painter.setBrush(QColor(242, 167, 195, 30)) # #F2A7C3 transparan
        painter.drawEllipse(-100, -100, 400, 400)
        
        # Lingkaran Kanan Bawah
        painter.setBrush(QColor(242, 167, 195, 25))
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
