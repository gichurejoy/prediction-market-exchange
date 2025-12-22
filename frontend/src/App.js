import React, { useState, useEffect } from 'react';
import OrderForm from './components/OrderForm';
import OrderBook from './components/OrderBook';
import TradeHistory from './components/TradeHistory';
import { fetchOrderBook, fetchTrades, fetchStats } from './api';
import './App.css';

/**
 * Main App Component
 * 
 * Orchestrates the entire application:
 * - Manages state for order book and trades
 * - Refreshes data after new orders
 * - Displays all components
 */
function App() {
  // State management
  const [orderBook, setOrderBook] = useState(null);
  const [trades, setTrades] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  /**
   * Fetch all data from backend
   */
  const loadData = async () => {
    try {
      setError(null);
      
      // Fetch order book, trades, and stats in parallel
      const [bookData, tradesData, statsData] = await Promise.all([
        fetchOrderBook(),
        fetchTrades(20),
        fetchStats()
      ]);
      
      setOrderBook(bookData);
      setTrades(tradesData);
      setStats(statsData);
      setLoading(false);
    } catch (err) {
      console.error('Error loading data:', err);
      setError('Failed to connect to backend. Make sure the server is running.');
      setLoading(false);
    }
  };

  /**
   * Initial data load on component mount
   */
  useEffect(() => {
    loadData();
  }, []);

  /**
   * Auto-refresh data every 5 seconds if enabled
   */
  useEffect(() => {
    if (!autoRefresh) return;
    
    const interval = setInterval(() => {
      loadData();
    }, 5000); // Refresh every 5 seconds
    
    // Cleanup interval on unmount
    return () => clearInterval(interval);
  }, [autoRefresh]);

  /**
   * Handle new order submission
   * Refresh data to show updated order book and trades
   */
  const handleOrderSubmitted = (result) => {
    console.log('Order submitted:', result);
    // Refresh data immediately after order submission
    loadData();
  };

  /**
   * Toggle auto-refresh
   */
  const toggleAutoRefresh = () => {
    setAutoRefresh(!autoRefresh);
  };

  /**
   * Manual refresh
   */
  const handleManualRefresh = () => {
    loadData();
  };

  // Loading state
  if (loading) {
    return (
      <div className="App">
        <div className="loading-screen">
          <div className="spinner"></div>
          <p>Loading Prediction Market...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="App">
        <div className="error-screen">
          <h2>⚠️ Connection Error</h2>
          <p>{error}</p>
          <button onClick={loadData} className="retry-btn">
            Retry Connection
          </button>
          <div className="error-help">
            <p><strong>Troubleshooting:</strong></p>
            <ul>
              <li>Make sure the backend is running: <code>uvicorn app.main:app --reload</code></li>
              <li>Check that backend is on <code>http://localhost:8000</code></li>
              <li>Look for CORS errors in browser console</li>
            </ul>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="App">
      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <h1>📊 Prediction Market Exchange</h1>
          <p className="tagline">Order Matching Engine Demo</p>
        </div>
        
        {/* Stats Bar */}
        {stats && (
          <div className="stats-bar">
            <div className="stat-item">
              <span className="stat-label">Total Trades:</span>
              <span className="stat-value">{stats.total_trades}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Active Orders:</span>
              <span className="stat-value">{stats.active_orders}</span>
            </div>
            {stats.last_trade_price !== null && (
              <div className="stat-item">
                <span className="stat-label">Last Price:</span>
                <span className="stat-value">{stats.last_trade_price}¢</span>
              </div>
            )}
          </div>
        )}
        
        {/* Controls */}
        <div className="header-controls">
          <button 
            onClick={handleManualRefresh} 
            className="refresh-btn"
            title="Refresh data"
          >
            🔄 Refresh
          </button>
          <label className="auto-refresh-toggle">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={toggleAutoRefresh}
            />
            <span>Auto-refresh (5s)</span>
          </label>
        </div>
      </header>

      {/* Main Content */}
      <main className="app-main">
        {/* Left Column: Order Form */}
        <aside className="sidebar">
          <OrderForm onOrderSubmitted={handleOrderSubmitted} />
          
          {/* Info Box */}
          <div className="info-box">
            <h3>💡 How It Works</h3>
            <ul>
              <li><strong>YES/NO Shares:</strong> Trade on event outcomes</li>
              <li><strong>Price Constraint:</strong> YES + NO = 100¢ always</li>
              <li><strong>Matching:</strong> Orders match when prices cross</li>
              <li><strong>Priority:</strong> Best price first, then time (FIFO)</li>
              <li><strong>Market Orders:</strong> Execute immediately at best available price</li>
            </ul>
          </div>
        </aside>

        {/* Right Column: Order Book and Trades */}
        <section className="main-content">
          <OrderBook orderBook={orderBook} />
          <TradeHistory trades={trades} />
        </section>
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <p>
          Built with FastAPI + React | 
          <a 
            href="http://localhost:8000/docs" 
            target="_blank" 
            rel="noopener noreferrer"
          >
            API Docs
          </a>
        </p>
      </footer>
    </div>
  );
}

export default App;