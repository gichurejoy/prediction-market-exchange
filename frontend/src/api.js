import axios from 'axios';

// Base URL for backend API
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Submit a new order to the matching engine
 * 
 * @param {Object} orderData - Order details
 * @param {string} orderData.user_id - User identifier
 * @param {string} orderData.side - "YES" or "NO"
 * @param {string} orderData.order_type - "BUY" or "SELL"
 * @param {number} orderData.price - Price in cents (0-100)
 * @param {number} orderData.quantity - Number of shares
 * @returns {Promise} Order result with trades
 */
export const submitOrder = async (orderData) => {
  try {
    const response = await api.post('/api/orders', orderData);
    return response.data;
  } catch (error) {
    console.error('Error submitting order:', error);
    throw error;
  }
};

/**
 * Fetch current order book state
 * 
 * @returns {Promise} Order book with bids and asks for YES/NO
 */
export const fetchOrderBook = async () => {
  try {
    const response = await api.get('/api/orderbook');
    return response.data;
  } catch (error) {
    console.error('Error fetching order book:', error);
    throw error;
  }
};

/**
 * Fetch recent trade history
 * 
 * @param {number} limit - Number of trades to fetch
 * @returns {Promise} List of recent trades
 */
export const fetchTrades = async (limit = 20) => {
  try {
    const response = await api.get(`/api/trades?limit=${limit}`);
    return response.data.trades;
  } catch (error) {
    console.error('Error fetching trades:', error);
    throw error;
  }
};

/**
 * Fetch market statistics
 * 
 * @returns {Promise} Market stats
 */
export const fetchStats = async () => {
  try {
    const response = await api.get('/api/stats');
    return response.data;
  } catch (error) {
    console.error('Error fetching stats:', error);
    throw error;
  }
};