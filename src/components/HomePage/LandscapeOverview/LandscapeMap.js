import React from "react";
import "./LandscapeMap.css";

const LandscapeMap = ({ landscapeCounts, totalArticles }) => {
  // Initialize regions with their names and default styles
  const regions = [
    {
      name: "Terai Arc Landscape",
      style: {
        top: "65%",
        left: "14%",
        height: "10%",
        width: "50%",
        position: "absolute",
        textAlign: "center",
      }, // Define the position styles for each region
    },
    {
      name: "Sacred Himalayan Landscape",
      style: {
        top: "67%",
        left: "80%",
        height: "10%",
        width: "10%",
        position: "absolute",
      }, // DefineDefine the position styles for each region
    },
    {
      name: "Kailash Sacred Landscape",
      style: {
        top: "19%",
        left: "15%",
        height: "10%",
        width: "10%",
        position: "absolute",
      }, // Define the position styles for each region
    },
    {
      name: "Chitwan Annapurna Landscape",
      style: {
        top: "50%",
        left: "50%",
        height: "10%",
        width: "10%",
        position: "absolute",
      }, /// Define the position styles for each region
    },
    {
      name: "Kanchenjunga Landscape",
      style: {
        top: "65%",
        left: "93%",
        height: "25%",
        width: "4%",
        position: "absolute",
      }, /// Define the position styles for each region
    },
    // ... other regions if necessary
  ].map((region) => ({
    ...region,
    // Assign count from landscapeCounts or default to 0 if not found
    count: landscapeCounts[region.name] || 0,
  }));

  let otherArticlesCount = totalArticles;

  regions.forEach((region) => {
    otherArticlesCount = otherArticlesCount - region.count;
  }); // Replace with actual count as needed

  return (
    <div className="landscape-map">
      <div className="map-container">
        {regions.map((region) => (
          <div
            key={region.name}
            className="region-overlay"
            style={region.style}
          ></div>
        ))}
        <div className="info-container">
          {regions.map((region) => (
            <div key={region.name} style={region.style} className="info">
              {region.count}
            </div>
          ))}
        </div>
      </div>
      <div className="other-articles-indicator">
        Other articles: {otherArticlesCount}
      </div>
    </div>
  );
};

export default LandscapeMap;
