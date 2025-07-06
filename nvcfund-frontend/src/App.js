import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './hooks/useAuth';
import { ErrorProvider, useGlobalError } from './contexts/ErrorContext';
import { setGlobalErrorHandler } from './services/api';
import './styles/global.css';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import AccountsPage from './pages/AccountsPage';
import TransactionsPage from './pages/TransactionsPage';
import TransfersPage from './pages/TransfersPage';
import CreateAccountPage from './pages/CreateAccountPage';
import ExchangePage from './pages/ExchangePage';
import CardsPage from './pages/CardsPage';
import CardApplicationPage from './pages/CardApplicationPage';
import PaymentFeaturesPage from './pages/PaymentFeaturesPage';
import ProfilePage from './pages/ProfilePage';
import AdminPage from './pages/AdminPage';
import SecurityPage from './pages/SecurityPage';
import TermsPage from './pages/TermsPage';
import PrivacyPage from './pages/PrivacyPage';
import { NotFoundPage } from './pages/ErrorPages';

// Import new modular pages
import TreasuryPage from './pages/TreasuryPage';
import CompliancePage from './pages/CompliancePage';
import InvestmentsPage from './pages/InvestmentsPage';
import InsurancePage from './pages/InsurancePage';
import SmartContractsPage from './pages/SmartContractsPage';
import NVCTStablecoinPage from './pages/NVCTStablecoinPage';
import SovereignBankingPage from './pages/SovereignBankingPage';
import IslamicBankingPage from './pages/IslamicBankingPage';
import TradingPage from './pages/TradingPage';
import AnalyticsPage from './pages/AnalyticsPage';
import BlockchainAnalyticsPage from './pages/BlockchainAnalyticsPage';
import ChatPage from './pages/ChatPage';
import ProtectedRoute from './components/ProtectedRoute';
import NotificationContainer from './components/NotificationContainer';
import ErrorBoundary from './components/ErrorBoundary';
import GlobalErrorHandler from './components/GlobalErrorHandler';

// Component to connect the global error handler to the API service
const AppWithErrorHandler = () => {
  const { showError } = useGlobalError();

  useEffect(() => {
    // Connect the global error handler to the API service
    setGlobalErrorHandler(showError);
  }, [showError]);

  return (
    <AuthProvider>
      <Router>
        <div className="App d-flex flex-column min-vh-100">
          <Navbar />
          <main className="flex-fill">
            <Routes>
              {/* Public Routes */}
              <Route path="/" element={<HomePage />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              <Route path="/security" element={<SecurityPage />} />
              <Route path="/terms" element={<TermsPage />} />
              <Route path="/privacy" element={<PrivacyPage />} />
              
              {/* Protected Routes */}
              <Route 
                path="/dashboard" 
                element={
                  <ProtectedRoute>
                    <DashboardPage />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/accounts" 
                element={
                  <ProtectedRoute>
                    <AccountsPage />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/transactions" 
                element={
                  <ProtectedRoute>
                    <TransactionsPage />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/transfers" 
                element={
                  <ProtectedRoute>
                    <TransfersPage />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/create-account" 
                element={
                  <ProtectedRoute>
                    <CreateAccountPage />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/exchange" 
                element={
                  <ProtectedRoute>
                    <ExchangePage />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/cards" 
                element={
                  <ProtectedRoute>
                    <CardsPage />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/apply-card" 
                element={
                  <ProtectedRoute>
                    <CardApplicationPage />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/payment-features" 
                element={
                  <ProtectedRoute>
                    <PaymentFeaturesPage />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/profile" 
                element={
                  <ProtectedRoute>
                    <ProfilePage />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/admin" 
                element={
                  <ProtectedRoute requiredRole="ADMIN">
                    <AdminPage />
                  </ProtectedRoute>
                } 
              />
              
              {/* New Modular Routes */}
              <Route 
                path="/treasury" 
                element={
                  <ProtectedRoute requiredRole="TREASURY_OFFICER">
                    <TreasuryPage />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/compliance" 
                element={
                  <ProtectedRoute requiredRole="COMPLIANCE_OFFICER">
                    <CompliancePage />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/investments" 
                element={
                  <ProtectedRoute>
                    <InvestmentsPage />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/insurance" 
                element={
                  <ProtectedRoute>
                    <InsurancePage />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/smart-contracts" 
                element={
                  <ProtectedRoute>
                    <SmartContractsPage />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/nvct-stablecoin" 
                element={
                  <ProtectedRoute>
                    <NVCTStablecoinPage />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/sovereign-banking" 
                element={
                  <ProtectedRoute requiredRole="SOVEREIGN_OFFICER">
                    <SovereignBankingPage />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/islamic-banking" 
                element={
                  <ProtectedRoute>
                    <IslamicBankingPage />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/trading" 
                element={
                  <ProtectedRoute>
                    <TradingPage />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/analytics" 
                element={
                  <ProtectedRoute>
                    <AnalyticsPage />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/blockchain-analytics" 
                element={
                  <ProtectedRoute>
                    <BlockchainAnalyticsPage />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/chat" 
                element={
                  <ProtectedRoute>
                    <ChatPage />
                  </ProtectedRoute>
                } 
              />
              
              {/* Catch-all route for 404 errors */}
              <Route path="*" element={<NotFoundPage />} />
            </Routes>
          </main>
          <Footer />
          <NotificationContainer />
          <GlobalErrorHandler /> 
        </div>
      </Router>
    </AuthProvider>
  );
};

function App() {
  return (
    <ErrorBoundary>
      <ErrorProvider>
        <AppWithErrorHandler />
      </ErrorProvider>
    </ErrorBoundary>
  );
}

export default App;