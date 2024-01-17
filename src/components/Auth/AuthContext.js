// AuthContext.js
import React, { createContext, useContext, useState, useEffect } from "react";

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  useEffect(() => {
    const token = JSON.parse(localStorage.getItem("authToken"));

    if (token && new Date(token.expiry) > new Date()) {
      setIsAuthenticated(true);
    } else {
      localStorage.removeItem("authToken");
    }
  }, []);

  const login = () => {
    const token = {
      value: "auth_token",
      expiry: new Date().getTime() + 7 * 24 * 60 * 60 * 1000, // 7 days from now
    };
    localStorage.setItem("authToken", JSON.stringify(token));
    setIsAuthenticated(true);
  };

  const logout = () => {
    localStorage.removeItem("authToken");
    setIsAuthenticated(false);
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
