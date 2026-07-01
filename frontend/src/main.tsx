import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Layout } from "./components/Layout";
import { AgentPage } from "./pages/Agent";
import { AskPage } from "./pages/Ask";
import { DashboardPage } from "./pages/Dashboard";
import { InsightsPage } from "./pages/Insights";
import { ReviewsPage } from "./pages/Reviews";
import { SearchPage } from "./pages/Search";
import { ThemesPage } from "./pages/Themes";
import "./index.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<DashboardPage />} />
          <Route path="search" element={<SearchPage />} />
          <Route path="ask" element={<AskPage />} />
          <Route path="agent" element={<AgentPage />} />
          <Route path="themes" element={<ThemesPage />} />
          <Route path="insights" element={<InsightsPage />} />
          <Route path="reviews" element={<ReviewsPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  </StrictMode>
);
