import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import '../styles/navbar.css';

const Navbar = () => {
  const { isAuthenticated, logout, isAdmin, isTreasury, getUserDisplayName } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  return (
    <nav className="navbar navbar-expand-lg navbar-dark bg-dark">
      <div className="container">
        <Link className="navbar-brand" to="/">
          <i className="fas fa-university me-2"></i>NVC Banking Platform
        </Link>
        
        <button 
          className="navbar-toggler" 
          type="button" 
          data-bs-toggle="collapse" 
          data-bs-target="#navbarNav"
        >
          <span className="navbar-toggler-icon"></span>
        </button>
        
        <div className="collapse navbar-collapse" id="navbarNav">
          <ul className="navbar-nav me-auto">
            <li className="nav-item">
              <Link className="nav-link" to="/">
                <i className="fas fa-home me-1"></i>Home
              </Link>
            </li>
            
            {isAuthenticated && (
              <>
                {/* Standard User Navigation */}
                {!isAdmin() && !isTreasury() && (
                  <>
                    <li className="nav-item">
                      <Link className="nav-link" to="/dashboard">
                        <i className="fas fa-chart-line me-1"></i>Dashboard
                      </Link>
                    </li>
                    
                    <li className="nav-item">
                      <Link className="nav-link" to="/accounts">
                        <i className="fas fa-wallet me-1"></i>Accounts
                      </Link>
                    </li>
                    
                    <li className="nav-item">
                      <Link className="nav-link" to="/transfers">
                        <i className="fas fa-exchange-alt me-1"></i>Transfers
                      </Link>
                    </li>
                    
                    <li className="nav-item">
                      <Link className="nav-link" to="/cards">
                        <i className="fas fa-credit-card me-1"></i>Cards
                      </Link>
                    </li>
                    
                    <li className="nav-item">
                      <Link className="nav-link" to="/transactions">
                        <i className="fas fa-history me-1"></i>History
                      </Link>
                    </li>
                    
                    <li className="nav-item dropdown">
                      <a 
                        className="nav-link dropdown-toggle" 
                        href="#services" 
                        role="button" 
                        data-bs-toggle="dropdown"
                        aria-expanded="false"
                      >
                        <i className="fas fa-concierge-bell me-1"></i>Services
                      </a>
                      <ul className="dropdown-menu shadow-lg" style={{
                        backgroundColor: '#0a2447', 
                        border: '1px solid #66ccff',
                        minWidth: '220px',
                        zIndex: 1100
                      }}>
                        <li><Link className="dropdown-item" to="/payment-features" style={{color: '#ffffff'}}>
                          <i className="fas fa-layer-group me-2" style={{color: '#f39c12'}}></i>Payment Features
                        </Link></li>
                        <li><Link className="dropdown-item" to="/create-account" style={{color: '#ffffff'}}>
                          <i className="fas fa-plus-circle me-2" style={{color: '#2ecc71'}}></i>Open New Account
                        </Link></li>
                        <li><Link className="dropdown-item" to="/apply-card" style={{color: '#ffffff'}}>
                          <i className="fas fa-credit-card me-2" style={{color: '#66ccff'}}></i>Apply for Card
                        </Link></li>
                        <li><a className="dropdown-item" href="#" onClick={(e) => e.preventDefault()} style={{color: '#ffffff'}}>
                          <i className="fas fa-receipt me-2" style={{color: '#e74c3c'}}></i>Pay Bills
                        </a></li>
                        <li><Link className="dropdown-item" to="/exchange" style={{color: '#ffffff'}}>
                          <i className="fas fa-coins me-2" style={{color: '#f39c12'}}></i>Currency Exchange
                        </Link></li>
                      </ul>
                    </li>
                  </>
                )}
                
                {/* Treasury User Navigation */}
                {isTreasury() && (
                  <>
                    <li className="nav-item">
                      <Link className="nav-link" to="/dashboard">
                        <i className="fas fa-chart-line me-1"></i>Dashboard
                      </Link>
                    </li>
                    
                    <li className="nav-item">
                      <a className="nav-link" href="#treasury-operations" onClick={(e) => e.preventDefault()}>
                        <i className="fas fa-coins me-1"></i>NVCT Operations
                      </a>
                    </li>
                    
                    <li className="nav-item">
                      <a className="nav-link" href="#liquidity" onClick={(e) => e.preventDefault()}>
                        <i className="fas fa-balance-scale me-1"></i>Liquidity
                      </a>
                    </li>
                    
                    <li className="nav-item">
                      <a className="nav-link" href="#risk-management" onClick={(e) => e.preventDefault()}>
                        <i className="fas fa-shield-alt me-1"></i>Risk Management
                      </a>
                    </li>
                    
                    <li className="nav-item">
                      <a className="nav-link" href="#reports" onClick={(e) => e.preventDefault()}>
                        <i className="fas fa-chart-bar me-1"></i>Treasury Reports
                      </a>
                    </li>
                  </>
                )}
                
                {/* Admin User Navigation */}
                {isAdmin() && (
                  <>
                    <li className="nav-item">
                      <Link className="nav-link" to="/admin">
                        <i className="fas fa-tachometer-alt me-1"></i>Admin Dashboard
                      </Link>
                    </li>
                    
                    <li className="nav-item">
                      <a className="nav-link" href="#user-management" onClick={(e) => e.preventDefault()}>
                        <i className="fas fa-users me-1"></i>Users
                      </a>
                    </li>
                    
                    <li className="nav-item">
                      <a className="nav-link" href="#system-monitor" onClick={(e) => e.preventDefault()}>
                        <i className="fas fa-desktop me-1"></i>System
                      </a>
                    </li>
                    
                    <li className="nav-item">
                      <a className="nav-link" href="#security-center" onClick={(e) => e.preventDefault()}>
                        <i className="fas fa-lock me-1"></i>Security
                      </a>
                    </li>
                    
                    <li className="nav-item">
                      <a className="nav-link" href="#compliance" onClick={(e) => e.preventDefault()}>
                        <i className="fas fa-clipboard-check me-1"></i>Compliance
                      </a>
                    </li>
                    
                    <li className="nav-item">
                      <a className="nav-link" href="#reports" onClick={(e) => e.preventDefault()}>
                        <i className="fas fa-file-alt me-1"></i>Reports
                      </a>
                    </li>
                  </>
                )}
              </>
            )}
          </ul>
          
          <ul className="navbar-nav">
            {!isAuthenticated ? (
              <>
                <li className="nav-item">
                  <Link className="nav-link" to="/login">
                    <i className="fas fa-sign-in-alt me-1"></i>Login
                  </Link>
                </li>
                <li className="nav-item">
                  <Link className="nav-link" to="/register">
                    <i className="fas fa-user-plus me-1"></i>Register
                  </Link>
                </li>
              </>
            ) : (
              <li className="nav-item dropdown">
                <a 
                  className="nav-link dropdown-toggle" 
                  href="#" 
                  role="button" 
                  data-bs-toggle="dropdown"
                >
                  <i className="fas fa-user me-1"></i>
                  {getUserDisplayName()}
                </a>
                <ul className="dropdown-menu dropdown-menu-end" style={{
                  backgroundColor: '#0a2447',
                  border: '1px solid #66ccff',
                  minWidth: '200px',
                  zIndex: 1100
                }}>
                  <li><Link className="dropdown-item" to="/profile" style={{color: '#ffffff'}}>
                    <i className="fas fa-user-edit me-2" style={{color: '#66ccff'}}></i>Profile
                  </Link></li>
                  <li><a className="dropdown-item" href="#" onClick={(e) => e.preventDefault()} style={{color: '#ffffff'}}>
                    <i className="fas fa-cog me-2" style={{color: '#95a5a6'}}></i>Settings
                  </a></li>
                  <li><hr className="dropdown-divider" style={{borderColor: '#66ccff'}} /></li>
                  <li><a className="dropdown-item" href="#" onClick={handleLogout} style={{color: '#ffffff'}}>
                    <i className="fas fa-sign-out-alt me-2" style={{color: '#e74c3c'}}></i>Logout
                  </a></li>
                </ul>
              </li>
            )}
          </ul>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;