import React, { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import api from '../services/api';

const AccountsPage = () => {
  const { user } = useAuth();
  const [accounts, setAccounts] = useState([]);
  const [selectedAccount, setSelectedAccount] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [transactionPage, setTransactionPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    fetchAccounts();
  }, []);

  useEffect(() => {
    if (selectedAccount) {
      fetchTransactions(selectedAccount.id, transactionPage);
    }
  }, [selectedAccount, transactionPage]);

  const fetchAccounts = async () => {
    try {
      setLoading(true);
      const response = await api.getAccounts();
      if (response.status === 'success') {
        const accountsList = response.data.accounts || [];
        setAccounts(accountsList);
        if (accountsList.length > 0 && !selectedAccount) {
          setSelectedAccount(accountsList[0]);
        }
      }
    } catch (err) {
      console.error('Error fetching accounts:', err);
      setError('Failed to load accounts');
    } finally {
      setLoading(false);
    }
  };

  const fetchTransactions = async (accountId, page = 1) => {
    try {
      const response = await api.getTransactions({ accountId, page, limit: 20 });
      if (response.status === 'success') {
        setTransactions(response.data.transactions || []);
        setTotalPages(response.data.total_pages || 1);
      }
    } catch (err) {
      console.error('Error fetching transactions:', err);
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

  const formatDateTime = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getAccountTypeIcon = (type) => {
    switch (type?.toLowerCase()) {
      case 'checking':
        return 'fas fa-university';
      case 'savings':
        return 'fas fa-piggy-bank';
      case 'credit':
        return 'fas fa-credit-card';
      case 'investment':
        return 'fas fa-chart-line';
      case 'business':
        return 'fas fa-briefcase';
      default:
        return 'fas fa-wallet';
    }
  };

  const getTransactionIcon = (type) => {
    switch (type?.toLowerCase()) {
      case 'transfer':
        return 'fas fa-exchange-alt';
      case 'deposit':
        return 'fas fa-arrow-down';
      case 'withdrawal':
        return 'fas fa-arrow-up';
      case 'payment':
        return 'fas fa-credit-card';
      case 'fee':
        return 'fas fa-exclamation-triangle';
      default:
        return 'fas fa-receipt';
    }
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
    <div className="container-fluid py-4">
      <div className="row">
        <div className="col-12">
          <h2 className="mb-4">My Accounts</h2>
        </div>
      </div>

      {error && (
        <div className="row mb-4">
          <div className="col-12">
            <div className="alert alert-danger">
              <i className="fas fa-exclamation-triangle me-2"></i>
              {error}
            </div>
          </div>
        </div>
      )}

      <div className="row">
        {/* Accounts List */}
        <div className="col-lg-4 mb-4">
          <div className="card">
            <div className="card-header d-flex justify-content-between align-items-center">
              <h5 className="mb-0">Accounts</h5>
              <button className="btn btn-primary btn-sm">
                <i className="fas fa-plus me-1"></i>Open Account
              </button>
            </div>
            <div className="card-body p-0">
              {accounts.length > 0 ? (
                accounts.map((account) => (
                  <div 
                    key={account.id} 
                    className={`list-group-item list-group-item-action border-0 ${selectedAccount?.id === account.id ? 'active' : ''}`}
                    onClick={() => setSelectedAccount(account)}
                    style={{ cursor: 'pointer' }}
                  >
                    <div className="d-flex align-items-center">
                      <div className="me-3">
                        <i className={`${getAccountTypeIcon(account.account_type)} fa-lg`}></i>
                      </div>
                      <div className="flex-grow-1">
                        <div className="d-flex justify-content-between align-items-start">
                          <div>
                            <h6 className="mb-1">{account.account_name}</h6>
                            <p className="mb-1 small text-muted">
                              {account.account_type} • •••{account.account_number?.slice(-4)}
                            </p>
                          </div>
                          <div className="text-end">
                            <div className="fw-bold">
                              {formatCurrency(account.available_balance, account.currency)}
                            </div>
                            <span className={`badge ${account.status === 'active' ? 'bg-success' : 'bg-warning'}`}>
                              {account.status}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="p-4 text-center">
                  <i className="fas fa-university fa-3x text-muted mb-3"></i>
                  <p className="text-muted">No accounts found</p>
                  <button className="btn btn-primary btn-sm">
                    Open Your First Account
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Account Details */}
        <div className="col-lg-8">
          {selectedAccount ? (
            <>
              {/* Account Overview */}
              <div className="card mb-4">
                <div className="card-header">
                  <div className="d-flex justify-content-between align-items-center">
                    <h5 className="mb-0">
                      <i className={`${getAccountTypeIcon(selectedAccount.account_type)} me-2`}></i>
                      {selectedAccount.account_name}
                    </h5>
                    <div className="btn-group">
                      <button className="btn btn-outline-primary btn-sm">
                        <i className="fas fa-paper-plane me-1"></i>Transfer
                      </button>
                      <button className="btn btn-outline-success btn-sm">
                        <i className="fas fa-download me-1"></i>Statement
                      </button>
                      <button className="btn btn-outline-info btn-sm">
                        <i className="fas fa-cog me-1"></i>Settings
                      </button>
                    </div>
                  </div>
                </div>
                <div className="card-body">
                  <div className="row">
                    <div className="col-md-6">
                      <div className="row mb-3">
                        <div className="col-sm-6">
                          <label className="text-muted small">Account Number</label>
                          <div className="fw-bold">{selectedAccount.account_number}</div>
                        </div>
                        <div className="col-sm-6">
                          <label className="text-muted small">Account Type</label>
                          <div className="fw-bold text-capitalize">{selectedAccount.account_type}</div>
                        </div>
                      </div>
                      <div className="row mb-3">
                        <div className="col-sm-6">
                          <label className="text-muted small">Currency</label>
                          <div className="fw-bold">{selectedAccount.currency}</div>
                        </div>
                        <div className="col-sm-6">
                          <label className="text-muted small">Status</label>
                          <div>
                            <span className={`badge ${selectedAccount.status === 'active' ? 'bg-success' : 'bg-warning'}`}>
                              {selectedAccount.status}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                    <div className="col-md-6">
                      <div className="row mb-3">
                        <div className="col-sm-6">
                          <label className="text-muted small">Available Balance</label>
                          <div className="h4 text-success mb-0">
                            {formatCurrency(selectedAccount.available_balance, selectedAccount.currency)}
                          </div>
                        </div>
                        <div className="col-sm-6">
                          <label className="text-muted small">Current Balance</label>
                          <div className="h5 mb-0">
                            {formatCurrency(selectedAccount.current_balance, selectedAccount.currency)}
                          </div>
                        </div>
                      </div>
                      {selectedAccount.pending_balance !== 0 && (
                        <div className="row mb-3">
                          <div className="col-sm-6">
                            <label className="text-muted small">Pending Balance</label>
                            <div className="text-warning fw-bold">
                              {formatCurrency(selectedAccount.pending_balance, selectedAccount.currency)}
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Account Limits */}
                  {(selectedAccount.daily_transfer_limit || selectedAccount.monthly_transfer_limit) && (
                    <div className="border-top pt-3 mt-3">
                      <h6 className="mb-3">Transfer Limits</h6>
                      <div className="row">
                        {selectedAccount.daily_transfer_limit && (
                          <div className="col-md-6">
                            <label className="text-muted small">Daily Transfer Limit</label>
                            <div className="fw-bold">
                              {formatCurrency(selectedAccount.daily_transfer_limit, selectedAccount.currency)}
                            </div>
                          </div>
                        )}
                        {selectedAccount.monthly_transfer_limit && (
                          <div className="col-md-6">
                            <label className="text-muted small">Monthly Transfer Limit</label>
                            <div className="fw-bold">
                              {formatCurrency(selectedAccount.monthly_transfer_limit, selectedAccount.currency)}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Account Transactions */}
              <div className="card">
                <div className="card-header d-flex justify-content-between align-items-center">
                  <h5 className="mb-0">Recent Transactions</h5>
                  <div className="btn-group btn-group-sm">
                    <button className="btn btn-outline-primary">Filter</button>
                    <button className="btn btn-outline-secondary">Export</button>
                  </div>
                </div>
                <div className="card-body">
                  {transactions.length > 0 ? (
                    <>
                      <div className="table-responsive">
                        <table className="table table-hover">
                          <thead>
                            <tr>
                              <th>Date</th>
                              <th>Description</th>
                              <th>Type</th>
                              <th className="text-end">Amount</th>
                              <th className="text-end">Balance</th>
                              <th>Status</th>
                            </tr>
                          </thead>
                          <tbody>
                            {transactions.map((transaction) => (
                              <tr key={transaction.id}>
                                <td>
                                  <div className="small">
                                    {formatDateTime(transaction.created_at)}
                                  </div>
                                </td>
                                <td>
                                  <div className="d-flex align-items-center">
                                    <i className={`${getTransactionIcon(transaction.transaction_type)} me-2 text-muted`}></i>
                                    <div>
                                      <div className="fw-bold">{transaction.description}</div>
                                      {transaction.reference_number && (
                                        <div className="small text-muted">
                                          Ref: {transaction.reference_number}
                                        </div>
                                      )}
                                    </div>
                                  </div>
                                </td>
                                <td>
                                  <span className="badge bg-secondary">
                                    {transaction.transaction_type}
                                  </span>
                                </td>
                                <td className="text-end">
                                  <span className={`fw-bold ${transaction.amount >= 0 ? 'text-success' : 'text-danger'}`}>
                                    {transaction.amount >= 0 ? '+' : ''}
                                    {formatCurrency(transaction.amount, transaction.currency)}
                                  </span>
                                </td>
                                <td className="text-end">
                                  <span className="fw-bold">
                                    {formatCurrency(transaction.balance_after, transaction.currency)}
                                  </span>
                                </td>
                                <td>
                                  <span className={`badge ${
                                    transaction.status === 'completed' ? 'bg-success' :
                                    transaction.status === 'pending' ? 'bg-warning' :
                                    transaction.status === 'failed' ? 'bg-danger' :
                                    'bg-secondary'
                                  }`}>
                                    {transaction.status}
                                  </span>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>

                      {/* Pagination */}
                      {totalPages > 1 && (
                        <nav className="mt-3">
                          <ul className="pagination pagination-sm justify-content-center">
                            <li className={`page-item ${transactionPage === 1 ? 'disabled' : ''}`}>
                              <button 
                                className="page-link"
                                onClick={() => setTransactionPage(transactionPage - 1)}
                                disabled={transactionPage === 1}
                              >
                                Previous
                              </button>
                            </li>
                            {[...Array(totalPages)].map((_, index) => (
                              <li key={index + 1} className={`page-item ${transactionPage === index + 1 ? 'active' : ''}`}>
                                <button 
                                  className="page-link"
                                  onClick={() => setTransactionPage(index + 1)}
                                >
                                  {index + 1}
                                </button>
                              </li>
                            ))}
                            <li className={`page-item ${transactionPage === totalPages ? 'disabled' : ''}`}>
                              <button 
                                className="page-link"
                                onClick={() => setTransactionPage(transactionPage + 1)}
                                disabled={transactionPage === totalPages}
                              >
                                Next
                              </button>
                            </li>
                          </ul>
                        </nav>
                      )}
                    </>
                  ) : (
                    <div className="text-center py-4">
                      <i className="fas fa-receipt fa-3x text-muted mb-3"></i>
                      <p className="text-muted">No transactions found for this account</p>
                    </div>
                  )}
                </div>
              </div>
            </>
          ) : (
            <div className="card">
              <div className="card-body text-center py-5">
                <i className="fas fa-university fa-3x text-muted mb-3"></i>
                <h5 className="text-muted">Select an account to view details</h5>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AccountsPage;