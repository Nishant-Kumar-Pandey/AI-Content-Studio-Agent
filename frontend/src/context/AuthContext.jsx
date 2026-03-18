import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [isAuthenticated, setIsAuthenticated] = useState(!!localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUser = async (authToken) => {
      try {
        const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8080";
        const BASE_CLEAN = API_BASE.endsWith('/') ? API_BASE.slice(0, -1) : API_BASE;
        const res = await fetch(`${BASE_CLEAN}/auth/me`, {
          headers: { 'Authorization': `Bearer ${authToken}` }
        });
        if (res.ok) {
          const userData = await res.json();
          localStorage.setItem('user', JSON.stringify(userData));
          setUser(userData);
          setIsAuthenticated(true);
        } else {
          logout();
        }
      } catch (err) {
        console.error("Failed to fetch user profile:", err);
        logout();
      } finally {
        setLoading(false);
      }
    };

    // Check for token in URL fragment (OAuth callback)
    const hash = window.location.hash;
    if (hash && hash.includes('token=')) {
      const tokenFromHash = hash.split('token=')[1].split('&')[0];
      localStorage.setItem('token', tokenFromHash);
      setToken(tokenFromHash);
      window.location.hash = ""; // Clear hash
      fetchUser(tokenFromHash);
    } else {
      const storedToken = localStorage.getItem('token');
      const storedUser = localStorage.getItem('user');
      if (storedToken && storedUser) {
        setToken(storedToken);
        setUser(JSON.parse(storedUser));
        setIsAuthenticated(true);
        setLoading(false);
      } else if (storedToken) {
        setToken(storedToken);
        fetchUser(storedToken);
      } else {
        setLoading(false);
      }
    }
  }, []);

  const login = (newToken, userData) => {
    localStorage.setItem('token', newToken);
    localStorage.setItem('user', JSON.stringify(userData));
    setToken(newToken);
    setUser(userData);
    setIsAuthenticated(true);
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setToken(null);
    setUser(null);
    setIsAuthenticated(false);
  };

  return (
    <AuthContext.Provider value={{ user, token, isAuthenticated, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

// eslint-disable-next-line react-refresh/only-export-components
export const useAuth = () => useContext(AuthContext);
