"""
Swarm router for managing evolutionary bot pools.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from app.database import get_db
from app.models.models import SwarmPool, User
from app.utils.auth import get_current_active_user
from app.utils.evolution import SwarmEvolution

router = APIRouter(prefix="/swarm", tags=["swarm"])


class SwarmPoolCreate(BaseModel):
    """Swarm pool creation request model."""
    name: str
    description: Optional[str] = None
    max_bots: int = 20
    selection_pressure: float = 0.5


class SwarmPoolResponse(BaseModel):
    """Swarm pool response model."""
    id: int
    name: str
    description: Optional[str]
    max_bots: int
    selection_pressure: float
    created_at: datetime
    last_evolution: Optional[datetime]
    best_fitness: float
    total_profit_loss: float
    
    class Config:
        from_attributes = True


@router.get("/pools", response_model=List[SwarmPoolResponse])
async def list_pools(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List all swarm pools.
    """
    pools = db.query(SwarmPool).offset(skip).limit(limit).all()
    return pools


@router.get("/pools/{pool_id}", response_model=SwarmPoolResponse)
async def get_pool(
    pool_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific swarm pool by ID.
    """
    pool = db.query(SwarmPool).filter(SwarmPool.id == pool_id).first()
    
    if not pool:
        raise HTTPException(status_code=404, detail="Pool not found")
    
    return pool


@router.post("/pools", response_model=SwarmPoolResponse, status_code=201)
async def create_pool(
    pool_data: SwarmPoolCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new swarm pool.
    """
    new_pool = SwarmPool(
        name=pool_data.name,
        description=pool_data.description,
        max_bots=pool_data.max_bots,
        selection_pressure=pool_data.selection_pressure
    )
    
    db.add(new_pool)
    db.commit()
    db.refresh(new_pool)
    
    return new_pool


@router.post("/pools/{pool_id}/evolve")
async def evolve_pool(
    pool_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Trigger evolution for a swarm pool.
    """
    pool = db.query(SwarmPool).filter(SwarmPool.id == pool_id).first()
    
    if not pool:
        raise HTTPException(status_code=404, detail="Pool not found")
    
    # Create evolution manager and evolve the pool
    evolution = SwarmEvolution(db)
    result = await evolution.evolve_pool(pool)
    
    # Update last evolution timestamp
    pool.last_evolution = datetime.utcnow()
    db.commit()
    
    return result
