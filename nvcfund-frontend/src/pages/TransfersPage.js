import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import api from '../services/api';
import { InputValidator } from '../security/InputValidator';
import { SecurityManager } from '../security/SecurityManager';

const TransfersPage = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [accounts, setAccounts] = useState([]);
  const [transferData, setTransferData] = useState({
    fromAccount: '',
    toAccount: '',
    amount: '',
    description: '',
    transferType: 'internal'
  });
  const [beneficiaries, setBeneficiaries] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [validationErrors, setValidationErrors] = useState({});
  const [transferHistory, setTransferHistory] = useState([]);
  const [showNoAccountsModal, setShowNoAccountsModal] = useState(false);
  
  const securityManager = new SecurityManager();
  const validator = new InputValidator();

  useEffect(() => {
    fetchAccountsAndBeneficiaries();
    fetchTransferHistory();
  }, []);

  const fetchAccountsAndBeneficiaries = async () => {
    try {
      // Fetch user accounts
      const accountsResponse = await api.getAccounts();
      if (accountsResponse.status === 'success') {
        const userAccounts = accountsResponse.data.accounts || [];
        setAccounts(userAccounts);
        
        // Check if user has no accounts
        if (userAccounts.length === 0) {
          setShowNoAccountsModal(true);
        }
      }

      // Fetch beneficiaries (using getAccounts for now, would need separate endpoint)
      const beneficiariesResponse = await api.getAccounts();
      if (beneficiariesResponse.status === 'success') {
        setBeneficiaries(beneficiariesResponse.data.accounts || []);
      }
    } catch (err) {
      console.error('Error fetching data:', err);
      setError('Failed to load account information');
    }
  };

  const handleCreateAccount = () => {
    navigate('/create-account?redirect=transfer');
  };

  const fetchTransferHistory = async () => {
    try {
      const response = await api.getTransactions({ limit: 20 });
      if (response.status === 'success') {
        setTransferHistory(response.data.transactions || []);
      }
    } catch (err) {
      console.error('Error fetching transfer history:', err);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setTransferData(prev => ({ ...prev, [name]: value }));
    
    // Clear previous errors
    if (validationErrors[name]) {
      setValidationErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
    
    setError('');
    setSuccess('');
  };

  const validateTransfer = () => {
    const errors = {};
    
    // Validate amount
    const amountValidation = validator.validateAmount(transferData.amount);
    if (!amountValidation.isValid) {
      errors.amount = amountValidation;
    }

    // Validate accounts
    if (!transferData.fromAccount) {
      errors.fromAccount = { isValid: false, errors: ['Please select a source account'] };
    }
    
    if (!transferData.toAccount) {
      errors.toAccount = { isValid: false, errors: ['Please select a destination account'] };
    }

    if (transferData.fromAccount === transferData.toAccount) {
      errors.toAccount = { isValid: false, errors: ['Source and destination accounts cannot be the same'] };
    }

    // Validate description
    if (transferData.description.trim().length < 3) {
      errors.description = { isValid: false, errors: ['Description must be at least 3 characters'] };
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleTransfer = async (e) => {
    e.preventDefault();
    
    if (!validateTransfer()) {
      return;
    }

    // Security check
    const securityEvent = securityManager.formatSecurityEvent('transfer_attempt', {
      fromAccount: transferData.fromAccount,
      amount: transferData.amount,
      transferType: transferData.transferType
    });
    
    try {
      await api.post('/api/v1/security/report-suspicious-activity', securityEvent);
    } catch (err) {
      console.warn('Security reporting failed:', err);
    }

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const response = await api.createTransfer({
        from_account_id: transferData.fromAccount,
        to_account: transferData.toAccount,
        amount: parseFloat(transferData.amount),
        description: transferData.description,
        transfer_type: transferData.transferType
      });

      if (response.status === 'success') {
        setSuccess('Transfer initiated successfully');
        setTransferData({
          fromAccount: '',
          toAccount: '',
          amount: '',
          description: '',
          transferType: 'internal'
        });
        fetchTransferHistory();
        fetchAccountsAndBeneficiaries(); // Refresh balances
      } else {
        setError(response.message || 'Transfer failed');
      }
    } catch (err) {
      console.error('Transfer error:', err);
      setError(err.response?.data?.message || 'Transfer failed. Please try again.');
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
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="container-fluid py-4">
      <div className="row">
        <div className="col-12">
          <h2 className="mb-4">Money Transfers</h2>
        </div>
      </div>

      <div className="row">
        {/* Transfer Form */}
        <div className="col-lg-8 mb-4">
          <div className="card">
            <div className="card-header">
              <h5 className="mb-0">
                <i className="fas fa-paper-plane me-2"></i>
                New Transfer
              </h5>
            </div>
            <div className="card-body">
              {error && (
                <div className="alert alert-danger">
                  <i className="fas fa-exclamation-triangle me-2"></i>
                  {error}
                </div>
              )}
              
              {success && (
                <div className="alert alert-success">
                  <i className="fas fa-check-circle me-2"></i>
                  {success}
                </div>
              )}

              <form onSubmit={handleTransfer}>
                <div className="row">
                  <div className="col-md-6 mb-3">
                    <label htmlFor="fromAccount" className="form-label">From Account</label>
                    <select
                      className={`form-select ${validationErrors.fromAccount ? 'is-invalid' : ''}`}
                      id="fromAccount"
                      name="fromAccount"
                      value={transferData.fromAccount}
                      onChange={handleInputChange}
                      required
                    >
                      <option value="">Select account</option>
                      {accounts.map(account => (
                        <option key={account.id} value={account.id}>
                          {account.account_name} - {formatCurrency(account.available_balance, account.currency)}
                        </option>
                      ))}
                    </select>
                    {validationErrors.fromAccount && (
                      <div className="invalid-feedback">
                        {validationErrors.fromAccount.errors.map((error, index) => (
                          <div key={index}>{error}</div>
                        ))}
                      </div>
                    )}
                  </div>

                  <div className="col-md-6 mb-3">
                    <label htmlFor="transferType" className="form-label">Transfer Type</label>
                    <select
                      className="form-select"
                      id="transferType"
                      name="transferType"
                      value={transferData.transferType}
                      onChange={handleInputChange}
                    >
                      <option value="internal">Internal Transfer</option>
                      <option value="external">External Transfer</option>
                      <option value="wire">Wire Transfer</option>
                    </select>
                  </div>
                </div>

                <div className="mb-3">
                  <label htmlFor="toAccount" className="form-label">
                    {transferData.transferType === 'internal' ? 'To Account' : 'Beneficiary/Account'}
                  </label>
                  {transferData.transferType === 'internal' ? (
                    <select
                      className={`form-select ${validationErrors.toAccount ? 'is-invalid' : ''}`}
                      id="toAccount"
                      name="toAccount"
                      value={transferData.toAccount}
                      onChange={handleInputChange}
                      required
                    >
                      <option value="">Select account</option>
                      {accounts.map(account => (
                        <option key={account.id} value={account.id}>
                          {account.account_name} ({account.account_number})
                        </option>
                      ))}
                    </select>
                  ) : (
                    <select
                      className={`form-select ${validationErrors.toAccount ? 'is-invalid' : ''}`}
                      id="toAccount"
                      name="toAccount"
                      value={transferData.toAccount}
                      onChange={handleInputChange}
                      required
                    >
                      <option value="">Select beneficiary</option>
                      {beneficiaries.map(beneficiary => (
                        <option key={beneficiary.id} value={beneficiary.account_number}>
                          {beneficiary.name} - {beneficiary.bank_name}
                        </option>
                      ))}
                    </select>
                  )}
                  {validationErrors.toAccount && (
                    <div className="invalid-feedback">
                      {validationErrors.toAccount.errors.map((error, index) => (
                        <div key={index}>{error}</div>
                      ))}
                    </div>
                  )}
                </div>

                <div className="row">
                  <div className="col-md-6 mb-3">
                    <label htmlFor="amount" className="form-label">Amount</label>
                    <div className="input-group">
                      <span className="input-group-text">$</span>
                      <input
                        type="number"
                        className={`form-control ${validationErrors.amount ? 'is-invalid' : ''}`}
                        id="amount"
                        name="amount"
                        value={transferData.amount}
                        onChange={handleInputChange}
                        placeholder="0.00"
                        step="0.01"
                        min="0.01"
                        required
                      />
                    </div>
                    {validationErrors.amount && (
                      <div className="invalid-feedback">
                        {validationErrors.amount.errors.map((error, index) => (
                          <div key={index}>{error}</div>
                        ))}
                      </div>
                    )}
                  </div>

                  <div className="col-md-6 mb-3">
                    <label htmlFor="description" className="form-label">Description</label>
                    <input
                      type="text"
                      className={`form-control ${validationErrors.description ? 'is-invalid' : ''}`}
                      id="description"
                      name="description"
                      value={transferData.description}
                      onChange={handleInputChange}
                      placeholder="Payment description"
                      maxLength="100"
                      required
                    />
                    {validationErrors.description && (
                      <div className="invalid-feedback">
                        {validationErrors.description.errors.map((error, index) => (
                          <div key={index}>{error}</div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>

                <div className="d-flex justify-content-between">
                  <button
                    type="button"
                    className="btn btn-outline-secondary"
                    onClick={() => setTransferData({
                      fromAccount: '',
                      toAccount: '',
                      amount: '',
                      description: '',
                      transferType: 'internal'
                    })}
                  >
                    Clear Form
                  </button>
                  <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={loading}
                  >
                    {loading ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                        Processing...
                      </>
                    ) : (
                      <>
                        <i className="fas fa-paper-plane me-2"></i>
                        Send Transfer
                      </>
                    )}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>

        {/* Quick Transfer Options */}
        <div className="col-lg-4 mb-4">
          <div className="card">
            <div className="card-header">
              <h6 className="mb-0">Quick Actions</h6>
            </div>
            <div className="card-body">
              <div className="d-grid gap-2">
                <button className="btn btn-outline-primary btn-sm">
                  <i className="fas fa-plus me-2"></i>Add Beneficiary
                </button>
                <button className="btn btn-outline-success btn-sm">
                  <i className="fas fa-schedule me-2"></i>Schedule Transfer
                </button>
                <button className="btn btn-outline-info btn-sm">
                  <i className="fas fa-history me-2"></i>Transfer Templates
                </button>
                <button className="btn btn-outline-warning btn-sm">
                  <i className="fas fa-download me-2"></i>Export History
                </button>
              </div>
            </div>
          </div>

          {/* Account Balances */}
          <div className="card mt-3">
            <div className="card-header">
              <h6 className="mb-0">Account Balances</h6>
            </div>
            <div className="card-body">
              {accounts.length > 0 ? (
                accounts.map(account => (
                  <div key={account.id} className="d-flex justify-content-between align-items-center mb-2">
                    <div>
                      <small className="text-muted">{account.account_name}</small>
                      <div className="small">{account.account_type}</div>
                    </div>
                    <div className="text-end">
                      <strong>{formatCurrency(account.available_balance, account.currency)}</strong>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-muted mb-0">No accounts available</p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Transfer History */}
      <div className="row">
        <div className="col-12">
          <div className="card">
            <div className="card-header d-flex justify-content-between align-items-center">
              <h5 className="mb-0">Transfer History</h5>
              <div className="btn-group btn-group-sm">
                <button className="btn btn-outline-primary">Filter</button>
                <button className="btn btn-outline-secondary">Export</button>
              </div>
            </div>
            <div className="card-body">
              {transferHistory.length > 0 ? (
                <div className="table-responsive">
                  <table className="table table-hover">
                    <thead>
                      <tr>
                        <th>Date</th>
                        <th>Type</th>
                        <th>From</th>
                        <th>To</th>
                        <th>Description</th>
                        <th className="text-end">Amount</th>
                        <th>Status</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {transferHistory.map(transfer => (
                        <tr key={transfer.id}>
                          <td>{formatDate(transfer.created_at)}</td>
                          <td>
                            <span className="badge bg-secondary">
                              {transfer.transfer_type}
                            </span>
                          </td>
                          <td>
                            <div className="small">
                              {transfer.from_account_name}
                              <div className="text-muted">{transfer.from_account_number}</div>
                            </div>
                          </td>
                          <td>
                            <div className="small">
                              {transfer.to_account_name || transfer.beneficiary_name}
                              <div className="text-muted">{transfer.to_account_number}</div>
                            </div>
                          </td>
                          <td>{transfer.description}</td>
                          <td className="text-end">
                            <strong>{formatCurrency(transfer.amount, transfer.currency)}</strong>
                          </td>
                          <td>
                            <span className={`badge ${
                              transfer.status === 'completed' ? 'bg-success' :
                              transfer.status === 'pending' ? 'bg-warning' :
                              transfer.status === 'failed' ? 'bg-danger' :
                              'bg-secondary'
                            }`}>
                              {transfer.status}
                            </span>
                          </td>
                          <td>
                            <div className="btn-group btn-group-sm">
                              <button className="btn btn-outline-primary btn-sm">
                                <i className="fas fa-eye"></i>
                              </button>
                              <button className="btn btn-outline-secondary btn-sm">
                                <i className="fas fa-receipt"></i>
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="text-center py-4">
                  <i className="fas fa-exchange-alt fa-3x text-muted mb-3"></i>
                  <p className="text-muted">No transfer history available</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* No Accounts Modal */}
      {showNoAccountsModal && (
        <div className="modal show d-block" tabIndex="-1" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog modal-dialog-centered">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">
                  <i className="fas fa-plus-circle me-2 text-primary"></i>Create Account Required
                </h5>
                <button
                  type="button"
                  className="btn-close"
                  onClick={() => setShowNoAccountsModal(false)}
                ></button>
              </div>
              <div className="modal-body">
                <div className="text-center mb-3">
                  <i className="fas fa-bank fa-4x text-muted mb-3"></i>
                  <h6>No Active Accounts Found</h6>
                  <p className="text-muted">
                    To make transfers, you need to create at least one bank account. 
                    Would you like to create an account now?
                  </p>
                </div>
                
                <div className="card bg-light">
                  <div className="card-body">
                    <h6 className="card-title">
                      <i className="fas fa-info-circle me-2"></i>Account Benefits
                    </h6>
                    <ul className="mb-0">
                      <li>FDIC insured up to $250,000</li>
                      <li>Instant transfers between accounts</li>
                      <li>Multiple currency support</li>
                      <li>Zero minimum balance requirement</li>
                    </ul>
                  </div>
                </div>
              </div>
              <div className="modal-footer">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setShowNoAccountsModal(false)}
                >
                  <i className="fas fa-times me-2"></i>Maybe Later
                </button>
                <button
                  type="button"
                  className="btn btn-primary"
                  onClick={handleCreateAccount}
                >
                  <i className="fas fa-plus-circle me-2"></i>Create Account Now
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TransfersPage;