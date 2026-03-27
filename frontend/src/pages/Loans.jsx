import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { BookOpen, AlertTriangle } from "lucide-react";
import toast from "react-hot-toast";
import { getLoans, returnTool } from "../api.js";

export default function Loans() {
  const [loans, setLoans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [returning, setReturning] = useState(null);

  useEffect(() => { fetchLoans(); }, []);

  const fetchLoans = async () => {
    try {
      const res = await getLoans();
      setLoans(res.data.loans || []);
    } catch {
      toast.error("Failed to load loans");
    } finally {
      setLoading(false);
    }
  };

  const handleReturn = async (toolId) => {
    setReturning(toolId);
    try {
      const res = await returnTool(toolId);
      toast.success(res.data.message);
      fetchLoans();
    } catch (err) {
      toast.error(err.response?.data?.error || "Failed to return tool");
    } finally {
      setReturning(null);
    }
  };

  const isOverdue = (loan) => {
    if (loan.status !== "active") return false;
    return loan.dueDate < new Date().toISOString().split("T")[0];
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        {[1, 2, 3].map((i) => <div key={i} className="skeleton h-24 rounded-lg mb-4"></div>)}
      </div>
    );
  }

  const active = loans.filter((l) => l.status === "active");
  const past = loans.filter((l) => l.status !== "active");

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">My Loans</h1>

      {loans.length === 0 ? (
        <div className="text-center py-12">
          <BookOpen className="h-12 w-12 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500">No loans yet. Browse tools to borrow one!</p>
          <Link to="/tools" className="inline-block mt-4 text-blue-600 hover:text-blue-700 text-sm font-medium">
            Browse Tools
          </Link>
        </div>
      ) : (
        <>
          {active.length > 0 && (
            <div className="mb-8">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Active Loans ({active.length})</h2>
              <div className="space-y-4">
                {active.map((loan) => (
                  <div key={loan.loanId} className={`bg-white rounded-lg border p-4 ${isOverdue(loan) ? "border-red-300" : "border-gray-200"}`}>
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <Link to={`/tools/${loan.toolId}`} className="text-base font-medium text-gray-900 hover:text-blue-600">
                            {loan.toolName}
                          </Link>
                          {isOverdue(loan) && (
                            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-700">
                              <AlertTriangle className="h-3 w-3" />
                              Overdue
                            </span>
                          )}
                        </div>
                        <div className="flex items-center gap-4 mt-1 text-sm text-gray-500">
                          <span>Borrowed: {loan.borrowDate}</span>
                          <span className={isOverdue(loan) ? "text-red-600 font-medium" : ""}>Due: {loan.dueDate}</span>
                        </div>
                      </div>
                      <button
                        onClick={() => handleReturn(loan.toolId)}
                        disabled={returning === loan.toolId}
                        className="bg-amber-600 text-white py-2 px-4 rounded-lg text-sm font-medium hover:bg-amber-700 disabled:opacity-50 transition-colors"
                      >
                        {returning === loan.toolId ? "Returning..." : "Return"}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {past.length > 0 && (
            <div>
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Past Loans ({past.length})</h2>
              <div className="space-y-4">
                {past.map((loan) => (
                  <div key={loan.loanId} className="bg-white rounded-lg border border-gray-200 p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <Link to={`/tools/${loan.toolId}`} className="text-base font-medium text-gray-900 hover:text-blue-600">
                          {loan.toolName}
                        </Link>
                        <div className="flex items-center gap-4 mt-1 text-sm text-gray-500">
                          <span>Borrowed: {loan.borrowDate}</span>
                          <span>Returned: {loan.returnedDate || "N/A"}</span>
                        </div>
                      </div>
                      <div className="text-right">
                        <span className="inline-block px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600">
                          Returned
                        </span>
                        {loan.lateFee > 0 && (
                          <p className="text-xs text-red-600 mt-1">Late fee: ${loan.lateFee}</p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
