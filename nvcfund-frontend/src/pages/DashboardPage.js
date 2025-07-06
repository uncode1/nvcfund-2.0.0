import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import api from '../services/api';

const DashboardPage = () => {
  const { user } = useAuth();
  const [accounts, setAccounts] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      // Fetch user accounts
      const accountsResponse = await api.getAccounts();
      if (accountsResponse.status === 'success') {
        setAccounts(accountsResponse.data || []);
      }

      // Fetch recent transactions (for now, set empty array as transactions endpoint needs schema fix)
      setTransactions([]);
    } catch (error) {
      // Central error handler will catch this automatically
      console.error('Dashboard data fetch error:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount, currency = 'USD') => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency
    }).format(amount);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  // Navigation handlers for onclick actions
  const handleViewAccount = (accountId) => {
    navigate(`/accounts?account=${accountId}`);
  };

  const handleTransferFromAccount = (accountId) => {
    navigate(`/transfers?from=${accountId}`);
  };

  const handleQuickTransfer = () => {
    navigate('/transfers');
  };

  const handlePayBills = () => {
    navigate('/bills');
  };

  const handleViewAccounts = () => {
    navigate('/accounts');
  };

  const handleViewProfile = () => {
    navigate('/profile');
  };

  const handleViewTransactions = () => {
    navigate('/transactions');
  };

  const handleViewStatements = () => {
    navigate('/statements');
  };

  const handleViewCards = () => {
    navigate('/cards');
  };

  const handleViewLoans = () => {
    navigate('/loans');
  };

  const handleApplyCard = () => {
    navigate('/apply-card');
  };

  const handleExchange = () => {
    navigate('/exchange');
  };

  if (loading) {
    return (
      <div className="container-fluid py-4">
        <div className="d-flex justify-content-center">
          <div className="spinner-border" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      </div>
    );
  }



  return (
    <div className="main-content">
      {/* Welcome Header */}
      <div className="row mb-4">
        <div className="col-12">
          <div className="card">
            <div className="card-header">
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <h2 className="mb-0">
                    Welcome back, {user?.first_name || user?.username}
                  </h2>
                  <p className="mb-0">
                    {new Date().toLocaleDateString('en-US', { 
                      weekday: 'long', 
                      year: 'numeric', 
                      month: 'long', 
                      day: 'numeric' 
                    })}
                  </p>
                </div>
                <div className="text-end">
                  <small className="d-block">Last Login</small>
                  <small>
                    {user?.last_login ? 
                      new Date(user.last_login).toLocaleDateString('en-US', {
                        month: 'short',
                        day: 'numeric',
                        year: 'numeric'
                      }) + ' at ' + 
                      new Date(user.last_login).toLocaleTimeString('en-US', {
                        hour: '2-digit',
                        minute: '2-digit'
                      })
                      : 'Welcome!'
                    }
                  </small>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="row mb-4">
        <div className="col-12">
          <h4 className="mb-3">Quick Actions</h4>
        </div>
        <div className="col-md-3 mb-3">
          <div className="card h-100 border-primary">
            <div className="card-body text-center">
              <i className="fas fa-exchange-alt fa-2x text-primary mb-2"></i>
              <h6 className="card-title">Transfer Money</h6>
              <p className="card-text small text-muted">Send money between accounts or to external recipients</p>
              <button 
                className="btn btn-primary btn-sm"
                onClick={handleQuickTransfer}
              >
                Transfer Now
              </button>
            </div>
          </div>
        </div>
        <div className="col-md-3 mb-3">
          <div className="card h-100 border-success">
            <div className="card-body text-center">
              <i className="fas fa-plus-circle fa-2x text-success mb-2"></i>
              <h6 className="card-title">Open Account</h6>
              <p className="card-text small text-muted">Create traditional, digital wallets, and exchange accounts</p>
              <button 
                className="btn btn-success btn-sm"
                onClick={() => navigate('/create-account')}
              >
                Create Account
              </button>
            </div>
          </div>
        </div>
        <div className="col-md-3 mb-3">
          <div className="card h-100 border-info">
            <div className="card-body text-center">
              <i className="fas fa-exchange-alt fa-2x text-info mb-2"></i>
              <h6 className="card-title">Currency Exchange</h6>
              <p className="card-text small text-muted">Convert fiat-to-digital and digital-to-fiat currencies</p>
              <button 
                className="btn btn-info btn-sm"
                onClick={() => navigate('/exchange')}
              >
                Start Exchange
              </button>
            </div>
          </div>
        </div>
        <div className="col-md-3 mb-3">
          <div className="card h-100 border-warning">
            <div className="card-body text-center">
              <i className="fas fa-receipt fa-2x text-warning mb-2"></i>
              <h6 className="card-title">Pay Bills</h6>
              <p className="card-text small text-muted">Pay utilities, loans, and other recurring bills</p>
              <button 
                className="btn btn-warning btn-sm"
                onClick={handlePayBills}
              >
                Pay Bills
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Banking Services */}
      <div className="row mb-4">
        <div className="col-12">
          <h4 className="mb-3">Banking Services</h4>
        </div>
        <div className="col-md-4 mb-3">
          <div className="card">
            <div className="card-body">
              <div className="d-flex align-items-center mb-3">
                <i className="fas fa-university fa-2x text-primary me-3"></i>
                <div>
                  <h6 className="mb-0">Account Management</h6>
                  <small className="text-muted">Manage your accounts and settings</small>
                </div>
              </div>
              <div className="d-grid gap-2">
                <button 
                  className="btn btn-outline-primary btn-sm"
                  onClick={handleViewAccounts}
                >
                  <i className="fas fa-wallet me-2"></i>View All Accounts
                </button>
                <button 
                  className="btn btn-outline-primary btn-sm"
                  onClick={handleViewProfile}
                >
                  <i className="fas fa-user-edit me-2"></i>Update Profile
                </button>
              </div>
            </div>
          </div>
        </div>
        <div className="col-md-4 mb-3">
          <div className="card">
            <div className="card-body">
              <div className="d-flex align-items-center mb-3">
                <i className="fas fa-chart-line fa-2x text-success me-3"></i>
                <div>
                  <h6 className="mb-0">Transaction History</h6>
                  <small className="text-muted">Review your transaction history</small>
                </div>
              </div>
              <div className="d-grid gap-2">
                <button 
                  className="btn btn-outline-success btn-sm"
                  onClick={handleViewTransactions}
                >
                  <i className="fas fa-history me-2"></i>View Transactions
                </button>
                <button 
                  className="btn btn-outline-success btn-sm"
                  onClick={handleViewStatements}
                >
                  <i className="fas fa-file-alt me-2"></i>Download Statements
                </button>
              </div>
            </div>
          </div>
        </div>
        <div className="col-md-4 mb-3">
          <div className="card">
            <div className="card-body">
              <div className="d-flex align-items-center mb-3">
                <i className="fas fa-hand-holding-usd fa-2x text-info me-3"></i>
                <div>
                  <h6 className="mb-0">Loans & Credit</h6>
                  <small className="text-muted">Manage loans and credit products</small>
                </div>
              </div>
              <div className="d-grid gap-2">
                <button 
                  className="btn btn-outline-info btn-sm"
                  onClick={handleViewLoans}
                >
                  <i className="fas fa-percentage me-2"></i>View Loans
                </button>
                <button 
                  className="btn btn-outline-info btn-sm"
                  onClick={() => navigate('/apply-loan')}
                >
                  <i className="fas fa-plus-circle me-2"></i>Apply for Loan
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Account Overview */}
      <div className="row mb-4">
        <div className="col-12">
          <h4 className="mb-3">Account Overview</h4>
        </div>
        {accounts.length > 0 ? (
          accounts.map((account) => (
            <div key={account.id} className="col-md-6 col-lg-4 mb-3">
              <div className="card h-100">
                <div className="card-body">
                  <div className="d-flex justify-content-between align-items-start mb-2">
                    <h6 className="card-title">{account.account_name}</h6>
                    <span className={`badge ${account.status === 'active' ? 'bg-success' : 'bg-warning'}`}>
                      {account.status}
                    </span>
                  </div>
                  <p className="card-text text-muted small">
                    {account.account_type} • {account.account_number}
                  </p>
                  <div className="mt-3">
                    <div className="d-flex justify-content-between">
                      <span className="text-muted">Available Balance:</span>
                      <strong>{formatCurrency(account.available_balance, account.currency)}</strong>
                    </div>
                    <div className="d-flex justify-content-between">
                      <span className="text-muted">Current Balance:</span>
                      <span>{formatCurrency(account.current_balance, account.currency)}</span>
                    </div>
                  </div>
                </div>
                <div className="card-footer bg-transparent">
                  <div className="btn-group w-100" role="group">
                    <button 
                      className="btn btn-outline-primary btn-sm"
                      onClick={() => handleViewAccount(account.id)}
                    >
                      <i className="fas fa-eye me-1"></i>View
                    </button>
                    <button 
                      className="btn btn-outline-success btn-sm"
                      onClick={() => handleTransferFromAccount(account.id)}
                    >
                      <i className="fas fa-paper-plane me-1"></i>Transfer
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="col-12">
            <div className="alert alert-info">
              <i className="fas fa-info-circle me-2"></i>
              No accounts found. Contact customer service to set up your banking accounts.
            </div>
          </div>
        )}
      </div>



      {/* Recent Transactions */}
      <div className="row">
        <div className="col-12">
          <div className="card">
            <div className="card-header d-flex justify-content-between align-items-center">
              <h5 className="mb-0">Recent Transactions</h5>
              <button className="btn btn-outline-primary btn-sm">
                View All
              </button>
            </div>
            <div className="card-body">
              {transactions.length > 0 ? (
                <div className="table-responsive">
                  <table className="table table-hover">
                    <thead>
                      <tr>
                        <th>Date</th>
                        <th>Description</th>
                        <th>Type</th>
                        <th className="text-end">Amount</th>
                        <th>Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {transactions.map((transaction) => (
                        <tr key={transaction.id}>
                          <td>{formatDate(transaction.created_at)}</td>
                          <td>
                            <div>
                              <strong>{transaction.description}</strong>
                              {transaction.reference_number && (
                                <div className="small text-muted">
                                  Ref: {transaction.reference_number}
                                </div>
                              )}
                            </div>
                          </td>
                          <td>
                            <span className="badge bg-secondary">
                              {transaction.transaction_type}
                            </span>
                          </td>
                          <td className="text-end">
                            <span className={`${transaction.amount >= 0 ? 'text-success' : 'text-danger'}`}>
                              {transaction.amount >= 0 ? '+' : ''}
                              {formatCurrency(transaction.amount, transaction.currency)}
                            </span>
                          </td>
                          <td>
                            <span className={`badge ${
                              transaction.status === 'completed' ? 'bg-success' :
                              transaction.status === 'pending' ? 'bg-warning' :
                              'bg-danger'
                            }`}>
                              {transaction.status}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="text-center py-4">
                  <i className="fas fa-receipt fa-3x text-muted mb-3"></i>
                  <p className="text-muted">No recent transactions</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;