import sys
from PyQt5.QtWidgets import QApplication, QStackedWidget
from gui.login import LoginPage
from gui.interface import MainPage

if __name__ == "__main__":
    app = QApplication(sys.argv)

    stack = QStackedWidget()

    main_page = MainPage()

    def go_to_main():
        stack.setCurrentIndex(1)

    login_page = LoginPage(go_to_main)

    stack.addWidget(login_page)  # index 0
    stack.addWidget(main_page)   # index 1

    stack.showMaximized()  # Start in full screen mode

    sys.exit(app.exec_())
