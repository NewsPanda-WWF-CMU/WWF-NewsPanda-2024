import React from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faNewspaper,
  faLeaf,
  faIndustry,
  faExclamationCircle,
} from "@fortawesome/free-solid-svg-icons";
import "./ArticleStats.css";

const ArticleStats = ({
  articleCount,
  conservationEvents,
  criticalLandscape,
  infrastructureEvents,
}) => {
  return (
    <div className="article-stats-container">
      <div className="stat-card">
        <FontAwesomeIcon icon={faNewspaper} className="icon articles" />
        <div className="stat-count">{articleCount}</div>
        <div className="stat-name">Articles</div>
      </div>

      <div className="stat-card">
        <FontAwesomeIcon icon={faLeaf} className="icon conservation" />
        <div className="stat-count">{conservationEvents}</div>
        <div className="stat-name">Conservation Event Related Articles</div>
      </div>

      <div className="stat-card critical">
        <FontAwesomeIcon icon={faExclamationCircle} className="icon critical" />
        <div className="stat-count">{criticalLandscape}</div>

        <div className="stat-name">Critical Landscape</div>
      </div>

      <div className="stat-card">
        <FontAwesomeIcon icon={faIndustry} className="icon infrastructure" />
        <div className="stat-count">{infrastructureEvents}</div>
        <div className="stat-name"> Infrastructure Event Related Articles</div>
      </div>
    </div>
  );
};

export default ArticleStats;
