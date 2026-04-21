import { Navigate, Route, Routes } from "react-router-dom";
import { ChatPage } from "./pages/ChatPage";
import { DashboardPage } from "./pages/DashboardPage";
import { DealershipDashboardPage } from "./pages/DealershipDashboardPage";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<ChatPage />} />
      <Route path="/d/:dealershipSlug" element={<ChatPage />} />
      <Route path="/dashboard" element={<DashboardPage />} />
      <Route path="/dashboard/:dealershipId" element={<DealershipDashboardPage />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

