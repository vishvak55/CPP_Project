import React, { useState, useEffect } from 'react';
import { toolsApi, usersApi, lendingsApi } from '../services/api';

function Dashboard() {
  const [stats, setStats] = useState({ tools: 0, users: 0, lendings: 0, available: 0 });
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchStats() {
      try {
        const [toolsData, usersData, lendingsData] = await Promise.all([
          toolsApi.list(), usersApi.list(), lendingsApi.list()
        ]);
        setStats({
          tools: toolsData.count || 0,
          users: usersData.count || 0,
          lendings: lendingsData.count || 0,
          available: (toolsData.tools || []).filter(t => t.is_available).length,
        });
      } catch (err) {
        setError('Backend not available. Start Flask server on port 5000.');
      }
    }
    fetchStats();
  }, []);

  return (
    <div>
      <div className="page-header">
        <h1>Dashboard</h1>
        <p style={{ color: '#666', fontSize: '14px' }}>Community Tool Lending Library Overview</p>
      </div>

      {error && (
        <div className="card" style={{ borderLeft: '4px solid #ff9800', marginBottom: '16px' }}>
          <p>{error}</p>
        </div>
      )}

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-value">{stats.tools}</div>
          <div className="stat-label">Total Tools</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{stats.available}</div>
          <div className="stat-label">Available Tools</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{stats.users}</div>
          <div className="stat-label">Registered Users</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{stats.lendings}</div>
          <div className="stat-label">Lending Records</div>
        </div>
      </div>

      <div className="card">
        <h3>About This System</h3>
        <p style={{ fontSize: '14px', lineHeight: '1.6' }}>
          The Community Tool Lending Library enables community members to share tools
          through a managed lending system. Built with Flask, React, and 7 AWS services
          (DynamoDB, S3, Lambda, API Gateway, Cognito, Step Functions, CloudWatch),
          it features a custom Python library (lendlib) for inventory management,
          availability checking, overdue detection, and borrower history tracking.
        </p>
        <p style={{ fontSize: '13px', color: '#666', marginTop: '12px' }}>
          Student: Vishvaksen Machana | ID: 25173421 | Module: Cloud Platform Programming | NCI
        </p>
      </div>
    </div>
  );
}

export default Dashboard;
