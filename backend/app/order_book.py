from collections import defaultdict
from typing import List, Optional
import heapq
from datetime import datetime
from .models import Order, Side, OrderType

class OrderBook:
    """
    The Order Book stores all resting (unfilled) orders.
    
    Think of it like 4 sorted lists:
    1. YES BUY orders  (sorted high price first)
    2. YES SELL orders (sorted low price first)
    3. NO BUY orders   (sorted high price first)
    4. NO SELL orders  (sorted low price first)
    
    Why? Because:
    - Buyers want the LOWEST sell price
    - Sellers want the HIGHEST buy price
    """
    
    def __init__(self):
        # Using heaps for efficient priority queue operations
        # Heap gives us O(log n) insertion and O(1) peek at best price
        
        # For BUY orders: We want HIGHEST price first
        # Python heapq is min-heap, so we negate prices for max-heap behavior
        self.yes_bids: List[tuple] = []  # [(negative_price, timestamp, order), ...]
        self.no_bids: List[tuple] = []
        
        # For SELL orders: We want LOWEST price first
        # Min-heap works naturally here
        self.yes_asks: List[tuple] = []  # [(price, timestamp, order), ...]
        self.no_asks: List[tuple] = []
        
        # Quick lookup by order ID
        self.orders_by_id: dict[str, Order] = {}
    
    def add_order(self, order: Order) -> None:
        """
        Add an order to the appropriate heap.
        
        Example:
        - BUY YES at 60 cents → goes to yes_bids
        - SELL NO at 40 cents → goes to no_asks
        """
        # Store in lookup dict
        self.orders_by_id[order.id] = order
        
        # Create heap entry: (priority, timestamp, order)
        # Timestamp ensures FIFO for same price (price-time priority)
        timestamp = order.timestamp.timestamp()
        
        if order.side == Side.YES:
            if order.order_type == OrderType.BUY:
                # Negate price for max-heap behavior (highest price first)
                heapq.heappush(self.yes_bids, (-order.price, timestamp, order))
            else:  # SELL
                # Normal min-heap (lowest price first)
                heapq.heappush(self.yes_asks, (order.price, timestamp, order))
        else:  # NO
            if order.order_type == OrderType.BUY:
                heapq.heappush(self.no_bids, (-order.price, timestamp, order))
            else:  # SELL
                heapq.heappush(self.no_asks, (order.price, timestamp, order))
    
    def get_best_bid(self, side: Side) -> Optional[Order]:
        """
        Get the highest BUY price for a side.
        
        Example:
        - YES bids: [60¢, 58¢, 55¢] → returns 60¢ order
        """
        heap = self.yes_bids if side == Side.YES else self.no_bids
        
        # Clean up filled orders from top of heap
        while heap and heap[0][2].remaining_quantity == 0:
            heapq.heappop(heap)
        
        return heap[0][2] if heap else None
    
    def get_best_ask(self, side: Side) -> Optional[Order]:
        """
        Get the lowest SELL price for a side.
        
        Example:
        - YES asks: [62¢, 65¢, 70¢] → returns 62¢ order
        """
        heap = self.yes_asks if side == Side.YES else self.no_asks
        
        # Clean up filled orders
        while heap and heap[0][2].remaining_quantity == 0:
            heapq.heappop(heap)
        
        return heap[0][2] if heap else None
    
    def remove_order(self, order_id: str) -> Optional[Order]:
        """
        Remove an order (e.g., if cancelled).
        
        Note: We don't actually remove from heap (expensive),
        we just mark as filled. Heap will clean itself up lazily.
        """
        order = self.orders_by_id.pop(order_id, None)
        if order:
            # Mark as fully filled so it gets skipped
            order.filled_quantity = order.quantity
        return order
    
    def get_all_orders(self, side: Side, order_type: OrderType) -> List[dict]:
        """
        Get all active orders for display in UI.
        
        Returns sorted by best price first.
        """
        if side == Side.YES:
            heap = self.yes_bids if order_type == OrderType.BUY else self.yes_asks
        else:
            heap = self.no_bids if order_type == OrderType.BUY else self.no_asks
        
        # Filter out filled orders and convert to dict
        active_orders = [
            {
                'id': order.id,
                'price': order.price,
                'quantity': order.remaining_quantity,
                'user_id': order.user_id
            }
            for _, _, order in heap
            if order.remaining_quantity > 0
        ]
        
        # Sort by price (best first)
        if order_type == OrderType.BUY:
            # BUY: highest price first
            active_orders.sort(key=lambda x: x['price'], reverse=True)
        else:
            # SELL: lowest price first
            active_orders.sort(key=lambda x: x['price'])
        
        return active_orders