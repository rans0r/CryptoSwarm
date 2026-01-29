"""
Bots router for managing trading bots.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models.models import Bot, User
from app.utils.auth import get_current_active_user
from app.utils.ai_interpreter import ai_interpreter

router = APIRouter(prefix="/bots", tags=["bots"])


class BotCreate(BaseModel):
    """Bot creation request model."""
    name: str
    description: Optional[str] = None
    natural_language_rule: str


class BotUpdate(BaseModel):
    """Bot update request model."""
    name: Optional[str] = None
    description: Optional[str] = None
    natural_language_rule: Optional[str] = None
    is_active: Optional[bool] = None


class BotResponse(BaseModel):
    """Bot response model."""
    id: int
    name: str
    description: Optional[str]
    natural_language_rule: str
    interpreted_rule: Optional[dict]
    is_active: bool
    total_trades: int
    winning_trades: int
    total_profit_loss: float
    fitness_score: float
    generation: int
    
    class Config:
        from_attributes = True


@router.get("/", response_model=List[BotResponse])
async def list_bots(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List all trading bots with optional filtering.
    """
    query = db.query(Bot)
    
    if is_active is not None:
        query = query.filter(Bot.is_active == is_active)
    
    bots = query.offset(skip).limit(limit).all()
    return bots


@router.get("/{bot_id}", response_model=BotResponse)
async def get_bot(
    bot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific bot by ID.
    """
    bot = db.query(Bot).filter(Bot.id == bot_id).first()
    
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    return bot


@router.post("/", response_model=BotResponse, status_code=201)
async def create_bot(
    bot_data: BotCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new trading bot.
    """
    # Interpret the natural language rule using AI
    interpreted_rule = await ai_interpreter.interpret_rule(bot_data.natural_language_rule)
    
    # Create new bot
    new_bot = Bot(
        name=bot_data.name,
        description=bot_data.description,
        natural_language_rule=bot_data.natural_language_rule,
        interpreted_rule=interpreted_rule,
        is_active=True,
        generation=0
    )
    
    db.add(new_bot)
    db.commit()
    db.refresh(new_bot)
    
    return new_bot


@router.put("/{bot_id}", response_model=BotResponse)
async def update_bot(
    bot_id: int,
    bot_data: BotUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update an existing bot.
    """
    bot = db.query(Bot).filter(Bot.id == bot_id).first()
    
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    # Update fields if provided
    if bot_data.name is not None:
        bot.name = bot_data.name
    
    if bot_data.description is not None:
        bot.description = bot_data.description
    
    if bot_data.is_active is not None:
        bot.is_active = bot_data.is_active
    
    if bot_data.natural_language_rule is not None:
        bot.natural_language_rule = bot_data.natural_language_rule
        # Re-interpret the rule
        bot.interpreted_rule = await ai_interpreter.interpret_rule(bot_data.natural_language_rule)
    
    db.commit()
    db.refresh(bot)
    
    return bot


@router.delete("/{bot_id}", status_code=204)
async def delete_bot(
    bot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a bot.
    """
    bot = db.query(Bot).filter(Bot.id == bot_id).first()
    
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    db.delete(bot)
    db.commit()
    
    return None


@router.post("/{bot_id}/reinterpret", response_model=BotResponse)
async def reinterpret_bot_rule(
    bot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Reinterpret a bot's rule using the AI interpreter.
    """
    bot = db.query(Bot).filter(Bot.id == bot_id).first()
    
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    # Reinterpret the rule
    bot.interpreted_rule = await ai_interpreter.interpret_rule(bot.natural_language_rule)
    
    db.commit()
    db.refresh(bot)
    
    return bot
