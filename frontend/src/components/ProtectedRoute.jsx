import { Navigate } from "react-router-dom";
import { useAuth } from "../context/auth.jsx";

export default function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="skeleton h-8 w-48"></div>
      </div>
    );
  }

  if (!user) return <Navigate to="/login" />;

  return children;
}
