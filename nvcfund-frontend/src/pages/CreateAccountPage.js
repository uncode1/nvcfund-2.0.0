import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import api from '../services/api';
import { InputValidator } from '../security/InputValidator';
import { SecurityManager } from '../security/SecurityManager';

const CreateAccountPage = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [validationErrors, setValidationErrors] = useState({});
  
  const [accountData, setAccountData] = useState({
    accountType: 'checking',
    accountName: '',
    initialDeposit: '',
    currency: 'USD'
  });

  const securityManager = new SecurityManager();
  const validator = new InputValidator();

  const accountTypes = [
    { value: 'checking', label: 'Checking Account', description: 'For everyday transactions and bill payments' },
    { value: 'savings', label: 'Savings Account', description: 'Earn interest on your deposits' },
    { value: 'business', label: 'Business Account', description: 'For business banking needs' },
    { value: 'investment', label: 'Investment Account', description: 'For trading and investment activities' },
    { value: 'digital_wallet', label: 'Digital Wallet', description: 'For cryptocurrency and digital asset storage' },
    { value: 'stablecoin_wallet', label: 'NVCT Stablecoin Wallet', description: 'Dedicated wallet for NVCT stablecoin transactions' },
    { value: 'exchange_account', label: 'Exchange Account', description: 'For fiat-to-digital and digital-to-fiat exchanges' }
  ];

  const currencies = [
    { value: 'USD', label: 'US Dollar (USD)' },
    { value: 'EUR', label: 'Euro (EUR)' },
    { value: 'GBP', label: 'British Pound (GBP)' },
    { value: 'NVCT', label: 'NVC Token (NVCT)' },
    { value: 'BTC', label: 'Bitcoin (BTC)' },
    { value: 'ETH', label: 'Ethereum (ETH)' },
    { value: 'USDC', label: 'USD Coin (USDC)' },
    { value: 'USDT', label: 'Tether (USDT)' }
  ];

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setAccountData(prev => ({ ...prev, [name]: value }));
    
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

  const validateForm = () => {
    const errors = {};
    
    // Validate account name
    if (!accountData.accountName.trim()) {
      errors.accountName = { isValid: false, errors: ['Account name is required'] };
    } else if (accountData.accountName.length < 3) {
      errors.accountName = { isValid: false, errors: ['Account name must be at least 3 characters'] };
    }

    // Validate initial deposit if provided
    if (accountData.initialDeposit) {
      const amountValidation = validator.validateAmount(accountData.initialDeposit);
      if (!amountValidation.isValid) {
        errors.initialDeposit = amountValidation;
      }
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      // Report security event
      await securityManager.reportSecurityEvent({
        event_type: 'account_creation_attempt',
        user_id: user?.id,
        details: {
          account_type: accountData.accountType,
          currency: accountData.currency,
          timestamp: new Date().toISOString()
        }
      });

      const response = await api.createAccount({
        account_type: accountData.accountType,
        account_name: accountData.accountName,
        initial_deposit: accountData.initialDeposit || '0',
        currency: accountData.currency
      });

      if (response.status === 'success') {
        setSuccess('Account created successfully!');
        
        // Report successful account creation
        await securityManager.reportSecurityEvent({
          event_type: 'account_created',
          user_id: user?.id,
          details: {
            account_id: response.data?.account_id,
            account_type: accountData.accountType,
            timestamp: new Date().toISOString()
          }
        });

        // Redirect after success
        setTimeout(() => {
          const urlParams = new URLSearchParams(window.location.search);
          const redirectTo = urlParams.get('redirect');
          
          if (redirectTo === 'transfer') {
            navigate(`/transfers?from=${response.data?.account_id}`);
          } else {
            navigate('/accounts');
          }
        }, 2000);
      } else {
        setError(response.error || 'Failed to create account');
      }
    } catch (err) {
      console.error('Account creation error:', err);
      setError('Service temporarily unavailable. Please try again later.');
      
      // Report failed creation attempt
      await securityManager.reportSecurityEvent({
        event_type: 'account_creation_failed',
        user_id: user?.id,
        details: {
          error: 'API_ERROR',
          timestamp: new Date().toISOString()
        }
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    const urlParams = new URLSearchParams(window.location.search);
    const redirectTo = urlParams.get('redirect');
    
    if (redirectTo === 'transfer') {
      navigate('/transfers');
    } else {
      navigate('/dashboard');
    }
  };

  return (
    <div className="container-fluid py-4">
      <div className="row justify-content-center">
        <div className="col-lg-8">
          <div className="card">
            <div className="card-header bg-primary text-white">
              <h2 className="h4 mb-0">
                <i className="fas fa-plus-circle me-2"></i>Create New Account
              </h2>
            </div>
            <div className="card-body">
              {error && (
                <div className="alert alert-danger" role="alert">
                  <i className="fas fa-exclamation-triangle me-2"></i>
                  {error}
                </div>
              )}
              
              {success && (
                <div className="alert alert-success" role="alert">
                  <i className="fas fa-check-circle me-2"></i>
                  {success}
                </div>
              )}

              <form onSubmit={handleSubmit}>
                <div className="row">
                  <div className="col-md-6 mb-3">
                    <label htmlFor="accountType" className="form-label">Account Type</label>
                    <select
                      className="form-select"
                      id="accountType"
                      name="accountType"
                      value={accountData.accountType}
                      onChange={handleInputChange}
                      required
                    >
                      {accountTypes.map(type => (
                        <option key={type.value} value={type.value}>
                          {type.label}
                        </option>
                      ))}
                    </select>
                    <div className="form-text">
                      {accountTypes.find(t => t.value === accountData.accountType)?.description}
                    </div>
                  </div>

                  <div className="col-md-6 mb-3">
                    <label htmlFor="currency" className="form-label">Currency</label>
                    <select
                      className="form-select"
                      id="currency"
                      name="currency"
                      value={accountData.currency}
                      onChange={handleInputChange}
                      required
                    >
                      {currencies.map(currency => (
                        <option key={currency.value} value={currency.value}>
                          {currency.label}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="mb-3">
                  <label htmlFor="accountName" className="form-label">Account Name</label>
                  <input
                    type="text"
                    className={`form-control ${validationErrors.accountName ? 'is-invalid' : ''}`}
                    id="accountName"
                    name="accountName"
                    value={accountData.accountName}
                    onChange={handleInputChange}
                    placeholder="Enter a name for your account"
                    required
                  />
                  {validationErrors.accountName && (
                    <div className="invalid-feedback">
                      {validationErrors.accountName.errors?.join(', ')}
                    </div>
                  )}
                </div>

                <div className="mb-3">
                  <label htmlFor="initialDeposit" className="form-label">Initial Deposit (Optional)</label>
                  <div className="input-group">
                    <span className="input-group-text">
                      {accountData.currency === 'NVCT' ? 'NVCT' : '$'}
                    </span>
                    <input
                      type="number"
                      className={`form-control ${validationErrors.initialDeposit ? 'is-invalid' : ''}`}
                      id="initialDeposit"
                      name="initialDeposit"
                      value={accountData.initialDeposit}
                      onChange={handleInputChange}
                      placeholder="0.00"
                      min="0"
                      step="0.01"
                    />
                    {validationErrors.initialDeposit && (
                      <div className="invalid-feedback">
                        {validationErrors.initialDeposit.errors?.join(', ')}
                      </div>
                    )}
                  </div>
                  <div className="form-text">
                    You can add funds to your account later if you prefer to start with zero balance.
                  </div>
                </div>

                <div className="d-flex justify-content-between">
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={handleCancel}
                    disabled={loading}
                  >
                    <i className="fas fa-times me-2"></i>Cancel
                  </button>
                  
                  <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={loading}
                  >
                    {loading ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                        Creating Account...
                      </>
                    ) : (
                      <>
                        <i className="fas fa-plus-circle me-2"></i>Create Account
                      </>
                    )}
                  </button>
                </div>
              </form>
              
              <div className="mt-4">
                <div className="card bg-light">
                  <div className="card-body">
                    <h6 className="card-title">
                      <i className="fas fa-info-circle me-2"></i>Account Information
                    </h6>
                    <ul className="mb-0">
                      <li>All accounts are FDIC insured up to $250,000</li>
                      <li>NVCT accounts are backed by verified collateral assets</li>
                      <li>Business accounts may require additional verification</li>
                      <li>You can create multiple accounts for different purposes</li>
                    </ul>
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

export default CreateAccountPage;