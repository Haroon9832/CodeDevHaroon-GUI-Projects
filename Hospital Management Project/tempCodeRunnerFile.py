import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget, QDialog, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout, QGroupBox,
    QTableWidget, QTableWidgetItem, QDateEdit, QComboBox, QTextEdit, QStatusBar,
    QHeaderView, QMessageBox, QStackedWidget, QToolBar
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QIcon, QFont, QPalette, QColor,QAction

# Global stylesheet for consistent text color
GLOBAL_STYLESHEET = """
    QWidget {
        color: #000000;  /* Black text */
    }
    QTableWidget {
        background-color: #FFFFFF;  /* White background */
        gridline-color: #E0E0E0;
    }
    QHeaderView::section {
        background-color: #F0F0F0;
        color: #000000;
        padding: 4px;
        border: 1px solid #E0E0E0;
    }
    QGroupBox {
        border: 1px solid #CCCCCC;
        border-radius: 4px;
        margin-top: 1ex;
        font-weight: bold;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 3px;
    }
    QLineEdit, QTextEdit, QComboBox, QDateEdit {
        background-color: #FFFFFF;
        color: #000000;
        border: 1px solid #CCCCCC;
        padding: 3px;
        border-radius: 3px;
    }
    QTabWidget::pane {
        border: 1px solid #CCCCCC;
        background: #FFFFFF;
    }
    QTabBar::tab {
        background: #F0F0F0;
        color: #000000;
        padding: 8px 12px;
        border: 1px solid #CCCCCC;
        border-bottom: none;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
    }
    QTabBar::tab:selected {
        background: #FFFFFF;
        border-bottom: 2px solid #2A82DA;
    }
    QPushButton {
        background-color: #F0F0F0;
        color: #000000;
        border: 1px solid #CCCCCC;
        padding: 5px 12px;
        border-radius: 4px;
    }
    QPushButton:hover {
        background-color: #E0E0E0;
    }
    QPushButton:pressed {
        background-color: #D0D0D0;
    }
"""

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hospital Management System - Login")
        self.setFixedSize(400, 200)
        self.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
            }
            QLabel {
                font-weight: bold;
                color: #000000;
            }
        """)
        
        layout = QVBoxLayout()
        
        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")
        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        
        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.attempt_login)
        
        layout.addWidget(QLabel("Admin/Receptionist Login"))
        layout.addWidget(self.username)
        layout.addWidget(self.password)
        layout.addWidget(login_btn)
        
        self.setLayout(layout)
    
    def attempt_login(self):
        if self.username.text() and self.password.text():
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Invalid credentials")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hospital Management System")
        self.setMinimumSize(1200, 800)
        self.setStyleSheet(GLOBAL_STYLESHEET)
        
        # Create main widgets
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Create modules
        self.patient_module = PatientManagement()
        self.billing_module = BillingManagement()
        self.doctor_module = DoctorManagement()
        self.ward_module = WardManagement()
        self.reports_module = ReportsAnalytics()
        
        # Add tabs
        self.tabs.addTab(self.patient_module, "Patient Management")
        self.tabs.addTab(self.billing_module, "Billing & Cost")
        self.tabs.addTab(self.doctor_module, "Doctor Management")
        self.tabs.addTab(self.ward_module, "Ward/Room Management")
        self.tabs.addTab(self.reports_module, "Reports & Analytics")
        
        # Create toolbar
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # Toolbar actions
        self.new_patient_action = QAction(QIcon("icons/new_patient.png"), "New Patient", self)
        self.new_patient_action.triggered.connect(self.patient_module.show_new_patient_form)
        toolbar.addAction(self.new_patient_action)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Sample data for demonstration
        self.load_sample_data()
    
    def load_sample_data(self):
        # Sample patients
        self.patient_module.add_sample_patient("P001", "John Doe", 45, "Male", "123-456-7890", 
                                              "Diabetes", QDate(2023, 10, 15), "Room 101", "Dr. Smith")
        
        # Sample doctors
        self.doctor_module.add_sample_doctor("D001", "Dr. Smith", "Cardiology")
        
        # Sample rooms
        self.ward_module.add_sample_room("101", "General", 150, "Available")

class PatientManagement(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("Patient Management")
        header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header.setStyleSheet("color: #000000;")
        layout.addWidget(header)
        
        # Search bar
        search_layout = QHBoxLayout()
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Search patients...")
        search_btn = QPushButton("Search")
        search_layout.addWidget(self.search_field)
        search_layout.addWidget(search_btn)
        layout.addLayout(search_layout)
        
        # Patient table
        self.patient_table = QTableWidget()
        self.patient_table.setColumnCount(9)
        self.patient_table.setHorizontalHeaderLabels([
            "ID", "Name", "Age", "Gender", "Contact", "Diagnosis", 
            "Admit Date", "Room", "Doctor", "Actions"
        ])
        self.patient_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.patient_table.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                color: #000000;
            }
            QHeaderView::section {
                background-color: #F0F0F0;
                color: #000000;
            }
        """)
        layout.addWidget(self.patient_table)
        
        # New patient button
        new_patient_btn = QPushButton("Register New Patient")
        new_patient_btn.clicked.connect(self.show_new_patient_form)
        layout.addWidget(new_patient_btn)
        
        self.setLayout(layout)
    
    def show_new_patient_form(self):
        self.form_dialog = PatientFormDialog()
        if self.form_dialog.exec() == QDialog.DialogCode.Accepted:
            patient_data = self.form_dialog.get_data()
            self.add_patient_to_table(patient_data)
    
    def add_patient_to_table(self, data):
        row = self.patient_table.rowCount()
        self.patient_table.insertRow(row)
        
        for col, value in enumerate(data):
            item = QTableWidgetItem(str(value))
            item.setForeground(QColor(0, 0, 0))  # Black text
            self.patient_table.setItem(row, col, item)
        
        # Add discharge button
        discharge_btn = QPushButton("Discharge")
        discharge_btn.setStyleSheet("color: #000000;")
        discharge_btn.clicked.connect(lambda: self.discharge_patient(row))
        self.patient_table.setCellWidget(row, 9, discharge_btn)
    
    def add_sample_patient(self, pid, name, age, gender, contact, diagnosis, admit_date, room, doctor):
        data = [pid, name, age, gender, contact, diagnosis, admit_date.toString("yyyy-MM-dd"), room, doctor]
        self.add_patient_to_table(data)
    
    def discharge_patient(self, row):
        patient_id = self.patient_table.item(row, 0).text()
        QMessageBox.information(self, "Discharge", f"Patient {patient_id} discharged")
        self.patient_table.removeRow(row)

class PatientFormDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("New Patient Registration")
        self.setFixedSize(500, 600)
        self.setStyleSheet("background-color: #FFFFFF; color: #000000;")
        
        layout = QVBoxLayout()
        
        # Form elements
        form = QFormLayout()
        
        self.pid = QLineEdit()
        self.name = QLineEdit()
        self.age = QLineEdit()
        self.gender = QComboBox()
        self.gender.addItems(["Male", "Female", "Other"])
        self.contact = QLineEdit()
        self.diagnosis = QTextEdit()
        self.diagnosis.setFixedHeight(80)
        self.admit_date = QDateEdit()
        self.admit_date.setDate(QDate.currentDate())
        self.room = QComboBox()
        self.room.addItems(["Room 101", "Room 102", "ICU 201", "ICU 202"])
        self.doctor = QComboBox()
        self.doctor.addItems(["Dr. Smith", "Dr. Johnson", "Dr. Williams"])
        
        form.addRow("Patient ID:", self.pid)
        form.addRow("Full Name:", self.name)
        form.addRow("Age:", self.age)
        form.addRow("Gender:", self.gender)
        form.addRow("Contact Info:", self.contact)
        form.addRow("Diagnosis:", self.diagnosis)
        form.addRow("Admit Date:", self.admit_date)
        form.addRow("Room/Ward:", self.room)
        form.addRow("Assigned Doctor:", self.doctor)
        
        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.validate_form)
        save_btn.setStyleSheet("color: #000000;")
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("color: #000000;")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(form)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def validate_form(self):
        if not self.pid.text() or not self.name.text():
            QMessageBox.warning(self, "Error", "Patient ID and Name are required!")
            return
        
        self.accept()
    
    def get_data(self):
        return [
            self.pid.text(),
            self.name.text(),
            self.age.text(),
            self.gender.currentText(),
            self.contact.text(),
            self.diagnosis.toPlainText(),
            self.admit_date.date(),
            self.room.currentText(),
            self.doctor.currentText()
        ]

class BillingManagement(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("Billing & Cost Management")
        header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header.setStyleSheet("color: #000000;")
        layout.addWidget(header)
        
        # Patient selection
        patient_layout = QHBoxLayout()
        patient_layout.addWidget(QLabel("Select Patient:"))
        self.patient_select = QComboBox()
        self.patient_select.addItems(["P001 - John Doe", "P002 - Jane Smith"])
        patient_layout.addWidget(self.patient_select)
        layout.addLayout(patient_layout)
        
        # Billing details in tabs
        billing_tabs = QTabWidget()
        
        # Charges tab
        charges_tab = QWidget()
        charges_layout = QVBoxLayout()
        
        # Charges table
        self.charges_table = QTableWidget()
        self.charges_table.setColumnCount(4)
        self.charges_table.setHorizontalHeaderLabels(["Date", "Service", "Quantity", "Amount"])
        self.charges_table.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                color: #000000;
            }
            QHeaderView::section {
                background-color: #F0F0F0;
                color: #000000;
            }
        """)
        charges_layout.addWidget(self.charges_table)
        
        # Add charge button
        add_charge_btn = QPushButton("Add Charge")
        add_charge_btn.setStyleSheet("color: #000000;")
        charges_layout.addWidget(add_charge_btn)
        charges_tab.setLayout(charges_layout)
        
        # Summary tab
        summary_tab = QWidget()
        summary_layout = QFormLayout()
        
        self.subtotal = QLabel("$0.00")
        self.tax = QLabel("$0.00")
        self.total = QLabel("$0.00")
        self.payment_status = QComboBox()
        self.payment_status.addItems(["Unpaid", "Partially Paid", "Paid"])
        self.insurance = QTextEdit()
        
        summary_layout.addRow("Subtotal:", self.subtotal)
        summary_layout.addRow("Tax:", self.tax)
        summary_layout.addRow("Total:", self.total)
        summary_layout.addRow("Payment Status:", self.payment_status)
        summary_layout.addRow("Insurance Details:", self.insurance)
        
        # Generate invoice button
        invoice_btn = QPushButton("Generate Invoice")
        invoice_btn.setStyleSheet("color: #000000;")
        summary_layout.addRow(invoice_btn)
        
        summary_tab.setLayout(summary_layout)
        
        billing_tabs.addTab(charges_tab, "Itemized Charges")
        billing_tabs.addTab(summary_tab, "Billing Summary")
        
        layout.addWidget(billing_tabs)
        self.setLayout(layout)

class DoctorManagement(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("Doctor Management")
        header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header.setStyleSheet("color: #000000;")
        layout.addWidget(header)
        
        # Doctor table
        self.doctor_table = QTableWidget()
        self.doctor_table.setColumnCount(4)
        self.doctor_table.setHorizontalHeaderLabels(["ID", "Name", "Specialization", "Assigned Patients"])
        self.doctor_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.doctor_table.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                color: #000000;
            }
            QHeaderView::section {
                background-color: #F0F0F0;
                color: #000000;
            }
        """)
        layout.addWidget(self.doctor_table)
        
        # New doctor button
        new_doctor_btn = QPushButton("Add New Doctor")
        new_doctor_btn.setStyleSheet("color: #000000;")
        layout.addWidget(new_doctor_btn)
        
        # Schedule section
        schedule_group = QGroupBox("Daily Schedule")
        schedule_layout = QVBoxLayout()
        
        # Schedule table
        self.schedule_table = QTableWidget()
        self.schedule_table.setColumnCount(4)
        self.schedule_table.setHorizontalHeaderLabels(["Time", "Patient", "Room", "Purpose"])
        self.schedule_table.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                color: #000000;
            }
            QHeaderView::section {
                background-color: #F0F0F0;
                color: #000000;
            }
        """)
        schedule_layout.addWidget(self.schedule_table)
        
        # Add appointment button
        add_appt_btn = QPushButton("Add Appointment")
        add_appt_btn.setStyleSheet("color: #000000;")
        schedule_layout.addWidget(add_appt_btn)
        
        schedule_group.setLayout(schedule_layout)
        layout.addWidget(schedule_group)
        
        self.setLayout(layout)
    
    def add_sample_doctor(self, did, name, specialization):
        row = self.doctor_table.rowCount()
        self.doctor_table.insertRow(row)
        
        self.doctor_table.setItem(row, 0, QTableWidgetItem(did))
        self.doctor_table.setItem(row, 1, QTableWidgetItem(name))
        self.doctor_table.setItem(row, 2, QTableWidgetItem(specialization))
        self.doctor_table.setItem(row, 3, QTableWidgetItem("2 patients"))

class WardManagement(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("Ward & Room Management")
        header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header.setStyleSheet("color: #000000;")
        layout.addWidget(header)
        
        # Room table
        self.room_table = QTableWidget()
        self.room_table.setColumnCount(5)
        self.room_table.setHorizontalHeaderLabels(["Room No.", "Type", "Cost/Day", "Status", "Patient"])
        self.room_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.room_table.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                color: #000000;
            }
            QHeaderView::section {
                background-color: #F0F0F0;
                color: #000000;
            }
        """)
        layout.addWidget(self.room_table)
        
        # Room management buttons
        btn_layout = QHBoxLayout()
        new_room_btn = QPushButton("Add New Room")
        new_room_btn.setStyleSheet("color: #000000;")
        update_btn = QPushButton("Update Room Status")
        update_btn.setStyleSheet("color: #000000;")
        btn_layout.addWidget(new_room_btn)
        btn_layout.addWidget(update_btn)
        layout.addLayout(btn_layout)
        
        # Occupancy stats
        stats_group = QGroupBox("Occupancy Statistics")
        stats_layout = QGridLayout()
        
        stats_layout.addWidget(QLabel("Total Rooms:"), 0, 0)
        stats_layout.addWidget(QLabel("50"), 0, 1)
        stats_layout.addWidget(QLabel("Occupied:"), 1, 0)
        stats_layout.addWidget(QLabel("35"), 1, 1)
        stats_layout.addWidget(QLabel("Available:"), 2, 0)
        stats_layout.addWidget(QLabel("15"), 2, 1)
        stats_layout.addWidget(QLabel("ICU Available:"), 3, 0)
        stats_layout.addWidget(QLabel("5"), 3, 1)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        self.setLayout(layout)
    
    def add_sample_room(self, room_no, room_type, cost, status):
        row = self.room_table.rowCount()
        self.room_table.insertRow(row)
        
        self.room_table.setItem(row, 0, QTableWidgetItem(room_no))
        self.room_table.setItem(row, 1, QTableWidgetItem(room_type))
        self.room_table.setItem(row, 2, QTableWidgetItem(f"${cost}"))
        self.room_table.setItem(row, 3, QTableWidgetItem(status))
        self.room_table.setItem(row, 4, QTableWidgetItem(""))

class ReportsAnalytics(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("Reports & Analytics")
        header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header.setStyleSheet("color: #000000;")
        layout.addWidget(header)
        
        # Report selection
        report_layout = QHBoxLayout()
        report_layout.addWidget(QLabel("Select Report:"))
        self.report_select = QComboBox()
        self.report_select.addItems([
            "Daily Admissions/Discharges",
            "Patient Count by Diagnosis",
            "Department-wise Statistics",
            "Billing Summary",
            "Occupancy Rates"
        ])
        report_layout.addWidget(self.report_select)
        
        # Date range
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("From:"))
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        date_layout.addWidget(self.start_date)
        date_layout.addWidget(QLabel("To:"))
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        date_layout.addWidget(self.end_date)
        
        # Generate button
        generate_btn = QPushButton("Generate Report")
        generate_btn.setStyleSheet("color: #000000;")
        
        layout.addLayout(report_layout)
        layout.addLayout(date_layout)
        layout.addWidget(generate_btn)
        
        # Report display area
        self.report_display = QTableWidget()
        self.report_display.setRowCount(10)
        self.report_display.setColumnCount(5)
        self.report_display.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                color: #000000;
            }
            QHeaderView::section {
                background-color: #F0F0F0;
                color: #000000;
            }
        """)
        layout.addWidget(self.report_display)
        
        # Chart placeholder
        chart_label = QLabel("Chart visualization area")
        chart_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chart_label.setStyleSheet("""
            background-color: #FFFFFF;
            border: 1px solid #CCCCCC;
            min-height: 300px;
            color: #000000;
            font-style: italic;
        """)
        layout.addWidget(chart_label)
        
        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Apply modern style with black text on white backgrounds
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))
    palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
    app.setPalette(palette)
    
    # Apply global stylesheet
    app.setStyleSheet(GLOBAL_STYLESHEET)
    
    # Show login dialog
    login = LoginDialog()
    if login.exec() == QDialog.DialogCode.Accepted:
        main_window = MainWindow()
        main_window.show()
        sys.exit(app.exec())