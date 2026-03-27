import React, { useState, useEffect } from 'react';
import { awsApi } from '../services/api';

function AWSStatusPage() {
  const [status, setStatus] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchStatus() {
      try {
        const data = await awsApi.status();
        setStatus(data);
      } catch {
        setError('Could not fetch AWS status. Ensure the backend is running.');
      }
    }
    fetchStatus();
  }, []);

  const serviceDescriptions = {
    dynamodb: 'NoSQL database storing tools, users, and lending records',
    s3: 'Object storage for tool images and photos',
    lambda: 'Serverless functions for validation, notifications, and reports',
    api_gateway: 'REST API endpoint management and rate limiting',
    cognito: 'User authentication and authorization',
    step_functions: 'Lending workflow orchestration (request > approve > lend > return)',
    cloudwatch: 'Monitoring, logging, metrics, and overdue scheduling',
  };

  return (
    <div>
      <div className="page-header">
        <h1>AWS Services Status</h1>
        <p style={{ color: '#666', fontSize: '14px' }}>
          7 AWS services integrated {status?.mock_mode ? '(running in mock mode)' : '(connected to AWS)'}
        </p>
      </div>

      {error && <div className="card" style={{ color: 'red' }}>{error}</div>}

      {status && (
        <div className="service-grid">
          {Object.entries(status.aws_services || {}).map(([key, svc]) => (
            <div className="service-card" key={key}>
              <h4>{svc.service || key}</h4>
              <p className="detail" style={{ marginBottom: '8px' }}>{serviceDescriptions[key]}</p>
              <div className="detail">
                Status: <span className={`badge ${svc.status === 'running' ? 'badge-green' : 'badge-red'}`}>{svc.status}</span>
              </div>
              <div className="detail">Mode: {svc.mock_mode ? 'Mock (Local)' : 'AWS (Production)'}</div>
              {svc.region && <div className="detail">Region: {svc.region}</div>}
              {Object.entries(svc).filter(([k]) => !['service','status','mock_mode','region'].includes(k)).map(([k, v]) => (
                <div className="detail" key={k}>{k.replace(/_/g, ' ')}: {typeof v === 'object' ? JSON.stringify(v) : String(v)}</div>
              ))}
            </div>
          ))}
        </div>
      )}

      {!status && !error && <div className="card"><p>Loading AWS service status...</p></div>}
    </div>
  );
}

export default AWSStatusPage;
