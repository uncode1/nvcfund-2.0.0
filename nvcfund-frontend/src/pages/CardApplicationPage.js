import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { useErrorHandler } from '../hooks/useErrorHandler';
import api from '../services/api';
import SecurityManager from '../security/SecurityManager';
import InputValidator from '../security/InputValidator';

const CardApplicationPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { } = useErrorHandler(); // Available for future error handling
  
  const [applicationData, setApplicationData] = useState({
    cardType: 'debit',
    cardNetwork: 'visa',
    accountId: '',
    annualIncome: '',
    employmentStatus: 'employed',
    employerName: '',
    workExperience: '1-2',
    requestedLimit: '',
    cardPurpose: 'personal',
    additionalFeatures: []
  });
  
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [validationErrors, setValidationErrors] = useState({});
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');
  const [selectedFeatures, setSelectedFeatures] = useState([]);
  const [eligibility, setEligibility] = useState(null);
  const [kycRequired, setKycRequired] = useState(false);

  const securityManager = new SecurityManager();
  // InputValidator available for future form validation

  // Card types and networks
  const cardTypes = [
    { value: 'debit', label: 'Debit Card', description: 'Direct access to your account funds' },
    { value: 'credit', label: 'Credit Card', description: 'Line of credit for purchases and cash advances' },
    { value: 'prepaid', label: 'Prepaid Card', description: 'Load funds in advance for controlled spending' }
  ];

  const cardNetworks = [
    { value: 'visa', label: 'Visa', description: 'Accepted worldwide at millions of locations' },
    { value: 'mastercard', label: 'Mastercard', description: 'Global acceptance with premium benefits' },
    { value: 'american_express', label: 'American Express', description: 'Premium rewards and exclusive perks' },
    { value: 'discover', label: 'Discover', description: 'Cashback rewards and no foreign transaction fees' }
  ];

  // Payment integrations
  const paymentIntegrations = [
    { value: 'paypal', label: 'PayPal Integration', description: 'Link to PayPal for seamless online payments' },
    { value: 'apple_pay', label: 'Apple Pay', description: 'Contactless payments on Apple devices' },
    { value: 'google_pay', label: 'Google Pay', description: 'Contactless payments on Android devices' },
    { value: 'samsung_pay', label: 'Samsung Pay', description: 'Mobile payments on Samsung devices' },
    { value: 'flutterwave', label: 'Flutterwave', description: 'African payment gateway integration' },
    { value: 'stripe', label: 'Stripe', description: 'Global payment processing integration' }
  ];

  // Card features
  const cardFeatures = [
    { value: 'contactless', label: 'Contactless Payments', description: 'Tap-to-pay technology' },
    { value: 'cashback', label: 'Cashback Rewards', description: 'Earn money back on purchases' },
    { value: 'travel_insurance', label: 'Travel Insurance', description: 'Coverage for travel-related incidents' },
    { value: 'fraud_protection', label: 'Enhanced Fraud Protection', description: 'Advanced security monitoring' },
    { value: 'virtual_card', label: 'Virtual Card Numbers', description: 'Generate virtual cards for online shopping' },
    { value: 'expense_tracking', label: 'Expense Tracking', description: 'Categorize and track spending' }
  ];

  const employmentStatuses = [
    { value: 'employed', label: 'Employed' },
    { value: 'self_employed', label: 'Self-Employed' },
    { value: 'student', label: 'Student' },
    { value: 'retired', label: 'Retired' },
    { value: 'unemployed', label: 'Unemployed' }
  ];

  const workExperienceOptions = [
    { value: '0-1', label: '0-1 years' },
    { value: '1-2', label: '1-2 years' },
    { value: '2-5', label: '2-5 years' },
    { value: '5-10', label: '5-10 years' },
    { value: '10+', label: '10+ years' }
  ];

  useEffect(() => {
    checkKYCEligibility();
    fetchUserAccounts();
  }, []);

  const checkKYCEligibility = async () => {
    try {
      const response = await api.get('/banking/card-eligibility');
      if (response.status === 'success') {
        setEligibility(response.data);
        setKycRequired(!response.data.eligible_for_cards);
        
        if (!response.data.eligible_for_cards) {
          setError(`KYC verification required: ${response.data.eligibility_reason}`);
        }
      }
    } catch (err) {
      console.error('Failed to check KYC eligibility:', err);
      setKycRequired(true);
      setError('Unable to verify KYC status. Please complete KYC verification to apply for cards.');
    }
  };

  const fetchUserAccounts = async () => {
    try {
      const response = await api.getAccounts();
      if (response.status === 'success') {
        setAccounts(response.data || []);
        
        // Set the first account as default if available
        if (response.data && response.data.length > 0 && !applicationData.accountId) {
          setApplicationData(prev => ({ ...prev, accountId: response.data[0].id }));
        }
      }
    } catch (err) {
      console.error('Failed to fetch accounts:', err);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setApplicationData(prev => ({ ...prev, [name]: value }));
    
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

  const handleFeatureChange = (featureValue) => {
    setSelectedFeatures(prev => {
      const updated = prev.includes(featureValue)
        ? prev.filter(f => f !== featureValue)
        : [...prev, featureValue];
      
      setApplicationData(prevData => ({
        ...prevData,
        additionalFeatures: updated
      }));
      
      return updated;
    });
  };

  const validateForm = () => {
    const errors = {};
    
    // Validate account selection
    if (!applicationData.accountId) {
      errors.accountId = { isValid: false, errors: ['Please select an account'] };
    }

    // Validate annual income for credit cards
    if (applicationData.cardType === 'credit') {
      if (!applicationData.annualIncome) {
        errors.annualIncome = { isValid: false, errors: ['Annual income is required for credit cards'] };
      } else if (parseFloat(applicationData.annualIncome) < 15000) {
        errors.annualIncome = { isValid: false, errors: ['Minimum annual income of $15,000 required'] };
      }

      if (!applicationData.employerName.trim()) {
        errors.employerName = { isValid: false, errors: ['Employer name is required for credit cards'] };
      }

      if (!applicationData.requestedLimit) {
        errors.requestedLimit = { isValid: false, errors: ['Requested credit limit is required'] };
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
        event_type: 'card_application_attempt',
        user_id: user?.id,
        details: {
          card_type: applicationData.cardType,
          card_network: applicationData.cardNetwork,
          timestamp: new Date().toISOString()
        }
      });

      const response = await api.submitCardApplication({
        ...applicationData,
        additional_features: selectedFeatures
      });

      if (response.status === 'success') {
        setSuccess(`Card application submitted successfully! Application ID: ${response.data?.application_id}`);
        
        // Report successful application
        await securityManager.reportSecurityEvent({
          event_type: 'card_application_submitted',
          user_id: user?.id,
          details: {
            application_id: response.data?.application_id,
            card_type: applicationData.cardType,
            timestamp: new Date().toISOString()
          }
        });

        // Reset form after delay
        setTimeout(() => {
          navigate('/cards');
        }, 3000);
      } else {
        setError(response.error || 'Card application failed');
      }
    } catch (err) {
      console.error('Card application error:', err);
      setError('Service temporarily unavailable. Please try again later.');
      
      // Report failed application
      await securityManager.reportSecurityEvent({
        event_type: 'card_application_failed',
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

  const getSelectedAccount = () => {
    return accounts.find(account => account.id === applicationData.accountId);
  };

  return (
    <div className="container-fluid py-4">
      <div className="row justify-content-center">
        <div className="col-lg-10">
          <div className="card">
            <div className="card-header bg-primary text-white">
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <h4 className="mb-0">
                    <i className="fas fa-credit-card me-2"></i>Card Application
                  </h4>
                  <small>Apply for debit, credit, or prepaid cards</small>
                </div>
                <button
                  type="button"
                  className="btn btn-light btn-sm"
                  onClick={() => navigate('/cards')}
                >
                  <i className="fas fa-arrow-left me-2"></i>Back to Cards
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
                {/* Card Type and Network Selection */}
                <div className="row mb-4">
                  <div className="col-md-6">
                    <label htmlFor="cardType" className="form-label">Card Type</label>
                    <select
                      className="form-select"
                      id="cardType"
                      name="cardType"
                      value={applicationData.cardType}
                      onChange={handleInputChange}
                      required
                    >
                      {cardTypes.map(type => (
                        <option key={type.value} value={type.value}>
                          {type.label}
                        </option>
                      ))}
                    </select>
                    <div className="form-text">
                      {cardTypes.find(t => t.value === applicationData.cardType)?.description}
                    </div>
                  </div>
                  
                  <div className="col-md-6">
                    <label htmlFor="cardNetwork" className="form-label">Card Network</label>
                    <select
                      className="form-select"
                      id="cardNetwork"
                      name="cardNetwork"
                      value={applicationData.cardNetwork}
                      onChange={handleInputChange}
                      required
                    >
                      {cardNetworks.map(network => (
                        <option key={network.value} value={network.value}>
                          {network.label}
                        </option>
                      ))}
                    </select>
                    <div className="form-text">
                      {cardNetworks.find(n => n.value === applicationData.cardNetwork)?.description}
                    </div>
                  </div>
                </div>

                {/* Account Selection */}
                <div className="mb-4">
                  <label htmlFor="accountId" className="form-label">Link to Account</label>
                  <select
                    className={`form-select ${validationErrors.accountId ? 'is-invalid' : ''}`}
                    id="accountId"
                    name="accountId"
                    value={applicationData.accountId}
                    onChange={handleInputChange}
                    required
                  >
                    <option value="">Select account to link</option>
                    {accounts.map(account => (
                      <option key={account.id} value={account.id}>
                        {account.account_name} ({account.currency}) - Balance: {account.balance || '0.00'}
                      </option>
                    ))}
                  </select>
                  {validationErrors.accountId && (
                    <div className="invalid-feedback">
                      {validationErrors.accountId.errors?.join(', ')}
                    </div>
                  )}
                </div>

                {/* Credit Card Specific Fields */}
                {applicationData.cardType === 'credit' && (
                  <div className="card border-warning mb-4">
                    <div className="card-header bg-warning text-dark">
                      <h6 className="mb-0">
                        <i className="fas fa-info-circle me-2"></i>Credit Card Information
                      </h6>
                    </div>
                    <div className="card-body">
                      <div className="row">
                        <div className="col-md-6 mb-3">
                          <label htmlFor="annualIncome" className="form-label">Annual Income</label>
                          <div className="input-group">
                            <span className="input-group-text">$</span>
                            <input
                              type="number"
                              className={`form-control ${validationErrors.annualIncome ? 'is-invalid' : ''}`}
                              id="annualIncome"
                              name="annualIncome"
                              value={applicationData.annualIncome}
                              onChange={handleInputChange}
                              placeholder="50000"
                              min="15000"
                              step="1000"
                              required
                            />
                            {validationErrors.annualIncome && (
                              <div className="invalid-feedback">
                                {validationErrors.annualIncome.errors?.join(', ')}
                              </div>
                            )}
                          </div>
                        </div>
                        
                        <div className="col-md-6 mb-3">
                          <label htmlFor="requestedLimit" className="form-label">Requested Credit Limit</label>
                          <div className="input-group">
                            <span className="input-group-text">$</span>
                            <input
                              type="number"
                              className={`form-control ${validationErrors.requestedLimit ? 'is-invalid' : ''}`}
                              id="requestedLimit"
                              name="requestedLimit"
                              value={applicationData.requestedLimit}
                              onChange={handleInputChange}
                              placeholder="5000"
                              min="500"
                              step="500"
                              required
                            />
                            {validationErrors.requestedLimit && (
                              <div className="invalid-feedback">
                                {validationErrors.requestedLimit.errors?.join(', ')}
                              </div>
                            )}
                          </div>
                        </div>
                        
                        <div className="col-md-6 mb-3">
                          <label htmlFor="employmentStatus" className="form-label">Employment Status</label>
                          <select
                            className="form-select"
                            id="employmentStatus"
                            name="employmentStatus"
                            value={applicationData.employmentStatus}
                            onChange={handleInputChange}
                            required
                          >
                            {employmentStatuses.map(status => (
                              <option key={status.value} value={status.value}>
                                {status.label}
                              </option>
                            ))}
                          </select>
                        </div>
                        
                        <div className="col-md-6 mb-3">
                          <label htmlFor="employerName" className="form-label">Employer Name</label>
                          <input
                            type="text"
                            className={`form-control ${validationErrors.employerName ? 'is-invalid' : ''}`}
                            id="employerName"
                            name="employerName"
                            value={applicationData.employerName}
                            onChange={handleInputChange}
                            placeholder="Company Name"
                            required
                          />
                          {validationErrors.employerName && (
                            <div className="invalid-feedback">
                              {validationErrors.employerName.errors?.join(', ')}
                            </div>
                          )}
                        </div>
                        
                        <div className="col-md-6 mb-3">
                          <label htmlFor="workExperience" className="form-label">Work Experience</label>
                          <select
                            className="form-select"
                            id="workExperience"
                            name="workExperience"
                            value={applicationData.workExperience}
                            onChange={handleInputChange}
                            required
                          >
                            {workExperienceOptions.map(exp => (
                              <option key={exp.value} value={exp.value}>
                                {exp.label}
                              </option>
                            ))}
                          </select>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Payment Integration Features */}
                <div className="mb-4">
                  <h6 className="mb-3">Payment Integration Options</h6>
                  <div className="row">
                    {paymentIntegrations.map(integration => (
                      <div key={integration.value} className="col-md-6 mb-3">
                        <div className="card border-info">
                          <div className="card-body">
                            <div className="form-check">
                              <input
                                className="form-check-input"
                                type="checkbox"
                                id={integration.value}
                                checked={selectedFeatures.includes(integration.value)}
                                onChange={() => handleFeatureChange(integration.value)}
                              />
                              <label className="form-check-label" htmlFor={integration.value}>
                                <strong>{integration.label}</strong>
                                <br />
                                <small className="text-muted">{integration.description}</small>
                              </label>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Additional Features */}
                <div className="mb-4">
                  <h6 className="mb-3">Additional Card Features</h6>
                  <div className="row">
                    {cardFeatures.map(feature => (
                      <div key={feature.value} className="col-md-6 mb-3">
                        <div className="card border-success">
                          <div className="card-body">
                            <div className="form-check">
                              <input
                                className="form-check-input"
                                type="checkbox"
                                id={feature.value}
                                checked={selectedFeatures.includes(feature.value)}
                                onChange={() => handleFeatureChange(feature.value)}
                              />
                              <label className="form-check-label" htmlFor={feature.value}>
                                <strong>{feature.label}</strong>
                                <br />
                                <small className="text-muted">{feature.description}</small>
                              </label>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Application Summary */}
                {applicationData.accountId && (
                  <div className="alert alert-light mb-4">
                    <h6><i className="fas fa-clipboard-list me-2"></i>Application Summary</h6>
                    <ul className="mb-0">
                      <li><strong>Card Type:</strong> {cardTypes.find(t => t.value === applicationData.cardType)?.label}</li>
                      <li><strong>Network:</strong> {cardNetworks.find(n => n.value === applicationData.cardNetwork)?.label}</li>
                      <li><strong>Linked Account:</strong> {getSelectedAccount()?.account_name}</li>
                      {applicationData.cardType === 'credit' && (
                        <>
                          <li><strong>Annual Income:</strong> ${applicationData.annualIncome}</li>
                          <li><strong>Requested Limit:</strong> ${applicationData.requestedLimit}</li>
                        </>
                      )}
                      <li><strong>Selected Features:</strong> {selectedFeatures.length} features selected</li>
                    </ul>
                  </div>
                )}

                {/* Submit Button */}
                <div className="d-flex justify-content-between">
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={() => navigate('/cards')}
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
                        Submitting Application...
                      </>
                    ) : (
                      <>
                        <i className="fas fa-paper-plane me-2"></i>
                        Submit Application
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

export default CardApplicationPage;