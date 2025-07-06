import React from 'react';

const TransactionsPage = () => {
  return (
    <div className="main-content">
      <div className="container py-4">
        <h2>Transactions</h2>
        <p className="text-muted">View your transaction history</p>
        
        <div className="card dashboard-card">
          <div className="card-body text-center py-5">
            <i className="fas fa-history fa-3x text-muted mb-3"></i>
            <h5>Transaction History</h5>
            <p className="text-muted">This page will show your detailed transaction history and analytics.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TransactionsPage;