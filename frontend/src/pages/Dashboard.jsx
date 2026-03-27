import { useState, useEffect } from "react";
import { Package, CheckCircle, Clock, AlertTriangle } from "lucide-react";
import toast from "react-hot-toast";
import { getDashboard, subscribe } from "../api.js";

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [subEmail, setSubEmail] = useState("");
  const [subscribing, setSubscribing] = useState(false);

  useEffect(() => {
    fetchDashboard();
  }, []);

  const fetchDashboard = async () => {
    try {
      const res = await getDashboard();
      setData(res.data);
    } catch {
      toast.error("Failed to load dashboard");
    } finally {
      setLoading(false);
    }
  };

  const handleSubscribe = async (e) => {
    e.preventDefault();
    if (!subEmail) return;
    setSubscribing(true);
    try {
      await subscribe(subEmail);
      toast.success("Subscription request sent! Check your email.");
      setSubEmail("");
    } catch {
      toast.error("Failed to subscribe");
    } finally {
      setSubscribing(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="skeleton h-28 rounded-lg"></div>
          ))}
        </div>
      </div>
    );
  }

  const stats = [
    { label: "Total Tools", value: data?.totalTools || 0, icon: Package, color: "text-blue-600", bg: "bg-blue-50" },
    { label: "Available", value: data?.availableCount || 0, icon: CheckCircle, color: "text-green-600", bg: "bg-green-50" },
    { label: "On Loan", value: data?.loanedCount || 0, icon: Clock, color: "text-amber-600", bg: "bg-amber-50" },
    { label: "Overdue", value: data?.overdueCount || 0, icon: AlertTriangle, color: "text-red-600", bg: "bg-red-50" },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Dashboard</h1>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {stats.map((stat) => (
          <div key={stat.label} className="bg-white rounded-lg border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500">{stat.label}</p>
                <p className="text-3xl font-bold text-gray-900 mt-1">{stat.value}</p>
              </div>
              <div className={`${stat.bg} p-3 rounded-lg`}>
                <stat.icon className={`h-6 w-6 ${stat.color}`} />
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Loans</h2>
          {data?.recentLoans?.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-3 px-2 font-medium text-gray-500">Tool</th>
                    <th className="text-left py-3 px-2 font-medium text-gray-500">Borrower</th>
                    <th className="text-left py-3 px-2 font-medium text-gray-500">Due Date</th>
                    <th className="text-left py-3 px-2 font-medium text-gray-500">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {data.recentLoans.map((loan) => (
                    <tr key={loan.loanId} className="border-b border-gray-100">
                      <td className="py-3 px-2 text-gray-900">{loan.toolName}</td>
                      <td className="py-3 px-2 text-gray-600">{loan.userName}</td>
                      <td className="py-3 px-2 text-gray-600">{loan.dueDate}</td>
                      <td className="py-3 px-2">
                        <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${
                          loan.status === "active" ? "bg-green-100 text-green-700" :
                          loan.status === "returned" ? "bg-gray-100 text-gray-700" :
                          "bg-red-100 text-red-700"
                        }`}>
                          {loan.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-gray-500 text-sm">No recent loans</p>
          )}
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Notifications</h2>
          <p className="text-sm text-gray-500 mb-4">Subscribe to get notified about tool availability and loan reminders.</p>
          <form onSubmit={handleSubscribe} className="space-y-3">
            <input
              type="email"
              value={subEmail}
              onChange={(e) => setSubEmail(e.target.value)}
              placeholder="Enter your email"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <button
              type="submit"
              disabled={subscribing}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              {subscribing ? "Subscribing..." : "Subscribe"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
