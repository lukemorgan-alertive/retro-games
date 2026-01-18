"""
Database models and connection management for the Retro Games API.
Shares schema with the CLI tool.
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional
from datetime import date

# Shared database path
DB_PATH = Path(__file__).parent.parent / "retro_games.db"


@contextmanager
def get_db_connection(db_path: Path = DB_PATH) -> Generator[sqlite3.Connection, None, None]:
    """
    Context manager for database connections.
    Ensures proper connection cleanup and foreign key enforcement.
    
    Edge cases handled:
        - Connection cleanup via finally block (even on exceptions)
        - Foreign key enforcement enabled
        - Timeout set to prevent indefinite blocking on locked database
        - Row factory enables dict-like access
    
    Raises:
        sqlite3.OperationalError: If database file cannot be accessed or is locked.
    """
    conn = sqlite3.connect(db_path, timeout=30.0)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row  # Enable column access by name
    try:
        yield conn
    finally:
        conn.close()


def init_db(db_path: Path = DB_PATH) -> None:
    """
    Initialize the database schema.
    Creates the games table if it doesn't exist.
    Safe to call multiple times (idempotent).
    
    ✓ SECURITY: Database initialization uses static DDL with no user input.
      CHECK constraint validates condition values at the database level,
      providing defense-in-depth alongside application-level validation.
    """
    with get_db_connection(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS games (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                release_year INTEGER NOT NULL,
                platform TEXT NOT NULL,
                date_acquired TEXT NOT NULL,
                condition TEXT CHECK(condition IN ('mint', 'vgc', 'gc', 'used'))
            )
        """)
        conn.commit()


class GameModel:
    """Database operations for games."""
    
    @staticmethod
    def create(title: str, release_year: int, platform: str, 
               date_acquired: date, condition: Optional[str] = None) -> int:
        """Create a new game and return its ID.
        
        ✓ SECURITY: Parameterized queries with ? placeholders prevent SQL injection.
          All user input (title, platform, condition) is passed separately from the
          SQL statement, preventing malicious SQL code injection through these fields.
        
        Edge cases handled:
            - Date object converted to ISO string for storage
            - Optional condition field handles None values
            - Database-level CHECK constraint validates condition values
            - Transaction committed before returning ID
            - Connection cleanup handled by context manager
        
        Raises:
            sqlite3.IntegrityError: If CHECK constraint fails (invalid condition).
            sqlite3.OperationalError: If database is locked or inaccessible.
        """
        with get_db_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO games (title, release_year, platform, date_acquired, condition)
                VALUES (?, ?, ?, ?, ?)
                """,
                (title, release_year, platform, date_acquired.isoformat(), condition)
            )
            conn.commit()
            return cursor.lastrowid
    
    @staticmethod
    def get_all(page: int = 1, page_size: int = 25) -> list[dict]:
        """Retrieve games with pagination.
        
        Args:
            page: Page number (1-indexed). Defaults to 1.
            page_size: Number of items per page. Defaults to 25.
        
        ✓ SECURITY: No user input is interpolated in this query. The SQL statement
          uses parameterized queries for LIMIT and OFFSET values, preventing SQL injection.
        """
        offset = (page - 1) * page_size
        with get_db_connection() as conn:
            cursor = conn.execute(
                "SELECT id, title, release_year, platform, date_acquired, condition "
                "FROM games ORDER BY release_year DESC LIMIT ? OFFSET ?",
                (page_size, offset)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def get_total_count() -> int:
        """Get the total count of games in the database.
        
        ✓ SECURITY: No user input is interpolated in this query. The SQL statement
          is static and contains no user-controlled data, preventing SQL injection.
        """
        with get_db_connection() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM games")
            return cursor.fetchone()[0]
    
    @staticmethod
    def get_by_id(game_id: int) -> Optional[dict]:
        """Retrieve a single game by ID.
        
        ✓ SECURITY: Parameterized query with ? placeholder prevents SQL injection.
          The game_id parameter is passed separately from the SQL statement,
          preventing SQL injection through the ID parameter.
        """
        with get_db_connection() as conn:
            cursor = conn.execute(
                "SELECT id, title, release_year, platform, date_acquired, condition "
                "FROM games WHERE id = ?",
                (game_id,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
    
    @staticmethod
    def update(game_id: int, title: str, release_year: int, platform: str,
               date_acquired: date, condition: Optional[str] = None) -> bool:
        """Update an existing game. Returns True if updated, False if not found.
        
        ✓ SECURITY: Parameterized queries with ? placeholders prevent SQL injection.
          All user input (title, platform, condition) is passed separately from the
          SQL statement, preventing malicious SQL code injection through these fields.
        """
        with get_db_connection() as conn:
            cursor = conn.execute(
                """
                UPDATE games 
                SET title = ?, release_year = ?, platform = ?, date_acquired = ?, condition = ?
                WHERE id = ?
                """,
                (title, release_year, platform, date_acquired.isoformat(), condition, game_id)
            )
            conn.commit()
            return cursor.rowcount > 0
    
    @staticmethod
    def delete(game_id: int) -> bool:
        """Delete a game. Returns True if deleted, False if not found.
        
        ✓ SECURITY: Parameterized query with ? placeholder prevents SQL injection.
          The game_id parameter is passed separately from the SQL statement,
          preventing SQL injection through the ID parameter.
        """
        with get_db_connection() as conn:
            cursor = conn.execute("DELETE FROM games WHERE id = ?", (game_id,))
            conn.commit()
            return cursor.rowcount > 0
