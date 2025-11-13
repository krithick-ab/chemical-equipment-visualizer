
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton, QFileDialog, QMessageBox, QListWidget, QHBoxLayout, QFrame
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt5.QtGui import QFont, QDragEnterEvent, QDropEvent
import requests
from results_page import ResultsPage

BASE_URL = "http://localhost:8000/api/equipment/"

class DragDropButton(QPushButton):
    file_dropped = pyqtSignal(str)

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setAcceptDrops(True)
        self.setFixedSize(400, 200) # Match the size of the original drag_drop_area
        self.setObjectName("dragDropArea") # Keep the same object name for styling

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if file_path.endswith('.csv'): # Only accept CSV files
                    self.file_dropped.emit(file_path)
                    event.acceptProposedAction()
                    return
        event.ignore()

class MainAppWindow(QMainWindow):
    def __init__(self, auth_token, login_window):
        super().__init__()
        self.auth_token = auth_token
        self.login_window = login_window
        self.setWindowTitle("Chem CSV Visualizer - Main Application")
        self.setGeometry(100, 100, 1000, 700) # Increased window size

        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f2f5;
            }
            #headerFrame {
                background-color: #3498db;
                color: white;
                border-bottom: 2px solid #2980b9;
            }
            #headerTitle {
                font-size: 24px;
                font-weight: bold;
                color: white;
            }
            #logoutButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
                font-size: 14px;
            }
            #logoutButton:hover {
                background-color: #c0392b;
            }
            #mainContentFrame {
                background-color: #ffffff;
                margin: 20px;
                border-radius: 10px;
                box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
            }
            #mainTitle {
                font-size: 32px;
                font-weight: bold;
                color: #2c3e50;
                margin-top: 20px;
            }
            #subtitle {
                font-size: 16px;
                color: #7f8c8d;
                margin-bottom: 30px;
            }
            #dragDropArea {
                border: 2px dashed #3498db;
                border-radius: 10px;
                background-color: #ecf0f1;
                color: #2c3e50;
                font-size: 20px; /* Increased font size for uploaded text */
                font-weight: bold;
                padding: 20px;
                text-align: center;
            }
            #dragDropArea:hover {
                background-color: #e0e6e8;
            }
            #analyzeButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 12px 45px; /* Increased horizontal padding again */
                border-radius: 5px;
                font-size: 18px;
                font-weight: bold;
                margin-top: 20px;
            }
            #analyzeButton:hover {
                background-color: #2980b9;
            }
            #hideHistoryButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
                margin-top: 20px;
            }
            #hideHistoryButton:hover {
                background-color: #2980b9;
            }
            #historyTitle {
                font-size: 20px;
                font-weight: bold;
                color: #2c3e50;
                margin-top: 20px;
                margin-bottom: 10px;
            }
            QListWidget {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background-color: #fdfefe;
                font-size: 15px; /* Slightly increased font size for history items */
                color: #34495e;
                padding: 5px;
            }
            QListWidget::item {
                padding: 10px 8px; /* Increased spacing for items */
                margin-bottom: 3px;
                border-bottom: 1px solid #ecf0f1;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QMessageBox {
                background-color: #f0f2f5;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                font-size: 14px;
            }
            QMessageBox QLabel {
                color: #2c3e50;
            }
            QMessageBox QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
                min-width: 70px;
            }
            QMessageBox QPushButton:hover {
                background-color: #2980b9;
            }
        """)

        # Main layout for the window
        self.main_layout = QVBoxLayout()

        # Header Frame
        self.header_frame = QFrame()
        self.header_frame.setObjectName("headerFrame")
        self.header_layout = QHBoxLayout(self.header_frame)
        self.header_layout.setContentsMargins(20, 10, 20, 10)

        self.header_title = QLabel("Chem CSV Visualizer")
        self.header_title.setObjectName("headerTitle")
        self.header_layout.addWidget(self.header_title)
        self.header_layout.addStretch()

        self.logout_button = QPushButton("Logout")
        self.logout_button.setObjectName("logoutButton")
        self.logout_button.clicked.connect(self.logout)
        self.header_layout.addWidget(self.logout_button)

        self.main_layout.addWidget(self.header_frame)

        # Central Widget for main content
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_widget.setLayout(self.main_layout)

        # Main Content Frame
        self.main_content_frame = QFrame()
        self.main_content_frame.setObjectName("mainContentFrame")
        self.content_layout = QVBoxLayout(self.main_content_frame)
        self.content_layout.setAlignment(Qt.AlignCenter) # Center align content

        self.main_title = QLabel("Equipment Data Analysis")
        self.main_title.setObjectName("mainTitle")
        self.main_title.setAlignment(Qt.AlignCenter)
        self.content_layout.addWidget(self.main_title)

        self.subtitle = QLabel("Upload your CSV file to get instant insights and visualizations.")
        self.subtitle.setObjectName("subtitle")
        self.subtitle.setAlignment(Qt.AlignCenter)
        self.content_layout.addWidget(self.subtitle)

        # Drag and Drop Area
        self.drag_drop_area = DragDropButton("Click to upload or drag and drop\nCSV files only (MAX: 800x600px)")
        self.drag_drop_area.file_dropped.connect(self.upload_csv)
        self.drag_drop_area.clicked.connect(self.upload_csv) # Also connect click event
        self.drag_drop_area.setStyleSheet("font-size: 20px; font-weight: bold;") # Reset to original font size
        self.content_layout.addWidget(self.drag_drop_area, alignment=Qt.AlignCenter)

        self.analyze_button = QPushButton("Analyze Now")
        self.analyze_button.setObjectName("analyzeButton")
        # self.analyze_button.setFixedSize(200, 50) # Removed fixed size to allow text to fit
        self.analyze_button.clicked.connect(self.open_results_for_last_uploaded_file) # Connect to the new method
        self.content_layout.addWidget(self.analyze_button, alignment=Qt.AlignCenter)

        self.hide_history_button = QPushButton("Show Upload History") # Changed to Show Upload History
        self.hide_history_button.setObjectName("hideHistoryButton")
        self.hide_history_button.clicked.connect(self.toggle_history_visibility)
        self.content_layout.addWidget(self.hide_history_button, alignment=Qt.AlignCenter)

        self.history_title = QLabel("Upload History")
        self.history_title.setObjectName("historyTitle")
        self.history_title.setAlignment(Qt.AlignCenter)
        self.history_title.hide() # Hide by default
        self.content_layout.addWidget(self.history_title)

        self.history_list_widget = QListWidget()
        self.history_list_widget.itemDoubleClicked.connect(self.view_dataset_details)
        self.history_list_widget.setFixedSize(600, 150) # Set a fixed size for the history list
        self.history_list_widget.hide() # Hide by default
        self.history_list_widget.setMaximumHeight(0) # Start with 0 height for animation
        self.max_history_height = 150 # Store the intended maximum height
        self.content_layout.addWidget(self.history_list_widget, alignment=Qt.AlignCenter)

        # Add the main content frame to the main layout
        self.main_layout.addWidget(self.main_content_frame)
        self.main_layout.addStretch() # Push content to the top

        self.results_page = None # Initialize results page attribute
        self.last_uploaded_file_id = None # Store the ID of the last uploaded file
        self.last_uploaded_file_name = None # Store the name of the last uploaded file

    def logout(self):
        # Implement logout logic here
        QMessageBox.information(self, "Logout", "Logged out successfully!")
        self.close()
        self.login_window.show()

    def toggle_history_visibility(self):
        self.animation = QPropertyAnimation(self.history_list_widget, b"maximumHeight")
        self.animation.setDuration(500) # Increased duration for smoother animation
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)

        if self.history_list_widget.isVisible():
            # Hide animation
            self.history_title.hide()
            self.animation.setStartValue(self.max_history_height)
            self.animation.setEndValue(0)
            self.animation.finished.connect(self.history_list_widget.hide)
            self.hide_history_button.setText("Show Upload History")
        else:
            # Show animation
            self.history_list_widget.show()
            self.history_title.show()
            self.animation.setStartValue(0)
            self.animation.setEndValue(self.max_history_height) # Animate to its full height
            self.hide_history_button.setText("Hide Upload History")
            self.view_upload_history() # Refresh history when shown

        self.animation.start()

    def show_results_page(self, dataset_id):
        print(f"show_results_page called with dataset_id: {dataset_id}")
        if self.results_page:
            self.results_page.close() # Close any existing results page
        print(f"Instantiating ResultsPage with dataset_id: {dataset_id}")
        self.results_page = ResultsPage(self.auth_token, dataset_id, self.login_window, self)
        self.results_page.fetch_dataset_details()
        print("Calling self.results_page.show()")
        self.results_page.show()

    def open_results_for_last_uploaded_file(self):
        if self.last_uploaded_file_id:
            self.show_results_page(self.last_uploaded_file_id)
        else:
            QMessageBox.warning(self, "No File Uploaded", "Please upload a CSV file before analyzing.")

    def upload_csv(self, dropped_file_path=None):
        file_path = dropped_file_path
        if not file_path:
            file_dialog = QFileDialog()
            file_path, _ = file_dialog.getOpenFileName(self, "Upload CSV File", "", "CSV Files (*.csv)")

        if file_path:
            # Reset font style before displaying new uploaded text
            self.drag_drop_area.setStyleSheet("font-size: 20px; font-weight: bold;")
            if not self.auth_token:
                QMessageBox.warning(self, "Authentication Error", "No authentication token found. Please log in again.")
                return

            try:
                with open(file_path, 'rb') as f:
                    files = {'file': (file_path, f, 'text/csv')}
                    headers = {'Authorization': f'Bearer {self.auth_token}'}
                    response = requests.post(BASE_URL + "upload/", files=files, headers=headers)

                    if response.status_code == 200 or response.status_code == 201:
                        response_data = response.json()
                        self.last_uploaded_file_id = response_data.get('id')
                        self.last_uploaded_file_name = response_data.get('filename')
                        QMessageBox.information(self, "Upload Success", "CSV file uploaded successfully!")
                        self.drag_drop_area.setText(f"Uploaded: {self.last_uploaded_file_name}")
                        self.drag_drop_area.setStyleSheet("font-size: 14px; font-weight: normal;") # Smaller font for uploaded text
                        self.view_upload_history() # Refresh history after successful upload
                        self.results_page = ResultsPage(self.auth_token, self.last_uploaded_file_id, self.login_window)
                        self.results_page.show()
                        self.hide()
                    elif response.status_code == 400 and "upload limit" in response.text:
                        self.manage_upload_limit(file_path, files, headers)
                    else:
                        QMessageBox.warning(self, "Upload Failed", f"Failed to upload CSV. Status: {response.status_code}, Response: {response.text}")
            except requests.exceptions.ConnectionError:
                QMessageBox.critical(self, "Error", "Could not connect to the backend server. Please ensure it is running.")
            except Exception as e:
                QMessageBox.critical(self, "Upload Error", f"An error occurred during file upload: {e}")

    def view_upload_history(self):
        if not self.auth_token:
            QMessageBox.warning(self, "Authentication Error", "No authentication token found. Please log in again.")
            return

        try:
            headers = {'Authorization': f'Bearer {self.auth_token}'}
            response = requests.get(BASE_URL + "history/", headers=headers)

            self.history_list_widget.clear()
            if response.status_code == 200:
                history_data = response.json()
                if history_data:
                    for item in history_data:
                        self.history_list_widget.addItem(f"ID: {item['id']}, Filename: {item['filename']}, Uploaded At: {item['uploaded_at']}")
                else:
                    self.history_list_widget.addItem("No CSV files uploaded yet.")
            else:
                self.history_list_widget.addItem(f"Failed to fetch upload history. Status: {response.status_code}, Response: {response.text}")
        except requests.exceptions.ConnectionError:
            QMessageBox.critical(self, "Error", "Could not connect to the backend server. Please ensure it is running.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while fetching upload history: {e}")

    def manage_upload_limit(self, new_file_path, new_files, new_headers):
        try:
            headers = {'Authorization': f'Bearer {self.auth_token}'}
            history_response = requests.get(BASE_URL + "history/", headers=headers)
            if history_response.status_code == 200:
                datasets = history_response.json()
                if len(datasets) >= 5:
                    oldest_dataset = min(datasets, key=lambda x: x['uploaded_at'])
                    oldest_dataset_id = oldest_dataset['id']
                    oldest_dataset_filename = oldest_dataset['filename']

                    reply = QMessageBox.question(self, 'Upload Limit Reached', 
                                                 f"You have reached your upload limit. The oldest file (Filename: {oldest_dataset_filename}) will be deleted to make space for the new upload. Do you want to proceed?",
                                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

                    if reply == QMessageBox.Yes:
                        delete_response = requests.delete(BASE_URL + f"datasets/{oldest_dataset_id}/", headers=headers)
                        if delete_response.status_code == 204:
                            # Removed the intermediate QMessageBox.information for deletion
                            new_files['file'][1].seek(0)
                            response = requests.post(BASE_URL + "upload/", files=new_files, headers=new_headers)
                            if response.status_code == 200 or response.status_code == 201:
                                response_data = response.json()
                                self.last_uploaded_file_id = response_data.get('id')
                                self.last_uploaded_file_name = response_data.get('filename')
                                QMessageBox.information(self, "Upload Success", "File uploaded successfully.") # More concise message
                                self.drag_drop_area.setText(f"Uploaded: {self.last_uploaded_file_name}")
                                self.view_upload_history() # Refresh history after successful upload and deletion
                            else:
                                QMessageBox.warning(self, "Upload Failed", f"Failed to upload CSV after retry. Status: {response.status_code}, Response: {response.text}")
                        else:
                            QMessageBox.warning(self, "Delete Failed", f"Failed to delete oldest file. Status: {delete_response.status_code}, Response: {delete_response.text}")
                    else:
                        QMessageBox.information(self, "Upload Cancelled", "Upload cancelled by user.")
                else:
                    QMessageBox.warning(self, "Upload Failed", "Upload limit not reached, but still failed. This should not happen.")
            else:
                QMessageBox.warning(self, "History Fetch Failed", f"Failed to fetch upload history. Status: {history_response.status_code}, Response: {history_response.text}")
        except requests.exceptions.ConnectionError:
            QMessageBox.critical(self, "Error", "Could not connect to the backend server. Please ensure it is running.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred during upload limit management: {e}")

    def view_dataset_details(self):
        selected_items = self.history_list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Selection Error", "Please select a dataset from the history list to view its details.")
            return

        selected_item_text = selected_items[0].text()
        # Extract ID from the string, assuming format "ID: <id>, ..."
        try:
            dataset_id = int(selected_item_text.split(',')[0].split(':')[1].strip())
        except (ValueError, IndexError):
            QMessageBox.critical(self, "Error", "Could not parse dataset ID from selected item.")
            return

        if not self.auth_token:
            QMessageBox.warning(self, "Authentication Error", "No authentication token found. Please log in again.")
            return

        try:
            headers = {'Authorization': f'Bearer {self.auth_token}'}
            response = requests.get(BASE_URL + f"datasets/{dataset_id}/", headers=headers)

            if response.status_code == 200:
                self.show_results_page(dataset_id)
            else:
                QMessageBox.warning(self, "Fetch Failed", f"Failed to fetch dataset details. Status: {response.status_code}, Response: {response.text}")
        except requests.exceptions.ConnectionError:
            QMessageBox.critical(self, "Error", "Could not connect to the backend server. Please ensure it is running.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while fetching dataset details: {e}")