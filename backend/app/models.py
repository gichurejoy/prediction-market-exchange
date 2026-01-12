from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional
from datetime import datetime, UTC
from enum import Enum
import uuid

# Enums for order properties
class Side(str, Enum):
    """YES or NO shares"""
    YES = "YES"
    NO = "NO"

class OrderType(str, Enum):
    """BUY or SELL"""
    BUY = "BUY"
    SELL = "SELL"

class OrderStatus(str, Enum):
    """Order lifecycle states"""
    PENDING = "PENDING"      # Just created
    PARTIAL = "PARTIAL"      # Partially filled
    FILLED = "FILLED"        # Completely filled
    CANCELLED = "CANCELLED"  # Cancelled by user

class Order(BaseModel):
    """
    Represents a single order in the system.
    
    Example:
    - User123 wants to BUY 100 YES shares at 55 cents each
    - Order(user_id="User123", side="YES", order_type="BUY", 
            price=55, quantity=100)
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    side: Side  # YES or NO
    order_type: OrderType  # BUY or SELL
    price: int  # In cents (0-100), 0 means market order
    quantity: int  # Number of shares
    filled_quantity: int = 0  # How many shares have been filled
    status: OrderStatus = OrderStatus.PENDING
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator('price')
    def validate_price(cls, v):
        """Price must be between 0 and 100 cents"""
        if not 0 <= v <= 100:
            raise ValueError('Price must be between 0 and 100 cents')
        return v
    
    @field_validator('quantity')
    def validate_quantity(cls, v):
        """Minimum order size is 1 share"""
        if v < 1:
            raise ValueError('Quantity must be at least 1')
        return v
    
    @property
    def remaining_quantity(self) -> int:
        """How many shares still need to be filled"""
        return self.quantity - self.filled_quantity
    
    @property
    def is_market_order(self) -> bool:
        """Market orders have price = 0"""
        return self.price == 0

class Trade(BaseModel):
    """
    Represents a completed trade between two orders.
    
    Example:
    - Alice's BUY order matched with Bob's SELL order
    - Trade(maker_order_id=Bob's_order, taker_order_id=Alice's_order,
            price=55, quantity=50)
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    maker_order_id: str  # Order that was resting in the book
    taker_order_id: str  # Order that came in and matched
    side: Side  # YES or NO
    price: int  # Price at which trade executed
    quantity: int  # Number of shares traded
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))

class OrderRequest(BaseModel):
    """
    What the API receives when someone submits an order.
    
    Example frontend request:
    {
      "user_id": "User123",
      "side": "YES",
      "order_type": "BUY",
      "price": 55,
      "quantity": 100
    }
    """
    user_id: str
    side: Side
    order_type: OrderType
    price: int
    quantity: int

class OrderBookResponse(BaseModel):
    """
    What we send to the frontend to display the order book.
    
    Shows all resting orders organized by YES/NO and BUY/SELL
    """
    yes_bids: list[dict]  # BUY orders for YES shares
    yes_asks: list[dict]  # SELL orders for YES shares
    no_bids: list[dict]   # BUY orders for NO shares
    no_asks: list[dict]   # SELL orders for NO shares

class MatchResult(BaseModel):
    """
    What we return after processing an order.
    
    Shows the submitted order and any trades that happened.
    """
    order: Order
    trades: list[Trade]
    message: str