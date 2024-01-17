// Login.js
import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "./AuthContext";
import CryptoJS from "crypto-js";
import "./Login.css";
import wwfLogo from "../../images/wwf-logo.png";

const Login = () => {
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (isAuthenticated) {
      navigate("/");
    }
  }, [isAuthenticated, navigate]);

  const handleLogin = (event) => {
    event.preventDefault(); // Prevent the default form submit action
    const hashedInputPassword = CryptoJS.SHA256(password).toString();
    const predefinedHashedPassword = process.env.REACT_APP_PASSWORD_HASH;

    if (hashedInputPassword === predefinedHashedPassword) {
      login();
      navigate("/");
      setError("");
    } else {
      setError("Incorrect Password");
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <img className="wwf-logo-login" src={wwfLogo} alt="wwf-logo" />
        <h2>WWF Nepal Dashboard</h2>
        <form onSubmit={handleLogin}>
          <input
            type="password"
            value={password}
            onChange={(e) => {
              setPassword(e.target.value);
              setError("");
            }}
            placeholder="Enter Password"
          />
          <button type="submit">Login</button>
          {error && <p className="error-text">{error}</p>}
        </form>
      </div>
    </div>
  );
};

export default Login;
