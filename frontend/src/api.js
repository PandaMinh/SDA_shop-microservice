import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use(config => {
  try {
    const user = localStorage.getItem('user');
    if (user) {
      const parsed = JSON.parse(user);
      if (parsed.customer_id) {
        config.headers['X-Customer-Id'] = parsed.customer_id;
      }
      if (parsed.token) {
        config.headers['X-Staff-Token'] = parsed.token;
      }
    }
  } catch (e) {}
  return config;
});

api.interceptors.response.use(
  response => response,
  error => {
    return Promise.reject(error);
  }
);

export default api;
