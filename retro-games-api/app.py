"""
FastAPI REST API for Retro Games Catalog.
Provides CRUD operations for the shared SQLite database.
"""

from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal
from datetime import date

from models import GameModel, init_db

# Initialize FastAPI app
app = FastAPI(
    title="Retro Games API",
    description="REST API for managing a retro games catalog",
    version="1.0.0"
)


# Pydantic models for request/response validation
class GameCreate(BaseModel):
    """Schema for creating a new game.
    
    Edge cases handled:
        - Title/platform length limits enforced via max_length
        - Year boundaries validated (1970-2030)
        - Date parsing validates ISO format automatically
        - Condition enum restricts to valid values only
        - Empty strings rejected via min_length=1
    """
    title: str = Field(..., min_length=1, max_length=500, description="Game title")
    release_year: int = Field(..., ge=1970, le=2030, description="Year the game was released")
    platform: str = Field(..., min_length=1, max_length=100, description="Gaming platform (e.g., SNES, PS1)")
    date_acquired: date = Field(..., description="Date acquired in ISO format (YYYY-MM-DD)")
    condition: Optional[Literal['mint', 'vgc', 'gc', 'used']] = Field(
        None, 
        description="Condition: mint, vgc (very good condition), gc (good condition), or used"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Super Mario World",
                "release_year": 1990,
                "platform": "SNES",
                "date_acquired": "2024-01-15",
                "condition": "vgc"
            }
        }


class GameUpdate(BaseModel):
    """Schema for updating an existing game.
    
    Edge cases handled:
        - Same validations as GameCreate to ensure data consistency
        - Prevents updates with invalid data
    """
    title: str = Field(..., min_length=1, max_length=500, description="Game title")
    release_year: int = Field(..., ge=1970, le=2030, description="Year the game was released")
    platform: str = Field(..., min_length=1, max_length=100, description="Gaming platform")
    date_acquired: date = Field(..., description="Date acquired in ISO format (YYYY-MM-DD)")
    condition: Optional[Literal['mint', 'vgc', 'gc', 'used']] = Field(
        None,
        description="Condition: mint, vgc, gc, or used"
    )


class GameResponse(BaseModel):
    """Schema for game responses."""
    id: int
    title: str
    release_year: int
    platform: str
    date_acquired: str  # Stored as ISO string in database
    condition: Optional[str]
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "Super Mario World",
                "release_year": 1990,
                "platform": "SNES",
                "date_acquired": "2024-01-15",
                "condition": "vgc"
            }
        }


class PaginatedGamesResponse(BaseModel):
    """Schema for paginated games response."""
    games: list[GameResponse]
    total: int = Field(..., description="Total number of games in the database")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")
    
    class Config:
        json_schema_extra = {
            "example": {
                "games": [
                    {
                        "id": 1,
                        "title": "Super Mario World",
                        "release_year": 1990,
                        "platform": "SNES",
                        "date_acquired": "2024-01-15",
                        "condition": "vgc"
                    }
                ],
                "total": 170,
                "page": 1,
                "page_size": 25,
                "total_pages": 7
            }
        }


# API Endpoints

@app.on_event("startup")
async def startup_event():
    """
    Initialize database on application startup.
    
    Ensures the database schema is created before handling any requests.
    This is idempotent and safe to call multiple times.
    """
    init_db()


@app.get("/", tags=["Root"])
async def root():
    """
    Welcome endpoint providing API information.
    
    Returns:
        dict: API metadata including name, documentation URL, and version.
    """
    return {
        "message": "Retro Games API",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.post("/games", response_model=GameResponse, status_code=status.HTTP_201_CREATED, tags=["Games"])
async def create_game(game: GameCreate):
    """
    Create a new game entry in the catalog.
    
    Args:
        game (GameCreate): Game data including title, release year, platform,
                          date acquired, and optional condition.
    
    Returns:
        GameResponse: The created game with its assigned ID.
    
    Raises:
        HTTPException: 500 if database operation fails.
    """
    try:
        game_id = GameModel.create(
            title=game.title,
            release_year=game.release_year,
            platform=game.platform,
            date_acquired=game.date_acquired,
            condition=game.condition
        )
        created_game = GameModel.get_by_id(game_id)
        if not created_game:
            raise HTTPException(status_code=500, detail="Failed to retrieve created game")
        return created_game
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create game: {str(e)}")


@app.get("/games", response_model=PaginatedGamesResponse, tags=["Games"])
async def list_games(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(25, ge=1, le=100, description="Number of items per page (max 100)")
):
    """
    Retrieve games from the catalog with pagination.
    
    Args:
        page (int): Page number (1-indexed). Defaults to 1.
        page_size (int): Number of items per page. Defaults to 25, max 100.
    
    Returns:
        PaginatedGamesResponse: Paginated list of games with metadata.
    
    Raises:
        HTTPException: 500 if database operation fails.
    """
    try:
        games = GameModel.get_all(page=page, page_size=page_size)
        total = GameModel.get_total_count()
        total_pages = (total + page_size - 1) // page_size  # Ceiling division
        
        return PaginatedGamesResponse(
            games=games,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve games: {str(e)}")


@app.get("/games/{game_id}", response_model=GameResponse, tags=["Games"])
async def get_game(game_id: int):
    """
    Retrieve a specific game by its ID.
    
    Args:
        game_id (int): The unique identifier of the game.
    
    Returns:
        GameResponse: The requested game.
    
    Raises:
        HTTPException: 404 if game not found.
    """
    game = GameModel.get_by_id(game_id)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Game with ID {game_id} not found"
        )
    return game


@app.put("/games/{game_id}", response_model=GameResponse, tags=["Games"])
async def update_game(game_id: int, game: GameUpdate):
    """
    Update an existing game in the catalog.
    
    Args:
        game_id (int): The unique identifier of the game to update.
        game (GameUpdate): Updated game data (all fields required).
    
    Returns:
        GameResponse: The updated game.
    
    Raises:
        HTTPException: 404 if game not found, 500 if database operation fails.
    """
    try:
        success = GameModel.update(
            game_id=game_id,
            title=game.title,
            release_year=game.release_year,
            platform=game.platform,
            date_acquired=game.date_acquired,
            condition=game.condition
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Game with ID {game_id} not found"
            )
        updated_game = GameModel.get_by_id(game_id)
        return updated_game
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update game: {str(e)}")


@app.delete("/games/{game_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Games"])
async def delete_game(game_id: int):
    """
    Delete a game from the catalog.
    
    Args:
        game_id (int): The unique identifier of the game to delete.
    
    Returns:
        None: 204 No Content on success.
    
    Raises:
        HTTPException: 404 if game not found.
    """
    success = GameModel.delete(game_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Game with ID {game_id} not found"
        )
    return None
