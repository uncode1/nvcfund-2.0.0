import React from 'react';

const AdminPage = () => {
  return (
    <div className="main-content">
      <div className="container py-4">
        <h2>Admin Dashboard</h2>
        <p className="text-muted">System administration and management</p>
        
        <div className="card dashboard-card">
          <div className="card-body text-center py-5">
            <i className="fas fa-cog fa-3x text-muted mb-3"></i>
            <h5>Admin Center</h5>
            <p className="text-muted">This page will provide comprehensive system administration tools.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminPage;