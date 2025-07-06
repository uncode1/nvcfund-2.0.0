import React from 'react';

const ProfilePage = () => {
  return (
    <div className="main-content">
      <div className="container py-4">
        <h2>Profile</h2>
        <p className="text-muted">Manage your profile settings</p>
        
        <div className="card dashboard-card">
          <div className="card-body text-center py-5">
            <i className="fas fa-user fa-3x text-muted mb-3"></i>
            <h5>User Profile</h5>
            <p className="text-muted">This page will allow you to update your profile information and settings.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;