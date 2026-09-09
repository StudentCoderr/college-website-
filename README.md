# College Website Project

A simple Flask web portal with a homepage, contact form, and basic admin notice board using SQLite for easy local storage.

## Requirements

- Python 3.11+ (or 3.10)
- No extra database server required

## Files

- `app.py` — Flask application
- `requirements.txt` — Python dependencies
- `templates/` — HTML templates
- `static/css/style.css` — custom CSS

## Setup and run

1. Open PowerShell in the project folder.

2. Create a Python virtual environment:

```powershell
python -m venv venv
```

3. Activate the virtual environment:

```powershell
venv\Scripts\Activate.ps1
```
```

4. Install dependencies:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

5. Run the Flask app:

```powershell
python app.py
```

7. Open a browser and visit:

- `http://localhost:8000/` for the home page
- `http://localhost:8000/contact` for the contact form
- `http://localhost:8000/admin` for admin notice management

## Admin credentials

- Admin password: `admin123`

## Notes

- The project uses SQLite, so no external database setup is needed.
- Data such as student profiles, staff profiles, notices, events, and uploads are stored in the local `portal.db` file.
