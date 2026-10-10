# Student Information System

![CI](https://github.com/ejhay-maker/student-info-system/actions/workflows/ci.yml/badge.svg)

A command-line Student Information System written in Python. It supports full
CRUD operations on student records stored in a JSON file, and is structured to be
cloud-ready: modular code, external configuration, environment-variable overrides,
error handling, and rotating logs.

## Features

- **Add** new students (with validation of ID, email, year level)
- **View** all students, look one up by ID, or **search** by name/course/ID
- **Update** student information (press Enter to keep a field)
- **Delete** students (with confirmation)
- **JSON storage** with atomic writes, so a crash never corrupts the data file
- **Configuration** via `config/config.json` plus environment variables
- **Logging** to `logs/app.log` (rotating) with levels INFO/WARNING/ERROR
- **Error handling** with custom exceptions; the app never crashes on bad input
- **Unit tests** and **GitHub Actions CI**

## Project Structure

```
student-info-system/
├── src/
│   ├── models/student.py            # Student dataclass + validation
│   ├── services/student_service.py  # CRUD logic + JSON persistence
│   ├── utils/                       # config, logger, custom exceptions
│   └── main.py                      # CLI entry point
├── data/students.json               # Data store
├── config/config.json               # Settings
├── logs/                            # Log output (ignored by git)
├── tests/                           # Unit tests
├── .github/workflows/ci.yml         # Automated tests on every push
├── requirements.txt
└── .gitignore
```

## Getting Started

Requires Python 3.9+.

```bash
git clone https://github.com/ejhay-maker/student-info-system.git
cd student-info-system
python -m venv .venv
# Windows: .venv\Scripts\activate    |  macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m src.main
```

## Configuration

Edit `config/config.json`:

| Key         | Default               | Environment override |
|-------------|-----------------------|----------------------|
| `data_file` | `data/students.json`  | `SIS_DATA_FILE`      |
| `log_file`  | `logs/app.log`        | `SIS_LOG_FILE`       |
| `log_level` | `INFO`                | `SIS_LOG_LEVEL`      |

Example: `SIS_DATA_FILE=/tmp/students.json python -m src.main`

## Running Tests

```bash
python -m pytest -v
```

## Data Format

```json
{
  "2024-001": {
    "student_id": "2024-001",
    "first_name": "Juan",
    "last_name": "Dela Cruz",
    "email": "juan@example.com",
    "course": "BSIT",
    "year_level": 3,
    "created_at": "2026-10-10T09:30:00"
  }
}
```
## Future Improvements

- Export student records to CSV
- Add a web interface
- Add a database backend (SQLite/PostgreSQL)

## Author

Eljie M. Gorospe
