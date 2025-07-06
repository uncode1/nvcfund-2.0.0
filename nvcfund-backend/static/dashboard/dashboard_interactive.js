/**
 * Dashboard Interactive Features
 * Enhances dashboard with real-time updates and interactive elements
 */

window.nvcDashboard = {
    // Key metrics cache
    keyMetrics: {
        totalAccounts: 0,
        totalBalance: 0,
        activeTransactions: 0,
        pendingApprovals: 0
    },

    // Initialize dashboard features
    init: function() {
        // Dashboard interactive features starting
        this.setupRealTimeMetrics();
        this.setupCharts();
        this.setupInteractiveElements();
        this.loadKeyMetrics();
    },

    // Setup real-time metrics updates
    setupRealTimeMetrics: function() {
        // Update metrics every 30 seconds
        setInterval(() => {
            this.updateKeyMetrics();
        }, 30000);
    },

    // Load initial key metrics
    loadKeyMetrics: function() {
        // Simulate loading metrics from API
        this.keyMetrics = {
            totalAccounts: 4,
            totalBalance: 676847.52,
            activeTransactions: 156,
            pendingApprovals: 12
        };
        
        this.updateMetricsDisplay();
    },

    // Update key metrics from server
    updateKeyMetrics: function() {
        // Updating metrics
        
        // Simulate metric changes
        this.keyMetrics.totalBalance += Math.random() * 1000 - 500;
        this.keyMetrics.activeTransactions = Math.floor(Math.random() * 200) + 100;
        this.keyMetrics.pendingApprovals = Math.floor(Math.random() * 20) + 5;
        
        this.updateMetricsDisplay();
    },

    // Update metrics display in DOM
    updateMetricsDisplay: function() {
        const balanceEl = document.querySelector('[data-metric="balance"]');
        const accountsEl = document.querySelector('[data-metric="total_accounts"]');
        
        if (balanceEl) {
            const formatted = '$' + this.keyMetrics.totalBalance.toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });
            balanceEl.textContent = formatted;
        }
        
        if (accountsEl) {
            accountsEl.textContent = this.keyMetrics.totalAccounts;
        }
    },

    // Setup interactive charts
    setupCharts: function() {
        // Balance trend chart
        const balanceChart = document.getElementById('balanceChart');
        if (balanceChart && typeof Chart !== 'undefined') {
            new Chart(balanceChart, {
                type: 'line',
                data: {
                    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                    datasets: [{
                        label: 'Account Balance',
                        data: [650000, 660000, 670000, 675000, 672000, 676847],
                        borderColor: '#0d6efd',
                        backgroundColor: 'rgba(13, 110, 253, 0.1)',
                        tension: 0.3
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    }
                }
            });
        }

        // Transaction types chart
        const transactionChart = document.getElementById('transactionChart');
        if (transactionChart && typeof Chart !== 'undefined') {
            new Chart(transactionChart, {
                type: 'doughnut',
                data: {
                    labels: ['Deposits', 'Withdrawals', 'Transfers', 'Payments'],
                    datasets: [{
                        data: [45, 25, 20, 10],
                        backgroundColor: [
                            '#198754',
                            '#dc3545',
                            '#0d6efd',
                            '#ffc107'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        }
    },

    // Setup interactive elements
    setupInteractiveElements: function() {
        // Enhanced search functionality
        this.setupSearch();
        
        // Real-time notifications
        this.setupNotifications();
        
        // Interactive tables
        this.setupTables();
    },

    // Setup search functionality
    setupSearch: function() {
        const searchInputs = document.querySelectorAll('.search-input');
        searchInputs.forEach(input => {
            input.addEventListener('input', (e) => {
                this.performSearch(e.target.value, e.target.dataset.searchTarget);
            });
        });
    },

    // Perform search filtering
    performSearch: function(query, target) {
        if (!query || !target) return;
        
        const rows = document.querySelectorAll(`[data-searchable="${target}"]`);
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            const matches = text.includes(query.toLowerCase());
            row.style.display = matches ? '' : 'none';
        });
        
        // Search filter applied
    },

    // Setup notifications
    setupNotifications: function() {
        // Simulate real-time notifications
        setTimeout(() => {
            this.showNotification('New deposit of $2,500 received', 'success');
        }, 5000);
        
        setTimeout(() => {
            this.showNotification('Pending approval: Wire transfer request', 'warning');
        }, 10000);
    },

    // Show notification
    showNotification: function(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show dashboard-notification`;
        notification.style.cssText = `
            position: fixed;
            top: 80px;
            right: 20px;
            z-index: 9999;
            min-width: 350px;
            max-width: 400px;
        `;
        notification.innerHTML = `
            <strong>Dashboard Alert:</strong> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 8 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.classList.remove('show');
                setTimeout(() => notification.remove(), 300);
            }
        }, 8000);
    },

    // Setup interactive tables
    setupTables: function() {
        const tables = document.querySelectorAll('table');
        tables.forEach(table => {
            // Add row hover effects
            const rows = table.querySelectorAll('tbody tr');
            rows.forEach(row => {
                row.addEventListener('mouseenter', function() {
                    this.style.backgroundColor = '#f8f9fa';
                });
                row.addEventListener('mouseleave', function() {
                    this.style.backgroundColor = '';
                });
            });
        });
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    if (window.nvcDashboard) {
        window.nvcDashboard.init();
    }
});

// Handle refresh events
document.addEventListener('dashboardRefresh', function() {
    if (window.nvcDashboard) {
        window.nvcDashboard.updateKeyMetrics();
    }
});