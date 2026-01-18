# Retro Games CLI (SQLite)

A simple Python CLI to store retro games in an SQLite database.

Schema: `title`, `release_year`, `platform`, `date_acquired`, `condition`.
- `condition` is optional and must be one of `mint`, `vgc`, `gc`, `used` when provided.

## Quick Start

### Initialize the database
```bash
python3 main.py init --db games.db
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

## CSV Format
- Required columns: `title`, `release_year`, `platform`, `date_acquired` (YYYY-MM-DD)
- Optional column: `condition` (one of `mint`, `vgc`, `gc`, `used`)
- Rows with invalid year/date/condition are skipped during import.

## Notes
- The database file defaults to `games.db` in the current directory; override with `--db <path>`.
- SQLite doesn't have a native ENUM; `condition` is enforced via a CHECK constraint and validation in the CLI.
