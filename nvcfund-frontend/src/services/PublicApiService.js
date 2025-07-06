/**
 * Public API Service
 * Handles all public API interactions for the frontend
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

class PublicApiService {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  /**
   * Make API request with error handling
   */
  async makeRequest(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    
    const defaultOptions = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    };

    try {
      const response = await fetch(url, defaultOptions);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || `HTTP error! status: ${response.status}`);
      }

      return {
        success: true,
        data: data.data || data,
        status: data.status || 'success'
      };
    } catch (error) {
      console.error('API request failed:', error);
      return {
        success: false,
        error: error.message,
        status: 'error'
      };
    }
  }

  /**
   * Check public API health
   */
  async checkHealth() {
    return this.makeRequest('/public/api/health');
  }

  /**
   * Submit contact form
   */
  async submitContactForm(formData) {
    return this.makeRequest('/public/api/contact', {
      method: 'POST',
      body: JSON.stringify(formData)
    });
  }

  /**
   * Get available public pages
   */
  async getPublicPages() {
    // Since the /api/v1/public endpoints aren't working yet, 
    // we'll provide static data for frontend development
    return {
      success: true,
      data: {
        pages: [
          {
            id: 'about',
            title: 'About Us',
            url: '/public/about',
            description: 'Learn about NVC Banking Platform'
          },
          {
            id: 'services',
            title: 'Services',
            url: '/public/services',
            description: 'Our banking and financial services'
          },
          {
            id: 'contact',
            title: 'Contact',
            url: '/public/contact',
            description: 'Get in touch with our team'
          },
          {
            id: 'privacy_policy',
            title: 'Privacy Policy',
            url: '/public/privacy-policy',
            description: 'Our privacy policy and data protection'
          },
          {
            id: 'terms_of_service',
            title: 'Terms of Service',
            url: '/public/terms-of-service',
            description: 'Terms and conditions of service'
          },
          {
            id: 'getting_started',
            title: 'Getting Started',
            url: '/public/getting-started',
            description: 'Getting started guide'
          },
          {
            id: 'user_guide',
            title: 'User Guide',
            url: '/public/user-guide',
            description: 'Complete user guide'
          },
          {
            id: 'faq',
            title: 'FAQ',
            url: '/public/faq',
            description: 'Frequently asked questions'
          },
          {
            id: 'documentation',
            title: 'Documentation',
            url: '/public/documentation',
            description: 'Technical documentation'
          },
          {
            id: 'nvct_whitepaper',
            title: 'NVCT Whitepaper',
            url: '/public/nvct-whitepaper',
            description: 'NVCT Stablecoin technical whitepaper'
          }
        ],
        total_pages: 10,
        timestamp: new Date().toISOString()
      },
      status: 'success'
    };
  }

  /**
   * Get banking services information
   */
  async getBankingServices() {
    return {
      success: true,
      data: {
        services: [
          {
            id: 'digital_banking',
            title: 'Digital Banking',
            description: 'Complete digital banking platform',
            features: [
              'Account Management',
              'Online Transfers',
              'Mobile Banking',
              'Digital Payments'
            ]
          },
          {
            id: 'blockchain_services',
            title: 'Blockchain Services',
            description: 'Blockchain-enabled financial services',
            features: [
              'NVCT Stablecoin',
              'Smart Contracts',
              'Cross-chain Transfers',
              'DeFi Integration'
            ]
          },
          {
            id: 'institutional_banking',
            title: 'Institutional Banking',
            description: 'Enterprise banking solutions',
            features: [
              'Corporate Accounts',
              'Treasury Management',
              'Trade Finance',
              'Risk Management'
            ]
          },
          {
            id: 'security_services',
            title: 'Security Services',
            description: 'Advanced security and compliance',
            features: [
              'Multi-factor Authentication',
              'Fraud Detection',
              'Compliance Monitoring',
              'Risk Assessment'
            ]
          }
        ],
        total_services: 4,
        timestamp: new Date().toISOString()
      },
      status: 'success'
    };
  }

  /**
   * Get NVCT whitepaper information
   */
  async getWhitepaperInfo() {
    return {
      success: true,
      data: {
        whitepaper: {
          title: 'NVCT Stablecoin Technical Whitepaper',
          version: '2.0',
          release_date: '2024-12-15',
          description: 'Comprehensive technical documentation for NVCT stablecoin',
          url: '/public/nvct-whitepaper',
          download_url: '/public/download-whitepaper',
          sections: [
            'Executive Summary',
            'Technical Architecture',
            'Blockchain Integration',
            'Smart Contract Design',
            'Security Framework',
            'Governance Model',
            'Economic Model',
            'Risk Management',
            'Compliance Framework',
            'Future Roadmap'
          ],
          key_features: [
            '$30 Trillion Total Supply',
            '189% Over-collateralization',
            'Multi-blockchain Support',
            'Institutional Grade Security',
            'Regulatory Compliance',
            'Cross-chain Interoperability'
          ],
          networks: [
            'Ethereum',
            'Polygon',
            'Binance Smart Chain',
            'Arbitrum',
            'Optimism'
          ]
        },
        timestamp: new Date().toISOString()
      },
      status: 'success'
    };
  }

  /**
   * Get documentation structure
   */
  async getDocumentation() {
    return {
      success: true,
      data: {
        documentation: {
          api_documentation: {
            title: 'API Documentation',
            description: 'Complete API reference guide',
            url: '/public/api-documentation',
            sections: [
              'Authentication',
              'Endpoints',
              'Request/Response Format',
              'Error Codes',
              'Rate Limiting',
              'Examples'
            ]
          },
          user_guide: {
            title: 'User Guide',
            description: 'Complete user guide for banking platform',
            url: '/public/user-guide',
            sections: [
              'Getting Started',
              'Account Management',
              'Transfers',
              'Cards & Payments',
              'Security',
              'Troubleshooting'
            ]
          },
          developer_docs: {
            title: 'Developer Documentation',
            description: 'Technical documentation for developers',
            url: '/public/documentation',
            sections: [
              'SDK Installation',
              'Integration Guide',
              'Webhooks',
              'Code Examples',
              'Best Practices'
            ]
          }
        },
        timestamp: new Date().toISOString()
      },
      status: 'success'
    };
  }

  /**
   * Get latest news and updates
   */
  async getNews() {
    return {
      success: true,
      data: {
        news: [
          {
            id: 'nvct_launch',
            title: 'NVCT Stablecoin Launch',
            summary: 'NVC Banking Platform launches institutional-grade stablecoin',
            date: '2024-12-15',
            category: 'Product Launch',
            url: '/public/news/nvct-launch'
          },
          {
            id: 'blockchain_integration',
            title: 'Multi-Blockchain Integration',
            summary: 'Platform now supports multiple blockchain networks',
            date: '2024-12-10',
            category: 'Technology',
            url: '/public/news/blockchain-integration'
          },
          {
            id: 'security_upgrade',
            title: 'Enhanced Security Framework',
            summary: 'New security features and compliance updates',
            date: '2024-12-05',
            category: 'Security',
            url: '/public/news/security-upgrade'
          }
        ],
        total_articles: 3,
        timestamp: new Date().toISOString()
      },
      status: 'success'
    };
  }
}

// Create singleton instance
const publicApiService = new PublicApiService();

export default publicApiService;