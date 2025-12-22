from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .models import (
    Order, OrderRequest, OrderBookResponse, 
    MatchResult, Side, OrderType
)
from .matcher import MatchingEngine

# Create FastAPI app
app = FastAPI(
    title="Prediction Market Order Matching Engine",
    description="A simplified order matching system for YES/NO prediction markets",
    version="1.0.0"
)

# Enable CORS so frontend can call our API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create single matching engine instance (in-memory)
matching_engine = MatchingEngine()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Prediction Market Matching Engine API",
        "status": "running"
    }

@app.post("/api/orders", response_model=MatchResult)
async def submit_order(order_request: OrderRequest):
    """
    Submit a new order to the matching engine.
    
    Example request:
    POST /api/orders
    {
      "user_id": "user123",
      "side": "YES",
      "order_type": "BUY",
      "price": 55,
      "quantity": 100
    }
    
    Returns:
    - The order (with filled status)
    - List of trades executed
    - Message describing what happened
    """
    try:
        # Create Order object from request
        order = Order(
            user_id=order_request.user_id,
            side=order_request.side,
            order_type=order_request.order_type,
            price=order_request.price,
            quantity=order_request.quantity
        )
        
        # Process through matching engine
        processed_order, trades = await matching_engine.process_order(order)
        
        # Generate result message
        if len(trades) == 0:
            message = f"Order added to book. No matches found."
        elif processed_order.status.value == "FILLED":
            message = f"Order completely filled with {len(trades)} trade(s)."
        else:
            message = f"Order partially filled with {len(trades)} trade(s). Remainder in book."
        
        return MatchResult(
            order=processed_order,
            trades=trades,
            message=message
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@app.get("/api/orderbook", response_model=OrderBookResponse)
async def get_order_book():
    """
    Get current state of the order book.
    
    Returns all active orders organized by:
    - YES bids (BUY orders)
    - YES asks (SELL orders)
    - NO bids
    - NO asks
    """
    try:
        state = matching_engine.get_order_book_state()
        return OrderBookResponse(**state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/trades")
async def get_trades(limit: int = 20):
    """
    Get recent trade history.
    
    Query params:
    - limit: number of trades to return (default 20)
    """
    try:
        trades = matching_engine.get_recent_trades(limit)
        return {"trades": trades}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats")
async def get_stats():
    """
    Get market statistics.
    
    Returns:
    - Total trades executed
    - Current order book depth
    - Last trade price
    """
    try:
        state = matching_engine.get_order_book_state()
        trades = matching_engine.get_recent_trades(1)
        
        total_orders = (
            len(state['yes_bids']) + len(state['yes_asks']) +
            len(state['no_bids']) + len(state['no_asks'])
        )
        
        last_price = trades[0]['price'] if trades else None
        
        return {
            "total_trades": len(matching_engine.trade_history),
            "active_orders": total_orders,
            "last_trade_price": last_price
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run with: uvicorn app.main:app --reload