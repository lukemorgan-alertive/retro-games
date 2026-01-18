# Retro Games CLI (SQLite)

A Python CLI to store retro games and manage admin users in an SQLite database.

## Installation

This CLI requires the `bcrypt` package for secure password hashing. Set up a virtual environment:

```bash
cd retro-games-cli
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Database Schema

### Games Table
- `id`: Auto-generated primary key
- `title`: Game title (required)
- `release_year`: Year the game was released (required)
- `platform`: Gaming platform, e.g., SNES, PS1, NES (required)
- `date_acquired`: Date acquired in YYYY-MM-DD format (required)
- `condition`: Optional, one of `mint`, `vgc`, `gc`, `used`

### Admin Users Table
- `id`: Auto-generated primary key (required, auto-assigned)
- `username`: Unique username, 3-50 alphanumeric characters, underscores, or hyphens (required)
- `firstname`: Admin's first name (optional)
- `lastname`: Admin's last name (optional)
- `password_hash`: Bcrypt-hashed password (required, stored securely)
- `created_at`: Timestamp when admin was created (required, auto-assigned)
- `updated_at`: Timestamp when admin was last updated (required, auto-assigned)

## Quick Start

### Initialize the database
```bash
python3 main.py init
```

### Add a game
```bash
python3 main.py add "The Legend of Zelda" 1986 NES 2025-12-20 --condition mint
```

### Import from CSV
CSV must include headers: `title,release_year,platform,date_acquired` and optional `condition`.
See `sample.csv` for an example.
```bash
python3 main.py import sample.csv
```

### List games
```bash
python3 main.py list
```

### Export to CSV
```bash
python3 main.py export exported.csv
```
Writes `exported.csv` with headers: `title,release_year,platform,date_acquired,condition`.

## Admin User Management

### Password Requirements
When creating an admin user, the password must meet the following requirements:
- Minimum 12 characters
- At least one letter (a-z or A-Z)
- At least one number (0-9)
- At least one special character (`!@#$%^&*()_+-=[]{}|;:,.<>?`)

### Add an admin user
```bash
python3 main.py admin-add johndoe --firstname John --lastname Doe
```
You will be prompted to enter and confirm a password (input is hidden). The CLI will display password requirements before prompting.

### List admin users
```bash
python3 main.py admin-list
```
Displays all admin users with their ID, username, name, and timestamps.
Note: Password hashes are never displayed for security reasons.

### Remove an admin user
```bash
python3 main.py admin-remove johndoe
```
You will be asked to confirm the removal. Use `--yes` or `-y` to skip confirmation:
```bash
python3 main.py admin-remove johndoe --yes
```

## CSV Format
- Required columns: `title`, `release_year`, `platform`, `date_acquired` (YYYY-MM-DD)
- Optional column: `condition` (one of `mint`, `vgc`, `gc`, `used`)
- Rows with invalid year/date/condition are skipped during import.

## Notes
- The database file defaults to `retro_games.db` in the project root; override with `--db <path>`.
- SQLite doesn't have a native ENUM; `condition` is enforced via a CHECK constraint and validation in the CLI.
- Admin passwords are securely hashed using bcrypt before storage.
- The virtual environment (`.venv`) is ignored by git and should not be committed.
