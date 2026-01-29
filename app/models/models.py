"""
Database models for CryptoSwarm application.
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    """User model for authentication."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Bot(Base):
    """Trading bot model."""
    __tablename__ = "bots"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text)
    natural_language_rule = Column(Text, nullable=False)
    interpreted_rule = Column(JSON)  # Structured rule from AI interpretation
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Performance metrics
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    total_profit_loss = Column(Float, default=0.0)
    fitness_score = Column(Float, default=0.0)
    
    # Evolutionary parameters
    generation = Column(Integer, default=0)
    parent_id = Column(Integer, ForeignKey("bots.id"), nullable=True)
    mutation_count = Column(Integer, default=0)
    
    # Relationships
    trades = relationship("Trade", back_populates="bot", cascade="all, delete-orphan")
    logs = relationship("BotLog", back_populates="bot", cascade="all, delete-orphan")


class Trade(Base):
    """Trade execution record."""
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    bot_id = Column(Integer, ForeignKey("bots.id"), nullable=False)
    
    # Trade details
    symbol = Column(String, nullable=False)  # e.g., BTC/USD
    side = Column(String, nullable=False)  # buy or sell
    order_type = Column(String, nullable=False)  # market, limit, etc.
    amount = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    
    # Execution details
    executed_at = Column(DateTime(timezone=True), server_default=func.now())
    exchange_order_id = Column(String)
    status = Column(String, default="pending")  # pending, filled, cancelled, failed
    
    # Financial tracking
    fee = Column(Float, default=0.0)
    profit_loss = Column(Float, default=0.0)
    
    # Relationships
    bot = relationship("Bot", back_populates="trades")


class BotLog(Base):
    """Bot activity and decision logs."""
    __tablename__ = "bot_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    bot_id = Column(Integer, ForeignKey("bots.id"), nullable=False)
    
    level = Column(String, default="info")  # info, warning, error
    message = Column(Text, nullable=False)
    details = Column(JSON)  # Additional structured data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    bot = relationship("Bot", back_populates="logs")


class SwarmPool(Base):
    """Pool of bots for evolutionary competition."""
    __tablename__ = "swarm_pools"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text)
    
    # Pool configuration
    max_bots = Column(Integer, default=20)
    selection_pressure = Column(Float, default=0.5)  # Top % to keep
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_evolution = Column(DateTime(timezone=True))
    
    # Performance tracking
    best_fitness = Column(Float, default=0.0)
    total_profit_loss = Column(Float, default=0.0)


class SystemConfig(Base):
    """System-wide configuration and state."""
    __tablename__ = "system_config"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, nullable=False, index=True)
    value = Column(Text)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
