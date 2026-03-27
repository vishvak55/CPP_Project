import React from 'react';

function Sidebar({ activePage, onNavigate }) {
  const links = [
    { id: 'dashboard', label: 'Dashboard' },
    { id: 'tools', label: 'Tools' },
    { id: 'users', label: 'Users' },
    { id: 'lendings', label: 'Lendings' },
    { id: 'aws', label: 'AWS Status' },
  ];

  return (
    <div className="sidebar">
      <h2>Tool Lending</h2>
      <div className="subtitle">Community Library System</div>
      <nav>
        {links.map(link => (
          <a
            key={link.id}
            href={`#${link.id}`}
            className={activePage === link.id ? 'active' : ''}
            onClick={(e) => { e.preventDefault(); onNavigate(link.id); }}
          >
            {link.label}
          </a>
        ))}
      </nav>
      <div style={{ padding: '20px', marginTop: 'auto', fontSize: '11px', opacity: 0.6 }}>
        <div>Vishvaksen Machana</div>
        <div>25173421</div>
        <div>NCI - CPP Module</div>
      </div>
    </div>
  );
}

export default Sidebar;
