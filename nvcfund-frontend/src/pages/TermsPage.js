import React from 'react';

const TermsPage = () => {
  return (
    <div className="main-content">
      <div className="container py-5">
        <div className="row">
          <div className="col-lg-8 mx-auto">
            <div className="card">
              <div className="card-header">
                <h1 className="mb-0">Terms of Service</h1>
                <p className="mb-0 text-muted">Last updated: June 30, 2025</p>
              </div>
              <div className="card-body">
                <h3>1. Agreement to Terms</h3>
                <p>By accessing and using NVC Banking Platform, you agree to be bound by these Terms of Service and all applicable laws and regulations.</p>
                
                <h3>2. Banking Services</h3>
                <p>NVC Banking Platform provides digital financial services including but not limited to:</p>
                <ul>
                  <li>Account management and transactions</li>
                  <li>Digital currency exchange services</li>
                  <li>Payment processing and transfers</li>
                  <li>Financial analytics and reporting</li>
                </ul>

                <h3>3. User Responsibilities</h3>
                <p>Users are responsible for:</p>
                <ul>
                  <li>Maintaining the confidentiality of their account credentials</li>
                  <li>Providing accurate and up-to-date information</li>
                  <li>Complying with all applicable financial regulations</li>
                  <li>Reporting unauthorized access or suspicious activity</li>
                </ul>

                <h3>4. Privacy and Data Protection</h3>
                <p>We are committed to protecting your personal and financial information in accordance with our Privacy Policy and applicable data protection laws.</p>

                <h3>5. Limitation of Liability</h3>
                <p>NVC Banking Platform provides services "as is" and limits liability to the extent permitted by applicable law.</p>

                <h3>6. Contact Information</h3>
                <p>For questions about these terms, please contact our legal department through the platform's secure messaging system.</p>

                <div className="alert alert-warning mt-4">
                  <i className="fas fa-exclamation-triangle me-2"></i>
                  By continuing to use our services, you acknowledge that you have read, understood, and agree to these terms.
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TermsPage;