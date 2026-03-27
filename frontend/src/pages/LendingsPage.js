import React, { useState, useEffect, useCallback } from 'react';
import { lendingsApi } from '../services/api';

function LendingsPage() {
  const [lendings, setLendings] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ tool_id: '', borrower_id: '', lending_days: 7, notes: '' });
  const [error, setError] = useState(null);

  const fetchLendings = useCallback(async () => {
    try {
      const data = await lendingsApi.list();
      setLendings(data.lendings || []);
    } catch { setError('Could not load lendings'); }
  }, []);

  useEffect(() => { fetchLendings(); }, [fetchLendings]);

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      await lendingsApi.create(form);
      setShowForm(false);
      setForm({ tool_id: '', borrower_id: '', lending_days: 7, notes: '' });
      fetchLendings();
    } catch (err) { setError(err.message); }
  };

  const handleAction = async (id, action) => {
    try {
      if (action === 'approve') await lendingsApi.approve(id);
      else if (action === 'activate') await lendingsApi.activate(id);
      else if (action === 'return') await lendingsApi.return_tool(id);
      else if (action === 'delete') {
        if (!window.confirm('Delete this lending record?')) return;
        await lendingsApi.delete(id);
      }
      fetchLendings();
    } catch (err) { setError(err.message); }
  };

  const statusBadge = (status) => {
    const map = { requested: 'badge-orange', approved: 'badge-blue', active: 'badge-green', returned: 'badge-gray', overdue: 'badge-red', cancelled: 'badge-gray' };
    return <span className={`badge ${map[status] || 'badge-gray'}`}>{status}</span>;
  };

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>Lendings</h1>
        <button className="btn btn-primary" onClick={() => setShowForm(true)}>New Lending Request</button>
      </div>

      {error && <div className="card" style={{ color: 'red' }}>{error}</div>}

      {showForm && (
        <div className="modal-overlay" onClick={() => setShowForm(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <h3>New Lending Request</h3>
            <form onSubmit={handleCreate}>
              <div className="form-group">
                <label>Tool ID</label>
                <input value={form.tool_id} onChange={e => setForm({...form, tool_id: e.target.value})} required />
              </div>
              <div className="form-group">
                <label>Borrower ID</label>
                <input value={form.borrower_id} onChange={e => setForm({...form, borrower_id: e.target.value})} required />
              </div>
              <div className="form-group">
                <label>Lending Days</label>
                <input type="number" value={form.lending_days} onChange={e => setForm({...form, lending_days: parseInt(e.target.value)})} />
              </div>
              <div className="form-group">
                <label>Notes</label>
                <textarea value={form.notes} onChange={e => setForm({...form, notes: e.target.value})} />
              </div>
              <div className="modal-actions">
                <button type="button" className="btn" onClick={() => setShowForm(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary">Create</button>
              </div>
            </form>
          </div>
        </div>
      )}

      <div className="card">
        <table>
          <thead>
            <tr><th>Record ID</th><th>Tool ID</th><th>Borrower</th><th>Status</th><th>Days</th><th>Due Date</th><th>Actions</th></tr>
          </thead>
          <tbody>
            {lendings.length === 0 ? (
              <tr><td colSpan="7" style={{ textAlign: 'center', color: '#999' }}>No lending records</td></tr>
            ) : lendings.map(l => (
              <tr key={l.record_id}>
                <td style={{fontSize:'12px'}}>{l.record_id.substring(0,8)}...</td>
                <td style={{fontSize:'12px'}}>{l.tool_id.substring(0,8)}...</td>
                <td style={{fontSize:'12px'}}>{l.borrower_id.substring(0,8)}...</td>
                <td>{statusBadge(l.status)}</td>
                <td>{l.lending_days}</td>
                <td style={{fontSize:'12px'}}>{l.due_date ? new Date(l.due_date).toLocaleDateString() : '-'}</td>
                <td>
                  {l.status === 'requested' && <button className="btn btn-sm btn-success" onClick={() => handleAction(l.record_id, 'approve')}>Approve</button>}
                  {l.status === 'approved' && <button className="btn btn-sm btn-success" onClick={() => handleAction(l.record_id, 'activate')}>Activate</button>}
                  {(l.status === 'active' || l.status === 'overdue') && <button className="btn btn-sm btn-primary" onClick={() => handleAction(l.record_id, 'return')}>Return</button>}
                  <button className="btn btn-sm btn-danger" onClick={() => handleAction(l.record_id, 'delete')}>Del</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default LendingsPage;
