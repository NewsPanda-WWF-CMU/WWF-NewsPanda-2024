// App.js
import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import AllArticleList from "./components/AllArticlesList";
import HomePage from "./components/HomePage";
import { AuthProvider } from "./components/Auth/AuthContext";
import ProtectedRoute from "./components/Auth/ProtectedRoute";
import Login from "./components/Auth/Login";
import AllEventsList from "./components/AllEvents";

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />

          <Route
            path="/articles"
            element={
              <ProtectedRoute>
                <AllArticleList />
              </ProtectedRoute>
            }
          />
          <Route
            path="/events"
            element={
              <ProtectedRoute>
                <AllEventsList />
              </ProtectedRoute>
            }
          />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <HomePage />
              </ProtectedRoute>
            }
          />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
