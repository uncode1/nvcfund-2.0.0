import React from 'react';

const TransferPage = () => {
  return (
    <div className="main-content">
      <div className="container py-4">
        <h2>Transfer Money</h2>
        <p className="text-muted">Send money securely</p>
        
        <div className="card dashboard-card">
          <div className="card-body text-center py-5">
            <i className="fas fa-exchange-alt fa-3x text-muted mb-3"></i>
            <h5>Money Transfer</h5>
            <p className="text-muted">This page will provide secure money transfer functionality.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TransferPage;