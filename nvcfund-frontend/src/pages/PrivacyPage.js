import React from 'react';

const PrivacyPage = () => {
  return (
    <div className="main-content">
      <div className="container py-5">
        <div className="row">
          <div className="col-lg-8 mx-auto">
            <div className="card">
              <div className="card-header">
                <h1 className="mb-0">Privacy Policy</h1>
                <p className="mb-0 text-muted">Last updated: June 30, 2025</p>
              </div>
              <div className="card-body">
                <h3>1. Information We Collect</h3>
                <p>We collect information necessary to provide secure banking services including:</p>
                <ul>
                  <li>Personal identification information</li>
                  <li>Financial account information</li>
                  <li>Transaction history and patterns</li>
                  <li>Device and session information</li>
                </ul>
                
                <h3>2. How We Use Your Information</h3>
                <p>Your information is used to:</p>
                <ul>
                  <li>Provide and maintain banking services</li>
                  <li>Process transactions and prevent fraud</li>
                  <li>Comply with financial regulations</li>
                  <li>Improve our services and security</li>
                </ul>

                <h3>3. Information Sharing</h3>
                <p>We do not sell your personal information. We may share information only:</p>
                <ul>
                  <li>With your explicit consent</li>
                  <li>To comply with legal requirements</li>
                  <li>With trusted service providers under strict agreements</li>
                  <li>To protect against fraud and ensure security</li>
                </ul>

                <h3>4. Data Security</h3>
                <p>We implement industry-leading security measures including encryption, secure data centers, and regular security audits to protect your information.</p>

                <h3>5. Your Rights</h3>
                <p>You have the right to:</p>
                <ul>
                  <li>Access your personal information</li>
                  <li>Request corrections to your data</li>
                  <li>Request deletion of your data (subject to legal requirements)</li>
                  <li>Opt-out of non-essential communications</li>
                </ul>

                <h3>6. Contact Us</h3>
                <p>For privacy concerns or to exercise your rights, contact our privacy team through the secure messaging system within your account.</p>

                <div className="alert alert-info mt-4">
                  <i className="fas fa-lock me-2"></i>
                  Your privacy is our priority. We are committed to protecting your personal and financial information.
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PrivacyPage;