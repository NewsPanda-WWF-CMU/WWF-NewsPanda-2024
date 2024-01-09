import React, { useState, useEffect } from "react";
// import { ComposableMap, Geographies, Geography } from "react-simple-maps";
// import nepalGeography from "../../mapData/output.json";
import ArticleStats from "./LandscapeOverview/ArticleStats";
import Papa from "papaparse";
import csvData from "../../data/test-last-year-nepal-cleaned.csv";
import "./LandscapeOverview.css";
import LandscapeMap from "./LandscapeOverview/LandscapeMap";

const LandscapeOverview = () => {
  const [data, setData] = useState([]);
  const [conservationEvents, setConservationEvents] = useState(0);
  const [infrastructureEvents, setInfrastructureEvents] = useState(0);
  const [criticalLandscape, setCriticalLandscape] = useState("");
  const [landscapeCounts, setLandscapeCounts] = useState("");

  useEffect(() => {
    Papa.parse(csvData, {
      download: true,
      header: true,
      complete: (results) => {
        const filteredData = results.data
          .filter((row) => {
            const hasPublishedDate =
              row.publishedAt && new Date(row.publishedAt).getTime() > 0;
            const isLandscapeNotOther = row["Landscape-Location"];
            const hasAuthor = row["author"];
            return hasPublishedDate && isLandscapeNotOther && hasAuthor;
          })
          .sort((a, b) => new Date(b.publishedAt) - new Date(a.publishedAt));
        setData(filteredData);
        let conservationCount = 0;
        let infrastructureCount = 0;
        const landscapeCounts = {};

        results.data.forEach((row) => {
          const relevanceConservation = parseFloat(row.conversation_relevance);
          const relevanceInfrastructure = parseFloat(
            row.infrastructure_relevance
          );
          const landscape = row["Landscape-Location"];

          // Count conservation events
          if (relevanceConservation > 0.5) {
            conservationCount++;
          }

          // Count infrastructure events
          if (relevanceInfrastructure > 0.5) {
            infrastructureCount++;
          }

          // Count articles by landscape
          if (landscape && landscape !== "Other") {
            if (!landscapeCounts[landscape]) {
              landscapeCounts[landscape] = 0;
            }
            landscapeCounts[landscape]++;
          }
        });

        // Determine the critical landscape with the most articles
        let maxCount = 0;
        let maxLandscape = "";
        for (const [landscape, count] of Object.entries(landscapeCounts)) {
          if (count > maxCount) {
            maxCount = count;
            maxLandscape = landscape;
          }
        }

        setConservationEvents(conservationCount);
        setInfrastructureEvents(infrastructureCount);
        setCriticalLandscape(maxLandscape);
        setLandscapeCounts(landscapeCounts);
      },
    });
  }, []);

  console.log(landscapeCounts);
  return (
    <div className="landscape-overview">
      <h2 className="landscape-heading">Landscape Overview</h2>
      <div className="landscape-content">
        <LandscapeMap landscapeCounts={landscapeCounts} />
        <ArticleStats
          articleCount={data.length}
          conservationEvents={conservationEvents}
          criticalLandscape={criticalLandscape}
          infrastructureEvents={infrastructureEvents}
        />
      </div>
      {/* <ComposableMap>
        <Geographies geography={nepalGeography}>
          {({ geographies }) =>
            geographies.map((geo) => (
              <Geography key={geo.rsmKey} geography={geo} />
            ))
          }
        </Geographies>
      </ComposableMap> */}
    </div>
  );
};

export default LandscapeOverview;
