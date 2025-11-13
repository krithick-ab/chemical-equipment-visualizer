
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QGridLayout, QFrame
from PyQt5.QtCore import Qt
from main_app_window import MainAppWindow
from register_window import RegisterWindow # Import RegisterWindow
import requests

BASE_URL = "http://localhost:8000/api/auth/"

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.setGeometry(100, 100, 450, 550) # Increased size
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
            #demoCredentials {
                background-color: #e0f7fa;
                border: 1px solid #b2ebf2;
                border-radius: 5px;
                padding: 10px;
                font-size: 12px;
                color: #00796b;
            }
        """)

        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignCenter) # Center the content vertically

        self.login_frame = QFrame()
        self.login_frame.setFrameShape(QFrame.NoFrame)
        self.login_frame.setFrameShadow(QFrame.Plain)
        self.login_frame.setObjectName("loginFrame") # Object name for styling

        self.layout = QVBoxLayout(self.login_frame)
        self.layout.setAlignment(Qt.AlignCenter)

        self.title_label = QLabel("Login")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        self.layout.addWidget(self.title_label)

        # Demo User Credentials
        self.demo_credentials_label = QLabel("""
            <p><b>Demo User Credentials:</b></p>
            <p>Username: user</p>
            <p>Password: fossee123</p>
        """)
        self.demo_credentials_label.setObjectName("demoCredentials")
        self.demo_credentials_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.demo_credentials_label)

        self.username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        self.layout.addWidget(self.username_label)
        self.layout.addWidget(self.username_input)

        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(self.password_label)
        self.layout.addWidget(self.password_input)

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.login)
        self.layout.addWidget(self.login_button)

        self.register_button = QPushButton("Don't have an account? Create Account")
        self.register_button.setStyleSheet("background-color: transparent; color: #007bff; border: none; font-size: 14px;")
        self.register_button.clicked.connect(self.register)
        self.layout.addWidget(self.register_button)

        self.main_layout.addWidget(self.login_frame)
        self.setLayout(self.main_layout)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        try:
            response = requests.post(BASE_URL + "token/", data={'username': username, 'password': password})
            if response.status_code == 200:
                auth_token = response.json().get('access')
                QMessageBox.information(self, "Login Success", "Logged in successfully!")
                self.main_app = MainAppWindow(auth_token, self)
                self.main_app.show()
                self.close()
                return True
            else:
                QMessageBox.warning(self, "Login Failed", "Invalid credentials.")
                return False
        except requests.exceptions.ConnectionError:
            QMessageBox.critical(self, "Error", "Could not connect to the backend server. Please ensure it is running.")
            return False

    def register(self):
        self.register_window = RegisterWindow(self)
        self.register_window.show()
        self.hide()

        username = self.username_input.text()
        password = self.password_input.text()
        try:
            response = requests.post(BASE_URL + "register/", json={'username': username, 'password': password})
            print(f"Registration Response Status Code: {response.status_code}")
            print(f"Registration Response Text: {response.text}")
            if response.status_code == 201:
                QMessageBox.information(self, "Registration Success", "Registered successfully!")
            else:
                QMessageBox.warning(self, "Registration Failed", response.json().get('detail', 'Registration failed.'))
        except requests.exceptions.ConnectionError:
            QMessageBox.critical(self, "Error", "Could not connect to the backend server. Please ensure it is running.")
        except requests.exceptions.JSONDecodeError:
            QMessageBox.critical(self, "Error", f"Failed to decode JSON response from registration endpoint. Status: {response.status_code}, Response: {response.text}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())