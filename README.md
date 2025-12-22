# Prediction Market Order Matching Engine

A full-stack order matching system for prediction markets. Users trade YES/NO shares on events using price-time priority matching.

## Quick Start

**Docker:**
```bash
docker-compose up --build
```

Frontend: http://localhost:3000  
Backend: http://localhost:8000/docs

**Manual:**

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

- **Order Book:** Python `heapq` for priority queues. O(log n) insertion, O(1) best-price access. Sufficient for moderate volumes.
- **Matching:** Price-time priority with FIFO. Trades execute at maker's price. Standard financial market approach.
- **Concurrency:** Asyncio locks serialize order processing. Ensures consistency. Production would use sharding or lock-free structures for better throughput.
- **Constraint:** YES + NO prices always sum to 100 cents, enforced at trade execution.

## Testing

```bash
cd backend
pytest tests/ -v
```

All 6 tests pass covering matching logic, partial fills, FIFO priority, and self-matching prevention.

## Limitations

Current implementation is in-memory only. Given more time, I would add:
- Order cancellation
- PostgreSQL persistence
- WebSocket for real-time updates
- Advanced order types (stop-loss, fill-or-kill)
- Authentication and rate limiting

## Tech Stack

FastAPI, React 18, pytest, Docker
