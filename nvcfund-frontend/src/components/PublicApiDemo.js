/**
 * Public API Demo Component
 * Demonstrates how to use the Public API Service in React
 */

import React, { useState, useEffect } from 'react';
import publicApiService from '../services/PublicApiService';

const PublicApiDemo = () => {
  const [apiStatus, setApiStatus] = useState(null);
  const [pages, setPages] = useState([]);
  const [services, setServices] = useState([]);
  const [whitepaper, setWhitepaper] = useState(null);
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Contact form state
  const [contactForm, setContactForm] = useState({
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    subject: '',
    message: ''
  });
  const [contactSubmitting, setContactSubmitting] = useState(false);
  const [contactResult, setContactResult] = useState(null);

  useEffect(() => {
    loadApiData();
  }, []);

  const loadApiData = async () => {
    setLoading(true);
    setError(null);

    try {
      // Load all public API data
      const [
        healthResponse,
        pagesResponse,
        servicesResponse,
        whitepaperResponse,
        newsResponse
      ] = await Promise.all([
        publicApiService.checkHealth(),
        publicApiService.getPublicPages(),
        publicApiService.getBankingServices(),
        publicApiService.getWhitepaperInfo(),
        publicApiService.getNews()
      ]);

      if (healthResponse.success) {
        setApiStatus(healthResponse.data);
      }

      if (pagesResponse.success) {
        setPages(pagesResponse.data.pages || []);
      }

      if (servicesResponse.success) {
        setServices(servicesResponse.data.services || []);
      }

      if (whitepaperResponse.success) {
        setWhitepaper(whitepaperResponse.data.whitepaper);
      }

      if (newsResponse.success) {
        setNews(newsResponse.data.news || []);
      }

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleContactSubmit = async (e) => {
    e.preventDefault();
    setContactSubmitting(true);
    setContactResult(null);

    try {
      const response = await publicApiService.submitContactForm(contactForm);
      
      if (response.success) {
        setContactResult({
          type: 'success',
          message: 'Thank you for your message. We will respond within 2 hours.'
        });
        setContactForm({
          firstName: '',
          lastName: '',
          email: '',
          phone: '',
          subject: '',
          message: ''
        });
      } else {
        setContactResult({
          type: 'error',
          message: response.error || 'Failed to submit contact form'
        });
      }
    } catch (err) {
      setContactResult({
        type: 'error',
        message: err.message
      });
    } finally {
      setContactSubmitting(false);
    }
  };

  const handleContactChange = (e) => {
    setContactForm({
      ...contactForm,
      [e.target.name]: e.target.value
    });
  };

  if (loading) {
    return (
      <div className="container mt-4">
        <div className="text-center">
          <div className="spinner-border" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
          <p className="mt-2">Loading Public API Demo...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mt-4">
      <h1 className="mb-4">Public API Demo</h1>
      
      {error && (
        <div className="alert alert-danger" role="alert">
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* API Health Status */}
      <div className="row mb-4">
        <div className="col-12">
          <div className="card">
            <div className="card-header">
              <h5 className="mb-0">API Health Status</h5>
            </div>
            <div className="card-body">
              {apiStatus ? (
                <div>
                  <span className={`badge ${apiStatus.status === 'healthy' ? 'bg-success' : 'bg-danger'} me-2`}>
                    {apiStatus.status?.toUpperCase()}
                  </span>
                  <small className="text-muted">
                    Module: {apiStatus.module} | Version: {apiStatus.version} | 
                    Last Check: {new Date(apiStatus.timestamp).toLocaleString()}
                  </small>
                </div>
              ) : (
                <span className="badge bg-warning">Unknown</span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Public Pages */}
      <div className="row mb-4">
        <div className="col-12">
          <div className="card">
            <div className="card-header">
              <h5 className="mb-0">Available Public Pages ({pages.length})</h5>
            </div>
            <div className="card-body">
              <div className="row">
                {pages.map((page) => (
                  <div key={page.id} className="col-md-6 col-lg-4 mb-3">
                    <div className="card h-100">
                      <div className="card-body">
                        <h6 className="card-title">{page.title}</h6>
                        <p className="card-text small">{page.description}</p>
                        <a href={page.url} className="btn btn-sm btn-outline-primary">
                          Visit Page
                        </a>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Banking Services */}
      <div className="row mb-4">
        <div className="col-12">
          <div className="card">
            <div className="card-header">
              <h5 className="mb-0">Banking Services ({services.length})</h5>
            </div>
            <div className="card-body">
              <div className="row">
                {services.map((service) => (
                  <div key={service.id} className="col-md-6 mb-3">
                    <div className="card h-100">
                      <div className="card-body">
                        <h6 className="card-title">{service.title}</h6>
                        <p className="card-text">{service.description}</p>
                        <ul className="list-unstyled">
                          {service.features.map((feature, index) => (
                            <li key={index} className="small">
                              <i className="fas fa-check-circle text-success me-1"></i>
                              {feature}
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* NVCT Whitepaper */}
      {whitepaper && (
        <div className="row mb-4">
          <div className="col-12">
            <div className="card">
              <div className="card-header">
                <h5 className="mb-0">NVCT Whitepaper</h5>
              </div>
              <div className="card-body">
                <h6>{whitepaper.title}</h6>
                <p className="text-muted">{whitepaper.description}</p>
                <div className="row">
                  <div className="col-md-6">
                    <h6>Key Features:</h6>
                    <ul>
                      {whitepaper.key_features.map((feature, index) => (
                        <li key={index} className="small">{feature}</li>
                      ))}
                    </ul>
                  </div>
                  <div className="col-md-6">
                    <h6>Supported Networks:</h6>
                    <ul>
                      {whitepaper.networks.map((network, index) => (
                        <li key={index} className="small">{network}</li>
                      ))}
                    </ul>
                  </div>
                </div>
                <div className="mt-3">
                  <a href={whitepaper.url} className="btn btn-primary me-2">
                    Read Whitepaper
                  </a>
                  <a href={whitepaper.download_url} className="btn btn-outline-secondary">
                    Download PDF
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Latest News */}
      <div className="row mb-4">
        <div className="col-12">
          <div className="card">
            <div className="card-header">
              <h5 className="mb-0">Latest News ({news.length})</h5>
            </div>
            <div className="card-body">
              {news.map((article) => (
                <div key={article.id} className="card mb-3">
                  <div className="card-body">
                    <div className="d-flex justify-content-between align-items-start">
                      <div>
                        <h6 className="card-title">{article.title}</h6>
                        <p className="card-text">{article.summary}</p>
                        <small className="text-muted">
                          {article.category} | {new Date(article.date).toLocaleDateString()}
                        </small>
                      </div>
                      <a href={article.url} className="btn btn-sm btn-outline-primary">
                        Read More
                      </a>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Contact Form Demo */}
      <div className="row mb-4">
        <div className="col-12">
          <div className="card">
            <div className="card-header">
              <h5 className="mb-0">Contact Form API Demo</h5>
            </div>
            <div className="card-body">
              {contactResult && (
                <div className={`alert ${contactResult.type === 'success' ? 'alert-success' : 'alert-danger'}`}>
                  {contactResult.message}
                </div>
              )}
              
              <form onSubmit={handleContactSubmit}>
                <div className="row">
                  <div className="col-md-6 mb-3">
                    <label htmlFor="firstName" className="form-label">First Name *</label>
                    <input
                      type="text"
                      className="form-control"
                      id="firstName"
                      name="firstName"
                      value={contactForm.firstName}
                      onChange={handleContactChange}
                      required
                    />
                  </div>
                  <div className="col-md-6 mb-3">
                    <label htmlFor="lastName" className="form-label">Last Name *</label>
                    <input
                      type="text"
                      className="form-control"
                      id="lastName"
                      name="lastName"
                      value={contactForm.lastName}
                      onChange={handleContactChange}
                      required
                    />
                  </div>
                </div>
                
                <div className="row">
                  <div className="col-md-6 mb-3">
                    <label htmlFor="email" className="form-label">Email *</label>
                    <input
                      type="email"
                      className="form-control"
                      id="email"
                      name="email"
                      value={contactForm.email}
                      onChange={handleContactChange}
                      required
                    />
                  </div>
                  <div className="col-md-6 mb-3">
                    <label htmlFor="phone" className="form-label">Phone</label>
                    <input
                      type="tel"
                      className="form-control"
                      id="phone"
                      name="phone"
                      value={contactForm.phone}
                      onChange={handleContactChange}
                    />
                  </div>
                </div>
                
                <div className="mb-3">
                  <label htmlFor="subject" className="form-label">Subject *</label>
                  <input
                    type="text"
                    className="form-control"
                    id="subject"
                    name="subject"
                    value={contactForm.subject}
                    onChange={handleContactChange}
                    required
                  />
                </div>
                
                <div className="mb-3">
                  <label htmlFor="message" className="form-label">Message *</label>
                  <textarea
                    className="form-control"
                    id="message"
                    name="message"
                    rows="4"
                    value={contactForm.message}
                    onChange={handleContactChange}
                    required
                  ></textarea>
                </div>
                
                <button 
                  type="submit" 
                  className="btn btn-primary"
                  disabled={contactSubmitting}
                >
                  {contactSubmitting ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                      Submitting...
                    </>
                  ) : (
                    'Submit Contact Form'
                  )}
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>

      <div className="row">
        <div className="col-12">
          <button 
            className="btn btn-secondary"
            onClick={loadApiData}
            disabled={loading}
          >
            {loading ? 'Refreshing...' : 'Refresh Data'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default PublicApiDemo;