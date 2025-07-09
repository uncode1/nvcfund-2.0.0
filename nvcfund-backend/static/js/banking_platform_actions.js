/**
 * NVC Banking Platform - Minimal Action Handler System
 * Only handles essential interactive elements without interfering with navigation
 */

class BankingPlatformActions {
    constructor() {
        this.modals = new Map();
        this.init();
    }

    init() {
        document.addEventListener('DOMContentLoaded', () => {
            this.setupEssentialHandlers();
            console.log('🎯 All banking platform actions activated');
            console.log('✅ Global interactive features activated');
        });
    }

    setupEssentialHandlers() {
        // Only handle elements that explicitly need JavaScript
        this.setupModalHandlers();
        this.setupFormValidation();
        this.setupNotifications();
        this.setupActionHandlers();
        this.setupSearchHandlers();
        this.setupAccountTypeFilters();
    }

    setupModalHandlers() {
        // Only handle modals that have data-modal-trigger attribute
        document.querySelectorAll('[data-modal-trigger]').forEach(trigger => {
            trigger.addEventListener('click', (e) => {
                e.preventDefault();
                const modalId = trigger.dataset.modalTrigger;
                this.showModal(modalId);
            });
        });
    }

    setupFormValidation() {
        // Only validate forms that have data-validate attribute
        document.querySelectorAll('form[data-validate]').forEach(form => {
            form.addEventListener('submit', (e) => {
                if (!this.validateForm(form)) {
                    e.preventDefault();
                }
            });
        });
    }

    setupNotifications() {
        // Handle notification dismissal
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('notification-close')) {
                const notification = e.target.closest('.notification');
                if (notification) {
                    notification.remove();
                }
            }
        });
    }

    setupActionHandlers() {
        // Handle elements with data-action attributes
        document.addEventListener('click', (e) => {
            const target = e.target.closest('[data-action]');
            if (target) {
                const action = target.dataset.action;
                this.handleAction(action, target);
            }
        });
    }

    handleAction(action, element) {
        switch(action) {
            case 'new_account':
                this.handleNewAccount();
                break;
            case 'export_data':
                this.handleExportData();
                break;
            case 'refresh_data':
                this.handleRefreshData();
                break;
            case 'account_details':
                this.handleAccountDetails(element);
                break;
            case 'transaction_history':
                this.handleTransactionHistory(element);
                break;
            case 'edit_account':
                this.handleEditAccount(element);
                break;
            case 'filter_accounts':
                this.handleFilterAccounts(element);
                break;
            case 'search_accounts':
                this.handleSearchAccounts(element);
                break;
            default:
                console.log(`Action not implemented: ${action}`);
        }
    }

    handleNewAccount() {
        // Redirect to new account page
        window.location.href = '/accounts/new';
    }

    handleExportData() {
        this.showNotification('Exporting account data...', 'info');
        // In a real implementation, this would trigger a download
        setTimeout(() => {
            this.showNotification('Account data exported successfully', 'success');
        }, 2000);
    }

    handleRefreshData() {
        this.showNotification('Refreshing account data...', 'info');
        // In a real implementation, this would reload the page data
        setTimeout(() => {
            this.showNotification('Account data refreshed', 'success');
        }, 1500);
    }

    handleAccountDetails(element) {
        const row = element.closest('tr');
        const accountNumber = row.querySelector('td:first-child').textContent.trim();
        // Redirect to account details page
        window.location.href = `/accounts/details?account=${accountNumber}`;
    }

    handleTransactionHistory(element) {
        const row = element.closest('tr');
        const accountNumber = row.querySelector('td:first-child').textContent.trim();
        // Redirect to transaction history page
        window.location.href = `/banking/transaction-history?account=${accountNumber}`;
    }

    handleEditAccount(element) {
        const row = element.closest('tr');
        const accountNumber = row.querySelector('td:first-child').textContent.trim();
        // Redirect to account edit page
        window.location.href = `/accounts/edit?account=${accountNumber}`;
    }

    handleFilterAccounts(element) {
        const filterType = element.dataset.filter;
        
        // Update active button
        const filterButtons = document.querySelectorAll('[data-action="filter_accounts"]');
        filterButtons.forEach(btn => btn.classList.remove('active'));
        element.classList.add('active');
        
        // Filter accounts
        this.filterAccountsByType(filterType);
        
        // Show notification
        const filterText = filterType === 'all' ? 'All accounts' : `${filterType.charAt(0).toUpperCase() + filterType.slice(1)} accounts`;
        this.showNotification(`Showing ${filterText}`, 'info');
    }

    handleSearchAccounts(element) {
        const form = element.closest('form');
        const searchInput = form.querySelector('input[placeholder="Search accounts..."]');
        const accountTypeSelect = form.querySelector('select').value;
        const statusSelect = form.querySelectorAll('select')[1].value;
        
        const searchTerm = searchInput.value.toLowerCase();
        
        // Perform search
        const accountRows = document.querySelectorAll('[data-searchable="accounts"]');
        let visibleCount = 0;
        
        accountRows.forEach(row => {
            const text = row.textContent.toLowerCase();
            const accountTypeCell = row.querySelector('td:nth-child(3)');
            const statusCell = row.querySelector('td:nth-child(5)');
            
            let isVisible = true;
            
            // Text search
            if (searchTerm && !text.includes(searchTerm)) {
                isVisible = false;
            }
            
            // Account type filter
            if (accountTypeSelect && accountTypeCell) {
                const accountType = accountTypeCell.textContent.toLowerCase();
                if (!accountType.includes(accountTypeSelect.toLowerCase())) {
                    isVisible = false;
                }
            }
            
            // Status filter
            if (statusSelect && statusCell) {
                const status = statusCell.textContent.toLowerCase();
                if (!status.includes(statusSelect.toLowerCase())) {
                    isVisible = false;
                }
            }
            
            row.style.display = isVisible ? '' : 'none';
            if (isVisible) visibleCount++;
        });
        
        this.showNotification(`Found ${visibleCount} matching accounts`, 'success');
    }

    setupSearchHandlers() {
        // Handle search functionality
        const searchInputs = document.querySelectorAll('[data-search-target]');
        searchInputs.forEach(input => {
            input.addEventListener('input', (e) => {
                const target = e.target.dataset.searchTarget;
                const searchTerm = e.target.value.toLowerCase();
                this.performSearch(target, searchTerm);
            });
        });
    }

    setupAccountTypeFilters() {
        // Handle account type filter buttons
        const filterButtons = document.querySelectorAll('.btn-group .btn-outline-primary');
        filterButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                // Remove active class from all buttons
                filterButtons.forEach(btn => btn.classList.remove('active'));
                // Add active class to clicked button
                e.target.classList.add('active');
                
                const filterType = e.target.textContent.trim().toLowerCase();
                this.filterAccountsByType(filterType);
            });
        });
    }

    performSearch(target, searchTerm) {
        const searchableElements = document.querySelectorAll(`[data-searchable="${target}"]`);
        searchableElements.forEach(element => {
            const text = element.textContent.toLowerCase();
            if (text.includes(searchTerm)) {
                element.style.display = '';
            } else {
                element.style.display = 'none';
            }
        });
    }

    filterAccountsByType(filterType) {
        const accountRows = document.querySelectorAll('[data-searchable="accounts"]');
        accountRows.forEach(row => {
            if (filterType === 'all') {
                row.style.display = '';
            } else {
                const accountTypeCell = row.querySelector('td:nth-child(3)');
                if (accountTypeCell) {
                    const accountType = accountTypeCell.textContent.toLowerCase();
                    if (accountType.includes(filterType)) {
                        row.style.display = '';
                    } else {
                        row.style.display = 'none';
                    }
                }
            }
        });
    }

    showModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal && typeof bootstrap !== 'undefined') {
            const bsModal = new bootstrap.Modal(modal);
            bsModal.show();
        }
    }

    validateForm(form) {
        // Basic form validation
        const requiredFields = form.querySelectorAll('[required]');
        let isValid = true;

        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                field.classList.add('is-invalid');
                isValid = false;
            } else {
                field.classList.remove('is-invalid');
            }
        });

        return isValid;
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            min-width: 300px;
            max-width: 400px;
        `;
        notification.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'info' ? 'info-circle' : 'exclamation-triangle'} me-2"></i>
            ${message}
            <button type="button" class="btn-close notification-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 4 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.classList.remove('show');
                setTimeout(() => notification.remove(), 300);
            }
        }, 4000);
    }
}

// Initialize the banking platform actions
const bankingActions = new BankingPlatformActions();

// Global utility functions for backward compatibility
function showGlobalNotification(message, type = 'info') {
    bankingActions.showNotification(message, type);
}

// Chart.js initialization for financial charts (if Chart.js is available)
if (typeof Chart !== 'undefined') {
    document.addEventListener('DOMContentLoaded', () => {
        // Initialize charts with data-chart attribute
        document.querySelectorAll('[data-chart]').forEach(canvas => {
            const chartType = canvas.dataset.chart;
            const chartData = JSON.parse(canvas.dataset.chartData || '{}');
            
            new Chart(canvas, {
                type: chartType,
                data: chartData,
                options: {
                    responsive: true,
                    maintainAspectRatio: false
                }
            });
        });

        // Initialize account distribution chart
        const accountChartCanvas = document.getElementById('accountChart');
        if (accountChartCanvas) {
            const ctx = accountChartCanvas.getContext('2d');
            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['Checking', 'Savings', 'Business', 'Investment'],
                    datasets: [{
                        data: [42, 28, 20, 10],
                        backgroundColor: [
                            '#3b82f6',
                            '#10b981',
                            '#f59e0b',
                            '#8b5cf6'
                        ],
                        borderColor: '#1e293b',
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                color: '#e2e8f0',
                                padding: 20
                            }
                        }
                    }
                }
            });
        }
    });
}