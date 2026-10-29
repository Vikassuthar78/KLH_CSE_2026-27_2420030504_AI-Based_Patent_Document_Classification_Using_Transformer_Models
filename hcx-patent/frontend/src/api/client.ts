import axios from 'axios';

const API_BASE = 'http://localhost:8000/api/v1';

export const api = axios.create({
  baseURL: API_BASE,
  timeout: 300000,
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);
