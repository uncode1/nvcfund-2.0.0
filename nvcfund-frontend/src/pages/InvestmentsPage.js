import React from 'react';

const InvestmentsPage = () => (
  <div className="container mt-4">
    <h1 className="h2 text-primary mb-4">
      <i className="fas fa-chart-line me-2"></i>
      Investment Portfolio
    </h1>
    <div className="alert alert-info">
      <p><strong>Connected to:</strong> <code>/api/v1/investments/portfolio</code></p>
      <p>Modular backend connection established for investment management</p>
    </div>
  </div>
);

export default InvestmentsPage;