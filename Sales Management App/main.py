import sys
import sqlite3
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QMessageBox, QHeaderView, QInputDialog,
    QDialog, QDialogButtonBox, QFormLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QBrush, QIntValidator, QDoubleValidator

class DatabaseManager:
    """
    Manages all interactions with the SQLite database.
    Handles connection, table creation, and CRUD operations for products and sales.
    """
    def __init__(self, db_name="retail_data.db"):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()
        self.add_sample_data() # Call to add sample data on initialization

    def connect(self):
        """Establishes a connection to the SQLite database."""
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            print(f"Connected to database: {self.db_name}")
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            QMessageBox.critical(None, "Database Error", f"Could not connect to database: {e}")
            sys.exit(1) # Exit if cannot connect to database

    def close(self):
        """Closes the database connection."""
        if self.conn:
            self.conn.close()
            print("Database connection closed.")

    def create_tables(self):
        """Creates the products and sales tables if they do not exist."""
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    stock INTEGER NOT NULL,
                    price REAL NOT NULL,
                    cost REAL NOT NULL,
                    color TEXT
                )
            """)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS sales (
                    sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    product_name TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    unit_price REAL NOT NULL,
                    cost_price REAL NOT NULL,
                    total_price REAL NOT NULL,
                    profit_loss REAL NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products (id)
                )
            """)
            self.conn.commit()
            print("Tables checked/created successfully.")
        except sqlite3.Error as e:
            print(f"Error creating tables: {e}")
            QMessageBox.critical(None, "Database Error", f"Could not create tables: {e}")
            sys.exit(1)

    def add_sample_data(self):
        """
        Adds sample data to the products and sales tables if they are empty.
        This is for temporary demonstration purposes.
        """
        self.cursor.execute("SELECT COUNT(*) FROM products")
        if self.cursor.fetchone()[0] == 0:
            print("Adding sample data...")
            # Sample Products
            products_to_add = [
                ("Laptop Pro", 50, 1200.00, 950.00, "Silver"),
                ("Wireless Mouse", 200, 25.50, 15.00, "Black"),
                ("Mechanical Keyboard", 75, 80.00, 50.00, "White"),
                ("External Hard Drive", 120, 70.00, 45.00, "Blue"),
                ("USB-C Hub", 150, 35.00, 20.00, "Grey")
            ]
            for name, stock, price, cost, color in products_to_add:
                product_id = self.add_product(name, stock, price, cost, color)
                # Add some sample sales for the newly added products
                if product_id:
                    if name == "Laptop Pro":
                        self.record_sale(product_id, name, 2, price, cost, 2 * price, (price - cost) * 2)
                        self.record_sale(product_id, name, 1, price, cost, 1 * price, (price - cost) * 1)
                        self.update_product_stock(product_id, stock - 3) # Update stock after sample sales
                    elif name == "Wireless Mouse":
                        self.record_sale(product_id, name, 5, price, cost, 5 * price, (price - cost) * 5)
                        self.update_product_stock(product_id, stock - 5) # Update stock after sample sales
            self.conn.commit()
            print("Sample data added.")
        else:
            print("Database already contains data, skipping sample data insertion.")

    # --- Product Operations ---
    def add_product(self, name, stock, price, cost, color):
        """Inserts a new product into the database."""
        try:
            self.cursor.execute("INSERT INTO products (name, stock, price, cost, color) VALUES (?, ?, ?, ?, ?)",
                                (name, stock, price, cost, color))
            self.conn.commit()
            return self.cursor.lastrowid # Return the ID of the newly inserted product
        except sqlite3.IntegrityError:
            # QMessageBox.warning(None, "Duplicate Product", f"A product named '{name}' already exists.")
            return None # Return None if duplicate, warning handled by calling UI
        except sqlite3.Error as e:
            print(f"Error adding product: {e}")
            QMessageBox.critical(None, "Database Error", f"Error adding product: {e}")
            return None

    def get_products(self, filter_text=""):
        """Retrieves products from the database, optionally filtered by name."""
        try:
            if filter_text:
                self.cursor.execute("SELECT id, name, stock, price, cost, color FROM products WHERE name LIKE ?", 
                                    (f"%{filter_text}%",))
            else:
                self.cursor.execute("SELECT id, name, stock, price, cost, color FROM products")
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching products: {e}")
            QMessageBox.critical(None, "Database Error", f"Error fetching products: {e}")
            return []

    def get_product_by_id(self, product_id):
        """Retrieves a single product by its ID."""
        try:
            self.cursor.execute("SELECT id, name, stock, price, cost, color FROM products WHERE id = ?", (product_id,))
            row = self.cursor.fetchone()
            if row:
                return {"id": row[0], "name": row[1], "stock": row[2], "price": row[3], "cost": row[4], "color": row[5]}
            return None
        except sqlite3.Error as e:
            print(f"Error fetching product by ID: {e}")
            QMessageBox.critical(None, "Database Error", f"Error fetching product: {e}")
            return None

    def update_product(self, product_id, name, stock, price, cost, color):
        """Updates an existing product in the database."""
        try:
            self.cursor.execute("""
                UPDATE products SET name = ?, stock = ?, price = ?, cost = ?, color = ?
                WHERE id = ?
            """, (name, stock, price, cost, color, product_id))
            self.conn.commit()
            return self.cursor.rowcount > 0 # Return True if updated, False otherwise
        except sqlite3.IntegrityError:
            # QMessageBox.warning(None, "Duplicate Product Name", f"Another product named '{name}' already exists.")
            return False # Return False if duplicate, warning handled by calling UI
        except sqlite3.Error as e:
            print(f"Error updating product: {e}")
            QMessageBox.critical(None, "Database Error", f"Error updating product: {e}")
            return False

    def update_product_stock(self, product_id, new_stock):
        """Updates only the stock of a product."""
        try:
            self.cursor.execute("UPDATE products SET stock = ? WHERE id = ?", (new_stock, product_id))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error updating product stock: {e}")
            QMessageBox.critical(None, "Database Error", f"Error updating stock: {e}")
            return False

    def delete_product(self, product_id):
        """Deletes a product from the database."""
        try:
            self.cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error deleting product: {e}")
            QMessageBox.critical(None, "Database Error", f"Error deleting product: {e}")
            return False

    # --- Sales Operations ---
    def record_sale(self, product_id, product_name, quantity, unit_price, cost_price, total_price, profit_loss):
        """Records a new sale transaction in the database."""
        try:
            self.cursor.execute("""
                INSERT INTO sales (product_id, product_name, quantity, unit_price, cost_price, total_price, profit_loss)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (product_id, product_name, quantity, unit_price, cost_price, total_price, profit_loss))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error recording sale: {e}")
            QMessageBox.critical(None, "Database Error", f"Error recording sale: {e}")
            return None

    def get_sales_history(self):
        """Retrieves all sales records from the database."""
        try:
            self.cursor.execute("SELECT sale_id, product_name, quantity, unit_price, cost_price, total_price, profit_loss FROM sales ORDER BY timestamp DESC")
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching sales history: {e}")
            QMessageBox.critical(None, "Database Error", f"Error fetching sales history: {e}")
            return []

    def clear_sales_history(self):
        """Deletes all records from the sales table."""
        try:
            self.cursor.execute("DELETE FROM sales")
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error clearing sales history: {e}")
            QMessageBox.critical(None, "Database Error", f"Error clearing sales history: {e}")
            return False

class AddProductDialog(QDialog):
    """
    Dialog for adding or editing product information.
    """
    def __init__(self, parent=None, product_data=None):
        super().__init__(parent)
        self.setWindowTitle("Add/Edit Product")
        self.setGeometry(200, 200, 400, 300)
        self.product_data = product_data
        self.is_edit_mode = product_data is not None

        self.layout = QVBoxLayout(self)
        self.form_layout = QFormLayout()
        self.layout.addLayout(self.form_layout)

        self.name_input = QLineEdit()
        self.stock_input = QLineEdit()
        self.stock_input.setValidator(QIntValidator())
        self.price_input = QLineEdit()
        self.price_input.setValidator(QDoubleValidator(0.0, 999999.0, 2))
        self.cost_input = QLineEdit()
        self.cost_input.setValidator(QDoubleValidator(0.0, 999999.0, 2))
        self.color_input = QLineEdit()

        self.form_layout.addRow("Product Name:", self.name_input)
        self.form_layout.addRow("Stock Quantity:", self.stock_input)
        self.form_layout.addRow("Selling Price:", self.price_input)
        self.form_layout.addRow("Cost Price:", self.cost_input)
        self.form_layout.addRow("Color:", self.color_input)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

        self.apply_styles()
        self.load_data_for_edit()

    def load_data_for_edit(self):
        """Pre-populates fields if in edit mode."""
        if self.is_edit_mode and self.product_data:
            self.setWindowTitle(f"Edit Product (ID: {self.product_data['id']})")
            self.name_input.setText(self.product_data["name"])
            self.stock_input.setText(str(self.product_data["stock"]))
            self.price_input.setText(f"{self.product_data['price']:.2f}")
            self.cost_input.setText(f"{self.product_data['cost']:.2f}")
            self.color_input.setText(self.product_data["color"])
            self.name_input.setFocus() # Focus on the name field for editing
        else:
            self.name_input.setFocus() # Focus on name field for new product

    def get_product_data(self):
        """Returns the entered product data as a dictionary."""
        name = self.name_input.text().strip()
        stock_str = self.stock_input.text().strip()
        price_str = self.price_input.text().strip()
        cost_str = self.cost_input.text().strip()
        color = self.color_input.text().strip()

        if not name or not stock_str or not price_str or not cost_str or not color:
            QMessageBox.warning(self, "Missing Fields", "All fields must be filled.")
            return None

        try:
            stock = int(stock_str)
            price = float(price_str)
            cost = float(cost_str)
            if stock < 0 or price < 0 or cost < 0:
                raise ValueError("Stock, selling price, and cost price cannot be negative.")
        except ValueError as e:
            QMessageBox.warning(self, "Invalid Input", f"Please enter valid numbers. {e}")
            return None
        
        data = {
            "name": name,
            "stock": stock,
            "price": price,
            "cost": cost,
            "color": color
        }
        if self.is_edit_mode and self.product_data:
            data["id"] = self.product_data["id"] # Preserve ID for edits
        return data
    
    def apply_styles(self):
        """Applies styles to the dialog widgets."""
        self.setStyleSheet("""
            QDialog {
                background-color: #2c313a;
                border: 1px solid #495057;
                border-radius: 8px;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
                font-size: 14px;
            }
            QLineEdit {
                background-color: #343a40;
                border: 1px solid #6c757d;
                border-radius: 5px;
                padding: 8px;
                color: #ffffff;
                font-size: 14px;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                padding: 8px 12px;
                border: none;
                border-radius: 5px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
            QDialogButtonBox {
                padding-top: 10px;
            }
        """)

class SellProductDialog(QDialog):
    """
    Dialog for recording a sale transaction.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Record Sale")
        self.setGeometry(300, 300, 350, 150)

        self.layout = QVBoxLayout(self)
        self.form_layout = QFormLayout()
        self.layout.addLayout(self.form_layout)

        self.product_id_input = QLineEdit()
        self.product_id_input.setValidator(QIntValidator(1, 999999))
        self.quantity_input = QLineEdit()
        self.quantity_input.setValidator(QIntValidator(1, 999999))

        self.form_layout.addRow("Product ID:", self.product_id_input)
        self.form_layout.addRow("Quantity:", self.quantity_input)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

        self.apply_styles()
        self.product_id_input.setFocus()

    def get_sale_data(self):
        """Returns the entered sale data as a dictionary."""
        product_id_str = self.product_id_input.text().strip()
        quantity_str = self.quantity_input.text().strip()

        if not product_id_str or not quantity_str:
            QMessageBox.warning(self, "Missing Fields", "Product ID and Quantity must be filled.")
            return None

        try:
            product_id = int(product_id_str)
            quantity = int(quantity_str)
            if quantity <= 0:
                raise ValueError("Quantity must be a positive number.")
        except ValueError as e:
            QMessageBox.warning(self, "Invalid Input", f"Please enter valid numbers. {e}")
            return None
        
        return {"product_id": product_id, "quantity": quantity}

    def apply_styles(self):
        """Applies styles to the dialog widgets."""
        self.setStyleSheet("""
            QDialog {
                background-color: #2c313a;
                border: 1px solid #495057;
                border-radius: 8px;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
                font-size: 14px;
            }
            QLineEdit {
                background-color: #343a40;
                border: 1px solid #6c757d;
                border-radius: 5px;
                padding: 8px;
                color: #ffffff;
                font-size: 14px;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                padding: 8px 12px;
                border: none;
                border-radius: 5px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
            QDialogButtonBox {
                padding-top: 10px;
            }
        """)

class RetailApp(QMainWindow):
    """
    Main application window for the Retail Store Management System.
    Manages the overall layout and switches between Inventory and Sales tabs.
    """
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager() 

        self.setWindowTitle("Retail Store Management System")
        self.setGeometry(100, 100, 1000, 700) 

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)

        self.inventory_tab = InventoryTab(self.db_manager) 
        self.sales_tab = SalesTab(self.inventory_tab, self.db_manager) 
        
        self.tab_widget.addTab(self.inventory_tab, "Inventory Management")
        self.tab_widget.addTab(self.sales_tab, "Sales Logging")

        self.apply_styles()

    def apply_styles(self):
        """
        Applies a clean, modern stylesheet to the application.
        Updated for a dark theme based on #23252B.
        """
        self.setStyleSheet("""
            QMainWindow {
                background-color: #23252B; /* Dark grey background */
            }
            QTabWidget::pane {
                border: 1px solid #495057; /* Darker border for pane */
                background-color: #2c313a; /* Dark background for tab content */
                border-radius: 8px; /* Rounded corners for tab content */
            }
            QTabBar::tab {
                background: #343a40; /* Darker tab background */
                border: 1px solid #495057; /* Border for tabs */
                border-bottom-color: #2c313a; /* Blend with pane color when unselected */
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                min-width: 120px;
                padding: 10px;
                margin-right: 2px;
                color: #ffffff; /* White text for tabs */
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: #2c313a; /* Same as pane for selected tab */
                border-bottom-color: #2c313a; /* Make the bottom border blend with the pane */
                color: #007bff; /* Blue text for selected tab */
            }
            QLabel {
                font-size: 14px;
                color: #ffffff; /* White text for labels */
            }
            QLineEdit, QTextEdit {
                padding: 8px;
                border: 1px solid #6c757d; /* Lighter border for input fields */
                border-radius: 5px;
                font-size: 14px;
                background-color: #343a40; /* Dark background for input fields */
                color: #ffffff; /* White text for input */
            }
            QPushButton {
                background-color: #007bff; /* Blue button */
                color: white;
                padding: 10px 15px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3; /* Darker blue on hover */
            }
            QPushButton:pressed {
                background-color: #004085; /* Even darker blue on press */
            }
            QTableWidget {
                border: 1px solid #495057; /* Darker border for table */
                border-radius: 5px;
                gridline-color: #6c757d; /* Lighter grid lines */
                font-size: 14px;
                background-color: #2c313a; /* Dark background for table */
                color: #ffffff; /* White text for table content */
            }
            QHeaderView::section {
                background-color: #343a40; /* Darker header background */
                padding: 8px;
                border: 1px solid #495057; /* Border for header sections */
                font-weight: bold;
                color: #ffffff; /* White text for header */
            }
        """)

    def closeEvent(self, event):
        """Ensures the database connection is closed when the application exits."""
        self.db_manager.close()
        event.accept()

class InventoryTab(QWidget):
    """
    Tab dedicated to managing product inventory.
    Allows adding, editing, deleting, and displaying product information.
    Includes a search feature and uses dialogs for input.
    """
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager 

        self.layout = QVBoxLayout(self)

        # Buttons
        self.button_layout = QHBoxLayout()
        self.layout.addLayout(self.button_layout)

        self.add_button = QPushButton("Add Product")
        self.add_button.clicked.connect(self.open_add_product_dialog)
        self.button_layout.addWidget(self.add_button)

        self.edit_button = QPushButton("Edit Product")
        self.edit_button.clicked.connect(self.open_edit_product_dialog)
        self.button_layout.addWidget(self.edit_button)

        self.delete_button = QPushButton("Delete Product")
        self.delete_button.clicked.connect(self.delete_product)
        self.button_layout.addWidget(self.delete_button)

        # Search Bar
        self.search_layout = QHBoxLayout()
        self.layout.addLayout(self.search_layout)
        self.search_label = QLabel("Search Product:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter product name or part of it...")
        self.search_input.textChanged.connect(self.perform_search) 

        self.search_layout.addWidget(self.search_label)
        self.search_layout.addWidget(self.search_input)

        # Product Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Stock", "Selling Price", "Cost Price", "Color"])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.layout.addWidget(self.table)

        self.update_table() # Load data from DB on startup

    def update_table(self, filter_text=""):
        """Refreshes the product table with current inventory data from the database."""
        products_data = self.db_manager.get_products(filter_text)
        self.table.setRowCount(0) 

        for row_index, data in enumerate(products_data):
            self.table.insertRow(row_index)
            product_id, name, stock, price, cost, color = data

            id_item = QTableWidgetItem(str(product_id))
            id_item.setBackground(QBrush(QColor("#2a5252"))) 
            self.table.setItem(row_index, 0, id_item)

            self.table.setItem(row_index, 1, QTableWidgetItem(name))
            self.table.setItem(row_index, 2, QTableWidgetItem(str(stock)))
            self.table.setItem(row_index, 3, QTableWidgetItem(f"{price:.2f}"))
            self.table.setItem(row_index, 4, QTableWidgetItem(f"{cost:.2f}"))
            self.table.setItem(row_index, 5, QTableWidgetItem(color))

    def perform_search(self):
        """Triggers the table update with the current search input."""
        search_query = self.search_input.text()
        self.update_table(search_query)

    def open_add_product_dialog(self):
        """Opens a dialog for adding a new product."""
        dialog = AddProductDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted: # Corrected: QDialog.DialogCode.Accepted
            product_data = dialog.get_product_data()
            if product_data:
                product_id = self.db_manager.add_product(
                    product_data["name"], product_data["stock"],
                    product_data["price"], product_data["cost"],
                    product_data["color"]
                )
                if product_id is not None:
                    self.update_table(self.search_input.text())
                    self.show_message("Success", f"Product '{product_data['name']}' added successfully with ID {product_id}.")

    def open_edit_product_dialog(self):
        """Opens a dialog for editing an existing product."""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            self.show_message("No Selection", "Please select a product from the table to edit.")
            return

        row = selected_rows[0].row()
        product_id = int(self.table.item(row, 0).text())
        
        # Retrieve full product data from DB for editing
        product_info = self.db_manager.get_product_by_id(product_id)
        if not product_info:
            self.show_message("Error", "Product not found in database for editing.")
            return

        dialog = AddProductDialog(self, product_data=product_info)
        if dialog.exec() == QDialog.DialogCode.Accepted: # Corrected: QDialog.DialogCode.Accepted
            updated_data = dialog.get_product_data()
            if updated_data:
                if self.db_manager.update_product(
                    product_info["id"], updated_data["name"], updated_data["stock"],
                    updated_data["price"], updated_data["cost"], updated_data["color"]
                ):
                    self.update_table(self.search_input.text())
                    self.show_message("Success", f"Product ID {product_info['id']} updated successfully.")
                else:
                    self.show_message("Error", "Failed to update product.")

    def delete_product(self):
        """Deletes a selected product from the database."""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            self.show_message("No Selection", "Please select a product from the table to delete.")
            return

        row = selected_rows[0].row()
        product_id = int(self.table.item(row, 0).text())
        product_name = self.table.item(row, 1).text()

        reply = QMessageBox.question(self, 'Confirm Deletion',
                                     f"Are you sure you want to delete '{product_name}' (ID: {product_id})?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            if self.db_manager.delete_product(product_id):
                self.update_table(self.search_input.text()) 
                self.show_message("Success", f"Product '{product_name}' deleted successfully.")
            else:
                self.show_message("Error", "Failed to delete product.")

    def get_product_info(self, product_id):
        """
        Retrieves product information by ID directly from the database.
        Used by the SalesTab.
        """
        return self.db_manager.get_product_by_id(product_id)

    def update_product_stock(self, product_id, quantity_sold):
        """
        Updates the stock of a product after a sale directly in the database.
        Used by the SalesTab.
        """
        product_info = self.db_manager.get_product_by_id(product_id)
        if product_info:
            current_stock = product_info["stock"]
            if current_stock >= quantity_sold:
                new_stock = current_stock - quantity_sold
                if self.db_manager.update_product_stock(product_id, new_stock):
                    self.update_table(self.search_input.text()) 
                    return True
                else:
                    self.show_message("Database Error", "Failed to update stock in database.")
                    return False
            else:
                self.show_message("Stock Error", f"Not enough stock for Product ID {product_id}. Available: {current_stock}")
                return False
        return False

    def show_message(self, title, message):
        """Helper function to display a QMessageBox."""
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.exec()


class SalesTab(QWidget):
    """
    Tab dedicated to logging sales transactions.
    Allows recording sales and views recent transactions.
    Interacts with InventoryTab to update stock.
    """
    def __init__(self, inventory_tab, db_manager):
        super().__init__()
        self.inventory_tab = inventory_tab
        self.db_manager = db_manager 
        self.sales_history = [] 

        self.layout = QVBoxLayout(self)

        # Sale Input Button (replaces direct inputs)
        self.record_sale_button = QPushButton("Record New Sale")
        self.record_sale_button.clicked.connect(self.open_record_sale_dialog)
        self.layout.addWidget(self.record_sale_button)

        # Sales History Table
        self.sales_table_label = QLabel("Recent Sales:")
        self.layout.addWidget(self.sales_table_label)

        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(7) 
        self.sales_table.setHorizontalHeaderLabels(["Sale ID", "Product Name", "Quantity", "Unit Price", "Cost Price", "Total Price", "Profit/Loss"])
        self.sales_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.sales_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.layout.addWidget(self.sales_table)
        
        self.clear_sales_button = QPushButton("Clear Sales History")
        self.clear_sales_button.clicked.connect(self.clear_sales_history)
        self.layout.addWidget(self.clear_sales_button)

        # Total Sales and Profit/Loss Display
        self.summary_layout = QHBoxLayout()
        self.layout.addLayout(self.summary_layout)

        self.total_sales_label = QLabel(f"Total Sales: $0.00") 
        self.total_sales_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #28a745;")
        self.summary_layout.addWidget(self.total_sales_label)

        self.total_profit_loss_label = QLabel(f"Total Profit/Loss: $0.00") 
        self.total_profit_loss_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #17a2b8;")
        self.summary_layout.addWidget(self.total_profit_loss_label)

        self.load_sales_data_and_update_summary() 

    def open_record_sale_dialog(self):
        """Opens a dialog for recording a new sale."""
        dialog = SellProductDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted: # Corrected: QDialog.DialogCode.Accepted
            sale_data = dialog.get_sale_data()
            if sale_data:
                product_id = sale_data["product_id"]
                quantity = sale_data["quantity"]

                product_info = self.inventory_tab.get_product_info(product_id)
                if not product_info:
                    self.show_message("Product Not Found", f"Product with ID {product_id} not found in inventory.")
                    return

                if product_info["stock"] < quantity:
                    self.show_message("Insufficient Stock", 
                                      f"Not enough stock for '{product_info['name']}'. Available: {product_info['stock']}")
                    return

                if self.inventory_tab.update_product_stock(product_id, quantity):
                    product_name = product_info["name"]
                    unit_price = product_info["price"]
                    cost_price = product_info["cost"]
                    total_price = quantity * unit_price
                    profit_loss = (unit_price - cost_price) * quantity
                    
                    sale_id = self.db_manager.record_sale(product_id, product_name, quantity, unit_price, cost_price, total_price, profit_loss)
                    
                    if sale_id is not None:
                        self.load_sales_data_and_update_summary()
                        self.show_message("Sale Recorded", 
                                          f"Sale of {quantity} x '{product_name}' recorded for a total of ${total_price:.2f}.")
                    else:
                        self.show_message("Error", "Failed to record sale in database.")
        
    def load_sales_data_and_update_summary(self):
        """Loads sales data from DB, updates table, and calculates/displays totals."""
        sales_data_from_db = self.db_manager.get_sales_history()
        self.sales_history = sales_data_from_db 

        current_total_sales = 0.0
        current_total_profit_loss = 0.0

        self.sales_table.setRowCount(0) 
        for row_index, sale_record in enumerate(self.sales_history):
            
            self.sales_table.insertRow(row_index)
            self.sales_table.setItem(row_index, 0, QTableWidgetItem(str(sale_record[0]))) 
            self.sales_table.setItem(row_index, 1, QTableWidgetItem(sale_record[1])) 
            self.sales_table.setItem(row_index, 2, QTableWidgetItem(str(sale_record[2]))) 
            self.sales_table.setItem(row_index, 3, QTableWidgetItem(f"{sale_record[3]:.2f}")) 
            self.sales_table.setItem(row_index, 4, QTableWidgetItem(f"{sale_record[4]:.2f}")) 
            self.sales_table.setItem(row_index, 5, QTableWidgetItem(f"{sale_record[5]:.2f}")) 
            
            profit_loss_value = sale_record[6]
            profit_loss_item = QTableWidgetItem(f"{profit_loss_value:.2f}")
            if profit_loss_value >= 0:
                profit_loss_item.setForeground(QBrush(QColor("#28a745"))) 
            else:
                profit_loss_item.setForeground(QBrush(QColor("#dc3545"))) 
            self.sales_table.setItem(row_index, 6, profit_loss_item) 

            current_total_sales += sale_record[5] 
            current_total_profit_loss += sale_record[6]

        self.total_sales = current_total_sales
        self.total_profit_loss = current_total_profit_loss
        self.update_summary_displays()

    def update_summary_displays(self):
        """Updates the labels displaying the total sales and total profit/loss."""
        self.total_sales_label.setText(f"Total Sales: ${self.total_sales:.2f}")
        self.total_profit_loss_label.setText(f"Total Profit/Loss: ${self.total_profit_loss:.2f}")
        
        if self.total_profit_loss >= 0:
            self.total_profit_loss_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #28a745;")
        else:
            self.total_profit_loss_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #dc3545;")


    def clear_sales_history(self):
        """Clears all sales history records from the database."""
        reply = QMessageBox.question(self, 'Confirm Clear History',
                                     "Are you sure you want to clear ALL sales history? This action cannot be undone.",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            if self.db_manager.clear_sales_history():
                self.load_sales_data_and_update_summary() 
                self.show_message("History Cleared", "Sales history has been cleared.")
            else:
                self.show_message("Error", "Failed to clear sales history.")

    def show_message(self, title, message):
        """Helper function to display a QMessageBox."""
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.exec()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RetailApp()
    window.show()
    sys.exit(app.exec())
