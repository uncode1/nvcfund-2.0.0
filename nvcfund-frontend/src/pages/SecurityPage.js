import React from 'react';

const SecurityPage = () => {
  return (
    <div className="main-content">
      <div className="container py-5">
        <div className="row">
          <div className="col-lg-8 mx-auto">
            <div className="card">
              <div className="card-header">
                <h1 className="mb-0">Security Information</h1>
              </div>
              <div className="card-body">
                <h3>Platform Security</h3>
                <p>NVC Banking Platform employs enterprise-grade security measures to protect your financial information and transactions.</p>
                
                <h4>Security Features</h4>
                <ul>
                  <li>Multi-factor authentication</li>
                  <li>Encrypted data transmission</li>
                  <li>Advanced fraud detection</li>
                  <li>Real-time transaction monitoring</li>
                  <li>Secure blockchain infrastructure</li>
                </ul>

                <h4>Your Security</h4>
                <p>We recommend that you:</p>
                <ul>
                  <li>Use strong, unique passwords</li>
                  <li>Enable two-factor authentication</li>
                  <li>Monitor your accounts regularly</li>
                  <li>Keep your contact information updated</li>
                  <li>Report suspicious activity immediately</li>
                </ul>

                <div className="alert alert-info mt-4">
                  <i className="fas fa-shield-alt me-2"></i>
                  For security concerns or to report suspicious activity, contact our security team immediately.
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SecurityPage;