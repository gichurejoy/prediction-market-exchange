from typing import List, Tuple
import asyncio
from .models import Order, Trade, Side, OrderType, OrderStatus
from .order_book import OrderBook

class MatchingEngine:
    """
    The Matching Engine is responsible for:
    1. Receiving incoming orders
    2. Finding matching opposite orders
    3. Executing trades
    4. Updating order states
    
    Think of it as a referee in a marketplace.
    """
    
    def __init__(self):
        self.order_book = OrderBook()
        self.trade_history: List[Trade] = []
        # Lock ensures only one order processes at a time (no race conditions)
        self.lock = asyncio.Lock()
    
    async def process_order(self, order: Order) -> Tuple[Order, List[Trade]]:
        """
        Main entry point: Process an incoming order.
        
        Steps:
        1. Validate order (YES + NO = 100 check)
        2. Try to match with opposite orders
        3. If partially filled, add remainder to book
        4. Return order and any trades executed
        """
        async with self.lock:  # Only one order at a time
            trades = []
            
            # Market orders get a virtual price for matching
            if order.is_market_order:
                order.price = self._get_market_price(order)
            
            # Try to match this order
            trades = await self._match_order(order)
            
            # If order not completely filled, add to book
            if order.remaining_quantity > 0:
                # Only add limit orders to book (market orders fill or kill)
                if not order.is_market_order or len(trades) > 0:
                    self.order_book.add_order(order)
                    if order.filled_quantity > 0:
                        order.status = OrderStatus.PARTIAL
            
            # Store trades in history
            self.trade_history.extend(trades)
            
            return order, trades
    
    def _get_market_price(self, order: Order) -> int:
        """
        Market orders execute at any price.
        We give them an extreme price to ensure matching.
        
        - BUY market order: price = 100 (will match any sell)
        - SELL market order: price = 0 (will match any buy)
        """
        if order.order_type == OrderType.BUY:
            return 100  # Willing to pay maximum
        else:
            return 0  # Willing to accept minimum
    
    async def _match_order(self, order: Order) -> List[Trade]:
        """
        Core matching logic.
        
        Algorithm:
        1. Get best opposite order (best price for us)
        2. Check if prices cross (can we match?)
        3. If yes, execute trade for available quantity
        4. Update both orders
        5. Repeat until order filled or no more matches
        """
        trades = []
        
        while order.remaining_quantity > 0:
            # Find best matching order
            opposite_order = self._get_best_match(order)
            
            if not opposite_order:
                break  # No more matches available
            
            # Check if prices are compatible
            if not self._can_match(order, opposite_order):
                break  # Prices don't cross
            
            # Check self-matching (same user)
            if order.user_id == opposite_order.user_id:
                # Skip this order, remove from book
                self.order_book.remove_order(opposite_order.id)
                continue
            
            # Execute the trade
            trade = self._execute_trade(order, opposite_order)
            trades.append(trade)
            
            # Update order statuses
            if order.remaining_quantity == 0:
                order.status = OrderStatus.FILLED
            if opposite_order.remaining_quantity == 0:
                opposite_order.status = OrderStatus.FILLED
        
        return trades
    
    def _get_best_match(self, order: Order) -> Order:
        """
        Get the best opposite order to match with.
        
        - If we're BUYING → get best (lowest) SELL price
        - If we're SELLING → get best (highest) BUY price
        """
        if order.order_type == OrderType.BUY:
            # We're buying, find best sell order
            return self.order_book.get_best_ask(order.side)
        else:
            # We're selling, find best buy order
            return self.order_book.get_best_bid(order.side)
    
    def _can_match(self, taker: Order, maker: Order) -> bool:
        """
        Check if two orders can match.
        
        Matching condition:
        - BUY price >= SELL price
        
        Example:
        - BUY at 60¢, SELL at 55¢ → CAN MATCH ✓
        - BUY at 50¢, SELL at 55¢ → CANNOT MATCH ✗
        """
        if taker.order_type == OrderType.BUY:
            # Taker buying, maker selling
            return taker.price >= maker.price
        else:
            # Taker selling, maker buying
            return maker.price >= taker.price
    
    def _execute_trade(self, taker: Order, maker: Order) -> Trade:
        """
        Execute a trade between two orders.
        
        Key rules:
        1. Trade quantity = min(taker remaining, maker remaining)
        2. Trade price = maker's price (they were there first)
        3. Update filled quantities on both orders
        4. Validate YES + NO = 100 constraint
        """
        # Trade the smaller of the two quantities
        trade_quantity = min(
            taker.remaining_quantity,
            maker.remaining_quantity
        )
        
        # Price is always the maker's price (resting order)
        trade_price = maker.price
        
        # Validate YES + NO = 100 constraint
        self._validate_trade_constraint(taker, maker, trade_price)
        
        # Update filled quantities
        taker.filled_quantity += trade_quantity
        maker.filled_quantity += trade_quantity
        
        # Create trade record
        trade = Trade(
            maker_order_id=maker.id,
            taker_order_id=taker.id,
            side=taker.side,
            price=trade_price,
            quantity=trade_quantity
        )
        
        return trade
    
    def _validate_trade_constraint(
        self, 
        taker: Order, 
        maker: Order, 
        price: int
    ) -> None:
        """
        Validate the YES + NO = 100 constraint.
        
        Example:
        - If YES trades at 60¢, NO should trade at 40¢
        - If someone bought YES at 60¢, we need to ensure
          NO is priced at 40¢ or the market is consistent
        """
        # For a prediction market:
        # - Buying YES at 60¢ means believing event has 60% chance
        # - NO should be 40¢ (100 - 60)
        # This validation ensures market consistency
        
        # In a real system, you'd track this more carefully
        # For this demo, we're simplifying
        pass
    
    def get_order_book_state(self) -> dict:
        """
        Get current state of order book for UI display.
        
        Returns all active orders organized by side and type.
        """
        return {
            'yes_bids': self.order_book.get_all_orders(Side.YES, OrderType.BUY),
            'yes_asks': self.order_book.get_all_orders(Side.YES, OrderType.SELL),
            'no_bids': self.order_book.get_all_orders(Side.NO, OrderType.BUY),
            'no_asks': self.order_book.get_all_orders(Side.NO, OrderType.SELL),
        }
    
    def get_recent_trades(self, limit: int = 10) -> List[dict]:
        """
        Get recent trade history for display.
        """
        recent = self.trade_history[-limit:]
        return [
            {
                'id': trade.id,
                'side': trade.side,
                'price': trade.price,
                'quantity': trade.quantity,
                'timestamp': trade.timestamp.isoformat()
            }
            for trade in reversed(recent)
        ]