# Retro Games Catalog - Project Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Components](#components)
4. [Database Schema](#database-schema)
5. [API Documentation](#api-documentation)
6. [CLI Documentation](#cli-documentation)
7. [Security](#security)
8. [Setup and Installation](#setup-and-installation)
9. [Usage Examples](#usage-examples)
10. [Development](#development)

---

## Project Overview

The Retro Games Catalog is a full-stack application for managing a personal collection of retro video games. It consists of two main components:

- **REST API** (FastAPI): A RESTful web service for CRUD operations
- **CLI Tool** (Python): A command-line interface for local database management

Both components share a common SQLite database (`retro_games.db`) and implement consistent data validation and security practices.

### Key Features
- Full CRUD operations (Create, Read, Update, Delete)
- CSV import/export functionality
- Shared database architecture
- Parameterized queries to prevent SQL injection
- Input validation with Pydantic (API) and argparse (CLI)
- Interactive API documentation (Swagger/ReDoc)
- Admin user management with secure password hashing (bcrypt)

---

## Architecture

```
retro-games/
├── retro_games.db                 # Shared SQLite database
├── retro-games-api/               # FastAPI REST API
│   ├── app.py                     # API endpoints and request handling
│   ├── models.py                  # Database models and operations
│   ├── requirements.txt           # Python dependencies
│   └── README.md                  # API-specific documentation
├── retro-games-cli/               # Command-line interface
│   ├── main.py                    # CLI commands and logic
│   ├── requirements.txt           # Python dependencies (bcrypt)
│   ├── sample.csv                 # Example CSV for import
│   └── README.md                  # CLI-specific documentation
├── SECURITY.md                    # Security considerations
├── SQL_INJECTION_REVIEW.md        # SQL injection prevention details
└── OWASP-Top-10-for-Web-Apps.md  # OWASP security reference
```

### Design Patterns
- **Shared Database**: Both components use the same SQLite database file
- **Repository Pattern**: `GameModel` class encapsulates database operations
- **Context Manager**: Database connections use `with` statements for automatic cleanup
- **Validation Layer**: Input validation at application boundaries (API/CLI)
- **Separation of Concerns**: Clear separation between API routes, business logic, and data access

---

## Components

### 1. REST API (`retro-games-api/`)

**Technology Stack:**
- FastAPI: Modern, fast web framework
- Pydantic: Data validation and serialization
- Uvicorn: ASGI server
- SQLite3: Database driver

**Key Files:**
- `app.py`: API endpoints, request/response models, error handling
- `models.py`: Database connection management and CRUD operations

### 2. CLI Tool (`retro-games-cli/`)

**Technology Stack:**
- Python 3.13+
- argparse: Command-line argument parsing
- csv: CSV file handling
- sqlite3: Database operations
- dataclasses: Data structure definitions
- bcrypt: Secure password hashing for admin users
- getpass: Hidden password input

**Key Files:**
- `main.py`: Complete CLI implementation with all commands
- `requirements.txt`: External dependencies (bcrypt)

---

## Database Schema

### Games Table

```sql
CREATE TABLE IF NOT EXISTS games (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    release_year INTEGER NOT NULL,
    platform TEXT NOT NULL,
    date_acquired TEXT NOT NULL,
    condition TEXT CHECK(condition IN ('mint', 'vgc', 'gc', 'used'))
)
```

### Games Field Descriptions

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique game identifier |
| `title` | TEXT | NOT NULL | Game title |
| `release_year` | INTEGER | NOT NULL, 1970-2030 (app-level) | Year the game was released |
| `platform` | TEXT | NOT NULL | Gaming platform (e.g., SNES, PS1, NES) |
| `date_acquired` | TEXT | NOT NULL, ISO format (YYYY-MM-DD) | Date the game was acquired |
| `condition` | TEXT | CHECK constraint | Optional: mint, vgc, gc, or used |

### Condition Values
- `mint`: Mint condition (sealed/perfect)
- `vgc`: Very Good Condition
- `gc`: Good Condition
- `used`: Used condition

### Admin Users Table

```sql
CREATE TABLE IF NOT EXISTS admin_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    firstname TEXT,
    lastname TEXT,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
)
```

### Admin Users Field Descriptions

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT, required | Unique admin identifier (auto-assigned) |
| `username` | TEXT | NOT NULL, UNIQUE, required | Unique username (3-50 alphanumeric chars, underscores, hyphens) |
| `firstname` | TEXT | nullable | Admin's first name (optional) |
| `lastname` | TEXT | nullable | Admin's last name (optional) |
| `password_hash` | TEXT | NOT NULL, required | Bcrypt-hashed password (never stored as plaintext) |
| `created_at` | TEXT | NOT NULL, required | ISO timestamp when admin was created (auto-assigned) |
| `updated_at` | TEXT | NOT NULL, required | ISO timestamp when admin was last modified (auto-assigned) |

---

## API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### 1. Root Endpoint
```http
GET /
```
Returns welcome message and API information.

**Response:**
```json
{
  "message": "Retro Games API",
  "docs": "/docs",
  "version": "1.0.0"
}
```

#### 2. List All Games
```http
GET /games
```
Retrieves all games from the database, ordered by release year (descending).

**Response:** Array of game objects

#### 3. Get Game by ID
```http
GET /games/{game_id}
```
Retrieves a specific game by ID.

**Response:** Game object or 404 error

#### 4. Create Game
```http
POST /games
```
Creates a new game entry.

**Request Body:**
```json
{
  "title": "Super Mario World",
  "release_year": 1990,
  "platform": "SNES",
  "date_acquired": "2024-01-15",
  "condition": "vgc"
}
```

**Response:** Created game object (201 status)

#### 5. Update Game
```http
PUT /games/{game_id}
```
Updates an existing game. All fields required.

**Request Body:** Same as Create Game

**Response:** Updated game object or 404 error

#### 6. Delete Game
```http
DELETE /games/{game_id}
```
Deletes a game by ID.

**Response:** 204 No Content or 404 error

### Request/Response Models

#### GameCreate / GameUpdate
```python
{
  "title": str,              # min_length=1
  "release_year": int,       # 1970 <= year <= 2030
  "platform": str,           # min_length=1
  "date_acquired": date,     # YYYY-MM-DD format
  "condition": str | None    # "mint" | "vgc" | "gc" | "used"
}
```

#### GameResponse
```python
{
  "id": int,
  "title": str,
  "release_year": int,
  "platform": str,
  "date_acquired": str,
  "condition": str | None
}
```

### Interactive Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## CLI Documentation

### Installation
No installation required beyond Python 3.x and standard library.

### Basic Usage
```bash
python3 main.py [command] [options]
```

### Commands

#### Initialize Database
```bash
python3 main.py init [--db PATH]
```
Creates the database schema. Safe to run multiple times (idempotent).

**Options:**
- `--db PATH`: Database file path (default: `../retro_games.db`)

#### Add a Game
```bash
python3 main.py add TITLE YEAR PLATFORM DATE [--condition COND]
```

**Example:**
```bash
python3 main.py add "The Legend of Zelda" 1986 NES 2025-12-20 --condition mint
```

**Arguments:**
- `TITLE`: Game title (string)
- `YEAR`: Release year (integer)
- `PLATFORM`: Platform name (string)
- `DATE`: Date acquired in YYYY-MM-DD format
- `--condition`: Optional condition (mint|vgc|gc|used)

#### Import from CSV
```bash
python3 main.py import CSV_FILE [--db PATH]
```

**Example:**
```bash
python3 main.py import sample.csv
```

**CSV Format:**
- **Required columns**: `title`, `release_year`, `platform`, `date_acquired`
- **Optional column**: `condition`
- Invalid rows are skipped with no error

#### List Games
```bash
python3 main.py list [--db PATH]
```
Displays all games in a formatted table.

#### Export to CSV
```bash
python3 main.py export OUTPUT_FILE [--db PATH]
```

**Example:**
```bash
python3 main.py export exported.csv
```

### CSV Format

#### Import/Export Format
```csv
title,release_year,platform,date_acquired,condition
Super Mario World,1990,SNES,2024-01-15,vgc
The Legend of Zelda,1986,NES,2025-12-20,mint
```

### Admin User Management Commands

#### Password Requirements
When creating an admin user, the password must meet the following strength requirements:
- Minimum 12 characters
- At least one letter (a-z or A-Z)
- At least one number (0-9)
- At least one special character (`!@#$%^&*()_+-=[]{}|;:,.<>?`)

The CLI will display these requirements and validate the password before creating the admin user.

#### Add an Admin User
```bash
python3 main.py admin-add USERNAME [--firstname NAME] [--lastname NAME]
```
Creates a new admin user. You will be prompted to enter and confirm a password (input is hidden for security).

**Example:**
```bash
python3 main.py admin-add johndoe --firstname John --lastname Doe
```

**Arguments:**
- `USERNAME`: Unique username (3-50 alphanumeric characters, underscores, or hyphens)
- `--firstname`: Optional first name
- `--lastname`: Optional last name

#### List Admin Users
```bash
python3 main.py admin-list [--db PATH]
```
Displays all admin users in a formatted table showing ID, username, name, and timestamps.
Note: Password hashes are never displayed for security reasons.

#### Remove an Admin User
```bash
python3 main.py admin-remove USERNAME [--yes]
```
Removes an admin user by username. Confirmation is required unless `--yes` flag is provided.

**Example:**
```bash
python3 main.py admin-remove johndoe --yes
```

**Arguments:**
- `USERNAME`: Username of the admin to remove
- `--yes`, `-y`: Skip confirmation prompt

---

## Security

### SQL Injection Prevention

Both components implement **parameterized queries** to prevent SQL injection attacks:

#### Parameterized Query Example (API)
```python
cursor = conn.execute(
    "INSERT INTO games (title, release_year, platform, date_acquired, condition) VALUES (?, ?, ?, ?, ?)",
    (title, release_year, platform, date_acquired.isoformat(), condition)
)
```

#### Key Security Measures

1. **Parameterized Queries**: All user input uses `?` placeholders, never string interpolation
2. **Input Validation**:
   - API: Pydantic models validate all request data
   - CLI: argparse type validators for all inputs
3. **Database-Level Constraints**: CHECK constraint on `condition` field, UNIQUE constraint on username
4. **Foreign Keys**: `PRAGMA foreign_keys = ON` enforces referential integrity
5. **No String Concatenation**: SQL statements never concatenate user input
6. **Secure Password Handling**:
   - Password strength validation enforced (min 12 chars, letters, numbers, special chars)
   - Passwords are hashed using bcrypt with automatic salting
   - Plaintext passwords are never stored in the database
   - Password input uses `getpass` for hidden terminal input
   - Password hashes are never displayed in list output
   - Bcrypt's constant-time comparison prevents timing attacks

### Validation Rules

**Release Year**: 1970 ≤ year ≤ 2030  
**Date Format**: ISO 8601 (YYYY-MM-DD)  
**Condition**: Enum-like restriction to 4 specific values  
**Required Fields**: title, release_year, platform, date_acquired must be non-empty  
**Admin Username**: 3-50 characters, alphanumeric with underscores and hyphens only  
**Admin Password**: Minimum 12 characters, must include letters, numbers, and special characters

### Security Documentation
- `SECURITY.md`: Comprehensive security overview
- `SQL_INJECTION_REVIEW.md`: Detailed SQL injection analysis
- `OWASP-Top-10-for-Web-Apps.md`: OWASP Top 10 reference

---

## Setup and Installation

### Prerequisites
- Python 3.13+ (3.9+ should work)
- pip (Python package manager)

### API Setup

1. Navigate to the API directory:
```bash
cd retro-games-api
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start the server:
```bash
uvicorn app:app --reload
```

4. Access the API:
- Base URL: http://localhost:8000
- Documentation: http://localhost:8000/docs

### CLI Setup

The CLI requires the `bcrypt` package for secure password hashing. Set up a virtual environment:

```bash
cd retro-games-cli
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
python3 main.py --help
```

The virtual environment (`.venv`) is ignored by git and should not be committed.

---

## Usage Examples

### Scenario 1: Setting Up a New Catalog

```bash
# Set up virtual environment
cd retro-games-cli
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Initialize database
python3 main.py init

# Add games manually
python3 main.py add "Super Mario World" 1990 SNES 2024-01-15 --condition vgc
python3 main.py add "Sonic the Hedgehog" 1991 Genesis 2024-02-20 --condition gc

# Import from CSV
python3 main.py import sample.csv

# List all games
python3 main.py list
```

### Scenario 2: Managing Admin Users

```bash
# Add an admin user (you'll be prompted for password)
python3 main.py admin-add admin1 --firstname Alice --lastname Smith

# Add another admin user
python3 main.py admin-add admin2 --firstname Bob

# List all admin users
python3 main.py admin-list

# Remove an admin user (with confirmation)
python3 main.py admin-remove admin2

# Remove an admin user (skip confirmation)
python3 main.py admin-remove admin2 --yes
```

### Scenario 3: Using the API

```bash
# Start the API server
cd retro-games-api
uvicorn app:app --reload

# In another terminal, use curl to interact
# Create a game
curl -X POST "http://localhost:8000/games" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Chrono Trigger",
    "release_year": 1995,
    "platform": "SNES",
    "date_acquired": "2024-03-10",
    "condition": "mint"
  }'

# Get all games
curl "http://localhost:8000/games"

# Get specific game
curl "http://localhost:8000/games/1"

# Update game
curl -X PUT "http://localhost:8000/games/1" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Chrono Trigger",
    "release_year": 1995,
    "platform": "SNES",
    "date_acquired": "2024-03-10",
    "condition": "vgc"
  }'

# Delete game
curl -X DELETE "http://localhost:8000/games/1"
```

### Scenario 4: Data Export/Backup

```bash
# Export current catalog to CSV
cd retro-games-cli
python3 main.py export backup-$(date +%Y%m%d).csv

# Later, restore from backup
python3 main.py import backup-20240315.csv
```

---

## Development

### Code Structure

#### API (`app.py`)
- **Lines 1-18**: Imports and FastAPI initialization
- **Lines 22-76**: Pydantic request/response models
- **Lines 79-95**: Root and startup endpoints
- **Lines 97-173**: CRUD endpoints (Create, Read, Update, Delete)

#### Models (`models.py`)
- **Lines 1-28**: Imports and database connection management
- **Lines 31-52**: Database initialization
- **Lines 55-141**: `GameModel` class with static CRUD methods

#### CLI (`main.py`)
- **Lines 1-22**: Imports and constants
- **Lines 16-27**: `Game` dataclass definition
- **Lines 30-52**: Database connection and initialization
- **Lines 55-73**: Input validation functions
- **Lines 75-99**: Add game function
- **Lines 102-137**: CSV import function
- **Lines 140-151**: List games function
- **Lines 154-169**: CSV export function
- **Lines 172-210**: CLI argument parser
- **Lines 213-267**: Main function and command routing

### Testing

#### API Testing
```bash
# Start the server
uvicorn app:app --reload

# Use the interactive docs at /docs to test endpoints
# Or use pytest (if tests are added)
pytest
```

#### CLI Testing
```bash
# Test with sample data
python3 main.py init --db test.db
python3 main.py import sample.csv --db test.db
python3 main.py list --db test.db
python3 main.py export test-export.csv --db test.db
```

### Adding New Features

#### Adding a New API Endpoint
1. Define Pydantic models for request/response
2. Add endpoint function with appropriate HTTP method decorator
3. Implement business logic using `GameModel` methods
4. Add error handling with `HTTPException`
5. Update API documentation

#### Adding a New CLI Command
1. Add subparser in `build_parser()` function
2. Define arguments and validators
3. Add command handling in `main()` function
4. Test with various input scenarios

### Best Practices

1. **Always use parameterized queries** - Never concatenate user input into SQL
2. **Validate all inputs** - At application boundaries (API/CLI)
3. **Use context managers** - For database connections (`with` statements)
4. **Handle errors gracefully** - Provide meaningful error messages
5. **Test edge cases** - Empty inputs, invalid dates, boundary values
6. **Document security measures** - Mark SQL queries with security comments
7. **Keep dependencies minimal** - Use standard library when possible

---

## Troubleshooting

### Common Issues

#### Database Locked
**Problem**: `sqlite3.OperationalError: database is locked`  
**Solution**: Ensure only one process writes at a time. Close connections properly.

#### Import Validation Errors
**Problem**: CSV import skips rows  
**Solution**: Check that dates are in YYYY-MM-DD format and release_year is a valid integer.

#### API Won't Start
**Problem**: Port 8000 already in use  
**Solution**: Use a different port: `uvicorn app:app --port 8001`

#### Invalid Condition Value
**Problem**: Database CHECK constraint violation  
**Solution**: Only use: mint, vgc, gc, or used (case-sensitive, lowercase)

---

## Contributing

When contributing to this project:

1. Maintain existing security practices (parameterized queries)
2. Add input validation for new fields
3. Update documentation for new features
4. Test both API and CLI if changes affect shared code
5. Follow existing code style and patterns

---

## License

This project is for educational purposes as part of an AI course.

---

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python argparse Tutorial](https://docs.python.org/3/howto/argparse.html)

---

**Last Updated**: 2026-01-18
