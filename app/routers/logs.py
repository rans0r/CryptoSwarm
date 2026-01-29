"""
Logs router for viewing bot activity logs.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from app.database import get_db
from app.models.models import BotLog, User
from app.utils.auth import get_current_active_user

router = APIRouter(prefix="/logs", tags=["logs"])


class LogResponse(BaseModel):
    """Log response model."""
    id: int
    bot_id: int
    level: str
    message: str
    details: Optional[dict]
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.get("/", response_model=List[LogResponse])
async def list_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    bot_id: Optional[int] = None,
    level: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List all bot logs with optional filtering.
    """
    query = db.query(BotLog)
    
    if bot_id is not None:
        query = query.filter(BotLog.bot_id == bot_id)
    
    if level is not None:
        query = query.filter(BotLog.level == level)
    
    # Order by most recent first
    query = query.order_by(BotLog.created_at.desc())
    
    logs = query.offset(skip).limit(limit).all()
    return logs


@router.get("/{log_id}", response_model=LogResponse)
async def get_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific log entry by ID.
    """
    log = db.query(BotLog).filter(BotLog.id == log_id).first()
    
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    
    return log
