import React, { useState, useEffect, useCallback } from 'react';
import { toolsApi } from '../services/api';

function ToolsPage() {
  const [tools, setTools] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [form, setForm] = useState({ name: '', description: '', category: 'hand_tool', condition: 'good', max_lending_days: 14 });
  const [error, setError] = useState(null);

  const fetchTools = useCallback(async () => {
    try {
      const data = await toolsApi.list();
      setTools(data.tools || []);
    } catch { setError('Could not load tools'); }
  }, []);

  useEffect(() => { fetchTools(); }, [fetchTools]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingId) {
        await toolsApi.update(editingId, form);
      } else {
        await toolsApi.create(form);
      }
      setShowForm(false);
      setEditingId(null);
      setForm({ name: '', description: '', category: 'hand_tool', condition: 'good', max_lending_days: 14 });
      fetchTools();
    } catch (err) { setError(err.message); }
  };

  const handleEdit = (tool) => {
    setForm({ name: tool.name, description: tool.description || '', category: tool.category, condition: tool.condition, max_lending_days: tool.max_lending_days });
    setEditingId(tool.tool_id);
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm('Delete this tool?')) {
      try { await toolsApi.delete(id); fetchTools(); }
      catch (err) { setError(err.message); }
    }
  };

  const categories = ['hand_tool', 'power_tool', 'garden', 'plumbing', 'electrical', 'painting', 'measurement', 'safety', 'other'];
  const conditions = ['excellent', 'good', 'fair', 'poor', 'needs_repair'];

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>Tools</h1>
        <button className="btn btn-primary" onClick={() => { setShowForm(true); setEditingId(null); setForm({ name: '', description: '', category: 'hand_tool', condition: 'good', max_lending_days: 14 }); }}>
          Add Tool
        </button>
      </div>

      {error && <div className="card" style={{ color: 'red' }}>{error}</div>}

      {showForm && (
        <div className="modal-overlay" onClick={() => setShowForm(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <h3>{editingId ? 'Edit Tool' : 'Add New Tool'}</h3>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Name</label>
                <input value={form.name} onChange={e => setForm({...form, name: e.target.value})} required />
              </div>
              <div className="form-group">
                <label>Description</label>
                <textarea value={form.description} onChange={e => setForm({...form, description: e.target.value})} />
              </div>
              <div className="form-group">
                <label>Category</label>
                <select value={form.category} onChange={e => setForm({...form, category: e.target.value})}>
                  {categories.map(c => <option key={c} value={c}>{c.replace('_', ' ')}</option>)}
                </select>
              </div>
              <div className="form-group">
                <label>Condition</label>
                <select value={form.condition} onChange={e => setForm({...form, condition: e.target.value})}>
                  {conditions.map(c => <option key={c} value={c}>{c.replace('_', ' ')}</option>)}
                </select>
              </div>
              <div className="form-group">
                <label>Max Lending Days</label>
                <input type="number" value={form.max_lending_days} onChange={e => setForm({...form, max_lending_days: parseInt(e.target.value)})} />
              </div>
              <div className="modal-actions">
                <button type="button" className="btn" onClick={() => setShowForm(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary">{editingId ? 'Update' : 'Create'}</button>
              </div>
            </form>
          </div>
        </div>
      )}

      <div className="card">
        <table>
          <thead>
            <tr><th>Name</th><th>Category</th><th>Condition</th><th>Max Days</th><th>Available</th><th>Actions</th></tr>
          </thead>
          <tbody>
            {tools.length === 0 ? (
              <tr><td colSpan="6" style={{ textAlign: 'center', color: '#999' }}>No tools found</td></tr>
            ) : tools.map(tool => (
              <tr key={tool.tool_id}>
                <td><strong>{tool.name}</strong><br/><span style={{fontSize:'12px',color:'#666'}}>{tool.description}</span></td>
                <td><span className="badge badge-blue">{tool.category}</span></td>
                <td>{tool.condition}</td>
                <td>{tool.max_lending_days}</td>
                <td><span className={`badge ${tool.is_available ? 'badge-green' : 'badge-red'}`}>{tool.is_available ? 'Yes' : 'No'}</span></td>
                <td>
                  <button className="btn btn-sm btn-primary" onClick={() => handleEdit(tool)}>Edit</button>
                  <button className="btn btn-sm btn-danger" onClick={() => handleDelete(tool.tool_id)}>Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default ToolsPage;
