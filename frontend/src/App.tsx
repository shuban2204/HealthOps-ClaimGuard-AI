import { Navigate, Route, Routes } from "react-router-dom";

import { AppShell } from "./components/AppShell";
import { ClaimDetailPage } from "./pages/ClaimDetailPage";
import { ClaimsPage } from "./pages/ClaimsPage";
import { DashboardPage } from "./pages/DashboardPage";
import { ModelInsightsPage } from "./pages/ModelInsightsPage";

export default function App() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route index element={<DashboardPage />} />
        <Route path="claims" element={<ClaimsPage />} />
        <Route path="claims/:claimId" element={<ClaimDetailPage />} />
        <Route path="model" element={<ModelInsightsPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}

