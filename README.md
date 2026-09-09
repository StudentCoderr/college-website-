
# College Portal Web Application

A lightweight, full-stack Flask web application designed for managing college portal interactions. The application features role-based access control (RBAC) for Students, Staff, and Administrators, enabling seamless profile management, announcement publishing, resource sharing, and contact message handling backed by a local SQLite database.

---
## Key Features

* **Role-Based Access Control (RBAC):** Customized dashboards and permissions for `student`, `staff`, and `admin` roles.

* **User Authentication & Management:** Secure registration and login workflows powered by Werkzeug password hashing.

* **Resource Sharing & File Management:** Upload and download capabilities for notes, academic calendars, and timetables.

* **Announcements & Notice Board:** System-wide notice publishing managed by staff and administrators.

* **Profile Management:** Independent profile creation and updates for both students and staff.

* **Staff Attendance & Contact Handling:** Tools for recording staff attendance and receiving user inquiries via a contact form.

---

## System Architecture & Technologies

### Backend & Database

* **Python 3.x:** Core backend programming language.

* **Flask (3.x):** Micro web framework handling routing, sessions, and request lifecycles.

* **Werkzeug:** Utility library utilized for secure password hashing/verification and safe file uploads.

* **SQLite (`portal.db`):** Serverless, zero-configuration embedded database for persistent local storage.

### Frontend & Styling

* **Jinja2:** Templating engine for dynamic rendering of HTML pages.

* **Bootstrap 5:** Mobile-first CSS framework for responsive layout and pre-built UI components.

* **Custom CSS (`style.css`):** Supplemental styling tailored to custom UI components.

---
## Project Directory Structure

```text
college-website/
│
├── app.py                  # Core backend application (routes, DB setup, RBAC logic)
├── requirements.txt        # Python package dependencies
├── README.md               # Project documentation
├── portal.db               # Local SQLite database (created automatically)
│
├── static/
│   └── style.css           # Custom stylesheets
│
├── templates/              # Jinja2 HTML templates
│   ├── base.html           # Shared layout (Navbar, Footer, Flash messages)
│   ├── index.html          # Homepage with previews
│   ├── login.html          # Login and registration forms
│   ├── dashboard.html      # Role-specific user dashboard
│   ├── contact.html        # Contact form page
│   └── admin.html          # Admin redirect handler
│
└── uploads/                # Local storage for uploaded documents (auto-generated)
    ├── notes/              # Lecture notes and study materials
    ├── calendars/          # Academic calendar documents
    └── timetables/         # Class and exam schedules
```[cite: 1]
---
## Step-by-Step Installation & Setup Guide

Follow these steps to set up and run the project locally on your machine[cite: 1].

### Step 1: Prerequisites
Ensure you have **Python 3.8+** installed on your operating system. You can verify your installation by running:
```bash
python --version

```
### Step 2: Clone or Download the Repository

Navigate to your desired workspace folder and clone or extract the project:

```bash
git clone https://github.com/StudentCoderr/college-website-.git
cd college-website-

```
### Step 3: Create and Activate a Virtual Environment

Isolate project dependencies by setting up a Python virtual environment:

* **On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
* **On macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate

```
### Step 4: Install Required Dependencies

Upgrade `pip` and install all necessary Python libraries specified in `requirements.txt`:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

```
---
## Database Initialization & Default Users

When starting the application for the first time, `app.py` automatically initializes the `portal.db` SQLite database with the required tables and populates default test accounts:

* **Database Tables Created:** `users`, `student_profiles`, `staff_profiles`, `announcements`, `resources`, `staff_attendance`, `contact_messages`, `exam_schedules`, `courses`.

* **Default Test Accounts:**
* **Admin:** Username: `admin` | Password: `admin123`

* **Staff:** Username: `staff` | Password: `staff123`

* **Student:** Username: `student` | Password: `student123`
---

## Running the Application

1. Execute the main application file:

```bash
python app.py

```

2. Open your web browser and navigate to:

```text
http://localhost:8000/

```

3. The server will launch in **Debug Mode** on port `8000`.

---

## Roles & Permissions Matrix

| Feature / Action                   | Student | Staff | Admin |
| ---                                | ---     | ---   | ---   |
| View Announcements & Resources     | Yes     | Yes   | Yes   |
| Submit Contact Messages            | Yes     | Yes   | Yes   |
| Manage Own Profile                 | Yes     | Yes   | —     |
| Upload Resources (Notes/Calendars) | —       | Yes   | —     |
| Publish System Announcements       | —       | Yes   | Yes   |
| Record Staff Attendance            | —       | Yes   | —     |
| Create & Delete User Accounts      | —       | —     | Yes   |
| Delete Announcements & Resources   | —       | —     | Yes   |

---
## API & Route Reference

### Public Routes

* `GET /` — Homepage presenting announcements and resource previews.

* `GET, POST /login/<role>` — Role-specific user authentication.

* `GET, POST /register/<role>` — Registration page for students and staff.

* `GET, POST /contact` — Public inquiry form.

* `GET /logout` — Session termination.

### Authenticated & Role-Restricted Routes

* `GET /dashboard` — Main control panel customized per logged-in user role.

* `POST /dashboard/student-profile` — Create or update student profile details.

* `POST /dashboard/staff-profile` — Create or update staff profile details.

* `POST /dashboard/staff-attendance` — Submit staff attendance records.

* `POST /dashboard/notice` — Create and publish portal notices.

* `POST /dashboard/upload/<kind>` — Upload resources (`notes`, `calendars`, or `timetables`).

* `GET /download/<path>` — Secure document downloading.

* `POST /dashboard/create-user` — Admin endpoint to create user accounts.

* `POST /dashboard/user/<id>/delete` — Admin endpoint to delete user accounts.

---

## Future Enhancements & Roadmap

* **Modular Refactoring:** Restructure `app.py` into Flask Blueprints for improved scalability.

* **Database Migrations:** Integrate `Flask-Migrate` / `Alembic` for database schema management.

* **Enhanced Security:** Implement CSRF protection, HTTPS redirect, and advanced input validation.

* **Unit & Integration Testing:** Introduce `pytest` suites to automate test coverage.
