import React, { createContext, useContext, useReducer, useEffect } from "react";
import axios from "axios";
import API_BASE_URL from "../config/api";

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Auth context
const AuthContext = createContext();

// Auth reducer
const authReducer = (state, action) => {
  switch (action.type) {
    case "LOGIN_START":
      return { ...state, loading: true, error: null };
    case "LOGIN_SUCCESS":
      return {
        ...state,
        loading: false,
        isAuthenticated: true,
        user: action.payload.user,
        token: action.payload.token,
        error: null,
      };
    case "LOGIN_FAILURE":
      return {
        ...state,
        loading: false,
        isAuthenticated: false,
        user: null,
        token: null,
        error: action.payload,
      };
    case "LOGOUT":
      return {
        ...state,
        isAuthenticated: false,
        user: null,
        token: null,
        error: null,
      };
    case "CLEAR_ERROR":
      return { ...state, error: null };
    default:
      return state;
  }
};

// Initial state
const initialState = {
  isAuthenticated: false,
  user: null,
  token: localStorage.getItem("token"),
  loading: false,
  error: null,
};

// Auth provider component
export const AuthProvider = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Set up axios interceptors
  useEffect(() => {
    // Request interceptor to add token
    const requestInterceptor = api.interceptors.request.use(
      (config) => {
        if (state.token) {
          config.headers.Authorization = `Bearer ${state.token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor to handle token expiration
    const responseInterceptor = api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          dispatch({ type: "LOGOUT" });
          localStorage.removeItem("token");
        }
        return Promise.reject(error);
      }
    );

    return () => {
      api.interceptors.request.eject(requestInterceptor);
      api.interceptors.response.eject(responseInterceptor);
    };
  }, [state.token]);

  // Check if user is logged in on app start
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      // Verify token validity by making a request
      api
        .get("/auth/verify")
        .then((response) => {
          dispatch({
            type: "LOGIN_SUCCESS",
            payload: {
              user: response.data.user,
              token: token,
            },
          });
        })
        .catch(() => {
          localStorage.removeItem("token");
          dispatch({ type: "LOGOUT" });
        });
    }
  }, []);

  // Login function
  const login = async (username, password) => {
    dispatch({ type: "LOGIN_START" });
    try {
      const response = await api.post("/auth/login", { username, password });
      const { access_token, user } = response.data;

      localStorage.setItem("token", access_token);
      dispatch({
        type: "LOGIN_SUCCESS",
        payload: { user, token: access_token },
      });

      return { success: true };
    } catch (error) {
      const errorMessage = error.response?.data?.error || "Login failed";
      dispatch({ type: "LOGIN_FAILURE", payload: errorMessage });
      return { success: false, error: errorMessage };
    }
  };

  // Register function
  const register = async (username, email, password) => {
    dispatch({ type: "LOGIN_START" });
    try {
      const response = await api.post("/auth/register", {
        username,
        email,
        password,
      });
      const { access_token, user_id } = response.data;

      localStorage.setItem("token", access_token);
      dispatch({
        type: "LOGIN_SUCCESS",
        payload: {
          user: { id: user_id, username, email },
          token: access_token,
        },
      });

      return { success: true };
    } catch (error) {
      const errorMessage = error.response?.data?.error || "Registration failed";
      dispatch({ type: "LOGIN_FAILURE", payload: errorMessage });
      return { success: false, error: errorMessage };
    }
  };

  // Logout function
  const logout = () => {
    localStorage.removeItem("token");
    dispatch({ type: "LOGOUT" });
  };

  // Clear error function
  const clearError = () => {
    dispatch({ type: "CLEAR_ERROR" });
  };

  const value = {
    ...state,
    login,
    register,
    logout,
    clearError,
    api,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Custom hook to use auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

export default AuthContext;
