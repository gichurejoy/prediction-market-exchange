import pytest
from app.models import Order, Side, OrderType
from app.matcher import MatchingEngine

@pytest.fixture
def engine():
    """Create a fresh matching engine for each test"""
    return MatchingEngine()

@pytest.mark.asyncio
async def test_simple_match(engine):
    """Test basic order matching"""
    # Create a sell order
    sell_order = Order(
        user_id="seller1",
        side=Side.YES,
        order_type=OrderType.SELL,
        price=55,
        quantity=100
    )
    
    # Process sell order (should go to order book)
    await engine.process_order(sell_order)
    
    # Create a buy order that matches
    buy_order = Order(
        user_id="buyer1",
        side=Side.YES,
        order_type=OrderType.BUY,
        price=60,  # Willing to pay more
        quantity=100
    )
    
    # Process buy order (should match with sell order)
    processed, trades = await engine.process_order(buy_order)
    
    # Assertions
    assert len(trades) == 1
    assert trades[0].price == 55  # Maker's price
    assert trades[0].quantity == 100
    assert buy_order.filled_quantity == 100
    assert sell_order.filled_quantity == 100

@pytest.mark.asyncio
async def test_partial_fill(engine):
    """Test partial order matching"""
    # Create a sell order for 100 shares
    sell_order = Order(
        user_id="seller1",
        side=Side.YES,
        order_type=OrderType.SELL,
        price=55,
        quantity=100
    )
    
    await engine.process_order(sell_order)
    
    # Create a buy order for only 50 shares
    buy_order = Order(
        user_id="buyer1",
        side=Side.YES,
        order_type=OrderType.BUY,
        price=60,
        quantity=50
    )
    
    processed, trades = await engine.process_order(buy_order)
    
    # Assertions
    assert len(trades) == 1
    assert trades[0].quantity == 50
    assert buy_order.filled_quantity == 50
    assert sell_order.filled_quantity == 50
    assert sell_order.remaining_quantity == 50

@pytest.mark.asyncio
async def test_no_match(engine):
    """Test orders that don't match"""
    # Sell at 60
    sell_order = Order(
        user_id="seller1",
        side=Side.YES,
        order_type=OrderType.SELL,
        price=60,
        quantity=100
    )
    
    await engine.process_order(sell_order)
    
    # Try to buy at 50 (too low)
    buy_order = Order(
        user_id="buyer1",
        side=Side.YES,
        order_type=OrderType.BUY,
        price=50,
        quantity=100
    )
    
    processed, trades = await engine.process_order(buy_order)
    
    # No match should occur
    assert len(trades) == 0
    assert buy_order.filled_quantity == 0

@pytest.mark.asyncio
async def test_market_order(engine):
    """Test market order execution"""
    # Add a sell order
    sell_order = Order(
        user_id="seller1",
        side=Side.YES,
        order_type=OrderType.SELL,
        price=55,
        quantity=100
    )
    
    await engine.process_order(sell_order)
    
    # Create market buy order (price = 0)
    market_order = Order(
        user_id="buyer1",
        side=Side.YES,
        order_type=OrderType.BUY,
        price=0,  # Market order
        quantity=100
    )
    
    processed, trades = await engine.process_order(market_order)
    
    # Should match immediately
    assert len(trades) == 1
    assert trades[0].price == 55
    assert market_order.filled_quantity == 100

@pytest.mark.asyncio
async def test_self_matching_prevention(engine):
    """Test that users can't match with their own orders"""
    # User places sell order
    sell_order = Order(
        user_id="user1",
        side=Side.YES,
        order_type=OrderType.SELL,
        price=55,
        quantity=100
    )
    
    await engine.process_order(sell_order)
    
    # Same user tries to buy
    buy_order = Order(
        user_id="user1",  # Same user!
        side=Side.YES,
        order_type=OrderType.BUY,
        price=60,
        quantity=100
    )
    
    processed, trades = await engine.process_order(buy_order)
    
    # Should not match
    assert len(trades) == 0

@pytest.mark.asyncio
async def test_fifo_priority(engine):
    """Test First-In-First-Out priority at same price"""
    # First seller
    sell1 = Order(
        user_id="seller1",
        side=Side.YES,
        order_type=OrderType.SELL,
        price=55,
        quantity=50
    )
    
    # Second seller at same price
    sell2 = Order(
        user_id="seller2",
        side=Side.YES,
        order_type=OrderType.SELL,
        price=55,
        quantity=50
    )
    
    await engine.process_order(sell1)
    await engine.process_order(sell2)
    
    # Buyer wants 50 shares
    buy_order = Order(
        user_id="buyer1",
        side=Side.YES,
        order_type=OrderType.BUY,
        price=60,
        quantity=50
    )
    
    processed, trades = await engine.process_order(buy_order)
    
    # Should match with first seller
    assert len(trades) == 1
    assert trades[0].maker_order_id == sell1.id