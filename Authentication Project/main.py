import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton,
    QHBoxLayout, QVBoxLayout, QFrame, QMessageBox, QStackedWidget
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtSql import QSqlDatabase, QSqlQuery
import hashlib
import re # For stronger password validation

class AuthWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_db()
        self.setWindowTitle("Secure Authentication System")
        self.setMinimumSize(400, 350) # Set a more appropriate minimum size
        # You might need to place 'icon.png' in the same directory as your script
        self.setWindowIcon(QIcon("icon.png")) # Add an application icon

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # Use QStackedWidget to switch between login and registration forms
        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)

        self.login_page = self.create_login_page()
        self.register_page = self.create_register_page()

        self.stacked_widget.addWidget(self.login_page)
        self.stacked_widget.addWidget(self.register_page)

        # Apply a professional stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f2f5;
            }
            QFrame#cardFrame {
                background-color: #ffffff;
                border-radius: 10px;
                box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1); /* Note: True box-shadow is limited in QSS */
                border: 1px solid #e0e0e0; /* Add a subtle border */
            }
            QLabel#titleLabel {
                font-size: 28px;
                font-weight: bold;
                color: #333333;
                margin-bottom: 20px;
            }
            QLabel {
                font-size: 15px;
                color: #555555;
            }
            QLineEdit {
                padding: 10px;
                border: 1px solid #cccccc;
                border-radius: 5px;
                font-size: 15px;
            }
            QLineEdit:focus {
                border: 1px solid #007bff;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                padding: 12px;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
                min-height: 30px; /* Ensure consistent button height */
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton#switchButton {
                background-color: transparent;
                color: #007bff;
                text-decoration: underline;
                font-size: 14px;
                padding: 5px;
                border: none;
                min-height: unset; /* Allow smaller height for text buttons */
            }
            QPushButton#switchButton:hover {
                color: #0056b3;
            }
        """)

        # Start on the login page
        self.stacked_widget.setCurrentWidget(self.login_page)

    def create_login_page(self):
        login_widget = QWidget()
        layout = QVBoxLayout(login_widget)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(15)

        title_label = QLabel("Welcome Back!")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        username_label = QLabel("Username:")
        self.login_username_entry = QLineEdit()
        self.login_username_entry.setPlaceholderText("Enter your username")

        password_label = QLabel("Password:")
        self.login_password_entry = QLineEdit()
        self.login_password_entry.setEchoMode(QLineEdit.EchoMode.Password)
        self.login_password_entry.setPlaceholderText("Enter your password")

        login_button = QPushButton("Login")
        login_button.clicked.connect(self.login_user)

        # --- FIX APPLIED HERE ---
        switch_to_register_button = QPushButton("Don't have an account? Register here.")
        switch_to_register_button.setObjectName("switchButton") # Set objectName separately
        # --- END FIX ---
        switch_to_register_button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.register_page))

        layout.addWidget(username_label)
        layout.addWidget(self.login_username_entry)
        layout.addWidget(password_label)
        layout.addWidget(self.login_password_entry)
        layout.addSpacing(20)
        layout.addWidget(login_button)
        layout.addWidget(switch_to_register_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch() # Push content to top

        # Wrap in a QFrame for a "card" like effect
        card_frame = QFrame()
        card_frame.setObjectName("cardFrame")
        card_frame.setLayout(layout)
        
        main_page_layout = QVBoxLayout()
        main_page_layout.addStretch()
        main_page_layout.addWidget(card_frame)
        main_page_layout.addStretch()

        container_widget = QWidget()
        container_widget.setLayout(main_page_layout)
        return container_widget

    def create_register_page(self):
        register_widget = QWidget()
        layout = QVBoxLayout(register_widget)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(15)

        title_label = QLabel("Create Account")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        username_label = QLabel("Username:")
        self.register_username_entry = QLineEdit()
        self.register_username_entry.setPlaceholderText("Choose a username")

        password_label = QLabel("Password:")
        self.register_password_entry = QLineEdit()
        self.register_password_entry.setEchoMode(QLineEdit.EchoMode.Password)
        self.register_password_entry.setPlaceholderText("Create a strong password")

        confirm_password_label = QLabel("Confirm Password:")
        self.register_confirm_password_entry = QLineEdit()
        self.register_confirm_password_entry.setEchoMode(QLineEdit.EchoMode.Password)
        self.register_confirm_password_entry.setPlaceholderText("Re-enter your password")

        register_button = QPushButton("Register")
        register_button.clicked.connect(self.register_user)

        # --- FIX APPLIED HERE ---
        switch_to_login_button = QPushButton("Already have an account? Login here.")
        switch_to_login_button.setObjectName("switchButton") # Set objectName separately
        # --- END FIX ---
        switch_to_login_button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.login_page))

        layout.addWidget(username_label)
        layout.addWidget(self.register_username_entry)
        layout.addWidget(password_label)
        layout.addWidget(self.register_password_entry)
        layout.addWidget(confirm_password_label)
        layout.addWidget(self.register_confirm_password_entry)
        layout.addSpacing(20)
        layout.addWidget(register_button)
        layout.addWidget(switch_to_login_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch() # Push content to top

        # Wrap in a QFrame for a "card" like effect
        card_frame = QFrame()
        card_frame.setObjectName("cardFrame")
        card_frame.setLayout(layout)

        main_page_layout = QVBoxLayout()
        main_page_layout.addStretch()
        main_page_layout.addWidget(card_frame)
        main_page_layout.addStretch()

        container_widget = QWidget()
        container_widget.setLayout(main_page_layout)
        return container_widget

    def init_db(self):
        db = QSqlDatabase.addDatabase("QSQLITE")
        db.setDatabaseName("user_auth.db") # Changed database name for clarity
        if not db.open():
            QMessageBox.critical(self, "Database Error", "Failed to connect to the database. Please check permissions.")
            return

        query = QSqlQuery()
        query.prepare("""
            CREATE TABLE IF NOT EXISTS users (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        """)
        if not query.exec():
            QMessageBox.critical(self, "Database Error", f"Failed to create table: {query.lastError().text()}")
        else:
            print("Database table 'users' ensured.")

    def register_user(self):
        username = self.register_username_entry.text().strip()
        raw_password = self.register_password_entry.text()
        confirm_password = self.register_confirm_password_entry.text()

        if not username or not raw_password or not confirm_password:
            QMessageBox.warning(self, "Input Error", "All fields are required for registration.")
            return

        if raw_password != confirm_password:
            QMessageBox.warning(self, "Input Error", "Passwords do not match. Please re-enter.")
            self.register_confirm_password_entry.clear()
            return

        # Password strength validation
        if len(raw_password) < 8:
            QMessageBox.warning(self, "Password Weak", "Password must be at least 8 characters long.")
            return
        if not re.search(r"[A-Z]", raw_password):
            QMessageBox.warning(self, "Password Weak", "Password must contain at least one uppercase letter.")
            return
        if not re.search(r"[a-z]", raw_password):
            QMessageBox.warning(self, "Password Weak", "Password must contain at least one lowercase letter.")
            return
        if not re.search(r"[0-9]", raw_password):
            QMessageBox.warning(self, "Password Weak", "Password must contain at least one digit.")
            return
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", raw_password):
            QMessageBox.warning(self, "Password Weak", "Password must contain at least one special character.")
            return

        password_hash = self.hash_password(raw_password)

        query = QSqlQuery()
        query.prepare("INSERT INTO users (username, password_hash) VALUES (?, ?)")
        query.addBindValue(username)
        query.addBindValue(password_hash)

        if query.exec():
            QMessageBox.information(self, "Success", "Registration successful! You can now log in.")
            self.register_username_entry.clear()
            self.register_password_entry.clear()
            self.register_confirm_password_entry.clear()
            self.stacked_widget.setCurrentWidget(self.login_page) # Switch to login after successful registration
        else:
            error_text = query.lastError().text()
            if "UNIQUE constraint failed" in error_text:
                QMessageBox.critical(self, "Registration Failed", "Username already exists. Please choose a different one.")
            else:
                QMessageBox.critical(self, "Registration Failed", f"An error occurred: {error_text}")

    def login_user(self):
        username = self.login_username_entry.text().strip()
        raw_password = self.login_password_entry.text()

        if not username or not raw_password:
            QMessageBox.warning(self, "Input Error", "Please enter both username and password.")
            return

        password_hash = self.hash_password(raw_password)

        query = QSqlQuery()
        query.prepare("SELECT password_hash FROM users WHERE username = ?")
        query.addBindValue(username)

        if query.exec() and query.next():
            stored_password_hash = query.value(0)
            if stored_password_hash == password_hash:
                QMessageBox.information(self, "Login Success", f"Welcome, {username}! You are logged in.")
                # Here you would typically open your main application window
                self.close() # Close the authentication window on successful login
            else:
                QMessageBox.warning(self, "Login Failed", "Incorrect username or password.")
        else:
            QMessageBox.warning(self, "Login Failed", "Incorrect username or password.")
        
        # Clear fields after attempt
        self.login_username_entry.clear()
        self.login_password_entry.clear()

    def hash_password(self, password):
        """Hashes the password using SHA256."""
        return hashlib.sha256(password.encode()).hexdigest()

    def closeEvent(self, event):
        """Closes database connection when the window is closed."""
        db = QSqlDatabase.database()
        if db.isOpen():
            db.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    auth_window = AuthWindow()
    auth_window.show()
    sys.exit(app.exec())