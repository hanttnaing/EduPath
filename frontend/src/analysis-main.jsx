import React from "react";
import ReactDOM from "react-dom/client";

import AnalysisDashboard from "./AnalysisDashboard";
import "./AnalysisDashboard.css";

ReactDOM.createRoot(
  document.getElementById("analysis-root")
).render(
  <React.StrictMode>
    <AnalysisDashboard />
  </React.StrictMode>
);