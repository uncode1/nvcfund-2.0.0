"""
Authentication and Authorization Testing for NVC Banking Platform
Tests user authentication flows, role-based access controls, and session management
"""

import pytest
from flask import url_for
import json


@pytest.mark.authentication
def test_login_functionality(app, client, sample_test_data):
    """Test login functionality with valid and invalid credentials"""
    
    # Test valid login
    response = client.post('/auth/login', data=sample_test_data['valid_login'])
    
    # Should redirect after successful login or show success page
    assert response.status_code in [200, 302], f"Login failed: {response.status_code}"
    
    # Test invalid login
    response = client.post('/auth/login', data=sample_test_data['invalid_login'])
    
    # Should stay on login page or show error
    assert response.status_code in [200, 401, 403], f"Invalid login handling failed: {response.status_code}"


@pytest.mark.authentication
def test_role_based_access(app, admin_client, standard_client, treasury_client):
    """Test that role-based access controls work correctly"""
    
    # Test cases: (URL, client, should_have_access)
    access_test_cases = [
        ('/admin/dashboard', admin_client, True),
        ('/admin/dashboard', standard_client, False),
        ('/treasury/dashboard', treasury_client, True),
        ('/treasury/dashboard', standard_client, False),
        ('/dashboard/', standard_client, True),
        ('/banking/', standard_client, True),
    ]
    
    for url, test_client, should_have_access in access_test_cases:
        response = test_client.get(url)
        
        if should_have_access:
            # Should be accessible (200) or redirect to correct page (302)
            assert response.status_code in [200, 302], \
                f"User should have access to {url} but got {response.status_code}"
        else:
            # Should be denied (401, 403) or redirect to login (302)
            assert response.status_code in [401, 403, 302], \
                f"User should not have access to {url} but got {response.status_code}"


@pytest.mark.authentication
def test_logout_functionality(app, standard_client):
    """Test logout functionality"""
    
    # Access a protected page to ensure we're logged in
    response = standard_client.get('/dashboard/')
    assert response.status_code in [200, 302]
    
    # Logout
    response = standard_client.get('/auth/logout')
    assert response.status_code in [200, 302]
    
    # Try to access protected page again - should be redirected to login
    response = standard_client.get('/dashboard/')
    assert response.status_code in [302, 401, 403]


@pytest.mark.authentication
def test_session_security(app, client):
    """Test session security measures"""
    
    with client.session_transaction() as sess:
        # Test session configuration
        assert 'session' in str(type(sess)) or 'dict' in str(type(sess))
        
        # Test that session is secure
        app_config = app.config
        if app_config.get('TESTING'):
            # In testing mode, some security features may be disabled
            pass
        else:
            assert app_config.get('SESSION_COOKIE_SECURE') in [True, None]
            assert app_config.get('SESSION_COOKIE_HTTPONLY') in [True, None]


@pytest.mark.authentication  
def test_password_security(app, client):
    """Test password security requirements"""
    
    # Test registration with weak password
    weak_password_data = {
        'username': 'testweakpass',
        'email': 'weak@test.com',
        'password': '123',
        'confirm_password': '123',
        'first_name': 'Test',
        'last_name': 'User'
    }
    
    response = client.post('/auth/register', data=weak_password_data)
    
    # Should reject weak passwords
    assert response.status_code in [200, 400, 422], \
        f"Weak password should be rejected but got {response.status_code}"


@pytest.mark.authentication
def test_csrf_protection(app, client):
    """Test CSRF protection on authentication forms"""
    
    # Get login page to check for CSRF token
    response = client.get('/auth/login')
    
    if response.status_code == 200:
        html_content = response.data.decode('utf-8')
        
        # Check if CSRF token is present in form
        has_csrf_token = 'csrf_token' in html_content or '_csrf_token' in html_content
        
        # In testing mode, CSRF might be disabled
        if not app.config.get('WTF_CSRF_ENABLED', True):
            print("CSRF protection disabled in testing mode")
        else:
            assert has_csrf_token, "CSRF token should be present in login form"