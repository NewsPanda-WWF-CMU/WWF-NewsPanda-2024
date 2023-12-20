import React from "react";
import { ComposableMap, Geographies, Geography } from "react-simple-maps";
import nepalGeography from "../../mapData/output.json";

const LandscapeOverview = () => {
  return (
    <div className="landscape-overview" style={{ width: "100%" }}>
      This is the map
      <ComposableMap>
        <Geographies geography={nepalGeography}>
          {({ geographies }) =>
            geographies.map((geo) => (
              <Geography key={geo.rsmKey} geography={geo} />
            ))
          }
        </Geographies>
      </ComposableMap>
    </div>
  );
};

export default LandscapeOverview;
