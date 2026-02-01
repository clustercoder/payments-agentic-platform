import * as React from "react"; // Added import for React
import * as ReactDOM from "react-dom/client"; // Fixed import for ReactDOM
import App from "./App";
import "./styles/globals.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App/>
  </React.StrictMode>
);
