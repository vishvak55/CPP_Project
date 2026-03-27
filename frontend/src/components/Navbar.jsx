import { Link, useNavigate } from "react-router-dom";
import { Wrench, LayoutDashboard, Package, BookOpen, LogOut } from "lucide-react";
import { useAuth } from "../context/auth.jsx";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <nav className="bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          <div className="flex items-center space-x-8">
            <Link to="/" className="flex items-center space-x-2">
              <Wrench className="h-6 w-6 text-blue-600" />
              <span className="text-xl font-bold text-gray-900">ToolShare</span>
            </Link>
            <div className="hidden sm:flex space-x-6">
              <Link to="/" className="flex items-center space-x-1 text-gray-600 hover:text-gray-900 text-sm font-medium">
                <LayoutDashboard className="h-4 w-4" />
                <span>Dashboard</span>
              </Link>
              <Link to="/tools" className="flex items-center space-x-1 text-gray-600 hover:text-gray-900 text-sm font-medium">
                <Package className="h-4 w-4" />
                <span>Tools</span>
              </Link>
              <Link to="/loans" className="flex items-center space-x-1 text-gray-600 hover:text-gray-900 text-sm font-medium">
                <BookOpen className="h-4 w-4" />
                <span>My Loans</span>
              </Link>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-500">{user?.email}</span>
            <button
              onClick={handleLogout}
              className="flex items-center space-x-1 text-gray-500 hover:text-red-600 text-sm font-medium"
            >
              <LogOut className="h-4 w-4" />
              <span>Logout</span>
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}
