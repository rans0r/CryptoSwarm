"""
Trades router for viewing trade history.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from app.database import get_db
from app.models.models import Trade, User
from app.utils.auth import get_current_active_user

router = APIRouter(prefix="/trades", tags=["trades"])


class TradeResponse(BaseModel):
    """Trade response model."""
    id: int
    bot_id: int
    symbol: str
    side: str
    order_type: str
    amount: float
    price: float
    executed_at: datetime
    exchange_order_id: Optional[str]
    status: str
    fee: float
    profit_loss: float
    
    class Config:
        from_attributes = True


@router.get("/", response_model=List[TradeResponse])
async def list_trades(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    bot_id: Optional[int] = None,
    symbol: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List all trades with optional filtering.
    """
    query = db.query(Trade)
    
    if bot_id is not None:
        query = query.filter(Trade.bot_id == bot_id)
    
    if symbol is not None:
        query = query.filter(Trade.symbol == symbol)
    
    if status is not None:
        query = query.filter(Trade.status == status)
    
    # Order by most recent first
    query = query.order_by(Trade.executed_at.desc())
    
    trades = query.offset(skip).limit(limit).all()
    return trades


@router.get("/{trade_id}", response_model=TradeResponse)
async def get_trade(
    trade_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific trade by ID.
    """
    trade = db.query(Trade).filter(Trade.id == trade_id).first()
    
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    
    return trade


@router.get("/bot/{bot_id}/stats")
async def get_bot_trade_stats(
    bot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get trading statistics for a specific bot.
    """
    trades = db.query(Trade).filter(Trade.bot_id == bot_id).all()
    
    if not trades:
        return {
            "bot_id": bot_id,
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "total_profit_loss": 0.0,
            "win_rate": 0.0,
            "avg_profit_per_trade": 0.0
        }
    
    winning_trades = sum(1 for t in trades if t.profit_loss > 0)
    losing_trades = sum(1 for t in trades if t.profit_loss < 0)
    total_profit_loss = sum(t.profit_loss for t in trades)
    
    return {
        "bot_id": bot_id,
        "total_trades": len(trades),
        "winning_trades": winning_trades,
        "losing_trades": losing_trades,
        "total_profit_loss": total_profit_loss,
        "win_rate": (winning_trades / len(trades)) * 100 if trades else 0.0,
        "avg_profit_per_trade": total_profit_loss / len(trades) if trades else 0.0
    }
