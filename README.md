# Retro Games Collection Manager

A retro games catalog management system with both a CLI tool and REST API, sharing a common SQLite database.

## Components

### CLI Tool (`retro-games-cli/`)
Command-line interface for managing your retro games collection and admin users. Supports adding individual games, bulk importing from CSV, listing, exporting, and admin user management.

**Features:**
- Initialize and manage SQLite database
- Add games with title, release year, platform, date acquired, and condition
- Import/export games via CSV
- Condition tracking (mint, vgc, gc, used)
- Admin user management (add, remove, list)
- Secure password hashing with bcrypt

### REST API (`retro-games-api/`)
FastAPI-based REST API providing programmatic access to the games catalog.

**Endpoints:**
- `GET /games` - List all games
- `GET /games/{id}` - Get a specific game
- `POST /games` - Create a new game
- `PUT /games/{id}` - Update a game
- `DELETE /games/{id}` - Delete a game

## Quick Start

```bash
# Set up the CLI tool
cd retro-games-cli
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Initialize the database
python3 main.py init

# Start the API (in a separate terminal)
cd ../retro-games-api
pip install -r requirements.txt
uvicorn app:app --reload
```

## Documentation

- [CLI Documentation](retro-games-cli/README.md)
- [API Documentation](retro-games-api/README.md)
- [Project Documentation](documentation/PROJECT_DOCUMENTATION.md)

## TODOS

- [x] Add the ability to create admin users through the cli tool.
- [ ] Add Login/Logout routes for admin users which utilise JWT http authentication to the REST API for the CREATE, UPDATE AND DELETE routes.