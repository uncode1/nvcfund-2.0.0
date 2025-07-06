import React from 'react';

const InsurancePage = () => (
  <div className="container mt-4">
    <h1 className="h2 text-primary mb-4">
      <i className="fas fa-umbrella me-2"></i>
      Insurance Services
    </h1>
    <div className="alert alert-info">
      <p><strong>Connected to:</strong> <code>/api/v1/insurance/policies</code></p>
    </div>
  </div>
);

export default InsurancePage;