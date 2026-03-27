import React, { useState, useEffect, useCallback } from 'react';
import { usersApi } from '../services/api';

function UsersPage() {
  const [users, setUsers] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [form, setForm] = useState({ username: '', email: '', full_name: '', role: 'borrower', phone: '' });
  const [error, setError] = useState(null);

  const fetchUsers = useCallback(async () => {
    try {
      const data = await usersApi.list();
      setUsers(data.users || []);
    } catch { setError('Could not load users'); }
  }, []);

  useEffect(() => { fetchUsers(); }, [fetchUsers]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingId) { await usersApi.update(editingId, form); }
      else { await usersApi.create(form); }
      setShowForm(false); setEditingId(null);
      setForm({ username: '', email: '', full_name: '', role: 'borrower', phone: '' });
      fetchUsers();
    } catch (err) { setError(err.message); }
  };

  const handleEdit = (user) => {
    setForm({ username: user.username, email: user.email, full_name: user.full_name, role: user.role, phone: user.phone || '' });
    setEditingId(user.user_id); setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm('Delete this user?')) {
      try { await usersApi.delete(id); fetchUsers(); }
      catch (err) { setError(err.message); }
    }
  };

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>Users</h1>
        <button className="btn btn-primary" onClick={() => { setShowForm(true); setEditingId(null); setForm({ username: '', email: '', full_name: '', role: 'borrower', phone: '' }); }}>
          Add User
        </button>
      </div>

      {error && <div className="card" style={{ color: 'red' }}>{error}</div>}

      {showForm && (
        <div className="modal-overlay" onClick={() => setShowForm(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <h3>{editingId ? 'Edit User' : 'Add New User'}</h3>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Username</label>
                <input value={form.username} onChange={e => setForm({...form, username: e.target.value})} required />
              </div>
              <div className="form-group">
                <label>Email</label>
                <input type="email" value={form.email} onChange={e => setForm({...form, email: e.target.value})} required />
              </div>
              <div className="form-group">
                <label>Full Name</label>
                <input value={form.full_name} onChange={e => setForm({...form, full_name: e.target.value})} required />
              </div>
              <div className="form-group">
                <label>Role</label>
                <select value={form.role} onChange={e => setForm({...form, role: e.target.value})}>
                  <option value="borrower">Borrower</option>
                  <option value="lender">Lender</option>
                  <option value="admin">Admin</option>
                </select>
              </div>
              <div className="form-group">
                <label>Phone</label>
                <input value={form.phone} onChange={e => setForm({...form, phone: e.target.value})} />
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
            <tr><th>Username</th><th>Full Name</th><th>Email</th><th>Role</th><th>Trust Score</th><th>Status</th><th>Actions</th></tr>
          </thead>
          <tbody>
            {users.length === 0 ? (
              <tr><td colSpan="7" style={{ textAlign: 'center', color: '#999' }}>No users found</td></tr>
            ) : users.map(user => (
              <tr key={user.user_id}>
                <td><strong>{user.username}</strong></td>
                <td>{user.full_name}</td>
                <td>{user.email}</td>
                <td><span className="badge badge-blue">{user.role}</span></td>
                <td>{user.trust_score}</td>
                <td><span className={`badge ${user.is_active ? 'badge-green' : 'badge-red'}`}>{user.is_active ? 'Active' : 'Inactive'}</span></td>
                <td>
                  <button className="btn btn-sm btn-primary" onClick={() => handleEdit(user)}>Edit</button>
                  <button className="btn btn-sm btn-danger" onClick={() => handleDelete(user.user_id)}>Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default UsersPage;
