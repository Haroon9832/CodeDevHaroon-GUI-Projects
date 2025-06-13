Hospital Management System
A comprehensive desktop application built using Python and PyQt6 for managing hospital operations, including patient registration, billing, doctor management, ward allocation, and reporting. The system features a secure authentication system with password encryption, role-based access control, and password recovery functionality.
Key Features

Patient Management: Register and manage patient details, including personal information, medical diagnosis, room assignments, and doctor allocation.
Billing & Cost Management: Track patient charges, generate invoices, and manage payment statuses with support for tax calculations and insurance details.
Doctor Management: Maintain doctor profiles, specializations, fee structures, and daily schedules.
Ward & Room Management: Monitor room occupancy, types, costs, and patient assignments with real-time statistics.
Reports & Analytics: Generate customizable reports for admissions, discharges, billing summaries, and occupancy rates.
Security & Authentication:
Secure user registration and login with bcrypt password hashing.
Password strength validation and history tracking to prevent reuse.
Account lockout after multiple failed login attempts.
Password recovery via security questions and simulated email service.


Modern UI: Clean, responsive interface with gradient headers, customizable themes, and a consistent design using PyQt6 and a global stylesheet.

Technologies Used

Python: Core programming language.
PyQt6: Framework for building the graphical user interface.
SQLite: Lightweight database for storing user and system data.
bcrypt: Secure password hashing for authentication.
Regular Expressions: For input validation (e.g., CNIC format).
JSON: For session management.

Project Structure

Authentication System: Handles user registration, login, password reset, and security question verification.
UI Components: Modular widgets for patient management, billing, doctor management, ward management, and reports, styled with a global stylesheet.
Sample Data: Pre-populated data for demonstration purposes, including patients, doctors, and rooms.
Email Service: Simulated email functionality for password reset tokens.

Installation

Clone the repository:git clone https://github.com/your-username/hospital-management-system.git


Install dependencies:pip install PyQt6 bcrypt


Run the application:python main.py



Usage

Default Credentials:
Username: admin
Password: Admin@12345678


Log in to access the main dashboard with tabs for different modules.
Use the toolbar to quickly add new patients or log out.
Explore each module to manage patients, billing, doctors, wards, or generate reports.

Future Enhancements

Integrate a real email service for password recovery.
Add chart visualizations for reports using a plotting library like Matplotlib.
Implement a full-fledged database for patient and billing records.
Support multi-language localization.
Enhance accessibility features for better usability.

License
This project is licensed under the MIT License. See the LICENSE file for details.
Contributing
Contributions are welcome! Please fork the repository and submit a pull request with your changes.
