import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Plus, Search, X } from "lucide-react";
import toast from "react-hot-toast";
import { getTools, createTool } from "../api.js";

const CATEGORIES = [
  { value: "", label: "All Categories" },
  { value: "power_tools", label: "Power Tools" },
  { value: "hand_tools", label: "Hand Tools" },
  { value: "garden", label: "Garden" },
  { value: "ladders", label: "Ladders" },
  { value: "cleaning", label: "Cleaning" },
  { value: "kitchen", label: "Kitchen" },
  { value: "other", label: "Other" },
];

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

export default function Tools() {
  const [tools, setTools] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState({ name: "", description: "", category: "other", condition: "good", imageUrl: "" });
  const [creating, setCreating] = useState(false);

  useEffect(() => { fetchTools(); }, []);

  const fetchTools = async () => {
    try {
      const res = await getTools();
      setTools(res.data.tools || []);
    } catch {
      toast.error("Failed to load tools");
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    setCreating(true);
    try {
      await createTool(form);
      toast.success("Tool added!");
      setShowModal(false);
      setForm({ name: "", description: "", category: "other", condition: "good", imageUrl: "" });
      fetchTools();
    } catch (err) {
      toast.error(err.response?.data?.error || "Failed to create tool");
    } finally {
      setCreating(false);
    }
  };

  const filtered = tools.filter((t) => {
    const matchSearch = !search || t.name?.toLowerCase().includes(search.toLowerCase()) || t.description?.toLowerCase().includes(search.toLowerCase());
    const matchCat = !category || t.category === category;
    return matchSearch && matchCat;
  });

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map((i) => <div key={i} className="skeleton h-48 rounded-lg"></div>)}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Tools</h1>
        <button onClick={() => setShowModal(true)} className="flex items-center space-x-2 bg-blue-600 text-white py-2 px-4 rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors">
          <Plus className="h-4 w-4" />
          <span>Add Tool</span>
        </button>
      </div>

      <div className="flex flex-col sm:flex-row gap-4 mb-6">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search tools..."
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
        <select
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
        >
          {CATEGORIES.map((c) => <option key={c.value} value={c.value}>{c.label}</option>)}
        </select>
      </div>

      {filtered.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500">No tools found</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {filtered.map((tool) => (
            <Link key={tool.toolId} to={`/tools/${tool.toolId}`} className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow">
              {tool.imageUrl && (
                <img src={tool.imageUrl} alt={tool.name} className="w-full h-40 object-cover rounded-lg mb-4" />
              )}
              <div className="flex items-start justify-between mb-2">
                <h3 className="text-lg font-semibold text-gray-900">{tool.name}</h3>
                <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${STATUS_BADGE[tool.status] || "bg-gray-100 text-gray-700"}`}>
                  {STATUS_LABEL[tool.status] || tool.status}
                </span>
              </div>
              <p className="text-sm text-gray-500 mb-3 line-clamp-2">{tool.description || "No description"}</p>
              <div className="flex items-center justify-between text-xs text-gray-400">
                <span className="capitalize">{tool.category?.replace("_", " ")}</span>
                <span className="capitalize">{tool.condition}</span>
              </div>
            </Link>
          ))}
        </div>
      )}

      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg w-full max-w-lg p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-semibold text-gray-900">Add New Tool</h2>
              <button onClick={() => setShowModal(false)} className="text-gray-400 hover:text-gray-600">
                <X className="h-5 w-5" />
              </button>
            </div>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                <input type="text" required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent" placeholder="e.g. Power Drill" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} rows={3} className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent" placeholder="Describe the tool..." />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
                  <select value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white">
                    {CATEGORIES.filter((c) => c.value).map((c) => <option key={c.value} value={c.value}>{c.label}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Condition</label>
                  <select value={form.condition} onChange={(e) => setForm({ ...form, condition: e.target.value })} className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white">
                    <option value="excellent">Excellent</option>
                    <option value="good">Good</option>
                    <option value="fair">Fair</option>
                    <option value="poor">Poor</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Image URL (optional)</label>
                <input type="url" value={form.imageUrl} onChange={(e) => setForm({ ...form, imageUrl: e.target.value })} className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent" placeholder="https://..." />
              </div>
              <div className="flex justify-end space-x-3 pt-2">
                <button type="button" onClick={() => setShowModal(false)} className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">Cancel</button>
                <button type="submit" disabled={creating} className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors">
                  {creating ? "Adding..." : "Add Tool"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
