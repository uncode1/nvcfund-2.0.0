import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { useErrorHandler } from '../hooks/useErrorHandler';
import api from '../services/api';
import SecurityManager from '../security/SecurityManager';
import InputValidator from '../security/InputValidator';

const ExchangePage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { showError } = useErrorHandler();
  
  const [accounts, setAccounts] = useState([]);
  const [exchangeData, setExchangeData] = useState({
    fromAccount: '',
    toAccount: '',
    fromCurrency: 'USD',
    toCurrency: 'NVCT',
    amount: '',
    exchangeType: 'fiat_to_digital'
  });
  
  const [exchangeRate, setExchangeRate] = useState(null);
  const [estimatedAmount, setEstimatedAmount] = useState('0.00');
  const [loading, setLoading] = useState(false);
  const [validationErrors, setValidationErrors] = useState({});
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');
  const [rateLoading, setRateLoading] = useState(false);

  const securityManager = new SecurityManager();
  const validator = new InputValidator();

  // Exchange types with descriptions
  const exchangeTypes = [
    { value: 'fiat_to_digital', label: 'Fiat to Digital', description: 'Convert traditional currency to cryptocurrency' },
    { value: 'digital_to_fiat', label: 'Digital to Fiat', description: 'Convert cryptocurrency to traditional currency' },
    { value: 'digital_to_digital', label: 'Digital to Digital', description: 'Exchange between different cryptocurrencies' }
  ];

  // Currency groups
  const fiatCurrencies = ['USD', 'EUR', 'GBP'];
  const digitalCurrencies = ['NVCT', 'BTC', 'ETH', 'USDC', 'USDT'];
  const allCurrencies = [...fiatCurrencies, ...digitalCurrencies];

  // Currency display names
  const currencyLabels = {
    USD: 'US Dollar',
    EUR: 'Euro',
    GBP: 'British Pound',
    NVCT: 'NVC Token',
    BTC: 'Bitcoin',
    ETH: 'Ethereum',
    USDC: 'USD Coin',
    USDT: 'Tether'
  };

  useEffect(() => {
    fetchUserAccounts();
  }, []);

  useEffect(() => {
    if (exchangeData.amount && exchangeData.fromCurrency && exchangeData.toCurrency) {
      fetchExchangeRate();
    }
  }, [exchangeData.amount, exchangeData.fromCurrency, exchangeData.toCurrency]);

  const fetchUserAccounts = async () => {
    try {
      const response = await api.getAccounts();
      if (response.status === 'success') {
        setAccounts(response.data || []);
      }
    } catch (err) {
      console.error('Failed to fetch accounts:', err);
    }
  };

  const fetchExchangeRate = async () => {
    setRateLoading(true);
    try {
      const response = await api.getExchangeRate({
        from_currency: exchangeData.fromCurrency,
        to_currency: exchangeData.toCurrency,
        amount: exchangeData.amount
      });
      
      if (response.status === 'success') {
        setExchangeRate(response.data.rate);
        setEstimatedAmount(response.data.estimated_amount);
      }
    } catch (err) {
      console.error('Failed to fetch exchange rate:', err);
      setExchangeRate(null);
      setEstimatedAmount('0.00');
    } finally {
      setRateLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    
    if (name === 'exchangeType') {
      // Update currency defaults based on exchange type
      let newFromCurrency = 'USD';
      let newToCurrency = 'NVCT';
      
      if (value === 'digital_to_fiat') {
        newFromCurrency = 'NVCT';
        newToCurrency = 'USD';
      } else if (value === 'digital_to_digital') {
        newFromCurrency = 'BTC';
        newToCurrency = 'ETH';
      }
      
      setExchangeData(prev => ({
        ...prev,
        [name]: value,
        fromCurrency: newFromCurrency,
        toCurrency: newToCurrency
      }));
    } else {
      setExchangeData(prev => ({ ...prev, [name]: value }));
    }
    
    // Clear validation errors
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
    
    // Validate amount
    if (!exchangeData.amount) {
      errors.amount = { isValid: false, errors: ['Amount is required'] };
    } else {
      const amountValidation = validator.validateAmount(exchangeData.amount);
      if (!amountValidation.isValid) {
        errors.amount = amountValidation;
      }
    }

    // Validate accounts
    if (!exchangeData.fromAccount) {
      errors.fromAccount = { isValid: false, errors: ['Source account is required'] };
    }
    
    if (!exchangeData.toAccount) {
      errors.toAccount = { isValid: false, errors: ['Destination account is required'] };
    }

    // Validate currencies are different
    if (exchangeData.fromCurrency === exchangeData.toCurrency) {
      errors.toCurrency = { isValid: false, errors: ['Destination currency must be different from source currency'] };
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
        event_type: 'currency_exchange_attempt',
        user_id: user?.id,
        details: {
          exchange_type: exchangeData.exchangeType,
          from_currency: exchangeData.fromCurrency,
          to_currency: exchangeData.toCurrency,
          amount: exchangeData.amount,
          timestamp: new Date().toISOString()
        }
      });

      const response = await api.createExchange({
        from_account_id: exchangeData.fromAccount,
        to_account_id: exchangeData.toAccount,
        from_currency: exchangeData.fromCurrency,
        to_currency: exchangeData.toCurrency,
        amount: exchangeData.amount,
        exchange_type: exchangeData.exchangeType,
        exchange_rate: exchangeRate
      });

      if (response.status === 'success') {
        setSuccess(`Exchange completed successfully! Transaction ID: ${response.data?.transaction_id}`);
        
        // Report successful exchange
        await securityManager.reportSecurityEvent({
          event_type: 'currency_exchange_completed',
          user_id: user?.id,
          details: {
            transaction_id: response.data?.transaction_id,
            exchange_type: exchangeData.exchangeType,
            timestamp: new Date().toISOString()
          }
        });

        // Reset form
        setExchangeData({
          fromAccount: '',
          toAccount: '',
          fromCurrency: 'USD',
          toCurrency: 'NVCT',
          amount: '',
          exchangeType: 'fiat_to_digital'
        });
        setExchangeRate(null);
        setEstimatedAmount('0.00');
        
        // Refresh accounts
        fetchUserAccounts();
      } else {
        setError(response.error || 'Exchange failed');
      }
    } catch (err) {
      console.error('Exchange error:', err);
      setError('Service temporarily unavailable. Please try again later.');
      
      // Report failed exchange
      await securityManager.reportSecurityEvent({
        event_type: 'currency_exchange_failed',
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

  const getAvailableFromCurrencies = () => {
    switch (exchangeData.exchangeType) {
      case 'fiat_to_digital':
        return fiatCurrencies;
      case 'digital_to_fiat':
        return digitalCurrencies;
      case 'digital_to_digital':
        return digitalCurrencies;
      default:
        return allCurrencies;
    }
  };

  const getAvailableToCurrencies = () => {
    switch (exchangeData.exchangeType) {
      case 'fiat_to_digital':
        return digitalCurrencies;
      case 'digital_to_fiat':
        return fiatCurrencies;
      case 'digital_to_digital':
        return digitalCurrencies.filter(c => c !== exchangeData.fromCurrency);
      default:
        return allCurrencies.filter(c => c !== exchangeData.fromCurrency);
    }
  };

  const getAccountsByCurrency = (currency) => {
    return accounts.filter(account => 
      account.currency === currency || 
      (currency === 'NVCT' && ['stablecoin_wallet', 'digital_wallet', 'exchange_account'].includes(account.account_type)) ||
      (['BTC', 'ETH', 'USDC', 'USDT'].includes(currency) && ['digital_wallet', 'exchange_account'].includes(account.account_type))
    );
  };

  return (
    <div className="container-fluid py-4">
      <div className="row justify-content-center">
        <div className="col-lg-8">
          <div className="card">
            <div className="card-header bg-primary text-white">
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <h4 className="mb-0">
                    <i className="fas fa-exchange-alt me-2"></i>Currency Exchange
                  </h4>
                  <small>Convert between fiat and digital currencies</small>
                </div>
                <button
                  type="button"
                  className="btn btn-light btn-sm"
                  onClick={() => navigate('/dashboard')}
                >
                  <i className="fas fa-arrow-left me-2"></i>Back to Dashboard
                </button>
              </div>
            </div>
            
            <div className="card-body">
              {success && (
                <div className="alert alert-success">
                  <i className="fas fa-check-circle me-2"></i>{success}
                </div>
              )}
              
              {error && (
                <div className="alert alert-danger">
                  <i className="fas fa-exclamation-triangle me-2"></i>{error}
                </div>
              )}

              <form onSubmit={handleSubmit}>
                {/* Exchange Type Selection */}
                <div className="mb-4">
                  <label htmlFor="exchangeType" className="form-label">Exchange Type</label>
                  <select
                    className="form-select"
                    id="exchangeType"
                    name="exchangeType"
                    value={exchangeData.exchangeType}
                    onChange={handleInputChange}
                    required
                  >
                    {exchangeTypes.map(type => (
                      <option key={type.value} value={type.value}>
                        {type.label}
                      </option>
                    ))}
                  </select>
                  <div className="form-text">
                    {exchangeTypes.find(t => t.value === exchangeData.exchangeType)?.description}
                  </div>
                </div>

                <div className="row">
                  {/* From Currency and Account */}
                  <div className="col-md-6 mb-3">
                    <div className="card border-secondary">
                      <div className="card-header bg-light">
                        <h6 className="mb-0">
                          <i className="fas fa-arrow-up me-2"></i>From
                        </h6>
                      </div>
                      <div className="card-body">
                        <div className="mb-3">
                          <label htmlFor="fromCurrency" className="form-label">Currency</label>
                          <select
                            className="form-select"
                            id="fromCurrency"
                            name="fromCurrency"
                            value={exchangeData.fromCurrency}
                            onChange={handleInputChange}
                            required
                          >
                            {getAvailableFromCurrencies().map(currency => (
                              <option key={currency} value={currency}>
                                {currency} - {currencyLabels[currency]}
                              </option>
                            ))}
                          </select>
                        </div>
                        
                        <div className="mb-3">
                          <label htmlFor="fromAccount" className="form-label">Account</label>
                          <select
                            className={`form-select ${validationErrors.fromAccount ? 'is-invalid' : ''}`}
                            id="fromAccount"
                            name="fromAccount"
                            value={exchangeData.fromAccount}
                            onChange={handleInputChange}
                            required
                          >
                            <option value="">Select account</option>
                            {getAccountsByCurrency(exchangeData.fromCurrency).map(account => (
                              <option key={account.id} value={account.id}>
                                {account.account_name} ({account.currency}) - Balance: {account.balance}
                              </option>
                            ))}
                          </select>
                          {validationErrors.fromAccount && (
                            <div className="invalid-feedback">
                              {validationErrors.fromAccount.errors?.join(', ')}
                            </div>
                          )}
                        </div>

                        <div className="mb-0">
                          <label htmlFor="amount" className="form-label">Amount</label>
                          <div className="input-group">
                            <span className="input-group-text">{exchangeData.fromCurrency}</span>
                            <input
                              type="number"
                              className={`form-control ${validationErrors.amount ? 'is-invalid' : ''}`}
                              id="amount"
                              name="amount"
                              value={exchangeData.amount}
                              onChange={handleInputChange}
                              placeholder="0.00"
                              min="0"
                              step="0.01"
                              required
                            />
                            {validationErrors.amount && (
                              <div className="invalid-feedback">
                                {validationErrors.amount.errors?.join(', ')}
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Exchange Rate Display */}
                  <div className="col-md-12 mb-3">
                    <div className="text-center">
                      <div className="d-flex justify-content-center align-items-center my-3">
                        <div className="border rounded-circle p-2 bg-primary text-white">
                          <i className="fas fa-exchange-alt"></i>
                        </div>
                      </div>
                      
                      {rateLoading ? (
                        <div className="text-muted">
                          <span className="spinner-border spinner-border-sm me-2"></span>
                          Fetching exchange rate...
                        </div>
                      ) : exchangeRate ? (
                        <div className="alert alert-info">
                          <strong>Exchange Rate:</strong> 1 {exchangeData.fromCurrency} = {exchangeRate} {exchangeData.toCurrency}
                          <br />
                          <strong>You will receive:</strong> {estimatedAmount} {exchangeData.toCurrency}
                        </div>
                      ) : (
                        <div className="text-muted">Enter amount to see exchange rate</div>
                      )}
                    </div>
                  </div>

                  {/* To Currency and Account */}
                  <div className="col-md-6 mb-3">
                    <div className="card border-success">
                      <div className="card-header bg-light">
                        <h6 className="mb-0">
                          <i className="fas fa-arrow-down me-2"></i>To
                        </h6>
                      </div>
                      <div className="card-body">
                        <div className="mb-3">
                          <label htmlFor="toCurrency" className="form-label">Currency</label>
                          <select
                            className={`form-select ${validationErrors.toCurrency ? 'is-invalid' : ''}`}
                            id="toCurrency"
                            name="toCurrency"
                            value={exchangeData.toCurrency}
                            onChange={handleInputChange}
                            required
                          >
                            {getAvailableToCurrencies().map(currency => (
                              <option key={currency} value={currency}>
                                {currency} - {currencyLabels[currency]}
                              </option>
                            ))}
                          </select>
                          {validationErrors.toCurrency && (
                            <div className="invalid-feedback">
                              {validationErrors.toCurrency.errors?.join(', ')}
                            </div>
                          )}
                        </div>
                        
                        <div className="mb-3">
                          <label htmlFor="toAccount" className="form-label">Account</label>
                          <select
                            className={`form-select ${validationErrors.toAccount ? 'is-invalid' : ''}`}
                            id="toAccount"
                            name="toAccount"
                            value={exchangeData.toAccount}
                            onChange={handleInputChange}
                            required
                          >
                            <option value="">Select account</option>
                            {getAccountsByCurrency(exchangeData.toCurrency).map(account => (
                              <option key={account.id} value={account.id}>
                                {account.account_name} ({account.currency}) - Balance: {account.balance}
                              </option>
                            ))}
                          </select>
                          {validationErrors.toAccount && (
                            <div className="invalid-feedback">
                              {validationErrors.toAccount.errors?.join(', ')}
                            </div>
                          )}
                        </div>

                        <div className="alert alert-light">
                          <strong>Estimated Receive:</strong>
                          <div className="h5 text-success mb-0">
                            {estimatedAmount} {exchangeData.toCurrency}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Exchange Fees Information */}
                <div className="alert alert-info mb-4">
                  <h6><i className="fas fa-info-circle me-2"></i>Exchange Information</h6>
                  <ul className="mb-0">
                    <li>Exchange rate updates every 30 seconds</li>
                    <li>Standard exchange fee: 0.1% of transaction amount</li>
                    <li>Minimum exchange amount: 1 {exchangeData.fromCurrency}</li>
                    <li>Exchange is processed instantly upon confirmation</li>
                  </ul>
                </div>

                {/* Submit Button */}
                <div className="d-flex justify-content-between">
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={() => navigate('/dashboard')}
                    disabled={loading}
                  >
                    <i className="fas fa-times me-2"></i>Cancel
                  </button>
                  
                  <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={loading || !exchangeRate}
                  >
                    {loading ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                        Processing Exchange...
                      </>
                    ) : (
                      <>
                        <i className="fas fa-exchange-alt me-2"></i>
                        Complete Exchange
                      </>
                    )}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ExchangePage;