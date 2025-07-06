import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import apiService from '../services/api';
import { useErrorHandler } from '../components/GlobalErrorHandler';

const PaymentFeaturesPage = () => {
    const [paymentData, setPaymentData] = useState(null);
    const [paymentLimits, setPaymentLimits] = useState(null);
    const [availableGateways, setAvailableGateways] = useState(null);
    const [feeCalculation, setFeeCalculation] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [amount, setAmount] = useState('1000.00');
    const [transactionType, setTransactionType] = useState('domestic_transfer');
    const { handleError } = useErrorHandler();

    useEffect(() => {
        loadPaymentData();
    }, []);

    const loadPaymentData = async () => {
        try {
            setIsLoading(true);
            
            // Load payment features, limits, and gateways in parallel
            const [featuresResponse, limitsResponse, gatewaysResponse] = await Promise.all([
                apiService.get('/banking/payment-features'),
                apiService.get('/banking/payment-limits'),
                apiService.get('/banking/available-gateways')
            ]);

            setPaymentData(featuresResponse.data);
            setPaymentLimits(limitsResponse.data);
            setAvailableGateways(gatewaysResponse.data);
        } catch (error) {
            handleError(error, 'Failed to load payment information');
        } finally {
            setIsLoading(false);
        }
    };

    const calculateFee = async () => {
        try {
            const response = await apiService.post('/banking/calculate-fee', {
                amount: amount,
                transaction_type: transactionType
            });
            setFeeCalculation(response.data);
        } catch (error) {
            handleError(error, 'Failed to calculate transaction fee');
        }
    };

    const handleStripeCheckout = async () => {
        try {
            if (!amount || parseFloat(amount) <= 0) {
                alert('Please enter a valid amount');
                return;
            }

            const response = await apiService.post('/banking/create-stripe-checkout', {
                amount: amount,
                transaction_type: transactionType,
                description: `${transactionType.replace('_', ' ')} for $${amount}`
            });

            if (response.status === 'success') {
                const checkoutData = response.data;
                
                // In production, this would redirect to the actual Stripe checkout URL
                const confirmPayment = window.confirm(
                    `Stripe Checkout Details:\n\n` +
                    `Amount: $${checkoutData.amount}\n` +
                    `Fee: $${checkoutData.fee}\n` +
                    `Total: $${checkoutData.total_amount}\n` +
                    `Account Type: ${checkoutData.account_type}\n` +
                    `Gateway: ${checkoutData.gateway}\n\n` +
                    `In production, you would be redirected to:\n${checkoutData.checkout_url}\n\n` +
                    `Click OK to simulate successful payment.`
                );

                if (confirmPayment) {
                    alert('Payment simulation completed successfully!\n\nIn production, Stripe would handle the actual payment processing.');
                }
            }
        } catch (error) {
            handleError(error, 'Failed to create Stripe checkout session');
        }
    };

    const transactionTypes = [
        { value: 'domestic_transfer', label: 'Domestic Transfer' },
        { value: 'international_transfer', label: 'International Transfer' },
        { value: 'card_transaction', label: 'Card Transaction' },
        { value: 'cryptocurrency', label: 'Cryptocurrency' },
        { value: 'wire_transfer', label: 'Wire Transfer' }
    ];

    const formatCurrency = (amount) => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(amount);
    };

    const getFeatureStatus = (available) => {
        return available ? (
            <span className="badge bg-success">Available</span>
        ) : (
            <span className="badge bg-secondary">Not Available</span>
        );
    };

    if (isLoading) {
        return (
            <div className="container py-4">
                <div className="text-center">
                    <div className="spinner-border text-primary" role="status">
                        <span className="visually-hidden">Loading payment features...</span>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="container py-4">
            <div className="row">
                <div className="col-md-12">
                    <div className="d-flex justify-content-between align-items-center mb-4">
                        <h1 className="mb-0">Payment Features</h1>
                        <nav aria-label="breadcrumb">
                            <ol className="breadcrumb mb-0">
                                <li className="breadcrumb-item"><Link to="/dashboard">Dashboard</Link></li>
                                <li className="breadcrumb-item active">Payment Features</li>
                            </ol>
                        </nav>
                    </div>

                    {/* Account Type Summary */}
                    {paymentData && (
                        <div className="card mb-4">
                            <div className="card-header bg-primary text-white">
                                <h5 className="mb-0">Account Type: {paymentData.account_type.replace('_', ' ').toUpperCase()}</h5>
                            </div>
                            <div className="card-body">
                                <div className="row">
                                    <div className="col-md-4">
                                        <p><strong>Payment Tier:</strong> {paymentData.payment_tier.toUpperCase()}</p>
                                        <p><strong>Available Gateways:</strong> {paymentData.gateway_count}</p>
                                        <p><strong>Supported Card Types:</strong> {paymentData.supported_card_types}</p>
                                    </div>
                                    <div className="col-md-8">
                                        <h6>Available Payment Gateways:</h6>
                                        <div className="d-flex flex-wrap gap-2">
                                            {paymentData.features.available_gateways.map(gateway => (
                                                <span key={gateway} className="badge bg-info text-dark">
                                                    {gateway.toUpperCase()}
                                                </span>
                                            ))}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    <div className="row">
                        {/* Payment Features */}
                        <div className="col-md-6">
                            <div className="card mb-4">
                                <div className="card-header">
                                    <h5 className="mb-0">Payment Features</h5>
                                </div>
                                <div className="card-body">
                                    {paymentData && (
                                        <div>
                                            <div className="row mb-3">
                                                <div className="col-8">International Transfers</div>
                                                <div className="col-4 text-end">
                                                    {getFeatureStatus(paymentData.features.international_transfers)}
                                                </div>
                                            </div>
                                            <div className="row mb-3">
                                                <div className="col-8">Cryptocurrency Support</div>
                                                <div className="col-4 text-end">
                                                    {getFeatureStatus(paymentData.features.cryptocurrency_support)}
                                                </div>
                                            </div>
                                            <div className="row mb-3">
                                                <div className="col-8">Priority Processing</div>
                                                <div className="col-4 text-end">
                                                    {getFeatureStatus(paymentData.features.priority_processing)}
                                                </div>
                                            </div>
                                            <div className="row mb-3">
                                                <div className="col-8">API Access</div>
                                                <div className="col-4 text-end">
                                                    {getFeatureStatus(paymentData.features.api_access)}
                                                </div>
                                            </div>
                                            <div className="row mb-3">
                                                <div className="col-8">Bulk Payments</div>
                                                <div className="col-4 text-end">
                                                    {getFeatureStatus(paymentData.features.bulk_payments)}
                                                </div>
                                            </div>
                                            <div className="row mb-3">
                                                <div className="col-8">Advanced Reporting</div>
                                                <div className="col-4 text-end">
                                                    {getFeatureStatus(paymentData.features.advanced_reporting)}
                                                </div>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>

                        {/* Payment Limits */}
                        <div className="col-md-6">
                            <div className="card mb-4">
                                <div className="card-header">
                                    <h5 className="mb-0">Payment Limits</h5>
                                </div>
                                <div className="card-body">
                                    {paymentLimits && (
                                        <div>
                                            <div className="row mb-3">
                                                <div className="col-8">Daily Transfer</div>
                                                <div className="col-4 text-end">
                                                    <strong>{formatCurrency(paymentLimits.limits.daily_transfer)}</strong>
                                                </div>
                                            </div>
                                            <div className="row mb-3">
                                                <div className="col-8">Monthly Transfer</div>
                                                <div className="col-4 text-end">
                                                    <strong>{formatCurrency(paymentLimits.limits.monthly_transfer)}</strong>
                                                </div>
                                            </div>
                                            <div className="row mb-3">
                                                <div className="col-8">Single Transaction</div>
                                                <div className="col-4 text-end">
                                                    <strong>{formatCurrency(paymentLimits.limits.single_transaction)}</strong>
                                                </div>
                                            </div>
                                            <div className="row mb-3">
                                                <div className="col-8">International Transfer</div>
                                                <div className="col-4 text-end">
                                                    <strong>{formatCurrency(paymentLimits.limits.international)}</strong>
                                                </div>
                                            </div>
                                            <div className="row mb-3">
                                                <div className="col-8">Cryptocurrency</div>
                                                <div className="col-4 text-end">
                                                    <strong>{formatCurrency(paymentLimits.limits.cryptocurrency)}</strong>
                                                </div>
                                            </div>
                                            <div className="row mb-3">
                                                <div className="col-8">Wire Transfer</div>
                                                <div className="col-4 text-end">
                                                    <strong>{formatCurrency(paymentLimits.limits.wire_transfer)}</strong>
                                                </div>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Fee Calculator */}
                    <div className="card mb-4">
                        <div className="card-header">
                            <h5 className="mb-0">Transaction Fee Calculator</h5>
                        </div>
                        <div className="card-body">
                            <div className="row">
                                <div className="col-md-4">
                                    <div className="mb-3">
                                        <label className="form-label">Amount</label>
                                        <input
                                            type="number"
                                            className="form-control"
                                            value={amount}
                                            onChange={(e) => setAmount(e.target.value)}
                                            min="0"
                                            step="0.01"
                                        />
                                    </div>
                                </div>
                                <div className="col-md-4">
                                    <div className="mb-3">
                                        <label className="form-label">Transaction Type</label>
                                        <select
                                            className="form-select"
                                            value={transactionType}
                                            onChange={(e) => setTransactionType(e.target.value)}
                                        >
                                            {transactionTypes.map(type => (
                                                <option key={type.value} value={type.value}>
                                                    {type.label}
                                                </option>
                                            ))}
                                        </select>
                                    </div>
                                </div>
                                <div className="col-md-4 d-flex align-items-end">
                                    <button
                                        className="btn btn-primary mb-3"
                                        onClick={calculateFee}
                                    >
                                        Calculate Fee
                                    </button>
                                </div>
                            </div>

                            {feeCalculation && (
                                <div className="alert alert-info mt-3">
                                    <h6>Fee Calculation Results:</h6>
                                    <div className="row">
                                        <div className="col-md-3">
                                            <strong>Amount:</strong><br/>
                                            {formatCurrency(feeCalculation.amount)}
                                        </div>
                                        <div className="col-md-3">
                                            <strong>Fee Rate:</strong><br/>
                                            {feeCalculation.fee_percentage}%
                                        </div>
                                        <div className="col-md-3">
                                            <strong>Fee:</strong><br/>
                                            {formatCurrency(feeCalculation.calculated_fee)}
                                        </div>
                                        <div className="col-md-3">
                                            <strong>Total:</strong><br/>
                                            <span className="text-primary fw-bold">
                                                {formatCurrency(feeCalculation.total_amount)}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Payment Gateway Integration */}
                    <div className="card mb-4">
                        <div className="card-header">
                            <h5 className="mb-0">Payment Gateway Integration</h5>
                        </div>
                        <div className="card-body">
                            <div className="row">
                                {availableGateways && availableGateways.available_gateways.map(gateway => (
                                    <div key={gateway} className="col-md-4 mb-3">
                                        <div className="card border">
                                            <div className="card-body text-center">
                                                <h6 className="card-title">{gateway.toUpperCase()}</h6>
                                                {gateway === 'stripe' && (
                                                    <button
                                                        className="btn btn-outline-primary"
                                                        onClick={handleStripeCheckout}
                                                    >
                                                        Pay with Stripe
                                                    </button>
                                                )}
                                                {gateway === 'paypal' && (
                                                    <button className="btn btn-outline-info">
                                                        Pay with PayPal
                                                    </button>
                                                )}
                                                {gateway === 'flutterwave' && (
                                                    <button className="btn btn-outline-success">
                                                        Pay with Flutterwave
                                                    </button>
                                                )}
                                                {!['stripe', 'paypal', 'flutterwave'].includes(gateway) && (
                                                    <button className="btn btn-outline-secondary">
                                                        {gateway.replace('_', ' ').toUpperCase()}
                                                    </button>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>

                            <div className="mt-4">
                                <h6>Account Type Upgrade Benefits</h6>
                                <div className="alert alert-warning">
                                    <p className="mb-1">
                                        <strong>Business Client Account:</strong> Access to 3+ gateways, higher limits, cryptocurrency support
                                    </p>
                                    <p className="mb-0">
                                        <strong>Partner Program:</strong> Access to 5+ gateways, unlimited limits, institutional features
                                    </p>
                                    <Link to="/account-upgrade" className="btn btn-sm btn-warning mt-2">
                                        Upgrade Account
                                    </Link>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default PaymentFeaturesPage;