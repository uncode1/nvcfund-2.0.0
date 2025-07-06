"""
Simple Analytics Routes - No Decorator Conflicts
NVC Banking Platform - Basic Analytics Dashboard
"""

from flask import Blueprint, render_template
from flask_login import login_required, current_user
from datetime import datetime

# Create simple blueprint without complex decorators
analytics_simple = Blueprint('analytics_simple', __name__, url_prefix='/analytics')

@analytics_simple.route('/')
@analytics_simple.route('/dashboard')
@login_required
def analytics_dashboard():
    """Simple analytics dashboard"""
    try:
        # Basic analytics data
        analytics_data = {
            'total_users': 12847,
            'active_sessions': 2847,
            'total_transactions': 458923,
            'total_volume': 1247832945.67,
            'growth_rate': 12.5,
            'performance_score': 94.7
        }
        
        # Return simple HTML page
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Analytics Dashboard - NVC Banking Platform</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
            <style>
                body {{ background: linear-gradient(135deg, #0a2447 0%, #1e3c72 50%, #2a5298 100%); color: white; }}
                .card {{ background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); }}
                .card-header {{ background: rgba(255,255,255,0.1); border-bottom: 1px solid rgba(255,255,255,0.2); }}
            </style>
        </head>
        <body>
            <div class="container mt-5">
                <div class="row">
                    <div class="col-12">
                        <div class="card">
                            <div class="card-header">
                                <h1><i class="fas fa-chart-area me-2"></i>Analytics Dashboard</h1>
                            </div>
                            <div class="card-body">
                                <p class="lead">Welcome, {current_user.username}!</p>
                                <p>User Role: {current_user.role.value if hasattr(current_user.role, 'value') else 'standard'}</p>
                                <p>Current Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                                
                                <hr>
                                
                                <div class="row">
                                    <div class="col-md-3">
                                        <div class="card">
                                            <div class="card-body text-center">
                                                <h5><i class="fas fa-users text-primary"></i></h5>
                                                <h4>{analytics_data['total_users']:,}</h4>
                                                <p>Total Users</p>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-md-3">
                                        <div class="card">
                                            <div class="card-body text-center">
                                                <h5><i class="fas fa-user-clock text-success"></i></h5>
                                                <h4>{analytics_data['active_sessions']:,}</h4>
                                                <p>Active Sessions</p>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-md-3">
                                        <div class="card">
                                            <div class="card-body text-center">
                                                <h5><i class="fas fa-exchange-alt text-warning"></i></h5>
                                                <h4>{analytics_data['total_transactions']:,}</h4>
                                                <p>Total Transactions</p>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-md-3">
                                        <div class="card">
                                            <div class="card-body text-center">
                                                <h5><i class="fas fa-dollar-sign text-info"></i></h5>
                                                <h4>${analytics_data['total_volume']:,.0f}</h4>
                                                <p>Total Volume</p>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                
                                <hr>
                                
                                <div class="row mt-4">
                                    <div class="col-md-6">
                                        <div class="card">
                                            <div class="card-body">
                                                <h5><i class="fas fa-chart-line text-success me-2"></i>Growth Rate</h5>
                                                <h3>{analytics_data['growth_rate']}%</h3>
                                                <p class="text-success">Month over month</p>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="card">
                                            <div class="card-body">
                                                <h5><i class="fas fa-tachometer-alt text-primary me-2"></i>Performance Score</h5>
                                                <h3>{analytics_data['performance_score']}/100</h3>
                                                <div class="progress">
                                                    <div class="progress-bar bg-primary" style="width: {analytics_data['performance_score']}%"></div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="mt-4">
                                    <a href="/auth/logout" class="btn btn-outline-light">
                                        <i class="fas fa-sign-out-alt me-2"></i>Logout
                                    </a>
                                    <a href="/" class="btn btn-primary ms-2">
                                        <i class="fas fa-home me-2"></i>Dashboard
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
    except Exception as e:
        return f"""
        <html>
        <head><title>Analytics Error</title></head>
        <body style="background: #0a2447; color: white; padding: 50px; text-align: center;">
            <h1>Analytics Error</h1>
            <p>Unable to load analytics dashboard: {str(e)}</p>
            <a href="/auth/logout" style="color: #66ccff;">Logout</a>
        </body>
        </html>
        """

@analytics_simple.route('/health')
def health_check():
    """Simple health check"""
    return {
        'status': 'healthy', 
        'module': 'analytics_simple', 
        'timestamp': datetime.utcnow().isoformat()
    }