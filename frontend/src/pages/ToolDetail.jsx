import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { ArrowLeft, Edit2, Trash2, X } from "lucide-react";
import toast from "react-hot-toast";
import { getTool, updateTool, deleteTool, borrowTool, returnTool } from "../api.js";
import { useAuth } from "../context/auth.jsx";

const STATUS_BADGE = {
  ready: "bg-green-100 text-green-700",
  loaned: "bg-amber-100 text-amber-700",
  under_repair: "bg-red-100 text-red-700",
};

const STATUS_LABEL = {
  ready: "Available",
  loaned: "On Loan",
  under_repair: "Under Repair",
};

export default function ToolDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [tool, setTool] = useState(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [showEdit, setShowEdit] = useState(false);
  const [editForm, setEditForm] = useState({});
  const [days, setDays] = useState(14);

  useEffect(() => { fetchTool(); }, [id]);

  const fetchTool = async () => {
    try {
      const res = await getTool(id);
      setTool(res.data.tool);
      setEditForm(res.data.tool);
    } catch {
      toast.error("Tool not found");
      navigate("/tools");
    } finally {
      setLoading(false);
    }
  };

  const handleBorrow = async () => {
    setActionLoading(true);
    try {
      await borrowTool(id, { days });
      toast.success("Tool borrowed successfully!");
      fetchTool();
    } catch (err) {
      toast.error(err.response?.data?.error || "Failed to borrow tool");
    } finally {
      setActionLoading(false);
    }
  };

  const handleReturn = async () => {
    setActionLoading(true);
    try {
      const res = await returnTool(id);
      toast.success(res.data.message);
      fetchTool();
    } catch (err) {
      toast.error(err.response?.data?.error || "Failed to return tool");
    } finally {
      setActionLoading(false);
    }
  };

  const handleUpdate = async (e) => {
    e.preventDefault();
    setActionLoading(true);
    try {
      await updateTool(id, {
        name: editForm.name,
        description: editForm.description,
        category: editForm.category,
        condition: editForm.condition,
        imageUrl: editForm.imageUrl,
      });
      toast.success("Tool updated!");
      setShowEdit(false);
      fetchTool();
    } catch (err) {
      toast.error(err.response?.data?.error || "Failed to update tool");
    } finally {
      setActionLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm("Are you sure you want to delete this tool?")) return;
    try {
      await deleteTool(id);
      toast.success("Tool deleted");
      navigate("/tools");
    } catch (err) {
      toast.error(err.response?.data?.error || "Failed to delete tool");
    }
  };

  if (loading) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-8">
        <div className="skeleton h-64 rounded-lg"></div>
      </div>
    );
  }

  if (!tool) return null;

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <button onClick={() => navigate("/tools")} className="flex items-center space-x-1 text-gray-500 hover:text-gray-700 text-sm mb-6">
        <ArrowLeft className="h-4 w-4" />
        <span>Back to Tools</span>
      </button>

      <div className="bg-white rounded-lg border border-gray-200 p-6">
        {tool.imageUrl && (
          <img src={tool.imageUrl} alt={tool.name} className="w-full h-64 object-cover rounded-lg mb-6" />
        )}
        <div className="flex items-start justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{tool.name}</h1>
            <p className="text-sm text-gray-500 capitalize mt-1">{tool.category?.replace("_", " ")} - {tool.condition}</p>
          </div>
          <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${STATUS_BADGE[tool.status] || "bg-gray-100 text-gray-700"}`}>
            {STATUS_LABEL[tool.status] || tool.status}
          </span>
        </div>

        {tool.description && (
          <p className="text-gray-600 mb-6">{tool.description}</p>
        )}

        <div className="flex flex-wrap gap-3 mb-6">
          {tool.status === "ready" && (
            <div className="flex items-center gap-3">
              <select value={days} onChange={(e) => setDays(Number(e.target.value))} className="px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white">
                <option value={7}>7 days</option>
                <option value={14}>14 days</option>
                <option value={21}>21 days</option>
                <option value={30}>30 days</option>
              </select>
              <button onClick={handleBorrow} disabled={actionLoading} className="bg-green-600 text-white py-2 px-4 rounded-lg text-sm font-medium hover:bg-green-700 disabled:opacity-50 transition-colors">
                {actionLoading ? "Processing..." : "Borrow Tool"}
              </button>
            </div>
          )}
          {tool.status === "loaned" && tool.borrowedBy === user?.userId && (
            <button onClick={handleReturn} disabled={actionLoading} className="bg-amber-600 text-white py-2 px-4 rounded-lg text-sm font-medium hover:bg-amber-700 disabled:opacity-50 transition-colors">
              {actionLoading ? "Processing..." : "Return Tool"}
            </button>
          )}
          <button onClick={() => setShowEdit(true)} className="flex items-center space-x-1 border border-gray-300 text-gray-700 py-2 px-4 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors">
            <Edit2 className="h-4 w-4" />
            <span>Edit</span>
          </button>
          <button onClick={handleDelete} className="flex items-center space-x-1 border border-red-300 text-red-600 py-2 px-4 rounded-lg text-sm font-medium hover:bg-red-50 transition-colors">
            <Trash2 className="h-4 w-4" />
            <span>Delete</span>
          </button>
        </div>

        <div className="border-t border-gray-200 pt-4">
          <p className="text-xs text-gray-400">Added on {tool.createdAt?.split("T")[0] || "N/A"}</p>
        </div>
      </div>

      {showEdit && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg w-full max-w-lg p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-semibold text-gray-900">Edit Tool</h2>
              <button onClick={() => setShowEdit(false)} className="text-gray-400 hover:text-gray-600">
                <X className="h-5 w-5" />
              </button>
            </div>
            <form onSubmit={handleUpdate} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                <input type="text" required value={editForm.name || ""} onChange={(e) => setEditForm({ ...editForm, name: e.target.value })} className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea value={editForm.description || ""} onChange={(e) => setEditForm({ ...editForm, description: e.target.value })} rows={3} className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
                  <select value={editForm.category || "other"} onChange={(e) => setEditForm({ ...editForm, category: e.target.value })} className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white">
                    <option value="power_tools">Power Tools</option>
                    <option value="hand_tools">Hand Tools</option>
                    <option value="garden">Garden</option>
                    <option value="ladders">Ladders</option>
                    <option value="cleaning">Cleaning</option>
                    <option value="kitchen">Kitchen</option>
                    <option value="other">Other</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Condition</label>
                  <select value={editForm.condition || "good"} onChange={(e) => setEditForm({ ...editForm, condition: e.target.value })} className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white">
                    <option value="excellent">Excellent</option>
                    <option value="good">Good</option>
                    <option value="fair">Fair</option>
                    <option value="poor">Poor</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Image URL</label>
                <input type="url" value={editForm.imageUrl || ""} onChange={(e) => setEditForm({ ...editForm, imageUrl: e.target.value })} className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent" />
              </div>
              <div className="flex justify-end space-x-3 pt-2">
                <button type="button" onClick={() => setShowEdit(false)} className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50">Cancel</button>
                <button type="submit" disabled={actionLoading} className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50">
                  {actionLoading ? "Saving..." : "Save Changes"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
