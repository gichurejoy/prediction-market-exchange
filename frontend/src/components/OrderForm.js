import React, { useState } from 'react';
import { submitOrder } from '../api';
import './OrderForm.css';

/**
 * OrderForm Component
 * 
 * Allows users to submit new orders to the matching engine.
 * Handles validation and provides feedback.
 */
const OrderForm = ({ onOrderSubmitted }) => {
  // Form state
  const [userId, setUserId] = useState('user' + Math.floor(Math.random() * 1000));
  const [side, setSide] = useState('YES');
  const [orderType, setOrderType] = useState('BUY');
  const [price, setPrice] = useState(50);
  const [quantity, setQuantity] = useState(10);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState(null);
  const [messageType, setMessageType] = useState('info'); // 'success', 'error', 'info'

  /**
   * Handle form submission
   */
  const handleSubmit = async (e) => {
    e.preventDefault(); // Prevent page reload
    
    // Validation
    if (quantity < 1) {
      showMessage('Quantity must be at least 1', 'error');
      return;
    }
    
    if (price < 0 || price > 100) {
      showMessage('Price must be between 0 and 100', 'error');
      return;
    }
    
    setIsSubmitting(true);
    setMessage(null);
    
    try {
      // Prepare order data
      const orderData = {
        user_id: userId,
        side: side,
        order_type: orderType,
        price: parseInt(price),
        quantity: parseInt(quantity)
      };
      
      // Submit to backend
      const result = await submitOrder(orderData);
      
      // Show success message
      showMessage(result.message, 'success');
      
      // Notify parent component to refresh data
      if (onOrderSubmitted) {
        onOrderSubmitted(result);
      }
      
    } catch (error) {
      // Handle errors
      const errorMsg = error.response?.data?.detail || 'Failed to submit order';
      showMessage(errorMsg, 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  /**
   * Display message to user
   */
  const showMessage = (msg, type) => {
    setMessage(msg);
    setMessageType(type);
    
    // Auto-hide message after 5 seconds
    setTimeout(() => {
      setMessage(null);
    }, 5000);
  };

  /**
   * Handle price type change (market vs limit)
   */
  const handlePriceTypeChange = (e) => {
    const isMarketOrder = e.target.value === 'market';
    if (isMarketOrder) {
      setPrice(0); // Market order price = 0
    } else {
      setPrice(50); // Reset to reasonable limit price
    }
  };

  return (
    <div className="order-form-container">
      <h2>Submit Order</h2>
      
      <form onSubmit={handleSubmit} className="order-form">
        {/* User ID */}
        <div className="form-group">
          <label htmlFor="userId">User ID:</label>
          <input
            type="text"
            id="userId"
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
            required
            placeholder="e.g., user123"
          />
          <small>Simulated user identifier</small>
        </div>

        {/* Side Selection (YES/NO) */}
        <div className="form-group">
          <label>Share Side:</label>
          <div className="radio-group">
            <label className={`radio-label ${side === 'YES' ? 'selected' : ''}`}>
              <input
                type="radio"
                value="YES"
                checked={side === 'YES'}
                onChange={(e) => setSide(e.target.value)}
              />
              <span className="radio-text yes">YES</span>
            </label>
            <label className={`radio-label ${side === 'NO' ? 'selected' : ''}`}>
              <input
                type="radio"
                value="NO"
                checked={side === 'NO'}
                onChange={(e) => setSide(e.target.value)}
              />
              <span className="radio-text no">NO</span>
            </label>
          </div>
          <small>Choose which outcome you're trading</small>
        </div>

        {/* Order Type (BUY/SELL) */}
        <div className="form-group">
          <label>Order Type:</label>
          <div className="radio-group">
            <label className={`radio-label ${orderType === 'BUY' ? 'selected' : ''}`}>
              <input
                type="radio"
                value="BUY"
                checked={orderType === 'BUY'}
                onChange={(e) => setOrderType(e.target.value)}
              />
              <span className="radio-text buy">BUY</span>
            </label>
            <label className={`radio-label ${orderType === 'SELL' ? 'selected' : ''}`}>
              <input
                type="radio"
                value="SELL"
                checked={orderType === 'SELL'}
                onChange={(e) => setOrderType(e.target.value)}
              />
              <span className="radio-text sell">SELL</span>
            </label>
          </div>
        </div>

        {/* Price Type (Market/Limit) */}
        <div className="form-group">
          <label htmlFor="priceType">Price Type:</label>
          <select 
            id="priceType"
            onChange={handlePriceTypeChange}
            defaultValue="limit"
          >
            <option value="limit">Limit Order (specify price)</option>
            <option value="market">Market Order (any price)</option>
          </select>
        </div>

        {/* Price Input */}
        {price > 0 && (
          <div className="form-group">
            <label htmlFor="price">Price (cents):</label>
            <input
              type="number"
              id="price"
              value={price}
              onChange={(e) => setPrice(e.target.value)}
              min="1"
              max="100"
              required
            />
            <small>Price per share (1-100 cents)</small>
            {side === 'YES' && (
              <small className="price-info">
                Implied NO price: {100 - price}¢
              </small>
            )}
            {side === 'NO' && (
              <small className="price-info">
                Implied YES price: {100 - price}¢
              </small>
            )}
          </div>
        )}

        {/* Quantity Input */}
        <div className="form-group">
          <label htmlFor="quantity">Quantity (shares):</label>
          <input
            type="number"
            id="quantity"
            value={quantity}
            onChange={(e) => setQuantity(e.target.value)}
            min="1"
            required
          />
          <small>Number of shares to trade</small>
        </div>

        {/* Order Summary */}
        <div className="order-summary">
          <h3>Order Summary</h3>
          <p>
            <strong>{orderType}</strong> {quantity} shares of <strong>{side}</strong> 
            {price > 0 ? ` at ${price}¢` : ' at market price'}
          </p>
          {price > 0 && (
            <p className="total-cost">
              Total: {(quantity * price).toFixed(0)}¢ (${(quantity * price / 100).toFixed(2)})
            </p>
          )}
        </div>

        {/* Message Display */}
        {message && (
          <div className={`message message-${messageType}`}>
            {message}
          </div>
        )}

        {/* Submit Button */}
        <button 
          type="submit" 
          className="submit-btn"
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Submitting...' : 'Submit Order'}
        </button>
      </form>
    </div>
  );
};

export default OrderForm;