import sys
import requests
import threading
import time
from urllib.parse import urlparse
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QPushButton, QTextEdit, QVBoxLayout, QHBoxLayout)
from PyQt5.QtCore import Qt

class Application(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.successful_gets = 0
        self.errors = 0
        self.running = False

    def initUI(self):
        self.setWindowTitle('GET Request Application')
        self.resize(800, 800)  # Set the initial size of the window

        # URL
        self.url_label = QLabel('URL:')
        self.url_entry = QLineEdit()

        # Number of GETs
        self.gets_label = QLabel('Number of GETs:')
        self.gets_entry = QLineEdit()

        # Delay
        self.delay_label = QLabel('Delay (ms):')
        self.delay_entry = QLineEdit()

        # Port
        self.port_label = QLabel('Port (optional):')
        self.port_entry = QLineEdit()

        # Start Button
        self.start_button = QPushButton('Start')
        self.start_button.clicked.connect(self.start_gets)

        # Successful GETs
        self.successful_gets_label = QLabel('Successful GETs: 0')

        # Errors
        self.errors_label = QLabel('Errors: 0')

        # Log
        self.log_label = QLabel('Log:')
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)

        # Layouts
        layout = QVBoxLayout()
        layout.addWidget(self.url_label)
        layout.addWidget(self.url_entry)
        layout.addWidget(self.gets_label)
        layout.addWidget(self.gets_entry)
        layout.addWidget(self.delay_label)
        layout.addWidget(self.delay_entry)
        layout.addWidget(self.port_label)
        layout.addWidget(self.port_entry)
        layout.addWidget(self.start_button)
        layout.addWidget(self.successful_gets_label)
        layout.addWidget(self.errors_label)
        layout.addWidget(self.log_label)
        layout.addWidget(self.log_text)

        self.setLayout(layout)

        # Apply dark theme
        self.apply_dark_theme()

    def apply_dark_theme(self):
        dark_stylesheet = """
        QWidget {
            background-color: #2e2e2e;
            color: #ffffff;
            font-family: Times New Roman;
            font-size: 12pt;
        }
        QLineEdit, QTextEdit {
            background-color: #1e1e1e;
            color: #ffffff;
            border: 1px solid #3e3e3e;
        }
        QPushButton {
            background-color: #3e3e3e;
            color: #ffffff;
            border: 1px solid #5e5e5e;
        }
        QPushButton:hover {
            background-color: #5e5e5e;
        }
        """
        self.setStyleSheet(dark_stylesheet)

    def start_gets(self):
        if not self.running:
            self.running = True
            self.successful_gets = 0
            self.errors = 0
            self.successful_gets_label.setText("Successful GETs: 0")
            self.errors_label.setText("Errors: 0")
            self.log_text.clear()
            self.thread = threading.Thread(target=self.send_gets)
            self.thread.start()

    def send_gets(self):
        url = self.url_entry.text()
        num_gets = int(self.gets_entry.text())
        delay = int(self.delay_entry.text())
        port = self.port_entry.text()
        parsed_url = urlparse(url)
        ip = parsed_url.hostname
        if port:
            port = int(port)
        else:
            port = parsed_url.port if parsed_url.port else 80 if parsed_url.scheme == 'http' else 443

        for i in range(num_gets):
            try:
                # Construct the URL with the specified port
                if port:
                    url_with_port = f"{parsed_url.scheme}://{ip}:{port}{parsed_url.path}"
                else:
                    url_with_port = url

                response = requests.get(url_with_port)
                if response.status_code == 200:
                    self.successful_gets += 1
                    self.successful_gets_label.setText(f"Successful GETs: {self.successful_gets}")
                    self.log(f"GET {url_with_port} successful ({response.status_code}) from {ip}:{port}")
                else:
                    self.errors += 1
                    self.errors_label.setText(f"Errors: {self.errors}")
                    self.log(f"GET {url_with_port} failed ({response.status_code}) from {ip}:{port}")
            except requests.exceptions.RequestException as e:
                self.errors += 1
                self.errors_label.setText(f"Errors: {self.errors}")
                self.log(f"GET {url_with_port} failed: {e} from {ip}:{port}")
            time.sleep(delay / 1000)
        self.running = False

    def log(self, message):
        self.log_text.append(message)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Application()
    ex.show()
    sys.exit(app.exec_())
