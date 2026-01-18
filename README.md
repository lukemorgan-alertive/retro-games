# Retro Games Collection Manager

A retro games catalog management system with both a CLI tool and REST API, sharing a common SQLite database.

## Components

### CLI Tool (`retro-games-cli/`)
Command-line interface for managing your retro games collection. Supports adding individual games, bulk importing from CSV, listing, and exporting.

**Features:**
- Initialize and manage SQLite database
- Add games with title, release year, platform, date acquired, and condition
- Import/export games via CSV
- Condition tracking (mint, vgc, gc, used)

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
# Initialize the database
cd retro-games-cli
python3 main.py init --db ../retro_games.db

# Start the API
cd ../retro-games-api
pip install -r requirements.txt
uvicorn app:app --reload
```

## Documentation

- [CLI Documentation](retro-games-cli/README.md)
- [API Documentation](retro-games-api/README.md)
- [Project Documentation](documentation/PROJECT_DOCUMENTATION.md)

## TODOS

[ ] Add the ability to create admin users through the cli tool.
[ ] Add Login/Lougout routues which utilise JWT http authentication to the REST API for the CREATE, UPDATE AND DELETE routes.