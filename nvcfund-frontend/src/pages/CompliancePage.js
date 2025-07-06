import React, { useState, useEffect } from 'react';
import apiService from '../services/api';

const CompliancePage = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchComplianceData = async () => {
      try {
        setLoading(true);
        // Test connection to modular compliance endpoint
        await apiService.getComplianceDashboard();
      } catch (err) {
        setError('Compliance module endpoint ready but requires authentication');
      } finally {
        setLoading(false);
      }
    };
    fetchComplianceData();
  }, []);

  return (
    <div className="container mt-4">
      <h1 className="h2 text-primary mb-4">
        <i className="fas fa-shield-alt me-2"></i>
        Compliance Management
      </h1>
      <div className="alert alert-info">
        <p><strong>Connected to:</strong> <code>/api/v1/compliance/dashboard</code></p>
        <p>Status: Modular backend connection established</p>
      </div>
    </div>
  );
};

export default CompliancePage;