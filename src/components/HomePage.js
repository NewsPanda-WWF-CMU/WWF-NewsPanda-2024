import React from "react";
import Header from "./Header";
import LandscapeOverview from "./HomePage/LandscapeOverview";
import FaunaFloraBreakdown from "./HomePage/FaunaFloraBreakdown";
import "./HomePage.css";
import AllArticlesList from "./AllArticlesList";
import { useNavigate } from "react-router-dom";

const HomePage = () => {
  const navigate = useNavigate();
  return (
    <div className="App">
      <Header />

      <h1 className="dashboard-title">Dashboard</h1>

      <div className="dashboard-content">
        <div className="dashboard-map">
          {/* Placeholder for the landscape map */}
          <LandscapeOverview />
        </div>

        <div className="articles-and-graph">
          <div className="recent-articles">
            <div className="article-heading">
              <h2 className="home-page-subtitle ">
                {" "}
                Landscape Related Articles{" "}
              </h2>
              <span
                className="click-more"
                onClick={() => {
                  navigate("/articles");
                }}
              >
                View more -{">"}
              </span>
            </div>
            <AllArticlesList isAbridged={true} />
          </div>

          <div className="flora">
            <h2 className="home-page-subtitle "> Flora Fauna Breakdown </h2>

            {/* Placeholder for the flora and fauna bar graph */}
            <FaunaFloraBreakdown />
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
