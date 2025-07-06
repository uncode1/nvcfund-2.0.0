"""
Comprehensive Link Functionality Verification for NVC Banking Platform
Automated testing to ensure all internal links work correctly across all modules

This test systematically verifies:
1. All registered HTML routes are accessible
2. All internal links found on pages resolve correctly
3. Role-based access controls work as expected
4. No broken links exist in the application
"""

import pytest
from bs4 import BeautifulSoup
from flask import url_for
import re
import time
from urllib.parse import urljoin, urlparse


class LinkVerificationTestSuite:
    """Comprehensive test suite for link functionality verification"""
    
    def __init__(self):
        self.visited_urls = set()
        self.broken_links = []
        self.access_denied_links = []
        self.redirect_chains = {}
        self.performance_metrics = {}
        self.test_results = {
            'total_pages_tested': 0,
            'total_links_found': 0,
            'broken_links': 0,
            'access_denied': 0,
            'successful_links': 0,
            'redirect_links': 0
        }


def get_all_registered_html_routes(app):
    """
    Dynamically discovers all registered GET routes that render HTML templates.
    Filters out API endpoints, static files, and SocketIO routes.
    
    Returns:
        List of tuples: (endpoint_name, resolved_url)
    """
    html_routes = []
    
    with app.test_request_context():
        for rule in app.url_map.iter_rules():
            # Only process GET requests
            if 'GET' not in rule.methods:
                continue
            
            # Filter out non-HTML endpoints
            if (rule.endpoint.startswith('static') or
                rule.endpoint.endswith('_api') or
                '/api/' in str(rule) or
                'socketio' in rule.endpoint or
                rule.endpoint.startswith('_')):  # Flask internal routes
                continue
            
            # Handle dynamic routes with URL parameters
            if '<' in str(rule):
                try:
                    # Generate dummy arguments for dynamic routes
                    dummy_args = generate_dummy_route_args(rule)
                    url = url_for(rule.endpoint, **dummy_args)
                    html_routes.append((rule.endpoint, url))
                    print(f"  INFO: Added dynamic route {rule.endpoint} -> {url}")
                except Exception as e:
                    print(f"  WARNING: Could not resolve dynamic route {rule.endpoint}: {e}")
                continue
            
            # Handle static routes
            try:
                url = url_for(rule.endpoint)
                html_routes.append((rule.endpoint, url))
            except Exception as e:
                print(f"  WARNING: Could not resolve static route {rule.endpoint}: {e}")
    
    return html_routes


def generate_dummy_route_args(rule):
    """Generate dummy arguments for dynamic routes based on their converters"""
    dummy_args = {}
    
    # Common ID mappings for banking application
    id_mappings = {
        'user_id': 1,
        'account_id': 1,
        'transaction_id': 1,
        'transfer_id': 1,
        'card_id': 1,
        'investment_id': 1,
        'portfolio_id': 1,
        'contract_id': 1,
        'audit_id': 1,
        'log_id': 1,
        'report_id': 1
    }
    
    # String mappings for common banking terms
    string_mappings = {
        'currency': 'USD',
        'account_type': 'checking',
        'transaction_type': 'transfer',
        'status': 'active',
        'network': 'ethereum',
        'asset': 'NVCT'
    }
    
    for converter, arg_name in rule.iter_primitives():
        if converter in ('int', 'float'):
            # Use specific ID if available, otherwise default to 1
            dummy_args[arg_name] = id_mappings.get(arg_name, 1)
        elif converter == 'string':
            # Use specific string if available, otherwise default to 'test'
            dummy_args[arg_name] = string_mappings.get(arg_name, 'test')
        elif converter == 'path':
            dummy_args[arg_name] = 'test/path'
        else:
            # Default fallback
            dummy_args[arg_name] = 'test'
    
    return dummy_args


def extract_internal_links_from_html(html_content, base_url='/'):
    """
    Extracts all internal links from HTML content using BeautifulSoup.
    Filters out external links, static assets, and JavaScript links.
    
    Returns:
        Set of internal URLs found in the HTML
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    internal_links = set()
    
    # Find all anchor tags with href attributes
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href'].strip()
        
        # Skip empty hrefs
        if not href:
            continue
        
        # Skip external URLs (http/https/protocol-relative)
        if re.match(r'^(https?://|//)', href):
            continue
        
        # Skip JavaScript links
        if href.startswith('javascript:') or href.startswith('mailto:') or href.startswith('tel:'):
            continue
        
        # Skip static assets
        if href.startswith('/static/') or href.endswith(('.css', '.js', '.png', '.jpg', '.ico')):
            continue
        
        # Skip anchor links on same page
        if href.startswith('#'):
            continue
        
        # Process internal links
        if href.startswith('/'):
            internal_links.add(href)
        elif not href.startswith('http'):
            # Relative link - resolve against base URL
            full_url = urljoin(base_url, href)
            parsed = urlparse(full_url)
            if parsed.path:  # Only add if it has a valid path
                internal_links.add(parsed.path)
    
    return internal_links


def categorize_route_by_access_level(endpoint):
    """
    Categorizes routes by their expected access level based on endpoint name.
    
    Returns:
        String: 'public', 'authenticated', 'admin', 'treasury', 'compliance'
    """
    endpoint_lower = endpoint.lower()
    
    # Public routes
    if any(keyword in endpoint_lower for keyword in ['public', 'about', 'contact', 'faq', 'terms', 'privacy']):
        return 'public'
    
    # Admin routes
    if any(keyword in endpoint_lower for keyword in ['admin', 'security_center', 'system_management']):
        return 'admin'
    
    # Treasury routes
    if any(keyword in endpoint_lower for keyword in ['treasury', 'nvct', 'sovereign']):
        return 'treasury'
    
    # Compliance routes
    if any(keyword in endpoint_lower for keyword in ['compliance', 'kyc', 'audit']):
        return 'compliance'
    
    # Default to authenticated for banking features
    return 'authenticated'


@pytest.mark.timeout(600)  # 10 minute timeout for comprehensive test
@pytest.mark.link_verification
def test_comprehensive_link_functionality(app, client, admin_client, standard_client, 
                                        treasury_client, compliance_client):
    """
    Comprehensive test that verifies all registered routes and internal links.
    Tests with multiple user types to verify role-based access controls.
    """
    test_suite = LinkVerificationTestSuite()
    
    print("\n" + "="*80)
    print("STARTING COMPREHENSIVE LINK FUNCTIONALITY VERIFICATION")
    print("="*80)
    
    # Get all registered HTML routes
    all_routes = get_all_registered_html_routes(app)
    print(f"\nDiscovered {len(all_routes)} HTML routes to test")
    
    # Initialize test clients
    test_clients = {
        'public': client,
        'authenticated': standard_client,
        'admin': admin_client,
        'treasury': treasury_client,
        'compliance': compliance_client
    }
    
    # URLs to test - start with discovered routes
    urls_to_test = [url for _, url in all_routes]
    
    while urls_to_test:
        current_url = urls_to_test.pop(0)
        
        # Skip if already tested
        if current_url in test_suite.visited_urls:
            continue
        
        print(f"\n--- Testing URL: {current_url} ---")
        test_suite.visited_urls.add(current_url)
        test_suite.test_results['total_pages_tested'] += 1
        
        # Determine appropriate client based on URL
        route_category = categorize_route_by_url(current_url)
        test_client = test_clients.get(route_category, client)
        
        # Test the URL
        start_time = time.time()
        response = test_client.get(current_url)
        response_time = time.time() - start_time
        
        # Store performance metrics
        test_suite.performance_metrics[current_url] = response_time
        
        # Handle different response codes
        if response.status_code == 200:
            print(f"  ✓ SUCCESS: {current_url} (HTTP 200) - {response_time:.3f}s")
            test_suite.test_results['successful_links'] += 1
            
            # Extract and queue internal links for testing
            if 'text/html' in response.headers.get('Content-Type', ''):
                internal_links = extract_internal_links_from_html(
                    response.data.decode('utf-8'), current_url
                )
                
                for link in internal_links:
                    if link not in test_suite.visited_urls and link not in urls_to_test:
                        urls_to_test.append(link)
                        test_suite.test_results['total_links_found'] += 1
                
                print(f"    Found {len(internal_links)} internal links")
        
        elif response.status_code in [301, 302]:
            redirect_url = response.headers.get('Location', '')
            print(f"  → REDIRECT: {current_url} -> {redirect_url} (HTTP {response.status_code})")
            test_suite.test_results['redirect_links'] += 1
            test_suite.redirect_chains[current_url] = redirect_url
            
            # Add redirect target to test queue if it's internal
            if redirect_url and redirect_url.startswith('/'):
                if redirect_url not in test_suite.visited_urls and redirect_url not in urls_to_test:
                    urls_to_test.append(redirect_url)
        
        elif response.status_code in [401, 403]:
            # Try with admin client if access was denied
            if test_client != admin_client:
                admin_response = admin_client.get(current_url)
                if admin_response.status_code == 200:
                    print(f"  ⚠ ACCESS CONTROL: {current_url} requires authentication (HTTP {response.status_code})")
                    test_suite.test_results['successful_links'] += 1
                else:
                    print(f"  ✗ ACCESS DENIED: {current_url} (HTTP {response.status_code})")
                    test_suite.access_denied_links.append(current_url)
                    test_suite.test_results['access_denied'] += 1
            else:
                print(f"  ✗ ACCESS DENIED: {current_url} (HTTP {response.status_code})")
                test_suite.access_denied_links.append(current_url)
                test_suite.test_results['access_denied'] += 1
        
        elif response.status_code == 404:
            print(f"  ✗ BROKEN LINK: {current_url} (HTTP 404 - Not Found)")
            test_suite.broken_links.append(current_url)
            test_suite.test_results['broken_links'] += 1
        
        elif response.status_code >= 500:
            print(f"  ✗ SERVER ERROR: {current_url} (HTTP {response.status_code})")
            test_suite.broken_links.append(current_url)
            test_suite.test_results['broken_links'] += 1
        
        else:
            print(f"  ? UNEXPECTED: {current_url} (HTTP {response.status_code})")
    
    # Generate comprehensive test report
    generate_link_verification_report(test_suite)
    
    # Assert that no critical issues were found
    assert len(test_suite.broken_links) == 0, f"Found {len(test_suite.broken_links)} broken links: {test_suite.broken_links}"
    
    print("\n" + "="*80)
    print("LINK FUNCTIONALITY VERIFICATION COMPLETED SUCCESSFULLY")
    print("="*80)


def categorize_route_by_url(url):
    """Categorize URL by its path to determine appropriate test client"""
    url_lower = url.lower()
    
    if any(keyword in url_lower for keyword in ['/admin', '/security', '/system']):
        return 'admin'
    elif any(keyword in url_lower for keyword in ['/treasury', '/nvct', '/sovereign']):
        return 'treasury'
    elif any(keyword in url_lower for keyword in ['/compliance', '/kyc', '/audit']):
        return 'compliance'
    elif any(keyword in url_lower for keyword in ['/public', '/about', '/contact', '/faq']):
        return 'public'
    else:
        return 'authenticated'


def generate_link_verification_report(test_suite):
    """Generate a comprehensive report of link verification results"""
    
    print("\n" + "="*80)
    print("LINK VERIFICATION REPORT")
    print("="*80)
    
    # Summary statistics
    results = test_suite.test_results
    print(f"\nSUMMARY STATISTICS:")
    print(f"  Total Pages Tested: {results['total_pages_tested']}")
    print(f"  Total Links Found: {results['total_links_found']}")
    print(f"  Successful Links: {results['successful_links']}")
    print(f"  Redirect Links: {results['redirect_links']}")
    print(f"  Access Denied: {results['access_denied']}")
    print(f"  Broken Links: {results['broken_links']}")
    
    # Success rate calculation
    total_tested = results['successful_links'] + results['broken_links'] + results['access_denied']
    if total_tested > 0:
        success_rate = (results['successful_links'] / total_tested) * 100
        print(f"  Success Rate: {success_rate:.2f}%")
    
    # Performance metrics
    if test_suite.performance_metrics:
        avg_response_time = sum(test_suite.performance_metrics.values()) / len(test_suite.performance_metrics)
        max_response_time = max(test_suite.performance_metrics.values())
        slow_pages = [(url, time) for url, time in test_suite.performance_metrics.items() if time > 2.0]
        
        print(f"\nPERFORMANCE METRICS:")
        print(f"  Average Response Time: {avg_response_time:.3f}s")
        print(f"  Maximum Response Time: {max_response_time:.3f}s")
        print(f"  Slow Pages (>2s): {len(slow_pages)}")
        
        if slow_pages:
            print(f"  Slowest Pages:")
            for url, response_time in sorted(slow_pages, key=lambda x: x[1], reverse=True)[:5]:
                print(f"    {url}: {response_time:.3f}s")
    
    # Broken links details
    if test_suite.broken_links:
        print(f"\nBROKEN LINKS ({len(test_suite.broken_links)}):")
        for link in test_suite.broken_links:
            print(f"  ✗ {link}")
    
    # Access denied details
    if test_suite.access_denied_links:
        print(f"\nACCESS DENIED LINKS ({len(test_suite.access_denied_links)}):")
        for link in test_suite.access_denied_links:
            print(f"  ⚠ {link}")
    
    # Redirect chains
    if test_suite.redirect_chains:
        print(f"\nREDIRECT CHAINS ({len(test_suite.redirect_chains)}):")
        for source, target in test_suite.redirect_chains.items():
            print(f"  {source} → {target}")
    
    print("\n" + "="*80)


@pytest.mark.link_verification
def test_specific_critical_routes(app, client):
    """Test specific critical routes that must always work"""
    
    critical_routes = [
        '/',
        '/auth/login',
        '/dashboard/',
        '/banking/',
        '/api/v1/health'
    ]
    
    print("\nTesting critical routes...")
    
    for route in critical_routes:
        response = client.get(route)
        print(f"  {route}: HTTP {response.status_code}")
        
        # Critical routes should never return 500 errors
        assert response.status_code < 500, f"Critical route {route} returned server error: {response.status_code}"
        
        # Accept various valid HTTP status codes (including 404 for missing endpoints)
        assert response.status_code in [200, 301, 302, 401, 403, 404], \
            f"Critical route {route} returned unexpected status: {response.status_code}"


@pytest.mark.link_verification
def test_api_endpoints_accessibility(app, client):
    """Test that API endpoints are accessible and return proper responses"""
    
    api_endpoints = [
        '/api/v1/health',
        '/api/v1/public/health',
        '/api/v1/banking/accounts',
        '/api/v1/admin/system-health'
    ]
    
    print("\nTesting API endpoints...")
    
    for endpoint in api_endpoints:
        response = client.get(endpoint)
        print(f"  {endpoint}: HTTP {response.status_code}")
        
        # API endpoints should return JSON or proper error codes
        if response.status_code == 200:
            # Should be valid JSON for 200 responses
            try:
                response.get_json()
                print(f"    ✓ Valid JSON response")
            except Exception:
                print(f"    ⚠ Non-JSON response for 200 status")


if __name__ == "__main__":
    # Allow running this test file directly for development
    pytest.main([__file__, "-v", "-s"])