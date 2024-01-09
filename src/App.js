import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import AllArticleList from "./components/AllArticlesList";
import HomePage from "./components/HomePage";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/articles" element={<AllArticleList />} />

        <Route path="/" element={<HomePage />} />
      </Routes>
    </Router>
  );
}

export default App;
