import React from "react";
import Header from "./HomePage/Header";
import LandscapeOverview from "./HomePage/LandscapeOverview";
import ArticleList from "./HomePage/ArticleList";
import FaunaFloraBreakdown from "./HomePage/FaunaFloraBreakdown";
import "./HomePage.css";

const HomePage = () => {
  return (
    <div className="App">
      <Header />

      <div style={{ width: "100%" }}>
        {" "}
        <span className="dashboard-title">Dashboard</span>{" "}
        <div style={{ marginLeft: "auto" }}> Filter here</div>
      </div>
      <div className="dashboard-content">
        <LandscapeOverview />
        <ArticleList />
        <FaunaFloraBreakdown />
      </div>
    </div>
  );
};

export default HomePage;
