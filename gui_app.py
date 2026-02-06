import sys
import threading
import webbrowser
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import QTimer
import app

class AppWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.start_server()

    def initUI(self):
        self.setWindowTitle('DEIS App')
        self.setGeometry(100, 100, 300, 200)

        layout = QVBoxLayout()

        self.label = QLabel('Starting DEIS App...')
        layout.addWidget(self.label)

        self.button = QPushButton('Open in Browser')
        self.button.clicked.connect(self.open_browser)
        self.button.setEnabled(False)
        layout.addWidget(self.button)

        self.setLayout(layout)
        self.show()

    def start_server(self):
        self.server_thread = threading.Thread(target=self.run_server)
        self.server_thread.daemon = True
        self.server_thread.start()

        # Check if server is ready
        QTimer.singleShot(2000, self.check_server)

    def run_server(self):
        app.app.run(debug=False, host='127.0.0.1', port=5000)

    def check_server(self):
        self.label.setText('DEIS App is running on http://127.0.0.1:5000')
        self.button.setEnabled(True)

    def open_browser(self):
        webbrowser.open('http://127.0.0.1:5000')

if __name__ == '__main__':
    app_qt = QApplication(sys.argv)
    ex = AppWindow()
    sys.exit(app_qt.exec_())
