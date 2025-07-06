import axios from 'axios';

// Global error handler reference (will be set by App component)
let globalErrorHandler = null;

export const setGlobalErrorHandler = (handler) => {
  globalErrorHandler = handler;
};

// Create axios instance with default config
const api = axios.create({
  baseURL: process.env.NODE_ENV === 'production' ? '/api/v1' : 'http://localhost:5000/api/v1',
  withCredentials: true, // Important for session cookies
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth headers if needed
api.interceptors.request.use(
  (config) => {
    // Add JWT token if available
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for central error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Handle unauthorized access (redirect to login)
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
      return Promise.reject(error);
    }

    // Handle access denied (403) - Treasury operations  
    if (error.response?.status === 403) {
      const message = 'Access restricted. This operation requires special authorization.';
      const sanitizedError = { ...error, message, userFriendly: true };
      if (globalErrorHandler) {
        globalErrorHandler(sanitizedError);
      }
      return Promise.reject(sanitizedError);
    }

    // Sanitize error messages to prevent technical exposure
    const sanitizedError = sanitizeError(error);
    
    // Trigger global error handler if available
    if (globalErrorHandler) {
      globalErrorHandler(sanitizedError);
    } else {
      // Fallback console error if no global handler
      console.error('API Error (No Global Handler):', sanitizedError);
    }

    return Promise.reject(sanitizedError);
  }
);

// Professional error sanitization - prevents technical stack exposure
const sanitizeError = (error) => {
  let userMessage = 'Service temporarily unavailable. Please try again shortly.';
  let errorType = 'general';

  // Map specific error conditions to user-friendly messages
  if (error.code === 'ECONNREFUSED' || error.code === 'ENOTFOUND') {
    userMessage = 'Unable to connect to banking services. Please check your connection.';
    errorType = 'network';
  } else if (error.response?.status === 404) {
    userMessage = 'The requested service is not available.';
    errorType = 'notfound';
  } else if (error.response?.status === 500) {
    userMessage = 'Our system is experiencing temporary difficulties.';
    errorType = 'server';
  } else if (error.response?.status === 429) {
    userMessage = 'Too many requests. Please wait a moment before trying again.';
    errorType = 'ratelimit';
  } else if (error.message?.includes('timeout')) {
    userMessage = 'Request timeout. Please try again.';
    errorType = 'timeout';
  }

  return {
    ...error,
    message: userMessage,
    errorType,
    userFriendly: true,
    originalError: {
      status: error.response?.status,
      code: error.code,
      // Don't include technical stack traces
    }
  };
};

// API service class
class ApiService {
  // Health check
  async checkHealth() {
    const response = await api.get('/health');
    return response.data;
  }

  // Authentication endpoints
  async login(username, password) {
    const response = await api.post('/auth/login', { username, password });
    return response.data;
  }

  async logout() {
    const response = await api.post('/auth/logout');
    return response.data;
  }

  async register(userData) {
    const response = await api.post('/auth/register', userData);
    return response.data;
  }

  async getAuthStatus() {
    const response = await api.get('/auth/status');
    return response.data;
  }

  async getProfile() {
    const response = await api.get('/auth/profile');
    return response.data;
  }

  async updateProfile(data) {
    const response = await api.put('/auth/profile', data);
    return response.data;
  }

  // Banking endpoints
  async getAccounts() {
    const response = await api.get('/banking/accounts');
    return response.data;
  }

  async getAccount(accountId) {
    const response = await api.get(`/banking/accounts/${accountId}`);
    return response.data;
  }

  async createAccount(accountData) {
    const response = await api.post('/banking/create-account', accountData);
    return response.data;
  }

  async getTransactions(params = {}) {
    const response = await api.get('/banking/transactions', { params });
    return response.data;
  }

  async createTransfer(transferData) {
    const response = await api.post('/banking/transfer', transferData);
    return response.data;
  }

  async getBalanceSummary() {
    const response = await api.get('/banking/balance-summary');
    return response.data;
  }

  // Exchange endpoints
  async getExchangeRate(params) {
    const response = await api.get('/banking/exchange-rate', { params });
    return response.data;
  }

  async createExchange(exchangeData) {
    const response = await api.post('/banking/exchange', exchangeData);
    return response.data;
  }

  async getExchangeHistory(params = {}) {
    const response = await api.get('/banking/exchange-history', { params });
    return response.data;
  }

  // Admin endpoints
  async getAdminStats() {
    const response = await api.get('/admin/stats');
    return response.data;
  }

  async getUsers(params = {}) {
    const response = await api.get('/admin/users', { params });
    return response.data;
  }

  // Security endpoints
  async getSecurityDashboard() {
    const response = await api.get('/security/dashboard');
    return response.data;
  }

  async createIncident(incidentData) {
    const response = await api.post('/security/create-incident', incidentData);
    return response.data;
  }

  // Treasury endpoints
  async getTreasuryBalance() {
    const response = await api.get('/treasury/balance');
    return response.data;
  }

  async getNVCTOperations() {
    const response = await api.get('/treasury/nvct-operations');
    return response.data;
  }

  // Card management endpoints
  async getUserCards() {
    const response = await api.get('/banking/cards');
    return response.data;
  }

  async getCardApplications() {
    const response = await api.get('/banking/card-applications');
    return response.data;
  }

  async submitCardApplication(applicationData) {
    const response = await api.post('/banking/apply-card', applicationData);
    return response.data;
  }

  async updateCardStatus(cardId, action) {
    const response = await api.patch(`/banking/cards/${cardId}/status`, { action });
    return response.data;
  }

  async getCardDetails(cardId) {
    const response = await api.get(`/banking/cards/${cardId}`);
    return response.data;
  }

  async activateCard(cardId, activationData) {
    const response = await api.post(`/banking/cards/${cardId}/activate`, activationData);
    return response.data;
  }

  async blockCard(cardId, reason) {
    const response = await api.post(`/banking/cards/${cardId}/block`, { reason });
    return response.data;
  }

  async getCardTransactions(cardId, params = {}) {
    const response = await api.get(`/banking/cards/${cardId}/transactions`, { params });
    return response.data;
  }

  async reportCardLost(cardId, reportData) {
    const response = await api.post(`/banking/cards/${cardId}/report-lost`, reportData);
    return response.data;
  }

  async requestCardReplacement(cardId, replacementData) {
    const response = await api.post(`/banking/cards/${cardId}/request-replacement`, replacementData);
    return response.data;
  }

  async updateCardLimits(cardId, limits) {
    const response = await api.patch(`/banking/cards/${cardId}/limits`, limits);
    return response.data;
  }

  async getPaymentIntegrations() {
    const response = await api.get('/banking/payment-integrations');
    return response.data;
  }

  async connectPaymentProvider(providerData) {
    const response = await api.post('/banking/connect-payment-provider', providerData);
    return response.data;
  }

  // ==========================================================================
  // NEW MODULAR ENDPOINTS - Connected to Backend Modules
  // ==========================================================================

  // Treasury Management Module
  async getTreasuryDashboard() {
    const response = await api.get('/treasury/dashboard');
    return response.data;
  }

  async getTreasuryAccounts() {
    const response = await api.get('/treasury/accounts');
    return response.data;
  }

  async executeTreasuryOperation(operationData) {
    const response = await api.post('/treasury/execute-operation', operationData);
    return response.data;
  }

  async getTreasuryReports(params = {}) {
    const response = await api.get('/treasury/reports', { params });
    return response.data;
  }

  // Settlement Module
  async getSettlementQueue() {
    const response = await api.get('/settlement/queue');
    return response.data;
  }

  async processSettlement(settlementData) {
    const response = await api.post('/settlement/process', settlementData);
    return response.data;
  }

  async getSettlementHistory(params = {}) {
    const response = await api.get('/settlement/history', { params });
    return response.data;
  }

  // Compliance Module
  async getComplianceDashboard() {
    const response = await api.get('/compliance/dashboard');
    return response.data;
  }

  async generateComplianceReport(reportType) {
    const response = await api.post('/compliance/generate-report', { reportType });
    return response.data;
  }

  async getComplianceAlerts() {
    const response = await api.get('/compliance/alerts');
    return response.data;
  }

  async updateComplianceStatus(alertId, status) {
    const response = await api.patch(`/compliance/alerts/${alertId}`, { status });
    return response.data;
  }

  // Investments Module
  async getInvestmentPortfolio() {
    const response = await api.get('/investments/portfolio');
    return response.data;
  }

  async createInvestment(investmentData) {
    const response = await api.post('/investments/create', investmentData);
    return response.data;
  }

  async getInvestmentAnalytics() {
    const response = await api.get('/investments/analytics');
    return response.data;
  }

  // Insurance Module
  async getInsurancePolicies() {
    const response = await api.get('/insurance/policies');
    return response.data;
  }

  async applyForInsurance(applicationData) {
    const response = await api.post('/insurance/apply', applicationData);
    return response.data;
  }

  async getInsuranceClaims() {
    const response = await api.get('/insurance/claims');
    return response.data;
  }

  // Smart Contracts Module
  async getSmartContracts() {
    const response = await api.get('/smart-contracts/list');
    return response.data;
  }

  async deploySmartContract(contractData) {
    const response = await api.post('/smart-contracts/deploy', contractData);
    return response.data;
  }

  async executeSmartContract(contractId, params) {
    const response = await api.post(`/smart-contracts/${contractId}/execute`, params);
    return response.data;
  }

  async getSmartContractAnalytics() {
    const response = await api.get('/smart-contracts/analytics');
    return response.data;
  }

  // NVCT Stablecoin Module
  async getNVCTBalance() {
    const response = await api.get('/nvct-stablecoin/balance');
    return response.data;
  }

  async mintNVCT(mintData) {
    const response = await api.post('/nvct-stablecoin/mint', mintData);
    return response.data;
  }

  async burnNVCT(burnData) {
    const response = await api.post('/nvct-stablecoin/burn', burnData);
    return response.data;
  }

  async getNVCTAnalytics() {
    const response = await api.get('/nvct-stablecoin/analytics');
    return response.data;
  }

  // Sovereign Banking Module
  async getSovereignAccounts() {
    const response = await api.get('/sovereign/accounts');
    return response.data;
  }

  async executeSovereignOperation(operationData) {
    const response = await api.post('/sovereign/execute-operation', operationData);
    return response.data;
  }

  async getSovereignReports() {
    const response = await api.get('/sovereign/reports');
    return response.data;
  }

  // Islamic Banking Module
  async getIslamicBankingProducts() {
    const response = await api.get('/islamic-banking/products');
    return response.data;
  }

  async applyIslamicBankingProduct(applicationData) {
    const response = await api.post('/islamic-banking/apply', applicationData);
    return response.data;
  }

  async getIslamicBankingCompliance() {
    const response = await api.get('/islamic-banking/compliance');
    return response.data;
  }

  // Interest Rate Management Module
  async getInterestRates() {
    const response = await api.get('/interest-rate-management/rates');
    return response.data;
  }

  async updateInterestRate(rateData) {
    const response = await api.post('/interest-rate-management/update-rate', rateData);
    return response.data;
  }

  async getInterestRateHistory() {
    const response = await api.get('/interest-rate-management/history');
    return response.data;
  }

  // Trading Module
  async getTradingDashboard() {
    const response = await api.get('/trading/dashboard');
    return response.data;
  }

  async executeTrade(tradeData) {
    const response = await api.post('/trading/execute', tradeData);
    return response.data;
  }

  async getTradingHistory(params = {}) {
    const response = await api.get('/trading/history', { params });
    return response.data;
  }

  async getTradingAnalytics() {
    const response = await api.get('/trading/analytics');
    return response.data;
  }

  // Institutional Module
  async getInstitutionalServices() {
    const response = await api.get('/institutional/services');
    return response.data;
  }

  async createInstitutionalAccount(accountData) {
    const response = await api.post('/institutional/create-account', accountData);
    return response.data;
  }

  async getInstitutionalReports() {
    const response = await api.get('/institutional/reports');
    return response.data;
  }

  // Binance Integration Module
  async getBinancePortfolio() {
    const response = await api.get('/binance-integration/portfolio');
    return response.data;
  }

  async executeBinanceTrade(tradeData) {
    const response = await api.post('/binance-integration/trade', tradeData);
    return response.data;
  }

  async getBinanceMarketData() {
    const response = await api.get('/binance-integration/market-data');
    return response.data;
  }

  // Blockchain Analytics Module
  async getBlockchainAnalytics() {
    const response = await api.get('/blockchain-analytics/dashboard');
    return response.data;
  }

  async trackBlockchainTransaction(txHash) {
    const response = await api.get(`/blockchain-analytics/transaction/${txHash}`);
    return response.data;
  }

  async getBlockchainReports() {
    const response = await api.get('/blockchain-analytics/reports');
    return response.data;
  }

  // Chat Module
  async getChatSessions() {
    const response = await api.get('/chat/sessions');
    return response.data;
  }

  async createChatSession(sessionData) {
    const response = await api.post('/chat/create-session', sessionData);
    return response.data;
  }

  async sendChatMessage(sessionId, message) {
    const response = await api.post(`/chat/sessions/${sessionId}/message`, { message });
    return response.data;
  }

  // Advanced Analytics Module
  async getAdvancedAnalytics() {
    const response = await api.get('/analytics/advanced');
    return response.data;
  }

  async generateCustomReport(reportConfig) {
    const response = await api.post('/analytics/custom-report', reportConfig);
    return response.data;
  }

  async getAnalyticsInsights() {
    const response = await api.get('/analytics/insights');
    return response.data;
  }

  // System Management Module
  async getSystemStatus() {
    const response = await api.get('/system/status');
    return response.data;
  }

  async getSystemLogs(params = {}) {
    const response = await api.get('/system/logs', { params });
    return response.data;
  }

  async executeSystemMaintenance(maintenanceData) {
    const response = await api.post('/system/maintenance', maintenanceData);
    return response.data;
  }

  // Real-time WebSocket endpoints
  async getWebSocketToken() {
    const response = await api.get('/api/websocket/token');
    return response.data;
  }

  async subscribeToRealTimeUpdates(subscriptionData) {
    const response = await api.post('/api/websocket/subscribe', subscriptionData);
    return response.data;
  }
}

const apiService = new ApiService();
export default apiService;