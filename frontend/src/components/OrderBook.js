import React from 'react';
import './OrderBook.css';

/**
 * OrderBook Component
 * 
 * Displays the current state of the order book.
 * Shows all resting orders organized by side (YES/NO) and type (BUY/SELL).
 */
const OrderBook = ({ orderBook }) => {
  // Check if we have data
  if (!orderBook) {
    return (
      <div className="order-book-container">
        <h2>Order Book</h2>
        <p className="loading">Loading order book...</p>
      </div>
    );
  }

  /**
   * Render a single side of the order book (YES or NO)
   */
  const renderSide = (sideName, bids, asks) => {
    const sideClass = sideName === 'YES' ? 'yes-side' : 'no-side';
    
    return (
      <div className={`order-book-side ${sideClass}`}>
        <h3>{sideName} Shares</h3>
        
        <div className="orders-container">
          {/* BUY Orders (Bids) */}
          <div className="order-column">
            <h4 className="buy-header">BUY Orders (Bids)</h4>
            {bids && bids.length > 0 ? (
              <div className="orders-list">
                <div className="order-header">
                  <span>Price</span>
                  <span>Quantity</span>
                  <span>User</span>
                </div>
                {bids.map((order, idx) => (
                  <div key={idx} className="order-row bid-row">
                    <span className="order-price">{order.price}¢</span>
                    <span className="order-quantity">{order.quantity}</span>
                    <span className="order-user">{order.user_id}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="empty-orders">No buy orders</p>
            )}
          </div>

          {/* SELL Orders (Asks) */}
          <div className="order-column">
            <h4 className="sell-header">SELL Orders (Asks)</h4>
            {asks && asks.length > 0 ? (
              <div className="orders-list">
                <div className="order-header">
                  <span>Price</span>
                  <span>Quantity</span>
                  <span>User</span>
                </div>
                {asks.map((order, idx) => (
                  <div key={idx} className="order-row ask-row">
                    <span className="order-price">{order.price}¢</span>
                    <span className="order-quantity">{order.quantity}</span>
                    <span className="order-user">{order.user_id}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="empty-orders">No sell orders</p>
            )}
          </div>
        </div>

        {/* Spread Information */}
        {bids && bids.length > 0 && asks && asks.length > 0 && (
          <div className="spread-info">
            <strong>Spread:</strong> {asks[0].price - bids[0].price}¢
            <span className="spread-detail">
              (Best Bid: {bids[0].price}¢ | Best Ask: {asks[0].price}¢)
            </span>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="order-book-container">
      <h2>Order Book</h2>
      
      <div className="order-book-grid">
        {/* YES Side */}
        {renderSide('YES', orderBook.yes_bids, orderBook.yes_asks)}
        
        {/* NO Side */}
        {renderSide('NO', orderBook.no_bids, orderBook.no_asks)}
      </div>

      {/* Market Info */}
      <div className="market-info">
        <p className="info-text">
          <strong>💡 Tip:</strong> YES price + NO price always equals 100¢
        </p>
        <p className="info-text">
          Orders are sorted by best price first (highest for bids, lowest for asks)
        </p>
      </div>
    </div>
  );
};

export default OrderBook;