# Prediction Market Order Matching Engine

A full-stack order matching system for prediction markets. Users trade YES/NO shares on events using price-time priority matching.

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Or: Python 3.11+ and Node.js 18+

### Running with Docker Compose (Recommended)

1. Clone the repository and navigate to the project directory:
```bash
cd prediction-market-exchange
```

2. Build and start all services:
```bash
docker-compose up --build
```

3. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

To stop the services, press `Ctrl+C` or run `docker-compose down`.

### Manual Setup

```bash
# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm start
```

## Architecture

**Backend (FastAPI):**
- `models.py` - Order and Trade data models
- `order_book.py` - Priority queue using heaps (O(log n) insertion)
- `matcher.py` - Price-time priority matching logic
- `main.py` - REST API endpoints

**Frontend (React):**
- Order submission form
- Live order book display
- Real-time trade history

## Design Decisions

### Data Structures
- **Order Book:** Uses Python's `heapq` module for priority queues. Provides O(log n) insertion for new orders and O(1) access to the best price. Heaps are a good balance between performance and code simplicity for moderate order volumes. BUY orders use a max-heap (achieved by negating prices) to prioritize highest bids, while SELL orders use a min-heap for lowest asks.

### Matching Algorithm
- **Price-Time Priority:** Orders match based on best price first, then by timestamp (FIFO) at the same price level. Trades execute at the maker's price (the resting order in the book), which is the standard approach in financial markets and ensures fairness.

### Concurrency Handling
- **Asyncio Locks:** Uses `asyncio.Lock` to serialize order processing, ensuring the order book remains consistent and preventing race conditions. While this limits throughput by processing orders sequentially, it guarantees correctness for this single-market demo. In production, you would shard order books by market or use lock-free data structures for better performance.

### Constraints
- **YES + NO = 100:** Prices always sum to 100 cents, reflecting prediction market mechanics where buying YES at 60¢ implies NO is 40¢.

## Testing

Run the test suite from the backend directory:

```bash
cd backend
pytest tests/ -v
```

The test suite includes 6 tests covering:

1. **Basic matching** (`test_simple_match`) - Verifies orders match when prices cross
2. **Partial fills** (`test_partial_fill`) - Tests orders that fill partially and remain in the book
3. **No matches** (`test_no_match`) - Ensures orders don't match when prices don't cross
4. **Market orders** (`test_market_order`) - Validates market orders (price=0) execute immediately
5. **Self-matching prevention** (`test_self_matching_prevention`) - Prevents users from trading with themselves
6. **FIFO priority** (`test_fifo_priority`) - Confirms time priority at same price levels

All tests use async/await to test the concurrent matching engine properly.

## Limitations

Current implementation is in-memory only. Given more time, I would add:
- Order cancellation
- PostgreSQL persistence
- WebSocket for real-time updates
- Advanced order types (stop-loss, fill-or-kill)
- Authentication and rate limiting

## Tech Stack

FastAPI, React 18, pytest, Docker
