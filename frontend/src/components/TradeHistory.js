import React from 'react';
import './TradeHistory.css';

/**
 * TradeHistory Component
 * 
 * Displays recent trades that have been executed.
 * Shows price, quantity, side, and timestamp.
 */
const TradeHistory = ({ trades }) => {
  /**
   * Format timestamp to readable string
   */
  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  /**
   * Format timestamp to show how long ago
   */
  const timeAgo = (timestamp) => {
    const now = new Date();
    const tradeTime = new Date(timestamp);
    const seconds = Math.floor((now - tradeTime) / 1000);
    
    if (seconds < 60) return `${seconds}s ago`;
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    return `${hours}h ago`;
  };

  return (
    <div className="trade-history-container">
      <h2>Recent Trades</h2>
      
      {!trades || trades.length === 0 ? (
        <div className="no-trades">
          <p>No trades yet. Submit orders to see matches!</p>
        </div>
      ) : (
        <div className="trades-list">
          <div className="trade-header">
            <span>Time</span>
            <span>Side</span>
            <span>Price</span>
            <span>Quantity</span>
            <span>Total</span>
          </div>
          
          {trades.map((trade) => (
            <div key={trade.id} className={`trade-row ${trade.side.toLowerCase()}-trade`}>
              <span className="trade-time" title={formatTime(trade.timestamp)}>
                {timeAgo(trade.timestamp)}
              </span>
              <span className={`trade-side ${trade.side.toLowerCase()}`}>
                {trade.side}
              </span>
              <span className="trade-price">{trade.price}¢</span>
              <span className="trade-quantity">{trade.quantity}</span>
              <span className="trade-total">
                {(trade.price * trade.quantity).toFixed(0)}¢
              </span>
            </div>
          ))}
        </div>
      )}
      
      <div className="trade-info">
        <p>
          <strong>💡 How to read:</strong> Each row shows a completed trade between a buyer and seller.
          The price is always the maker's (resting order's) price.
        </p>
      </div>
    </div>
  );
};

export default TradeHistory;