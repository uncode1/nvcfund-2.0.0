import React, { useState, useEffect } from 'react';
import apiService from '../services/api';

const TreasuryPage = () => {
  const [treasuryData, setTreasuryData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchTreasuryData = async () => {
      try {
        setLoading(true);
        const data = await apiService.getTreasuryDashboard();
        setTreasuryData(data);
      } catch (err) {
        setError('Unable to load treasury data');
        console.error('Treasury data fetch error:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchTreasuryData();
  }, []);

  if (loading) {
    return (
      <div className="container mt-4">
        <div className="text-center">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading treasury data...</span>
          </div>
          <p className="mt-2">Loading treasury dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mt-4">
        <div className="alert alert-warning" role="alert">
          <h4 className="alert-heading">Treasury Module</h4>
          <p>{error}</p>
          <hr />
          <p className="mb-0">This module connects to: <code>/api/v1/treasury/dashboard</code></p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mt-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1 className="h2 text-primary">
          <i className="fas fa-university me-2"></i>
          Treasury Management
        </h1>
        <div className="badge bg-success fs-6">Connected to Modular Backend</div>
      </div>

      <div className="row">
        <div className="col-md-6">
          <div className="card border-primary">
            <div className="card-header bg-primary text-white">
              <h5 className="card-title mb-0">
                <i className="fas fa-chart-line me-2"></i>
                Treasury Dashboard
              </h5>
            </div>
            <div className="card-body">
              <p className="card-text">
                Connected to modular treasury backend at:
              </p>
              <code className="text-primary">/api/v1/treasury/dashboard</code>
              
              {treasuryData && (
                <div className="mt-3">
                  <h6>Live Data Retrieved:</h6>
                  <pre className="bg-light p-2 small">
                    {JSON.stringify(treasuryData, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="col-md-6">
          <div className="card border-info">
            <div className="card-header bg-info text-white">
              <h5 className="card-title mb-0">
                <i className="fas fa-cogs me-2"></i>
                Available Operations
              </h5>
            </div>
            <div className="card-body">
              <ul className="list-group list-group-flush">
                <li className="list-group-item d-flex justify-content-between align-items-center">
                  Treasury Accounts
                  <span className="badge bg-primary rounded-pill">Active</span>
                </li>
                <li className="list-group-item d-flex justify-content-between align-items-center">
                  Execute Operations
                  <span className="badge bg-success rounded-pill">Ready</span>
                </li>
                <li className="list-group-item d-flex justify-content-between align-items-center">
                  Generate Reports
                  <span className="badge bg-info rounded-pill">Available</span>
                </li>
                <li className="list-group-item d-flex justify-content-between align-items-center">
                  NVCT Operations
                  <span className="badge bg-warning rounded-pill">Connected</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <div className="row mt-4">
        <div className="col-12">
          <div className="card border-success">
            <div className="card-header bg-success text-white">
              <h5 className="card-title mb-0">
                <i className="fas fa-check-circle me-2"></i>
                Modular Backend Connection Status
              </h5>
            </div>
            <div className="card-body">
              <div className="row">
                <div className="col-md-3">
                  <div className="text-center">
                    <i className="fas fa-server fa-3x text-success mb-2"></i>
                    <h6>Backend Status</h6>
                    <span className="badge bg-success">Connected</span>
                  </div>
                </div>
                <div className="col-md-3">
                  <div className="text-center">
                    <i className="fas fa-database fa-3x text-primary mb-2"></i>
                    <h6>Database</h6>
                    <span className="badge bg-primary">PostgreSQL</span>
                  </div>
                </div>
                <div className="col-md-3">
                  <div className="text-center">
                    <i className="fas fa-shield-alt fa-3x text-info mb-2"></i>
                    <h6>Security</h6>
                    <span className="badge bg-info">Enterprise</span>
                  </div>
                </div>
                <div className="col-md-3">
                  <div className="text-center">
                    <i className="fas fa-chart-bar fa-3x text-warning mb-2"></i>
                    <h6>Logging</h6>
                    <span className="badge bg-warning">Active</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TreasuryPage;