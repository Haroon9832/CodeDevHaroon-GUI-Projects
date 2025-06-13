import sys
import os
import bcrypt
import re


from random import randint
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget, QDialog, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout, QGroupBox,
    QTableWidget, QTableWidgetItem, QDateEdit, QComboBox, QTextEdit, QStatusBar,
    QHeaderView, QMessageBox, QStackedWidget, QToolBar,  QFileDialog, 
    QCheckBox
)
from PyQt6.QtCore import Qt, QDate, QSize
from PyQt6.QtGui import (
    QIcon, QFont, QPalette, QColor, QPixmap, QImage, QBrush, 
    QLinearGradient, QPainter,QAction
)

# Global stylesheet for consistent text color
GLOBAL_STYLESHEET = """
    QWidget {
        color: #000000;  /* Black text */
        font-family: 'Segoe UI', Arial;
    }
    QTableWidget {
        background-color: #FFFFFF;  /* White background */
        gridline-color: #E0E0E0;
        font-size: 12px;
    }
    QHeaderView::section {
        background-color: #2A82DA;
        color: #FFFFFF;
        padding: 4px;
        border: 1px solid #1E6EB8;
        font-weight: bold;
    }
    QGroupBox {
        border: 1px solid #CCCCCC;
        border-radius: 4px;
        margin-top: 1ex;
        font-weight: bold;
        background-color: #F8F8F8;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 3px;
        color: #2A82DA;
    }
    QLineEdit, QTextEdit, QComboBox, QDateEdit {
        background-color: #FFFFFF;
        color: #000000;
        border: 1px solid #CCCCCC;
        padding: 5px;
        border-radius: 3px;
        font-size: 12px;
    }
    QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDateEdit:focus {
        border: 1px solid #2A82DA;
    }
    QTabWidget::pane {
        border: 1px solid #CCCCCC;
        background: #FFFFFF;
    }
    QTabBar::tab {
        background: #E0E0E0;
        color: #000000;
        padding: 8px 15px;
        border: 1px solid #CCCCCC;
        border-bottom: none;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
        font-weight: bold;
    }
    QTabBar::tab:selected {
        background: #FFFFFF;
        border-bottom: 3px solid #2A82DA;
    }
    QPushButton {
        background-color: #2A82DA;
        color: #FFFFFF;
        border: none;
        padding: 8px 15px;
        border-radius: 4px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #1E6EB8;
    }
    QPushButton:pressed {
        background-color: #155799;
    }
    QPushButton:disabled {
        background-color: #A0A0A0;
        color: #E0E0E0;
    }
    QStatusBar {
        background-color: #F0F0F0;
        color: #000000;
        font-size: 11px;
    }
    QToolBar {
        background-color: #F0F0F0;
        border-bottom: 1px solid #CCCCCC;
        padding: 3px;
    }
    QCheckBox {
        spacing: 5px;
    }
    QCheckBox::indicator {
        width: 16px;
        height: 16px;
    }
"""

# =====================
# SECURITY & AUTH SYSTEM
# =====================
import sqlite3
import json
from pathlib import Path

class AuthSystem:
    def __init__(self):
        self.db_path = Path('hospital_auth.db')
        self.reset_tokens = {}
        self.init_database()
    
    def init_database(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password_hash BLOB NOT NULL,
                    email TEXT NOT NULL,
                    security_question TEXT NOT NULL,
                    security_answer BLOB NOT NULL,
                    role TEXT NOT NULL,
                    last_password_change TIMESTAMP,
                    failed_attempts INTEGER DEFAULT 0,
                    lockout_until TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS password_history (
                    username TEXT,
                    password_hash BLOB,
                    changed_at TIMESTAMP,
                    FOREIGN KEY (username) REFERENCES users(username)
                )
            """)
            conn.commit()
    
    def register_user(self, username, password, email, security_question, security_answer):
        if not self.validate_password_strength(password):
            return False, "Password does not meet security requirements"
            
        try:
            hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            hashed_answer = bcrypt.hashpw(security_answer.lower().encode('utf-8'), bcrypt.gensalt())
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO users 
                    (username, password_hash, email, security_question, security_answer, role, last_password_change)
                    VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
                """, (username, hashed_pw, email, security_question, hashed_answer, 
                       'admin' if username == 'admin' else 'reception'))
                
                # Store in password history
                conn.execute("""
                    INSERT INTO password_history (username, password_hash, changed_at)
                    VALUES (?, ?, datetime('now'))
                """, (username, hashed_pw))
                conn.commit()
            return True, "User registered successfully"
        except sqlite3.IntegrityError:
            return False, "Username already exists"
            
    def verify_security_answer(self, username, answer):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT security_answer FROM users WHERE username = ?", (username,))
            result = cursor.fetchone()
            
            if not result:
                return False
                
            stored_answer_hash = result[0]
            return bcrypt.checkpw(answer.lower().encode('utf-8'), stored_answer_hash)
    
    def verify_user(self, username, password):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT password_hash, failed_attempts, lockout_until 
                FROM users WHERE username = ?
            """, (username,))
            result = cursor.fetchone()
            
            if not result:
                return False
                
            stored_hash, failed_attempts, lockout_until = result
            
            # Check account lockout
            if lockout_until and datetime.fromisoformat(lockout_until) > datetime.now():
                return False
            
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                # Reset failed attempts on successful login
                conn.execute("""
                    UPDATE users 
                    SET failed_attempts = 0, lockout_until = NULL 
                    WHERE username = ?
                """, (username,))
                return True
            else:
                # Increment failed attempts
                new_attempts = failed_attempts + 1
                lockout_time = None
                if new_attempts >= 5:
                    lockout_time = (datetime.now() + timedelta(minutes=30)).isoformat()
                
                conn.execute("""
                    UPDATE users 
                    SET failed_attempts = ?, lockout_until = ? 
                    WHERE username = ?
                """, (new_attempts, lockout_time, username))
                return False
    
    def reset_password(self, username, new_password):
        if not self.validate_password_strength(new_password):
            return False, "Password does not meet security requirements"
            
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Check password history
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT password_hash FROM password_history 
                    WHERE username = ? 
                    ORDER BY changed_at DESC LIMIT 5
                """, (username,))
                
                # Prevent reuse of last 5 passwords
                for (old_hash,) in cursor.fetchall():
                    if bcrypt.checkpw(new_password.encode('utf-8'), old_hash):
                        return False, "Cannot reuse recent passwords"
                
                # Update password
                new_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
                conn.execute("""
                    UPDATE users 
                    SET password_hash = ?, last_password_change = datetime('now'),
                        failed_attempts = 0, lockout_until = NULL
                    WHERE username = ?
                """, (new_hash, username))
                
                # Add to history
                conn.execute("""
                    INSERT INTO password_history (username, password_hash, changed_at)
                    VALUES (?, ?, datetime('now'))
                """, (username, new_hash))
                
                # Invalidate all reset tokens for this user
                for token in list(self.reset_tokens.keys()):
                    if self.reset_tokens[token]['username'] == username:
                        self.reset_tokens[token]['used'] = True
                        
                conn.commit()
                return True, "Password updated successfully"
        except Exception as e:
            return False, str(e)
    
    def validate_password_strength(self, password):
        if len(password) < 12:  # Increased minimum length
            return False
        if not re.search(r"[A-Z]", password):  # Uppercase
            return False
        if not re.search(r"[a-z]", password):  # Lowercase
            return False
        if not re.search(r"\d", password):     # Digit
            return False
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):  # Special character
            return False
        return True

# Initialize authentication system
auth_system = AuthSystem()

# =====================
# EMAIL SERVICE
# =====================
class EmailService:
    @staticmethod
    def send_reset_email(email, token):
        """Simulate sending an email with reset token"""
        print(f"Simulating email to {email}")
        print(f"Subject: Password Reset Request")
        print(f"Message: Your reset token is: {token}")
        print("This token is valid for 15 minutes.")
        return True

# =====================
# UI COMPONENTS
# =====================
class GradientHeader(QLabel):
    def __init__(self, text):
        super().__init__(text)
        self.setFixedHeight(60)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        
    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, self.width(), 0)
        gradient.setColorAt(0, QColor("#2A82DA"))
        gradient.setColorAt(1, QColor("#1E6EB8"))
        painter.fillRect(event.rect(), QBrush(gradient))
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(event.rect(), Qt.AlignmentFlag.AlignCenter, self.text())

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hospital Management System - Login")
        self.setFixedSize(500, 400)
        self.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
            }
            QLabel {
                color: #000000;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Header
        header = GradientHeader("Hospital Management System")
        layout.addWidget(header)
        
        # Form elements
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(15)
        
        self.username = QLineEdit()
        self.username.setPlaceholderText("Enter username")
        self.password = QLineEdit()
        self.password.setPlaceholderText("Enter password")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        
        form_layout.addRow("Username:", self.username)
        form_layout.addRow("Password:", self.password)
        
        # Remember me checkbox
        self.remember_me = QCheckBox("Remember me")
        form_layout.addRow("", self.remember_me)
        
        # Buttons
        btn_layout = QHBoxLayout()
        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.attempt_login)
        forgot_btn = QPushButton("Forgot Password?")
        forgot_btn.setStyleSheet("background-color: #E0E0E0; color: #2A82DA;")
        forgot_btn.clicked.connect(self.show_forgot_password)
        
        btn_layout.addWidget(forgot_btn)
        btn_layout.addWidget(login_btn)
        
        layout.addLayout(form_layout)
        layout.addLayout(btn_layout)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #D32F2F;")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
    
    def attempt_login(self):
        username = self.username.text().strip()
        password = self.password.text().strip()
        
        if not username or not password:
            self.status_label.setText("Please enter both username and password")
            return
        
        if auth_system.verify_user(username, password):
            # Fetch user role from database
            with sqlite3.connect(auth_system.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT role FROM users WHERE username = ?", (username,))
                result = cursor.fetchone()
                role = result[0] if result else 'reception'
            # Store login session
            self.logged_in_user = {
                'username': username,
                'role': role,
                'login_time': datetime.now()
            }
            if self.remember_me.isChecked():
                self.save_session()
            self.accept()
        else:
            # Check if account is locked out
            with sqlite3.connect(auth_system.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT lockout_until FROM users WHERE username = ?", (username,))
                result = cursor.fetchone()
                if result and result[0]:
                    lockout_time = datetime.fromisoformat(result[0])
                    if lockout_time > datetime.now():
                        self.status_label.setText("Account is locked out. Please try again later.")
                        return
            self.status_label.setText("Invalid username or password")
    
    def save_session(self):
        # Save session data (for remember me functionality)
        session_data = {
            'username': self.logged_in_user['username'],
            'login_time': self.logged_in_user['login_time'].isoformat()
        }
        with open('session.dat', 'w') as f:
            json.dump(session_data, f)
    
    def show_forgot_password(self):
        self.forgot_dialog = ForgotPasswordDialog()
        self.forgot_dialog.exec()

class ForgotPasswordDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Password Recovery")
        self.setFixedSize(500, 400)
        
        layout = QVBoxLayout()
        header = GradientHeader("Password Recovery")
        layout.addWidget(header)
        
        self.stacked_widget = QStackedWidget()
        
        # Step 1: Username input
        step1_widget = QWidget()
        step1_layout = QVBoxLayout()
        
        step1_layout.addWidget(QLabel("Please enter your username:"))
        self.username_input = QLineEdit()
        step1_layout.addWidget(self.username_input)
        
        next_btn = QPushButton("Next")
        next_btn.clicked.connect(self.verify_username)
        step1_layout.addWidget(next_btn)
        
        step1_widget.setLayout(step1_layout)
        
        # Step 2: Security question
        step2_widget = QWidget()
        step2_layout = QVBoxLayout()
        
        self.security_label = QLabel("")
        self.security_label.setWordWrap(True)
        step2_layout.addWidget(self.security_label)
        
        self.answer_input = QLineEdit()
        step2_layout.addWidget(QLabel("Your answer:"))
        step2_layout.addWidget(self.answer_input)
        
        verify_btn = QPushButton("Verify Answer")
        verify_btn.clicked.connect(self.verify_answer)
        step2_layout.addWidget(verify_btn)
        
        step2_widget.setLayout(step2_layout)
        
        # Step 3: Reset password
        step3_widget = QWidget()
        step3_layout = QVBoxLayout()
        
        step3_layout.addWidget(QLabel("Create a new password:"))
        
        self.new_password = QLineEdit()
        self.new_password.setPlaceholderText("New password")
        self.new_password.setEchoMode(QLineEdit.EchoMode.Password)
        step3_layout.addWidget(self.new_password)
        
        self.confirm_password = QLineEdit()
        self.confirm_password.setPlaceholderText("Confirm password")
        self.confirm_password.setEchoMode(QLineEdit.EchoMode.Password)
        step3_layout.addWidget(self.confirm_password)
        
        self.password_strength = QLabel("")
        self.password_strength.setStyleSheet("color: #D32F2F; font-size: 11px;")
        step3_layout.addWidget(self.password_strength)
        
        reset_btn = QPushButton("Reset Password")
        reset_btn.clicked.connect(self.reset_password)
        step3_layout.addWidget(reset_btn)
        
        step3_widget.setLayout(step3_layout)
        
        # Add steps to stack
        self.stacked_widget.addWidget(step1_widget)
        self.stacked_widget.addWidget(step2_widget)
        self.stacked_widget.addWidget(step3_widget)
        
        layout.addWidget(self.stacked_widget)
        self.setLayout(layout)
    
    def verify_username(self):
        username = self.username_input.text().strip()
        if not username:
            QMessageBox.warning(self, "Error", "Please enter a username")
            return
        
        # Query the database to check if user exists
        with sqlite3.connect(auth_system.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT security_question FROM users WHERE username = ?", (username,))
            result = cursor.fetchone()
            
            if not result:
                QMessageBox.warning(self, "Error", "Username not found")
                return
            
            # Get security question
            question = result[0]
            self.security_label.setText(f"Security Question: {question}")
            self.current_username = username
            self.stacked_widget.setCurrentIndex(1)
    
    def verify_answer(self):
        answer = self.answer_input.text().strip()
        if not answer:
            QMessageBox.warning(self, "Error", "Please enter your answer")
            return
        
        if auth_system.verify_security_answer(self.current_username, answer):
            self.stacked_widget.setCurrentIndex(2)
        else:
            QMessageBox.warning(self, "Error", "Incorrect answer")
    
    def reset_password(self):
        new_pass = self.new_password.text()
        confirm_pass = self.confirm_password.text()
        
        if new_pass != confirm_pass:
            self.password_strength.setText("Passwords do not match")
            return
        
        # Password strength validation
        if not auth_system.validate_password_strength(new_pass):
            self.password_strength.setText("Password does not meet security requirements")
            return
        
        # Reset password
        if auth_system.reset_password(self.current_username, new_pass):
            QMessageBox.information(self, "Success", "Password has been reset successfully")
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Failed to reset password")

class MainWindow(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.setWindowTitle(f"Hospital Management System - Welcome {username}")
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
        
        # Add logout button
        logout_action = QAction(QIcon("icons/logout.png"), "Logout", self)
        logout_action.triggered.connect(self.logout)
        toolbar.addAction(logout_action)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(f"Logged in as {username} | Ready")
        
        # Sample data for demonstration
        self.load_sample_data()
    
    def logout(self):
        self.close()
    
    def load_sample_data(self):
        # Sample patients
        self.patient_module.add_sample_patient("P001", "John Doe", 45, "Male", "123-456-7890", 
                                              "12345-6789012-3", "Diabetes", QDate(2023, 10, 15), 
                                              "Room 101", "Dr. Smith", "sample_photo.jpg")
        
        # Sample doctors
        self.doctor_module.add_sample_doctor("D001", "Dr. Smith", "Cardiology", True, 1500)
        self.doctor_module.add_sample_doctor("D002", "Dr. Johnson", "Pediatrics", False, 1000)
        
        # Sample rooms
        self.ward_module.add_sample_room("101", "General", 150, "Occupied")
        self.ward_module.add_sample_room("102", "Private", 300, "Available")
        self.ward_module.add_sample_room("ICU201", "ICU", 500, "Available")

class PatientManagement(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header = GradientHeader("Patient Management")
        layout.addWidget(header)
        
        # Search bar
        search_layout = QHBoxLayout()
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Search patients by name, ID, or CNIC...")
        search_btn = QPushButton("Search")
        search_layout.addWidget(self.search_field)
        search_layout.addWidget(search_btn)
        layout.addLayout(search_layout)
        
        # Patient table
        self.patient_table = QTableWidget()
        self.patient_table.setColumnCount(10)
        self.patient_table.setHorizontalHeaderLabels([
            "ID", "Name", "Age", "Gender", "Contact", "CNIC", "Diagnosis", 
            "Admit Date", "Room", "Doctor", "Actions"
        ])
        self.patient_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.patient_table.verticalHeader().setVisible(False)
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
            self.patient_table.setItem(row, col, item)
        
        # Add view details button
        view_btn = QPushButton("View Details")
        view_btn.clicked.connect(lambda: self.view_patient_details(row))
        self.patient_table.setCellWidget(row, 10, view_btn)
    
    def add_sample_patient(self, pid, name, age, gender, contact, cnic, diagnosis, admit_date, room, doctor, photo_path):
        data = [pid, name, age, gender, contact, cnic, diagnosis, 
                admit_date.toString("yyyy-MM-dd"), room, doctor]
        self.add_patient_to_table(data)
    
    def view_patient_details(self, row):
        patient_id = self.patient_table.item(row, 0).text()
        QMessageBox.information(self, "Patient Details", f"Showing details for patient {patient_id}")

class PatientFormDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("New Patient Registration")
        self.setFixedSize(700, 700)
        self.photo_path = ""
        
        layout = QVBoxLayout()
        
        # Header
        header = GradientHeader("Patient Registration")
        layout.addWidget(header)
        
        # Main form
        main_layout = QHBoxLayout()
        
        # Left column: Personal details
        details_group = QGroupBox("Personal Information")
        details_layout = QFormLayout()
        
        self.pid = QLineEdit()
        self.name = QLineEdit()
        self.age = QLineEdit()
        self.gender = QComboBox()
        self.gender.addItems(["Male", "Female", "Other"])
        self.contact = QLineEdit()
        self.cnic = QLineEdit()
        self.cnic.setPlaceholderText("XXXXX-XXXXXXX-X")
        self.diagnosis = QTextEdit()
        self.diagnosis.setFixedHeight(80)
        self.admit_date = QDateEdit()
        self.admit_date.setDate(QDate.currentDate())
        
        details_layout.addRow("Patient ID*:", self.pid)
        details_layout.addRow("Full Name*:", self.name)
        details_layout.addRow("Age*:", self.age)
        details_layout.addRow("Gender*:", self.gender)
        details_layout.addRow("Contact Info*:", self.contact)
        details_layout.addRow("CNIC*:", self.cnic)
        details_layout.addRow("Diagnosis:", self.diagnosis)
        details_layout.addRow("Admit Date:", self.admit_date)
        
        details_group.setLayout(details_layout)
        main_layout.addWidget(details_group)
        
        # Right column: Photo and assignment
        right_layout = QVBoxLayout()
        
        # Photo section
        photo_group = QGroupBox("Patient Photo")
        photo_layout = QVBoxLayout()
        
        self.photo_label = QLabel()
        self.photo_label.setFixedSize(200, 200)
        self.photo_label.setStyleSheet("""
            border: 2px dashed #CCCCCC;
            background-color: #F8F8F8;
        """)
        self.photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.photo_label.setText("No photo selected")
        
        upload_btn = QPushButton("Upload Photo")
        upload_btn.clicked.connect(self.upload_photo)
        
        photo_layout.addWidget(self.photo_label)
        photo_layout.addWidget(upload_btn)
        photo_group.setLayout(photo_layout)
        right_layout.addWidget(photo_group)
        
        # Assignment section
        assign_group = QGroupBox("Patient Assignment")
        assign_layout = QFormLayout()
        
        self.room = QComboBox()
        self.room.addItems(["Room 101", "Room 102", "ICU 201", "ICU 202"])
        self.doctor = QComboBox()
        self.doctor.addItems(["Dr. Smith (Cardiology)", "Dr. Johnson (Pediatrics)", "Dr. Williams (Neurology)"])
        
        assign_layout.addRow("Room/Ward:", self.room)
        assign_layout.addRow("Assigned Doctor:", self.doctor)
        
        # Doctor fee payment
        self.fee_paid = QCheckBox("Doctor fee has been paid")
        self.fee_paid.setEnabled(False)
        
        assign_layout.addRow("", self.fee_paid)
        
        # Payment button
        self.pay_btn = QPushButton("Pay Doctor Fee Now")
        self.pay_btn.setEnabled(False)
        self.pay_btn.clicked.connect(self.process_payment)
        assign_layout.addRow("", self.pay_btn)
        
        assign_group.setLayout(assign_layout)
        right_layout.addWidget(assign_group)
        
        main_layout.addLayout(right_layout)
        layout.addLayout(main_layout)
        
        # Connect doctor selection change
        self.doctor.currentIndexChanged.connect(self.update_fee_requirements)
        
        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save Patient")
        save_btn.clicked.connect(self.validate_form)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def upload_photo(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Patient Photo", "", 
            "Images (*.png *.jpg *.jpeg)"
        )
        
        if file_path:
            self.photo_path = file_path
            pixmap = QPixmap(file_path)
            pixmap = pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio, 
                                  Qt.TransformationMode.SmoothTransformation)
            self.photo_label.setPixmap(pixmap)
    
    def update_fee_requirements(self):
        doctor_name = self.doctor.currentText()
        requires_payment = "Dr. Smith" in doctor_name  # Simulate payment requirement
        
        if requires_payment:
            self.fee_paid.setEnabled(True)
            self.pay_btn.setEnabled(True)
            self.fee_paid.setChecked(False)
        else:
            self.fee_paid.setEnabled(False)
            self.pay_btn.setEnabled(False)
            self.fee_paid.setChecked(True)
    
    def process_payment(self):
        # Simulate payment processing
        payment_dialog = QDialog(self)
        payment_dialog.setWindowTitle("Doctor Fee Payment")
        payment_dialog.setFixedSize(400, 300)
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Processing payment for Dr. Smith..."))
        
        # Simulate payment form
        form_layout = QFormLayout()
        card_number = QLineEdit()
        card_number.setPlaceholderText("XXXX-XXXX-XXXX-XXXX")
        expiry = QLineEdit()
        expiry.setPlaceholderText("MM/YY")
        cvv = QLineEdit()
        cvv.setPlaceholderText("CVV")
        
        form_layout.addRow("Card Number:", card_number)
        form_layout.addRow("Expiry Date:", expiry)
        form_layout.addRow("CVV:", cvv)
        
        layout.addLayout(form_layout)
        
        pay_btn = QPushButton("Pay $1500")
        pay_btn.clicked.connect(lambda: self.complete_payment(payment_dialog))
        layout.addWidget(pay_btn)
        
        payment_dialog.setLayout(layout)
        payment_dialog.exec()
    
    def complete_payment(self, dialog):
        self.fee_paid.setChecked(True)
        dialog.accept()
        QMessageBox.information(self, "Success", "Payment processed successfully")
    
    def validate_form(self):
        errors = []
        
        # Required fields
        if not self.pid.text():
            errors.append("Patient ID is required")
        if not self.name.text():
            errors.append("Patient name is required")
        if not self.age.text():
            errors.append("Age is required")
        if not self.contact.text():
            errors.append("Contact information is required")
        if not self.cnic.text():
            errors.append("CNIC is required")
        
        # CNIC format validation
        if self.cnic.text() and not re.match(r"^\d{5}-\d{7}-\d{1}$", self.cnic.text()):
            errors.append("CNIC must be in XXXXX-XXXXXXX-X format")
        
        # Doctor fee payment
        if "Dr. Smith" in self.doctor.currentText() and not self.fee_paid.isChecked():
            errors.append("Doctor fee must be paid for this specialist")
        
        if errors:
            QMessageBox.warning(self, "Validation Error", "\n".join(errors))
            return
        
        self.accept()
    
    def get_data(self):
        return [
            self.pid.text(),
            self.name.text(),
            self.age.text(),
            self.gender.currentText(),
            self.contact.text(),
            self.cnic.text(),
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
        header = GradientHeader("Billing & Cost Management")
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
        self.charges_table.setColumnCount(5)
        self.charges_table.setHorizontalHeaderLabels(["Date", "Service", "Quantity", "Unit Price", "Amount"])
        self.charges_table.verticalHeader().setVisible(False)
        charges_layout.addWidget(self.charges_table)
        
        # Add charge button
        add_charge_btn = QPushButton("Add Charge")
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
        summary_layout.addRow("Tax (10%):", self.tax)
        summary_layout.addRow("Total:", self.total)
        summary_layout.addRow("Payment Status:", self.payment_status)
        summary_layout.addRow("Insurance Details:", self.insurance)
        
        # Generate invoice button
        invoice_btn = QPushButton("Generate Invoice")
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
        header = GradientHeader("Doctor Management")
        layout.addWidget(header)
        
        # Doctor table
        self.doctor_table = QTableWidget()
        self.doctor_table.setColumnCount(6)
        self.doctor_table.setHorizontalHeaderLabels(["ID", "Name", "Specialization", "Requires Fee", "Fee Amount", "Assigned Patients"])
        self.doctor_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.doctor_table.verticalHeader().setVisible(False)
        layout.addWidget(self.doctor_table)
        
        # New doctor button
        new_doctor_btn = QPushButton("Add New Doctor")
        layout.addWidget(new_doctor_btn)
        
        # Schedule section
        schedule_group = QGroupBox("Daily Schedule")
        schedule_layout = QVBoxLayout()
        
        # Schedule table
        self.schedule_table = QTableWidget()
        self.schedule_table.setColumnCount(5)
        self.schedule_table.setHorizontalHeaderLabels(["Time", "Patient", "Room", "Purpose", "Status"])
        self.schedule_table.verticalHeader().setVisible(False)
        schedule_layout.addWidget(self.schedule_table)
        
        # Add appointment button
        add_appt_btn = QPushButton("Add Appointment")
        schedule_layout.addWidget(add_appt_btn)
        
        schedule_group.setLayout(schedule_layout)
        layout.addWidget(schedule_group)
        
        self.setLayout(layout)
    
    def add_sample_doctor(self, did, name, specialization, requires_fee, fee_amount):
        row = self.doctor_table.rowCount()
        self.doctor_table.insertRow(row)
        
        self.doctor_table.setItem(row, 0, QTableWidgetItem(did))
        self.doctor_table.setItem(row, 1, QTableWidgetItem(name))
        self.doctor_table.setItem(row, 2, QTableWidgetItem(specialization))
        self.doctor_table.setItem(row, 3, QTableWidgetItem("Yes" if requires_fee else "No"))
        self.doctor_table.setItem(row, 4, QTableWidgetItem(f"${fee_amount}"))
        self.doctor_table.setItem(row, 5, QTableWidgetItem("2 patients"))

class WardManagement(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header = GradientHeader("Ward & Room Management")
        layout.addWidget(header)
        
        # Room table
        self.room_table = QTableWidget()
        self.room_table.setColumnCount(6)
        self.room_table.setHorizontalHeaderLabels(["Room No.", "Type", "Cost/Day", "Status", "Patient", "Doctor"])
        self.room_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.room_table.verticalHeader().setVisible(False)
        layout.addWidget(self.room_table)
        
        # Room management buttons
        btn_layout = QHBoxLayout()
        new_room_btn = QPushButton("Add New Room")
        update_btn = QPushButton("Update Room Status")
        btn_layout.addWidget(new_room_btn)
        btn_layout.addWidget(update_btn)
        layout.addLayout(btn_layout)
        
        # Occupancy stats
        stats_group = QGroupBox("Occupancy Statistics")
        stats_layout = QGridLayout()
        
        stats_layout.addWidget(QLabel("Total Rooms:"), 0, 0)
        stats_layout.addWidget(QLabel("50"), 0, 1)
        stats_layout.addWidget(QLabel("Occupied:"), 1, 0)
        stats_layout.addWidget(QLabel("35 (70%)"), 1, 1)
        stats_layout.addWidget(QLabel("Available:"), 2, 0)
        stats_layout.addWidget(QLabel("15 (30%)"), 2, 1)
        stats_layout.addWidget(QLabel("ICU Available:"), 3, 0)
        stats_layout.addWidget(QLabel("5"), 3, 1)
        stats_layout.addWidget(QLabel("General Available:"), 4, 0)
        stats_layout.addWidget(QLabel("8"), 4, 1)
        stats_layout.addWidget(QLabel("Private Available:"), 5, 0)
        stats_layout.addWidget(QLabel("2"), 5, 1)
        
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
        self.room_table.setItem(row, 4, QTableWidgetItem("John Doe" if status == "Occupied" else ""))
        self.room_table.setItem(row, 5, QTableWidgetItem("Dr. Smith" if status == "Occupied" else ""))

class ReportsAnalytics(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header = GradientHeader("Reports & Analytics")
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
            "Occupancy Rates",
            "Doctor Performance"
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
        
        layout.addLayout(report_layout)
        layout.addLayout(date_layout)
        layout.addWidget(generate_btn)
        
        # Report display area
        self.report_display = QTableWidget()
        self.report_display.setRowCount(10)
        self.report_display.setColumnCount(5)
        self.report_display.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.report_display.verticalHeader().setVisible(False)
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
    
    # Register admin user
    auth_system.register_user(
        username="admin",
        password="Admin@12345678",
        email="admin@hospital.com",
        security_question="What is your favorite color?",
        security_answer="blue"
    )
    
    # Show login dialog
    login = LoginDialog()
    if login.exec() == QDialog.DialogCode.Accepted:
        main_window = MainWindow(login.username.text())
        main_window.show()
        sys.exit(app.exec())