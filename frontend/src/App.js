import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import ToolsPage from './pages/ToolsPage';
import UsersPage from './pages/UsersPage';
import LendingsPage from './pages/LendingsPage';
import AWSStatusPage from './pages/AWSStatusPage';

function App() {
  const [page, setPage] = useState('dashboard');

  const renderPage = () => {
    switch (page) {
      case 'tools': return <ToolsPage />;
      case 'users': return <UsersPage />;
      case 'lendings': return <LendingsPage />;
      case 'aws': return <AWSStatusPage />;
      default: return <Dashboard />;
    }
  };

  return (
    <div className="app-container">
      <Sidebar activePage={page} onNavigate={setPage} />
      <div className="main-content">
        {renderPage()}
      </div>
    </div>
  );
}

export default App;
