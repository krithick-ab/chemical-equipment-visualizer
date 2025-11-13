import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QFrame
from PyQt5.QtCore import Qt
import requests

BASE_URL = "http://localhost:8000/api/auth/"

class RegisterWindow(QWidget):
    def __init__(self, login_window_instance):
        super().__init__()
        self.login_window = login_window_instance
        self.setWindowTitle("Register")
        self.setGeometry(100, 100, 450, 550)
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f2f5;
            }
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 20px;
            }
            QLabel {
                font-size: 14px;
                color: #333;
            }
            QLineEdit {
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)

        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignCenter)

        self.register_frame = QFrame()
        self.register_frame.setFrameShape(QFrame.NoFrame)
        self.register_frame.setFrameShadow(QFrame.Plain)
        self.register_frame.setObjectName("registerFrame")

        self.layout = QVBoxLayout(self.register_frame)
        self.layout.setAlignment(Qt.AlignCenter)

        self.title_label = QLabel("Register")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        self.layout.addWidget(self.title_label)

        self.username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        self.layout.addWidget(self.username_label)
        self.layout.addWidget(self.username_input)

        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(self.password_label)
        self.layout.addWidget(self.password_input)

        self.confirm_password_label = QLabel("Confirm Password:")
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(self.confirm_password_label)
        self.layout.addWidget(self.confirm_password_input)

        self.register_button = QPushButton("Register")
        self.register_button.clicked.connect(self.register)
        self.layout.addWidget(self.register_button)

        self.login_link_button = QPushButton("Already have an account? Login")
        self.login_link_button.setStyleSheet("background-color: transparent; color: #007bff; border: none; font-size: 14px;")
        self.login_link_button.clicked.connect(self.show_login_window)
        self.layout.addWidget(self.login_link_button)

        self.main_layout.addWidget(self.register_frame)
        self.setLayout(self.main_layout)

    def register(self):
        username = self.username_input.text()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()

        if not username or not password or not confirm_password:
            QMessageBox.warning(self, "Registration Failed", "All fields are required.")
            return

        if password != confirm_password:
            QMessageBox.warning(self, "Registration Failed", "Passwords do not match.")
            return

        try:
            response = requests.post(BASE_URL + "register/", json={'username': username, 'password': password})
            if response.status_code == 201:
                QMessageBox.information(self, "Registration Success", "Registered successfully! You can now log in.")
                self.show_login_window()
            else:
                QMessageBox.warning(self, "Registration Failed", response.json().get('detail', 'Registration failed.'))
        except requests.exceptions.ConnectionError:
            QMessageBox.critical(self, "Error", "Could not connect to the backend server. Please ensure it is running.")
        except requests.exceptions.JSONDecodeError:
            QMessageBox.critical(self, "Error", f"Failed to decode JSON response from registration endpoint. Status: {response.status_code}, Response: {response.text}")

    def show_login_window(self):
        self.login_window.show()
        self.close()