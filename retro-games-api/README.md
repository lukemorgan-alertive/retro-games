# Retro Games REST API

A FastAPI-based REST API for managing a retro games catalog. This API shares the SQLite database with the CLI tool.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the API server:
```bash
uvicorn app:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once running, visit:
- Interactive docs: `http://localhost:8000/docs`

## Endpoints

- `GET /games` - List all games
- `GET /games/{id}` - Get a specific game
- `POST /games` - Create a new game
- `PUT /games/{id}` - Update a game
- `DELETE /games/{id}` - Delete a game

## Database

The API uses the shared SQLite database at `../retro_games.db` which is also used by the CLI tool.
