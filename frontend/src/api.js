import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:3000";

const api = axios.create({
  baseURL: API_URL,
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("toolshare_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth
export const registerUser = (data) => api.post("/auth/register", data);
export const loginUser = (data) => api.post("/auth/login", data);

// Tools
export const getTools = () => api.get("/tools");
export const getTool = (id) => api.get(`/tools/${id}`);
export const createTool = (data) => api.post("/tools", data);
export const updateTool = (id, data) => api.put(`/tools/${id}`, data);
export const deleteTool = (id) => api.delete(`/tools/${id}`);

// Loans
export const borrowTool = (toolId, data) => api.post(`/tools/${toolId}/borrow`, data);
export const returnTool = (toolId) => api.post(`/tools/${toolId}/return`);
export const getLoans = () => api.get("/loans");
export const getOverdueLoans = () => api.get("/loans/overdue");

// Dashboard
export const getDashboard = () => api.get("/dashboard");

// Notifications
export const subscribe = (email) => api.post("/subscribe", { email });
export const getSubscribers = () => api.get("/subscribers");

export default api;
