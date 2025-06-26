import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QLabel, QLineEdit, QFileDialog, QMessageBox, QHBoxLayout, QCheckBox, QSizePolicy
)
from PyQt6.QtCore import Qt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Secure File Encryption Tool")
      
        self.setGeometry(100, 100, 700, 350)
  
 
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15) 

        password_group_layout = QVBoxLayout()
        password_group_layout.setSpacing(5)

        password_label = QLabel("Enter Password (to derive encryption key):")
        password_label.setStyleSheet("font-weight: bold;")
        password_group_layout.addWidget(password_label)

        password_input_layout = QHBoxLayout()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password) # Hide characters
        self.password_input.setPlaceholderText("Enter a strong password (e.g., a passphrase)")
        password_input_layout.addWidget(self.password_input)

        self.show_password_checkbox = QCheckBox("Show Password")
        self.show_password_checkbox.stateChanged.connect(self.toggle_password_visibility)
        password_input_layout.addWidget(self.show_password_checkbox)
        password_group_layout.addLayout(password_input_layout)
        main_layout.addLayout(password_group_layout)

        
        file_selection_group_layout = QVBoxLayout()
        file_selection_group_layout.setSpacing(5)

        file_label = QLabel("File to Encrypt/Decrypt:")
        file_label.setStyleSheet("font-weight: bold;")
        file_selection_group_layout.addWidget(file_label)

        file_path_layout = QHBoxLayout()
        self.file_path_label = QLabel("No file selected.")
        self.file_path_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.file_path_label.setStyleSheet("border: 1px solid #ccc; padding: 5px; border-radius: 5px;")
        file_path_layout.addWidget(self.file_path_label)

        select_file_button = QPushButton("Select File...")
        select_file_button.clicked.connect(self.select_file)
        file_path_layout.addWidget(select_file_button)
        file_selection_group_layout.addLayout(file_path_layout)
        main_layout.addLayout(file_selection_group_layout)


     
        button_layout = QHBoxLayout()
        encrypt_button = QPushButton("Encrypt File")
        encrypt_button.clicked.connect(self.encrypt_file_action)
        decrypt_button = QPushButton("Decrypt File")
        decrypt_button.clicked.connect(self.decrypt_file_action)


        button_style = """
            QPushButton {
                background-color: #4CAF50; /* Green */
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #367c39;
                /* For pressed state, you can use a slightly darker color or a border */
            }
        """

        decrypt_button_style = button_style.replace("#4CAF50", "#008CBA").replace("#45a049", "#007bb5").replace("#367c39", "#006080")

        encrypt_button.setStyleSheet(button_style)
        decrypt_button.setStyleSheet(decrypt_button_style)

        button_layout.addStretch(1) 
        button_layout.addWidget(encrypt_button)
        button_layout.addWidget(decrypt_button)
        button_layout.addStretch(1) 
        main_layout.addLayout(button_layout)

       
        self.status_label = QLabel("Ready. Please select a file and enter a password.")
        self.status_label.setStyleSheet("font-style: italic; color: #555;")
        main_layout.addWidget(self.status_label)

        main_layout.addStretch(1)

        self.setLayout(main_layout)

        self.selected_file_path = None


        self.setStyleSheet("""
            QWidget {
                font-family: "Inter", sans-serif;
                background-color: #f0f2f5;
            }
            QLabel {
                color: #333;
            }
            QLineEdit {
                border: 1px solid #a0a0a0;
                border-radius: 5px;
                padding: 8px;
                background-color: white;
            }
            QMessageBox {
                background-color: #f0f0f0;
                font-family: "Inter", sans-serif;
            }
        """)

    def toggle_password_visibility(self, state):
        """Toggles the visibility of the password input field."""
        if state == Qt.CheckState.Checked.value:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

    def select_file(self):
        """Opens a file dialog to let the user select a file."""
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                self.selected_file_path = selected_files[0]
                self.file_path_label.setText(f"Selected: {os.path.basename(self.selected_file_path)}")
                self.status_label.setText("File selected. Enter password and choose action.")
            else:
                self.selected_file_path = None
                self.file_path_label.setText("No file selected.")
                self.status_label.setText("Please select a file to continue.")

    def derive_key_from_password(self, password: bytes, salt: bytes) -> bytes:
        """
        Derives a Fernet key from a password and salt using PBKDF2HMAC.
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32, 
            salt=salt,
            iterations=480000, 
            backend=default_backend()
        )
        return base64.urlsafe_b64encode(kdf.derive(password))

    def get_password(self):
        """Retrieves the password from the input field."""
        password = self.password_input.text().strip()
        if not password:
            self.show_message("Error", "Please enter a password.", QMessageBox.Icon.Warning)
            return None
        return password.encode('utf-8')

    def encrypt_file_action(self):
        """Handles the encryption process when the encrypt button is clicked."""
        if not self.selected_file_path:
            self.show_message("No File Selected", "Please select a file to encrypt.", QMessageBox.Icon.Warning)
            return

        password = self.get_password()
        if not password:
            return

       
        salt = os.urandom(16)
        fernet_key = self.derive_key_from_password(password, salt)
        fernet = Fernet(fernet_key)

      
        output_file_path, _ = QFileDialog.getSaveFileName(self, "Save Encrypted File As",
                                                        self.selected_file_path + ".encrypted",
                                                        "Encrypted Files (*.encrypted);;All Files (*)")
        if not output_file_path:
            self.status_label.setText("Encryption cancelled by user.")
            return

       
        if os.path.exists(output_file_path):
            reply = QMessageBox.question(self, 'Overwrite File?',
                                         f"The file '{os.path.basename(output_file_path)}' already exists. Do you want to overwrite it?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.No:
                self.status_label.setText("Encryption cancelled to prevent overwrite.")
                return

        self.status_label.setText("Encrypting file... Please wait.")
        QApplication.processEvents()

        try:
            with open(self.selected_file_path, 'rb') as file:
                original_data = file.read()

            encrypted_data = fernet.encrypt(original_data)

            
            final_data_to_write = salt + encrypted_data

            with open(output_file_path, 'wb') as file:
                file.write(final_data_to_write)

            self.status_label.setText(f"File encrypted successfully: {os.path.basename(output_file_path)}")
            self.show_message("Success", "File encrypted successfully! Remember your password!", QMessageBox.Icon.Information)
        except Exception as e:
            self.status_label.setText(f"Encryption failed: {e}")
            self.show_message("Encryption Error", f"An error occurred during encryption: {e}", QMessageBox.Icon.Critical)

    def decrypt_file_action(self):
        """Handles the decryption process when the decrypt button is clicked."""
        if not self.selected_file_path:
            self.show_message("No File Selected", "Please select a file to decrypt.", QMessageBox.Icon.Warning)
            return

        password = self.get_password()
        if not password:
            return

       
        base_name = os.path.basename(self.selected_file_path)
        if base_name.endswith(".encrypted"):
            suggested_name = base_name[:-len(".encrypted")] + ".decrypted"
        else:
            suggested_name = base_name + ".decrypted"

        output_file_path, _ = QFileDialog.getSaveFileName(self, "Save Decrypted File As",
                                                        os.path.join(os.path.dirname(self.selected_file_path), suggested_name),
                                                        "All Files (*)")
        if not output_file_path:
            self.status_label.setText("Decryption cancelled by user.")
            return

        if os.path.exists(output_file_path):
            reply = QMessageBox.question(self, 'Overwrite File?',
                                         f"The file '{os.path.basename(output_file_path)}' already exists. Do you want to overwrite it?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.No:
                self.status_label.setText("Decryption cancelled to prevent overwrite.")
                return

        self.status_label.setText("Decrypting file... Please wait.")
        QApplication.processEvents() 

        try:
            with open(self.selected_file_path, 'rb') as file:
                full_encrypted_data = file.read()

           
            salt = full_encrypted_data[:16]
            encrypted_data_without_salt = full_encrypted_data[16:]

            fernet_key = self.derive_key_from_password(password, salt)
            fernet = Fernet(fernet_key)

            decrypted_data = fernet.decrypt(encrypted_data_without_salt)

            with open(output_file_path, 'wb') as file:
                file.write(decrypted_data)

            self.status_label.setText(f"File decrypted successfully: {os.path.basename(output_file_path)}")
            self.show_message("Success", "File decrypted successfully!", QMessageBox.Icon.Information)
        except Exception as e:
           
            self.status_label.setText(f"Decryption failed: {e}")
            self.show_message("Decryption Error",
                               f"An error occurred during decryption. This might be due to:\n"
                               f"1. Incorrect password.\n"
                               f"2. The file is not a valid encrypted file or is corrupted.\n"
                               f"\nError details: {e}",
                               QMessageBox.Icon.Critical)

    def show_message(self, title, message, icon):
        """Helper function to display a QMessageBox."""
        msg_box = QMessageBox(self)
        msg_box.setIcon(icon)
        msg_box.setText(message)
        msg_box.setWindowTitle(title)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
