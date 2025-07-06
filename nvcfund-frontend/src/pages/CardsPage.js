import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { useErrorHandler } from '../hooks/useErrorHandler';
import api from '../services/api';

const CardsPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  // const { user } = useAuth(); // Will be used for user-specific card data
  // const { showError } = useErrorHandler(); // Central error handling is active
  
  const [cards, setCards] = useState([]);
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState({});
  const [activeTab, setActiveTab] = useState('cards');

  useEffect(() => {
    fetchCardsData();
  }, []);

  const fetchCardsData = async () => {
    try {
      setLoading(true);
      const [cardsResponse, applicationsResponse] = await Promise.all([
        api.getUserCards(),
        api.getCardApplications()
      ]);
      
      if (cardsResponse.status === 'success') {
        setCards(cardsResponse.data || []);
      }
      
      if (applicationsResponse.status === 'success') {
        setApplications(applicationsResponse.data || []);
      }
    } catch (err) {
      console.error('Failed to fetch cards data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCardAction = async (cardId, action) => {
    setActionLoading(prev => ({ ...prev, [cardId]: action }));
    
    try {
      const response = await api.updateCardStatus(cardId, action);
      if (response.status === 'success') {
        fetchCardsData(); // Refresh data
      }
    } catch (err) {
      console.error(`Failed to ${action} card:`, err);
    } finally {
      setActionLoading(prev => ({ ...prev, [cardId]: null }));
    }
  };

  const getCardIcon = (network) => {
    const icons = {
      visa: 'fab fa-cc-visa',
      mastercard: 'fab fa-cc-mastercard',
      american_express: 'fab fa-cc-amex',
      discover: 'fab fa-cc-discover',
      paypal: 'fab fa-paypal'
    };
    return icons[network] || 'fas fa-credit-card';
  };

  const getStatusBadge = (status) => {
    const badges = {
      active: 'success',
      blocked: 'danger',
      expired: 'warning',
      pending: 'info',
      approved: 'success',
      rejected: 'danger',
      under_review: 'warning'
    };
    return badges[status] || 'secondary';
  };

  const maskCardNumber = (number) => {
    if (!number) return '**** **** **** ****';
    return number.replace(/\d(?=\d{4})/g, '*');
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
          <div className="d-flex justify-content-between align-items-center mb-4">
            <div>
              <h2><i className="fas fa-credit-card me-2"></i>My Cards</h2>
              <p className="text-muted mb-0">Manage your debit, credit, and prepaid cards</p>
            </div>
            <button
              className="btn btn-primary"
              onClick={() => navigate('/apply-card')}
            >
              <i className="fas fa-plus me-2"></i>Apply for New Card
            </button>
          </div>
        </div>
      </div>

      {/* Active Cards */}
      <div className="row mb-4">
        <div className="col-12">
          <h4 className="mb-3">Active Cards</h4>
          {cards.length === 0 ? (
            <div className="card">
              <div className="card-body text-center py-5">
                <i className="fas fa-credit-card fa-3x text-muted mb-3"></i>
                <h5 className="text-muted">No Cards Found</h5>
                <p className="text-muted">You don't have any cards yet. Apply for your first card to get started.</p>
                <button
                  className="btn btn-primary"
                  onClick={() => navigate('/apply-card')}
                >
                  <i className="fas fa-plus me-2"></i>Apply for Card
                </button>
              </div>
            </div>
          ) : (
            <div className="row">
              {cards.map(card => (
                <div key={card.id} className="col-lg-4 col-md-6 mb-4">
                  <div className="card h-100 card-lift">
                    <div className={`card-header bg-gradient-${card.type === 'credit' ? 'warning' : card.type === 'debit' ? 'primary' : 'info'} text-white`}>
                      <div className="d-flex justify-content-between align-items-center">
                        <div>
                          <h6 className="mb-0 text-white">{card.card_name || `${card.type.charAt(0).toUpperCase() + card.type.slice(1)} Card`}</h6>
                          <small className="text-white-50">{card.network.charAt(0).toUpperCase() + card.network.slice(1)}</small>
                        </div>
                        <i className={`${getCardIcon(card.network)} fa-2x`}></i>
                      </div>
                    </div>
                    
                    <div className="card-body">
                      <div className="mb-3">
                        <h5 className="font-monospace">{maskCardNumber(card.card_number)}</h5>
                        <div className="row text-small">
                          <div className="col-6">
                            <small className="text-muted">Expires</small><br />
                            <strong>{card.expiry_date || '12/28'}</strong>
                          </div>
                          <div className="col-6">
                            <small className="text-muted">Status</small><br />
                            <span className={`badge bg-${getStatusBadge(card.status)}`}>
                              {card.status.charAt(0).toUpperCase() + card.status.slice(1)}
                            </span>
                          </div>
                        </div>
                      </div>
                      
                      {card.type === 'credit' && (
                        <div className="mb-3">
                          <div className="d-flex justify-content-between">
                            <small className="text-muted">Credit Used</small>
                            <small className="text-muted">${card.current_balance || 0} / ${card.credit_limit || 5000}</small>
                          </div>
                          <div className="progress" style={{ height: '6px' }}>
                            <div 
                              className="progress-bar"
                              style={{ width: `${((card.current_balance || 0) / (card.credit_limit || 5000)) * 100}%` }}
                            ></div>
                          </div>
                        </div>
                      )}
                      
                      <div className="row g-2">
                        <div className="col-6">
                          <button 
                            className="btn btn-outline-primary btn-sm w-100"
                            onClick={() => navigate(`/card-details/${card.id}`)}
                          >
                            <i className="fas fa-eye me-1"></i>Details
                          </button>
                        </div>
                        <div className="col-6">
                          {card.status === 'active' ? (
                            <button 
                              className="btn btn-outline-warning btn-sm w-100"
                              onClick={() => handleCardAction(card.id, 'block')}
                              disabled={actionLoading[card.id]}
                            >
                              {actionLoading[card.id] === 'block' ? (
                                <span className="spinner-border spinner-border-sm"></span>
                              ) : (
                                <>
                                  <i className="fas fa-lock me-1"></i>Block
                                </>
                              )}
                            </button>
                          ) : (
                            <button 
                              className="btn btn-outline-success btn-sm w-100"
                              onClick={() => handleCardAction(card.id, 'activate')}
                              disabled={actionLoading[card.id]}
                            >
                              {actionLoading[card.id] === 'activate' ? (
                                <span className="spinner-border spinner-border-sm"></span>
                              ) : (
                                <>
                                  <i className="fas fa-unlock me-1"></i>Activate
                                </>
                              )}
                            </button>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Payment Integration Status */}
      <div className="row mb-4">
        <div className="col-12">
          <h4 className="mb-3">Payment Integration Status</h4>
          <div className="row">
            <div className="col-lg-3 col-md-6 mb-3">
              <div className="card border-success">
                <div className="card-body text-center">
                  <i className="fab fa-paypal fa-2x text-success mb-2"></i>
                  <h6>PayPal</h6>
                  <span className="badge bg-success">Connected</span>
                </div>
              </div>
            </div>
            <div className="col-lg-3 col-md-6 mb-3">
              <div className="card border-success">
                <div className="card-body text-center">
                  <i className="fab fa-apple fa-2x text-success mb-2"></i>
                  <h6>Apple Pay</h6>
                  <span className="badge bg-success">Connected</span>
                </div>
              </div>
            </div>
            <div className="col-lg-3 col-md-6 mb-3">
              <div className="card border-warning">
                <div className="card-body text-center">
                  <i className="fab fa-google fa-2x text-warning mb-2"></i>
                  <h6>Google Pay</h6>
                  <span className="badge bg-warning">Pending</span>
                </div>
              </div>
            </div>
            <div className="col-lg-3 col-md-6 mb-3">
              <div className="card border-info">
                <div className="card-body text-center">
                  <i className="fas fa-credit-card fa-2x text-info mb-2"></i>
                  <h6>Flutterwave</h6>
                  <span className="badge bg-info">Available</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Applications */}
      {applications.length > 0 && (
        <div className="row">
          <div className="col-12">
            <h4 className="mb-3">Recent Applications</h4>
            <div className="card">
              <div className="card-body">
                <div className="table-responsive">
                  <table className="table table-hover">
                    <thead>
                      <tr>
                        <th>Application ID</th>
                        <th>Card Type</th>
                        <th>Network</th>
                        <th>Status</th>
                        <th>Applied Date</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {applications.map(application => (
                        <tr key={application.id}>
                          <td className="font-monospace">{application.application_id}</td>
                          <td>
                            <span className="text-capitalize">{application.card_type}</span>
                          </td>
                          <td>
                            <i className={`${getCardIcon(application.card_network)} me-2`}></i>
                            {application.card_network.charAt(0).toUpperCase() + application.card_network.slice(1)}
                          </td>
                          <td>
                            <span className={`badge bg-${getStatusBadge(application.status)}`}>
                              {application.status.replace('_', ' ').charAt(0).toUpperCase() + application.status.replace('_', ' ').slice(1)}
                            </span>
                          </td>
                          <td>{new Date(application.created_at).toLocaleDateString()}</td>
                          <td>
                            <button 
                              className="btn btn-outline-primary btn-sm"
                              onClick={() => navigate(`/application-details/${application.id}`)}
                            >
                              <i className="fas fa-eye me-1"></i>View
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="row mt-4">
        <div className="col-12">
          <h4 className="mb-3">Quick Actions</h4>
          <div className="row">
            <div className="col-lg-3 col-md-6 mb-3">
              <button 
                className="btn btn-outline-primary w-100 p-3"
                onClick={() => navigate('/apply-card')}
              >
                <i className="fas fa-plus fa-2x mb-2 d-block"></i>
                Apply for New Card
              </button>
            </div>
            <div className="col-lg-3 col-md-6 mb-3">
              <button 
                className="btn btn-outline-success w-100 p-3"
                onClick={() => navigate('/card-payments')}
              >
                <i className="fas fa-mobile-alt fa-2x mb-2 d-block"></i>
                Mobile Payments
              </button>
            </div>
            <div className="col-lg-3 col-md-6 mb-3">
              <button 
                className="btn btn-outline-warning w-100 p-3"
                onClick={() => navigate('/card-security')}
              >
                <i className="fas fa-shield-alt fa-2x mb-2 d-block"></i>
                Security Settings
              </button>
            </div>
            <div className="col-lg-3 col-md-6 mb-3">
              <button 
                className="btn btn-outline-info w-100 p-3"
                onClick={() => navigate('/card-benefits')}
              >
                <i className="fas fa-gift fa-2x mb-2 d-block"></i>
                Rewards & Benefits
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CardsPage;