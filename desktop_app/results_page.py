import sys
import datetime
import os
import tempfile
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton, QComboBox, QCheckBox, QHBoxLayout, QScrollArea, QMessageBox, QFrame, QFileDialog
from PyQt5.QtChart import QChart, QChartView, QBarSet, QBarSeries, QPieSeries, QPieSlice, QCategoryAxis, QValueAxis
from PyQt5.QtGui import QPixmap, QPainter, QCursor
from PyQt5.QtCore import Qt
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
import requests
from PyQt5.QtWidgets import QToolTip
BASE_URL = "http://localhost:8000/api/equipment/"

class ResultsPage(QMainWindow):
    def __init__(self, auth_token, dataset_id, login_window, main_app_window):
        super().__init__()
        self.auth_token = auth_token
        self.dataset_id = dataset_id
        self.login_window = login_window
        self.main_app_window = main_app_window
        self.setWindowTitle("Dataset Results (ID: " + str(self.dataset_id) + ")")
        self.setGeometry(100, 100, 1400, 880) # Adjusted window size slightly smaller

        self.dataset = None
        self.available_columns = []
        self.numeric_columns = []

        self.selected_bar_x = 'Equipment Name'
        self.selected_bar_y = [] # Initialize as empty, will be populated with all numeric columns
        self.selected_pie_data = 'Temperature'

        # Initialize UI components that will be populated later
        self.bar_x_combo = QComboBox()
        self.bar_y_checkboxes = []
        self.pie_data_combo = QComboBox()
        self.insights_label = QLabel("Data Insights will appear here.")
        self.bar_chart_view = QChartView()
        self.pie_chart_view = QChartView()

        self.init_ui() # Initialize the UI layout
        self.fetch_dataset_details() # Fetch data and then populate UI controls
        self.show()

    def init_ui(self):
        print("Calling init_ui")
        # Main layout for the entire page
        main_page_layout = QVBoxLayout()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0) # Remove margins for the main layout
        main_layout.setSpacing(0) # Remove spacing for the main layout

        # Header
        header_frame = QFrame() # Create a QFrame for the header
        header_frame.setStyleSheet("background-color: #3498db; color: white; font-size: 20px; font-weight: bold;")
        header_layout = QHBoxLayout(header_frame) # Set the layout for the frame
        header_layout.setContentsMargins(20, 10, 20, 10)
        header_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        app_title = QLabel("Chem CSV Visualizer")
        header_layout.addWidget(app_title)
        header_layout.addStretch()

        logout_button = QPushButton("Logout")
        logout_button.setStyleSheet("background-color: #e74c3c; color: white; padding: 8px 15px; border-radius: 5px; font-size: 14px;")
        logout_button.clicked.connect(self.logout)
        header_layout.addWidget(logout_button)
        main_layout.addWidget(header_frame) # Add the header frame to the main layout

        # Main content area
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        main_layout.addLayout(content_layout)

        # Analysis Results Title
        analysis_title = QLabel("Analysis Results")
        analysis_title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 10px;")
        content_layout.addWidget(analysis_title)

        # Action Buttons
        action_buttons_layout = QHBoxLayout()
        action_buttons_layout.setAlignment(Qt.AlignRight)
        
        restore_button = QPushButton("Restore Default Charts")
        restore_button.setStyleSheet("background-color: #f39c12; color: white; padding: 8px 15px; border-radius: 5px; font-size: 14px;")
        restore_button.clicked.connect(self.restore_default_charts) # Connect this later if needed
        action_buttons_layout.addWidget(restore_button)

        back_button = QPushButton("Back to Home")
        back_button.setStyleSheet("background-color: #34495e; color: white; padding: 8px 15px; border-radius: 5px; font-size: 14px;")
        back_button.clicked.connect(self.back_to_home)
        action_buttons_layout.addWidget(back_button)

        download_pdf_button = QPushButton("Generate PDF")
        download_pdf_button.setStyleSheet("background-color: #2ecc71; color: white; padding: 8px 15px; border-radius: 5px; font-size: 14px;")
        download_pdf_button.clicked.connect(self.generate_pdf_report)
        action_buttons_layout.addWidget(download_pdf_button)
        
        content_layout.addLayout(action_buttons_layout)

        # Two-column layout for charts and insights
        charts_insights_layout = QHBoxLayout()
        charts_insights_layout.setSpacing(20)
        content_layout.addLayout(charts_insights_layout)

        # Left Column: Bar Chart and Controls
        left_column_layout = QVBoxLayout()
        charts_insights_layout.addLayout(left_column_layout)

        # Bar Chart View
        self.bar_chart_view.setStyleSheet("background-color: white; border-radius: 10px; padding: 15px; box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1);")
        left_column_layout.addWidget(self.bar_chart_view)

        # Bar Chart Controls Frame (moved below the chart)
        bar_chart_controls_frame = QFrame()
        bar_chart_controls_frame.setFrameShape(QFrame.StyledPanel)
        bar_chart_controls_frame.setStyleSheet("background-color: white; border-radius: 10px; padding: 15px; box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1);")
        bar_chart_controls_layout = QVBoxLayout(bar_chart_controls_frame)
        bar_chart_x_label = QLabel("Bar Chart X-axis:")
        bar_chart_x_label.setStyleSheet("font-size: 18px;")
        bar_chart_controls_layout.addWidget(bar_chart_x_label)
        self.bar_x_combo.setFixedWidth(250) # Adjusted width for consistency
        self.bar_x_combo.setStyleSheet("font-size: 18px;") # Increased font size for bar chart x-axis combo
        bar_chart_controls_layout.addWidget(self.bar_x_combo) # Add the pre-initialized combo box
        bar_chart_y_label = QLabel("Bar Chart Y-axis (select multiple):")
        bar_chart_y_label.setStyleSheet("font-size: 18px;")
        bar_chart_controls_layout.addWidget(bar_chart_y_label)
        
        self.bar_y_checkboxes_layout = QHBoxLayout() # Create a layout for checkboxes
        bar_chart_controls_layout.addLayout(self.bar_y_checkboxes_layout) # Add the layout to the frame
        left_column_layout.addWidget(bar_chart_controls_frame)

        # Right Column: Data Insights and Pie Chart
        right_column_layout = QVBoxLayout()
        charts_insights_layout.addLayout(right_column_layout)

        # Data Insights Frame
        insights_frame = QFrame()
        insights_frame.setFrameShape(QFrame.StyledPanel)
        insights_frame.setStyleSheet("background-color: white; border-radius: 10px; padding: 15px; box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1);")
        insights_frame.setMaximumHeight(200) # Set maximum height for data insights frame
        insights_layout = QVBoxLayout(insights_frame)
        insights_layout.addWidget(QLabel("Data Insights:"))
        insights_scroll_area = QScrollArea()
        insights_scroll_area.setWidgetResizable(True)
        insights_scroll_area.setWidget(self.insights_label)
        insights_scroll_area.setStyleSheet("border: none; QScrollBar:vertical { width: 20px; } QScrollBar:horizontal { height: 20px; } QScrollBar::handle:vertical { min-height: 30px; } QScrollBar::handle:horizontal { min-width: 30px; }") # Remove border from scroll area and make scrollbar bigger
        insights_layout.addWidget(insights_scroll_area)
        self.insights_label.setWordWrap(True)
        self.insights_label.setStyleSheet("font-size: 16px;") # Increased font size for insights label
        self.insights_label.setTextFormat(Qt.RichText) # Enable rich text rendering for bold tags
        insights_layout.addWidget(self.insights_label)
        right_column_layout.addWidget(insights_frame)

        # Pie Chart Controls Frame
        pie_chart_frame = QFrame()
        pie_chart_frame.setFrameShape(QFrame.StyledPanel)
        pie_chart_frame.setStyleSheet("background-color: white; border-radius: 10px; padding: 15px; box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1);")
        pie_chart_frame.setMaximumHeight(100) # Set maximum height for pie chart controls frame
        pie_chart_layout = QVBoxLayout(pie_chart_frame)
        pie_chart_layout.addWidget(QLabel("Pie Chart Data:"))
        self.pie_data_combo.setFixedWidth(200) # Adjusted width for consistency (smaller)
        self.pie_data_combo.setStyleSheet("font-size: 18px;") # Increased font size for pie chart combo
        pie_chart_layout.addWidget(self.pie_data_combo) # Add the pre-initialized combo box
        right_column_layout.addWidget(pie_chart_frame)

        # Pie Chart View
        self.pie_chart_view.setStyleSheet("background-color: white; border-radius: 10px; padding: 15px; box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1);")
        self.pie_chart_view.setMinimumHeight(400) # Decreased height for pie chart box to make space
        right_column_layout.addWidget(self.pie_chart_view)

        main_layout.addLayout(content_layout) # Add content layout to main layout
        self.central_widget.setLayout(main_layout) # Set the main layout for the central widget

    def fetch_dataset_details(self):
        print("Calling fetch_dataset_details")
        if not self.auth_token:
            QMessageBox.warning(self, "Authentication Error", "No authentication token found. Please log in again.")
            return

        headers = {
            "Authorization": f"Bearer {self.auth_token}"
        }
        try:
            response = requests.get(f"http://127.0.0.1:8000/api/equipment/datasets/{self.dataset_id}/", headers=headers)
            print(f"Response status code: {response.status_code}")
            print(f"Response text: {response.text}")
            if response.status_code == 200:
                self.dataset = response.json()
                print(f"Dataset fetched: {self.dataset}")

                if self.dataset and 'equipment_data' in self.dataset and self.dataset['equipment_data']:
                    # Extract all unique keys as available columns
                    all_keys = set()
                    for item in self.dataset['equipment_data']:
                        all_keys.update(item.keys())
                    self.available_columns = list(all_keys)

                    # Determine numeric columns
                    self.numeric_columns = []
                    for key in self.available_columns:
                        # Check if at least one value for this key is numeric
                        if any(isinstance(item.get(key), (int, float)) for item in self.dataset['equipment_data']):
                            self.numeric_columns.append(key)
                    self.selected_bar_y = self.numeric_columns[:] # Select all numeric columns by default
                else:
                    self.available_columns = []
                    self.numeric_columns = []

                print(f"Available columns: {self.available_columns}")
                print(f"Numeric columns: {self.numeric_columns}")
                self.update_chart_controls() # Populate UI controls after data is fetched
            else:
                QMessageBox.warning(self, "Fetch Failed", f"Failed to fetch dataset details. Status: {response.status_code}, Response: {response.text}")
        except requests.exceptions.ConnectionError:
            QMessageBox.critical(self, "Error", "Could not connect to the backend server. Please ensure it is running.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while fetching dataset details: {e}")

    def update_chart_controls(self):
        print("Updating chart controls")
        # Clear existing items and disconnect signals
        self.bar_x_combo.clear()
        self.pie_data_combo.clear()
        for checkbox in self.bar_y_checkboxes:
            checkbox.stateChanged.disconnect(self.update_charts)
            checkbox.setParent(None)
        self.bar_y_checkboxes.clear()

        # Populate bar_x_combo and pie_data_combo
        self.bar_x_combo.addItems(self.available_columns)
        self.bar_x_combo.setCurrentText(self.selected_bar_x)
        self.bar_x_combo.currentTextChanged.connect(self.update_charts)

        self.pie_data_combo.addItems(self.available_columns)
        self.pie_data_combo.setCurrentText(self.selected_pie_data)
        self.pie_data_combo.currentTextChanged.connect(self.update_charts)

        # Create and add bar_y_checkboxes
        for col in self.numeric_columns:
            checkbox = QCheckBox(col)
            checkbox.setStyleSheet("font-size: 18px;") # Increased font size for checkboxes
            if col in self.selected_bar_y:
                checkbox.setChecked(True)
            checkbox.stateChanged.connect(self.update_charts)
            self.bar_y_checkboxes.append(checkbox)
            self.bar_y_checkboxes_layout.addWidget(checkbox)
        
        self.update_charts() # Initial chart update after controls are populated

    def update_charts(self):
        self.selected_bar_x = self.bar_x_combo.currentText()
        # Invert the logic: include data if the checkbox is NOT checked
        self.selected_bar_y = [cb.text() for cb in self.bar_y_checkboxes if not cb.isChecked()]
        self.selected_pie_data = self.pie_data_combo.currentText()

        self.create_bar_chart()
        self.create_pie_chart()
        self.generate_data_insights()

    def create_bar_chart(self):
        if not self.dataset or not self.dataset['equipment_data'] or not self.selected_bar_x or not self.selected_bar_y:
            # Clear the chart if no data or selections
            self.bar_chart_view.setChart(QChart())
            return

        chart = QChart()
        chart.setTitle("Bar Chart: " + ", ".join(self.selected_bar_y) + " by " + self.selected_bar_x)

        series = QBarSeries()
        bar_sets = {col: QBarSet(col) for col in self.selected_bar_y}

        categories = []
        for item in self.dataset['equipment_data']:
            x_value = str(item.get(self.selected_bar_x, 'N/A'))
            categories.append(x_value)
            for y_col in self.selected_bar_y:
                value = item.get(y_col, 0)
                if isinstance(value, (int, float)):
                    bar_sets[y_col].append(value)
                else:
                    bar_sets[y_col].append(0) # Default to 0 for non-numeric data

        for bar_set in bar_sets.values():
            series.append(bar_set)
        chart.addSeries(series)
        series.hovered.connect(self.show_bar_chart_tooltip)

        # Create X-axis (CategoryAxis for labels)
        axis_x = QCategoryAxis()
        axis_x.setLabelsPosition(QCategoryAxis.AxisLabelsPositionOnValue)
        
        unique_categories = []
        for item in self.dataset['equipment_data']:
            x_value = str(item.get(self.selected_bar_x, 'N/A'))
            if x_value not in unique_categories:
                unique_categories.append(x_value)

        for category in unique_categories:
            axis_x.append(category, unique_categories.index(category))
        
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)

        # Create Y-axis (ValueAxis for numerical data)
        axis_y = QValueAxis()
        axis_y.setTitleText("Value")
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)

        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)

        self.bar_chart_view.setChart(chart)
        self.bar_chart_view.setRenderHint(QPainter.Antialiasing)

    def show_bar_chart_tooltip(self, is_hovering_signal, index_in_barset, barset_obj):
        if is_hovering_signal:
            value = barset_obj.at(index_in_barset)
            category = barset_obj.label()
            x_axis_label = self.bar_x_combo.currentText()
            # Get the actual x-axis category label
            x_category = "N/A"
            if index_in_barset < len(self.dataset['equipment_data']):
                x_category = str(self.dataset['equipment_data'][index_in_barset].get(x_axis_label, "N/A"))

            numerical_columns = ['Flowrate', 'Pressure', 'Temperature']
            tooltip_text = f"{category}: {value:.2f}"

            # Only add the x-axis information if the x_axis_label is not a numerical column
            if x_axis_label not in numerical_columns:
                tooltip_text += f"\n{x_axis_label}: {x_category}"
            QToolTip.showText(QCursor.pos(), tooltip_text, self)
        else:
            QToolTip.hideText()

    def create_pie_chart(self):
        if not self.dataset or not self.dataset['equipment_data'] or not self.selected_pie_data:
            # Clear the chart if no data or selections
            self.pie_chart_view.setChart(QChart())
            return

        chart = QChart()
        chart.setTitle("Pie Chart: Distribution of " + self.selected_pie_data)

        series = QPieSeries()
        dynamic_distribution = self.calculate_dynamic_distribution()
        for category, count in dynamic_distribution.items():
            slice = QPieSlice(category, count)
            slice.setLabel(category) # Set label for each slice
            series.append(slice)
        chart.addSeries(series)
        series.hovered.connect(self.show_pie_chart_tooltip)

        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignRight)

        self.pie_chart_view.setChart(chart)
        self.pie_chart_view.setRenderHint(QPainter.Antialiasing)

    def show_pie_chart_tooltip(self, slice, is_hovering):
        if is_hovering:
            total_value = sum(s.value() for s in slice.series().slices())
            percentage = (slice.value() / total_value) * 100 if total_value > 0 else 0
            tooltip_text = f"{slice.label()}: {slice.value():.0f} ({percentage:.1f}%)"
            QToolTip.showText(QCursor.pos(), tooltip_text, self)
        else:
            QToolTip.hideText()

    def calculate_dynamic_distribution(self):
        dynamic_distribution = {}
        equipment_data = self.dataset['equipment_data']
        if not equipment_data: return {}

        for item in equipment_data:
            value = item.get(self.selected_pie_data)
            if isinstance(value, (int, float)):
                min_val = min(e.get(self.selected_pie_data, 0) for e in equipment_data if isinstance(e.get(self.selected_pie_data), (int, float)))
                max_val = max(e.get(self.selected_pie_data, 0) for e in equipment_data if isinstance(e.get(self.selected_pie_data), (int, float)))
                category = self.get_category(value, min_val, max_val, self.selected_pie_data)
                dynamic_distribution[category] = dynamic_distribution.get(category, 0) + 1
            else:
                dynamic_distribution[value] = dynamic_distribution.get(value, 0) + 1
        return dynamic_distribution

    def get_category(self, value, min_val, max_val, data_type):
        if data_type == 'Temperature':
            if value < 290: return "Cool (<290°C)"
            if value >= 290 and value < 310: return "Warm (290-310°C)"
            if value >= 310 and value < 330: return "Moderately High (310-330°C)"
            if value >= 330 and value < 350: return "High (330-350°C)"
            return "Extremely High (>350°C)"
        else:
            # Generic categorization for other numeric data
            range_val = max_val - min_val
            if range_val == 0: return f"{value:.2f}"
            step = range_val / 4
            if value < min_val + step: return f"<{min_val + step:.2f}"
            if value < min_val + 2 * step: return f"{min_val + step:.2f}-{min_val + 2 * step:.2f}"
            if value < min_val + 3 * step: return f"{min_val + 2 * step:.2f}-{min_val + 3 * step:.2f}"
            return f">{min_val + 3 * step:.2f}"

    def generate_data_insights(self):
        if not self.dataset or not self.dataset['equipment_data']:
            self.insights_label.setText("No data available for insights.")
            return

        equipment_data = self.dataset['equipment_data']
        insights = [f"The dataset contains data for {len(equipment_data)} pieces of equipment."]

        for col in self.numeric_columns:
            values = [item.get(col) for item in equipment_data if isinstance(item.get(col), (int, float))]
            if values:
                min_val = min(values)
                max_val = max(values)
                avg_val = sum(values) / len(values)
                insights.append(f"{col.title()}:<br>  Min={min_val:.2f}<br>  Max={max_val:.2f}<br>  Avg=<b>{avg_val:.2f}</b>") # Made average bold and added newlines

        self.insights_label.setText("<br><br>".join(insights))

    def logout(self):
        self.close()
        self.login_window.show()
        self.main_app_window.hide()

    def restore_default_charts(self):
        self.selected_bar_x = 'Equipment Name'
        # self.selected_bar_y = self.numeric_columns[:] # Removed: Handled by update_chart_controls and update_charts with inverted logic
        self.selected_pie_data = 'Temperature'
        self.update_chart_controls()
        self.update_charts()

    def back_to_home(self):
        self.close()
        self.main_app_window.show()

    def generate_pdf_report(self):
        if not self.dataset:
            QMessageBox.warning(self, "No Data", "No dataset loaded to generate a report.")
            return

        file_name, _ = QFileDialog.getSaveFileName(self, "Save PDF Report", "Chemical_Report.pdf", "PDF Files (*.pdf)")
        if not file_name:
            return

        doc = SimpleDocTemplate(file_name, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Title
        story.append(Paragraph("Chemical Equipment Parameter Report", styles['h1']))
        story.append(Spacer(1, 0.2 * inch))

        # Dataset Details
        story.append(Paragraph(f"<b>Report generated on:</b> {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Paragraph(f"<b>Dataset ID:</b> {self.dataset.get('id', 'N/A')}", styles['Normal']))
        story.append(Paragraph(f"<b>File Name:</b> {self.dataset.get('file_name', 'N/A')}", styles['Normal']))
        story.append(Spacer(1, 0.2 * inch))

        # Data Insights
        story.append(Paragraph("Data Insights", styles['h2']))
        # Ensure insights_label text is properly formatted for PDF
        insights_text = self.insights_label.text().replace('<br>', '<br/>') # reportlab uses <br/> for line breaks
        story.append(Paragraph(insights_text, styles['Normal']))
        story.append(Spacer(1, 0.2 * inch))

        # Capture Bar Chart
        bar_chart_pixmap = QPixmap(self.bar_chart_view.size())
        painter = QPainter(bar_chart_pixmap)
        self.bar_chart_view.render(painter)
        painter.end()
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_bar_chart_file:
            bar_chart_image_path = tmp_bar_chart_file.name
        bar_chart_pixmap.save(bar_chart_image_path)
        story.append(Paragraph("Equipment Metrics", styles['h2']))
        story.append(Image(bar_chart_image_path, width=500, height=300))
        story.append(Spacer(1, 0.2 * inch))

        # Capture Pie Chart
        pie_chart_pixmap = QPixmap(self.pie_chart_view.size())
        painter = QPainter(pie_chart_pixmap)
        self.pie_chart_view.render(painter)
        painter.end()
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_pie_chart_file:
            pie_chart_image_path = tmp_pie_chart_file.name
        pie_chart_pixmap.save(pie_chart_image_path)
        story.append(Paragraph("Flowrate Distribution", styles['h2']))
        story.append(Image(pie_chart_image_path, width=400, height=250))
        story.append(Spacer(1, 0.2 * inch))

        # Raw Data
        story.append(Paragraph("Raw Data", styles['h2']))
        if self.dataset and 'equipment_data' in self.dataset and self.dataset['equipment_data']:
            headers = list(self.dataset['equipment_data'][0].keys())
            data = [headers]
            for item in self.dataset['equipment_data']:
                row = [str(item.get(header, "N/A")) for header in headers]
                data.append(row)

            table_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ])

            table = Table(data)
            table.setStyle(table_style)
            story.append(table)
        else:
            story.append(Paragraph("No raw data available.", styles['Normal']))
        story.append(Spacer(1, 0.2 * inch))

        try:
            doc.build(story)
            QMessageBox.information(self, "PDF Generated", f"{os.path.basename(file_name)} has been successfully generated.")
        except Exception as e:
            QMessageBox.critical(self, "PDF Error", f"Failed to generate PDF: {e}")
        finally:
            # Clean up temporary image files
            if os.path.exists(bar_chart_image_path):
                os.remove(bar_chart_image_path)
            if os.path.exists(pie_chart_image_path):
                os.remove(pie_chart_image_path)