import os
import sqlite3
import uuid
from flask import Flask, render_template, request, redirect, url_for, flash, session, abort, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "college-portal-secret-key"
app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "uploads")
app.config["DATABASE"] = os.path.join(app.root_path, "portal.db")
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
for folder in ["notes", "calendars", "timetables"]:
    os.makedirs(os.path.join(app.config["UPLOAD_FOLDER"], folder), exist_ok=True)

role_credentials = {
    "student": {"username": "student", "password": "student123"},
    "staff": {"username": "staff", "password": "staff123"},
    "admin": {"username": "admin", "password": "admin123"},
}


def get_db_connection():
    conn = sqlite3.connect(app.config["DATABASE"])
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password):
    return generate_password_hash(password)


def verify_password(stored_password, provided_password):
    if stored_password and stored_password.startswith(("pbkdf2:", "scrypt:", "argon2:")):
        return check_password_hash(stored_password, provided_password)
    return stored_password == provided_password


def get_user_by_username(username):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    return dict(row) if row else None


def init_db():
    conn = get_db_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS student_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            father_name TEXT,
            mother_name TEXT,
            phone TEXT,
            email TEXT,
            course TEXT,
            department TEXT,
            year TEXT,
            academic_details TEXT,
            address TEXT,
            username TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS staff_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            staff_name TEXT NOT NULL,
            designation TEXT,
            department TEXT,
            phone TEXT,
            email TEXT,
            qualification TEXT,
            experience TEXT,
            address TEXT,
            username TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS announcements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            event_date TEXT,
            kind TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kind TEXT NOT NULL,
            title TEXT NOT NULL,
            filename TEXT NOT NULL,
            path TEXT NOT NULL,
            description TEXT,
            username TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    try:
        conn.execute("ALTER TABLE resources ADD COLUMN username TEXT")
    except sqlite3.OperationalError:
        pass

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS staff_attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            subject TEXT NOT NULL,
            attendance_status TEXT NOT NULL,
            percentage INTEGER NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS contact_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS exam_schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course TEXT NOT NULL,
            exam_name TEXT NOT NULL,
            exam_date TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            location TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_name TEXT NOT NULL,
            course_code TEXT NOT NULL,
            instructor TEXT NOT NULL,
            credits INTEGER,
            semester TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    student_columns = {row[1] for row in conn.execute("PRAGMA table_info(student_profiles)").fetchall()}
    if "username" not in student_columns:
        conn.execute("ALTER TABLE student_profiles ADD COLUMN username TEXT")

    staff_columns = {row[1] for row in conn.execute("PRAGMA table_info(staff_profiles)").fetchall()}
    if "username" not in staff_columns:
        conn.execute("ALTER TABLE staff_profiles ADD COLUMN username TEXT")
    if "date_of_birth" not in staff_columns:
        conn.execute("ALTER TABLE staff_profiles ADD COLUMN date_of_birth TEXT")
    if "gender" not in staff_columns:
        conn.execute("ALTER TABLE staff_profiles ADD COLUMN gender TEXT")
    if "emergency_contact" not in staff_columns:
        conn.execute("ALTER TABLE staff_profiles ADD COLUMN emergency_contact TEXT")

    exam_columns = {row[1] for row in conn.execute("PRAGMA table_info(exam_schedules)").fetchall()}
    courses_columns = {row[1] for row in conn.execute("PRAGMA table_info(courses)").fetchall()}

    conn.commit()
    conn.close()


def seed_default_users():
    conn = get_db_connection()
    for role, info in role_credentials.items():
        existing = conn.execute("SELECT 1 FROM users WHERE username = ?", (info["username"],)).fetchone()
        if not existing:
            conn.execute(
                "INSERT INTO users (role, username, password) VALUES (?, ?, ?)",
                (role, info["username"], hash_password(info["password"])),
            )
    conn.commit()
    conn.close()


def get_users():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM users ORDER BY id ASC").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_student_profiles(username=None):
    conn = get_db_connection()
    if username:
        rows = conn.execute("SELECT * FROM student_profiles WHERE username = ? ORDER BY id DESC", (username,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM student_profiles ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_staff_profiles(username=None):
    conn = get_db_connection()
    if username:
        rows = conn.execute("SELECT * FROM staff_profiles WHERE username = ? ORDER BY id DESC", (username,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM staff_profiles ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_student_profile(username):
    if not username:
        return None
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM student_profiles WHERE username = ? ORDER BY id DESC LIMIT 1", (username,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_staff_profile(username):
    if not username:
        return None
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM staff_profiles WHERE username = ? ORDER BY id DESC LIMIT 1", (username,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_staff_attendance(username=None):
    conn = get_db_connection()
    if username:
        rows = conn.execute("SELECT * FROM staff_attendance WHERE username = ? ORDER BY id DESC", (username,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM staff_attendance ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def save_student_profile(profile, username):
    conn = get_db_connection()
    conn.execute("DELETE FROM student_profiles WHERE username = ?", (username,))
    conn.execute(
        """
        INSERT INTO student_profiles (
            student_name, father_name, mother_name, phone, email, course, department, year, academic_details, address, username
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            profile["student_name"],
            profile["father_name"],
            profile["mother_name"],
            profile["phone"],
            profile["email"],
            profile["course"],
            profile["department"],
            profile["year"],
            profile["academic_details"],
            profile["address"],
            username,
        ),
    )
    conn.commit()
    conn.close()


def save_staff_profile(profile, username):
    conn = get_db_connection()
    conn.execute("DELETE FROM staff_profiles WHERE username = ?", (username,))
    conn.execute(
        """
        INSERT INTO staff_profiles (
            staff_name, designation, department, phone, email, qualification, experience,
            date_of_birth, gender, emergency_contact, address, username
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            profile["staff_name"],
            profile["designation"],
            profile["department"],
            profile["phone"],
            profile["email"],
            profile["qualification"],
            profile["experience"],
            profile["date_of_birth"],
            profile["gender"],
            profile["emergency_contact"],
            profile["address"],
            username,
        ),
    )
    conn.commit()
    conn.close()


def get_announcements():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM announcements ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_resources(kind=None, username=None):
    conn = get_db_connection()
    if kind and username:
        rows = conn.execute(
            "SELECT * FROM resources WHERE kind = ? AND username = ? ORDER BY id DESC",
            (kind, username),
        ).fetchall()
    elif kind:
        rows = conn.execute("SELECT * FROM resources WHERE kind = ? ORDER BY id DESC", (kind,)).fetchall()
    elif username:
        rows = conn.execute("SELECT * FROM resources WHERE username = ? ORDER BY id DESC", (username,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM resources ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_activity_summary():
    conn = get_db_connection()
    counts = {
        "students": conn.execute("SELECT COUNT(*) FROM student_profiles").fetchone()[0],
        "staff": conn.execute("SELECT COUNT(*) FROM staff_profiles").fetchone()[0],
        "accounts": conn.execute("SELECT COUNT(*) FROM users").fetchone()[0],
        "announcements": conn.execute("SELECT COUNT(*) FROM announcements").fetchone()[0],
        "resources": conn.execute("SELECT COUNT(*) FROM resources").fetchone()[0],
    }
    conn.close()
    return counts


init_db()
seed_default_users()


@app.context_processor
def inject_user():
    return {
        "logged_in": session.get("logged_in", False),
        "current_role": session.get("role"),
        "current_user": session.get("username"),
    }


@app.route("/")
def home():
    return render_template(
        "index.html",
        announcements=get_announcements()[:4],
        resources={
            "notes": get_resources("notes")[:3],
            "calendars": get_resources("calendars")[:3],
            "timetables": get_resources("timetables")[:3],
        },
    )


@app.route("/login/<role>", methods=["GET", "POST"])
def login(role):
    if role not in role_credentials:
        abort(404)

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        matching_user = get_user_by_username(username)
        if matching_user and verify_password(matching_user["password"], password):
            if matching_user["role"] == role:
                session["logged_in"] = True
                session["role"] = role
                session["username"] = username
                flash(f"Welcome back, {role.title()}.", "success")
                return redirect(url_for("dashboard"))
            flash(
                f"Your account belongs to the {matching_user['role'].title()} portal. Please use the {matching_user['role']} login page.",
                "warning",
            )
        else:
            flash("Invalid credentials. Please try again.", "danger")

    return render_template("login.html", role=role, register=False)


@app.route("/register/<role>", methods=["GET", "POST"])
def register(role):
    if role not in {"student", "staff"}:
        abort(404)

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()

        if not username or not password:
            flash("Please enter both username and password.", "danger")
            return redirect(url_for("register", role=role))

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("register", role=role))

        if get_user_by_username(username):
            flash("That username already exists. Please choose a different one.", "danger")
            return redirect(url_for("register", role=role))

        conn = get_db_connection()
        conn.execute("INSERT INTO users (role, username, password) VALUES (?, ?, ?)",
                     (role, username, hash_password(password)))
        conn.commit()
        conn.close()
        flash(f"{role.title()} account created successfully. Please sign in.", "success")
        return redirect(url_for("login", role=role))

    return render_template("login.html", role=role, register=True)


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))


@app.route("/dashboard")
def dashboard():
    if not session.get("logged_in"):
        flash("Please sign in first.", "warning")
        return redirect(url_for("home"))

    current_username = session.get("username")
    role = session.get("role")

    student_profiles = get_student_profiles() if role == "admin" else get_student_profiles(current_username)
    staff_profiles = get_staff_profiles() if role == "admin" else get_staff_profiles(current_username)
    staff_attendance = get_staff_attendance() if role == "admin" else get_staff_attendance(current_username if role == "staff" else None)
    student_profile = get_student_profile(current_username) if role == "student" else None
    staff_profile = get_staff_profile(current_username) if role == "staff" else None
    resource_owner = current_username if role == "staff" else None

    return render_template(
        "dashboard.html",
        role=role,
        users=get_users(),
        student_profiles=student_profiles,
        staff_profiles=staff_profiles,
        student_profile=student_profile,
        staff_profile=staff_profile,
        staff_attendance=staff_attendance,
        announcements=get_announcements(),
        resources={
            "notes": get_resources("notes", resource_owner),
            "timetables": get_resources("timetables", resource_owner),
        },
        summary=get_activity_summary(),
    )


@app.route("/dashboard/staff-attendance", methods=["POST"])
def staff_attendance():
    if session.get("role") != "staff":
        flash("Only staff can add attendance records.", "danger")
        return redirect(url_for("dashboard"))

    subject = request.form.get("subject", "").strip()
    attendance_status = request.form.get("attendance_status", "").strip()
    percentage = request.form.get("percentage", "").strip()

    if not subject or not attendance_status or not percentage:
        flash("Please fill in subject, attendance status, and percentage.", "danger")
        return redirect(url_for("dashboard"))

    try:
        percentage_value = int(percentage)
        if percentage_value < 0 or percentage_value > 100:
            raise ValueError
    except ValueError:
        flash("Attendance percentage must be a number between 0 and 100.", "danger")
        return redirect(url_for("dashboard"))

    conn = get_db_connection()
    conn.execute(
        "INSERT INTO staff_attendance (username, subject, attendance_status, percentage) VALUES (?, ?, ?, ?)",
        (session.get("username"), subject, attendance_status, percentage_value),
    )
    conn.commit()
    conn.close()

    flash("Attendance record added successfully.", "success")
    return redirect(url_for("dashboard"))


@app.route("/dashboard/staff-attendance/<int:record_id>/delete", methods=["POST"])
def delete_staff_attendance(record_id):
    if session.get("role") not in {"staff", "admin"}:
        flash("Only staff and admins can delete attendance records.", "danger")
        return redirect(url_for("dashboard"))

    conn = get_db_connection()
    record = conn.execute("SELECT username FROM staff_attendance WHERE id = ?", (record_id,)).fetchone()
    if record:
        if session.get("role") == "staff" and record[0] != session.get("username"):
            flash("You can only delete your own attendance records.", "danger")
        else:
            conn.execute("DELETE FROM staff_attendance WHERE id = ?", (record_id,))
            conn.commit()
            flash("Attendance record deleted.", "success")
    else:
        flash("Attendance record not found.", "danger")
    conn.close()
    return redirect(url_for("dashboard"))


@app.route("/dashboard/notice", methods=["POST"])
def add_notice():
    if session.get("role") not in {"staff", "admin"}:
        flash("Only staff and admins can add notices.", "danger")
        return redirect(url_for("dashboard"))

    title = request.form.get("title", "").strip()
    content = request.form.get("content", "").strip()

    if title and content:
        conn = get_db_connection()
        conn.execute("INSERT INTO announcements (title, content, kind) VALUES (?, ?, ?)", (title, content, "announcement"))
        conn.commit()
        conn.close()
        flash("Notice published successfully.", "success")
    else:
        flash("Please enter a title and notice content.", "danger")

    return redirect(url_for("dashboard"))


@app.route("/dashboard/create-user", methods=["POST"])
def create_user():
    if session.get("role") != "admin":
        flash("Only admins can add users.", "danger")
        return redirect(url_for("dashboard"))

    role = request.form.get("role", "student").strip()
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()

    if role not in {"student", "staff"}:
        flash("Only student and staff roles can be created.", "danger")
        return redirect(url_for("dashboard"))

    if not username or not password:
        flash("Username and password are required.", "danger")
        return redirect(url_for("dashboard"))

    if any(u["username"] == username for u in get_users()):
        flash("That username already exists.", "danger")
        return redirect(url_for("dashboard"))

    conn = get_db_connection()
    conn.execute("INSERT INTO users (role, username, password) VALUES (?, ?, ?)", (role, username, hash_password(password)))
    conn.commit()
    conn.close()
    flash(f"{role.title()} account created successfully.", "success")
    return redirect(url_for("dashboard"))


@app.route("/dashboard/user/<int:user_id>/delete", methods=["POST"])
def delete_user(user_id):
    if session.get("role") != "admin":
        flash("Only admins can delete user accounts.", "danger")
        return redirect(url_for("dashboard"))

    current_admin = session.get("username")
    conn = get_db_connection()
    row = conn.execute("SELECT username FROM users WHERE id = ?", (user_id,)).fetchone()
    if row:
        username = row[0]
        if username == current_admin:
            flash("You cannot delete your own admin account.", "warning")
        else:
            conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            flash(f"User '{username}' deleted successfully.", "success")
    else:
        flash("User not found.", "danger")
    conn.close()
    return redirect(url_for("dashboard"))


@app.route("/dashboard/student-profile/<int:profile_id>/delete", methods=["POST"])
def delete_student_profile(profile_id):
    if session.get("role") != "admin":
        flash("Only admins can delete student profiles.", "danger")
        return redirect(url_for("dashboard"))

    conn = get_db_connection()
    conn.execute("DELETE FROM student_profiles WHERE id = ?", (profile_id,))
    conn.commit()
    conn.close()
    flash("Student profile deleted.", "success")
    return redirect(url_for("dashboard"))


@app.route("/dashboard/staff-profile/<int:profile_id>/delete", methods=["POST"])
def delete_staff_profile(profile_id):
    if session.get("role") != "admin":
        flash("Only admins can delete staff profiles.", "danger")
        return redirect(url_for("dashboard"))

    conn = get_db_connection()
    conn.execute("DELETE FROM staff_profiles WHERE id = ?", (profile_id,))
    conn.commit()
    conn.close()
    flash("Staff profile deleted.", "success")
    return redirect(url_for("dashboard"))


@app.route("/dashboard/student-profile", methods=["POST"])
def student_profile():
    if session.get("role") != "student":
        flash("Only students can submit student profile details.", "danger")
        return redirect(url_for("dashboard"))

    profile = {
        "student_name": request.form.get("student_name", "").strip(),
        "father_name": request.form.get("father_name", "").strip(),
        "mother_name": request.form.get("mother_name", "").strip(),
        "phone": request.form.get("phone", "").strip(),
        "email": request.form.get("email", "").strip(),
        "course": request.form.get("course", "").strip(),
        "department": request.form.get("department", "").strip(),
        "year": request.form.get("year", "").strip(),
        "academic_details": request.form.get("academic_details", "").strip(),
        "address": request.form.get("address", "").strip(),
    }

    if not all([profile["student_name"], profile["father_name"], profile["mother_name"], profile["phone"], profile["email"], profile["course"], profile["department"], profile["year"]]):
        flash("Please fill all required student details.", "danger")
        return redirect(url_for("dashboard"))

    save_student_profile(profile, session.get("username"))
    flash("Student profile saved successfully.", "success")
    return redirect(url_for("dashboard"))


@app.route("/dashboard/staff-profile", methods=["POST"])
def staff_profile():
    if session.get("role") != "staff":
        flash("Only staff can submit staff profile details.", "danger")
        return redirect(url_for("dashboard"))

    profile = {
        "staff_name": request.form.get("staff_name", "").strip(),
        "designation": request.form.get("designation", "").strip(),
        "department": request.form.get("department", "").strip(),
        "phone": request.form.get("phone", "").strip(),
        "email": request.form.get("email", "").strip(),
        "qualification": request.form.get("qualification", "").strip(),
        "experience": request.form.get("experience", "").strip(),
        "date_of_birth": request.form.get("date_of_birth", "").strip(),
        "gender": request.form.get("gender", "").strip(),
        "emergency_contact": request.form.get("emergency_contact", "").strip(),
        "address": request.form.get("address", "").strip(),
    }

    if not all([profile["staff_name"], profile["designation"], profile["department"], profile["phone"], profile["email"]]):
        flash("Please fill all required staff details.", "danger")
        return redirect(url_for("dashboard"))

    save_staff_profile(profile, session.get("username"))
    flash("Staff profile saved successfully.", "success")
    return redirect(url_for("dashboard"))


@app.route("/dashboard/upload/<kind>", methods=["POST"])
def upload_resource(kind):
    if session.get("role") not in {"staff", "admin"}:
        flash("Only staff and admins can upload files.", "danger")
        return redirect(url_for("dashboard"))

    if kind not in {"notes", "calendars", "timetables"}:
        abort(404)

    uploaded_file = request.files.get("file")
    if not uploaded_file or uploaded_file.filename == "":
        flash("Please choose a file to upload.", "danger")
        return redirect(url_for("dashboard"))

    filename = secure_filename(uploaded_file.filename)
    if not filename:
        flash("Please choose a valid file name.", "danger")
        return redirect(url_for("dashboard"))

    name, extension = os.path.splitext(filename)
    unique_name = f"{secure_filename(name) or 'upload'}-{uuid.uuid4().hex[:8]}{extension.lower()}"
    target_folder = os.path.join(app.config["UPLOAD_FOLDER"], kind)
    os.makedirs(target_folder, exist_ok=True)
    save_path = os.path.join(target_folder, unique_name)
    uploaded_file.save(save_path)

    title = request.form.get("title", "").strip() or unique_name
    description = request.form.get("description", "").strip()
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO resources (kind, title, filename, path, description, username) VALUES (?, ?, ?, ?, ?, ?)",
        (kind, title, unique_name, f"{kind}/{unique_name}", description, session.get("username")),
    )
    conn.commit()
    conn.close()

    flash(f"{kind.replace('notes', 'Notes').replace('timetables', 'Timetable')} uploaded successfully.", "success")
    return redirect(url_for("dashboard"))


@app.route("/download/<path:filename>")
def download_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=True)


@app.route("/dashboard/announcement", methods=["POST"])
def add_announcement():
    if session.get("role") not in {"staff", "admin"}:
        flash("Only staff and admins can publish announcements.", "danger")
        return redirect(url_for("dashboard"))

    title = request.form.get("title", "").strip()
    content = request.form.get("content", "").strip()
    event_date = request.form.get("event_date", "").strip()

    if not title or not content:
        flash("Please enter both a title and details.", "danger")
        return redirect(url_for("dashboard"))

    conn = get_db_connection()
    conn.execute(
        "INSERT INTO announcements (title, content, event_date, kind) VALUES (?, ?, ?, ?)",
        (title, content, event_date or None, "event" if event_date else "announcement"),
    )
    conn.commit()
    conn.close()

    flash("Announcement published successfully.", "success")
    return redirect(url_for("dashboard"))


@app.route("/dashboard/announcement/<int:item_id>/delete", methods=["POST"])
def delete_announcement(item_id):
    if session.get("role") not in {"staff", "admin"}:
        flash("Only staff and admins can remove announcements.", "danger")
        return redirect(url_for("dashboard"))

    conn = get_db_connection()
    conn.execute("DELETE FROM announcements WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    flash("Announcement removed.", "success")
    return redirect(url_for("dashboard"))


@app.route("/dashboard/resource/<kind>/<int:resource_id>/delete", methods=["POST"])
def delete_resource(kind, resource_id):
    if session.get("role") not in {"staff", "admin"}:
        flash("Only staff and admins can delete resources.", "danger")
        return redirect(url_for("dashboard"))

    conn = get_db_connection()
    item = conn.execute("SELECT * FROM resources WHERE id = ? AND kind = ?", (resource_id, kind)).fetchone()
    if item:
        if session.get("role") == "staff" and item["username"] != session.get("username"):
            flash("You can only delete your own resource uploads.", "danger")
        else:
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], item["path"])
            if os.path.exists(file_path):
                os.remove(file_path)
            conn.execute("DELETE FROM resources WHERE id = ?", (resource_id,))
            conn.commit()
            flash("Resource deleted.", "success")
    else:
        flash("Resource not found.", "danger")
    conn.close()
    return redirect(url_for("dashboard"))


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        message = request.form.get("message", "").strip()
        if name and email and message:
            conn = get_db_connection()
            conn.execute(
                "INSERT INTO contact_messages (name, email, message) VALUES (?, ?, ?)",
                (name, email, message),
            )
            conn.commit()
            conn.close()
            flash("Thank you. Your message has been sent.", "success")
        else:
            flash("Please fill in all contact fields.", "danger")

        return redirect(url_for("contact"))

    return render_template("contact.html")

@app.route("/admin")
def admin():
    return redirect(url_for("login", role="admin"))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)









  
