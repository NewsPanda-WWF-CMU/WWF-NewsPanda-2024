// Header.js
import React from "react";
import "./Header.css"; // Make sure the path to the CSS file is correct
import wwfLogo from "../images/wwf-logo.png";
import { useNavigate } from "react-router-dom";
import { useAuth } from "./Auth/AuthContext";
const Header = () => {
  const navigate = useNavigate();
  const { logout } = useAuth();
  return (
    <header className="header">
      <div className="header-logo">
        <img src={wwfLogo} alt="WWF Logo" />{" "}
        {/* Replace with the path to your actual logo */}
      </div>
      <div className="header-navigation">
        <div className="header-dropdown">
          <span
            className="header-dropdown-item"
            onClick={() => {
              navigate("/");
            }}
          >
            Dashboard
          </span>
          <span
            className="header-dropdown-item"
            onClick={() => {
              navigate("/articles");
            }}
          >
            All Articles View
          </span>
          <span
            className="header-dropdown-item"
            onClick={() => {
              navigate("/events");
            }}
          >
            All Events View
          </span>
          <span
            className="header-dropdown-item"
            onClick={() => {
              logout();
              navigate("/login");
            }}
          >
            Logout
          </span>
        </div>
      </div>
    </header>
  );
};

export default Header;
