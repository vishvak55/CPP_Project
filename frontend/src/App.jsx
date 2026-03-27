import { Routes, Route, Navigate } from "react-router-dom";
import { useAuth } from "./context/auth.jsx";
import Navbar from "./components/Navbar.jsx";
import ProtectedRoute from "./components/ProtectedRoute.jsx";
import Login from "./pages/Login.jsx";
import Register from "./pages/Register.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Tools from "./pages/Tools.jsx";
import ToolDetail from "./pages/ToolDetail.jsx";
import Loans from "./pages/Loans.jsx";

export default function App() {
  const { user } = useAuth();

  return (
    <div className="min-h-screen bg-gray-50">
      {user && <Navbar />}
      <Routes>
        <Route path="/login" element={user ? <Navigate to="/" /> : <Login />} />
        <Route path="/register" element={user ? <Navigate to="/" /> : <Register />} />
        <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        <Route path="/tools" element={<ProtectedRoute><Tools /></ProtectedRoute>} />
        <Route path="/tools/:id" element={<ProtectedRoute><ToolDetail /></ProtectedRoute>} />
        <Route path="/loans" element={<ProtectedRoute><Loans /></ProtectedRoute>} />
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </div>
  );
}
