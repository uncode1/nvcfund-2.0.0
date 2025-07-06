#!/usr/bin/env python3
"""
Comprehensive Link Tester for NVC Banking Platform
Tests ALL navigation links, dropdown menus, and interface accessibility
with active super admin session
"""

import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
from urllib.parse import urljoin, urlparse
import time

class ComprehensiveLinkTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.tested_urls = set()
        self.broken_links = []
        self.working_links = []
        self.rendering_issues = []
        self.authentication_issues = []
        
        # Super admin credentials for testing
        self.admin_credentials = {
            'username': 'uncode',
            'password': 'Zx9Wq2@#ComplexCeo'
        }
        
    def authenticate_as_super_admin(self):
        """Login as super admin to access all protected routes"""
        print("Authenticating as Super Admin...")
        
        # Get login page first
        login_url = f"{self.base_url}/auth/login"
        login_page = self.session.get(login_url)
        
        if login_page.status_code != 200:
            print(f"✗ Cannot access login page: {login_page.status_code}")
            return False
            
        # Parse login form
        soup = BeautifulSoup(login_page.content, 'html.parser')
        login_form = soup.find('form')
        
        if not login_form:
            print("✗ No login form found")
            return False
            
        # Extract form action and method
        form_action = login_form.get('action', '/auth/login')
        form_method = login_form.get('method', 'POST').upper()
        
        # Prepare login data
        login_data = self.admin_credentials.copy()
        
        # Add any hidden fields
        hidden_fields = login_form.find_all('input', type='hidden')
        for field in hidden_fields:
            name = field.get('name')
            value = field.get('value', '')
            if name:
                login_data[name] = value
        
        # Submit login
        if form_method == 'POST':
            response = self.session.post(urljoin(self.base_url, form_action), data=login_data)
        else:
            response = self.session.get(urljoin(self.base_url, form_action), params=login_data)
            
        # Check if login was successful
        if response.status_code in [200, 302]:
            # Check if we're redirected or get a success page
            if 'login' not in response.url.lower() or response.status_code == 302:
                print("✓ Super Admin authentication successful")
                return True
            else:
                print("✗ Authentication failed - still on login page")
                return False
        else:
            print(f"✗ Authentication failed: {response.status_code}")
            return False
    
    def extract_all_navigation_links(self, soup, current_url):
        """Extract ALL navigation links including dropdowns"""
        navigation_links = []
        
        # Find all navigation elements
        nav_selectors = [
            'nav a',                    # Standard navigation links
            'header a',                 # Header navigation
            '.navbar a',                # Bootstrap navbar
            '.nav-link',                # Navigation link classes
            '.dropdown-menu a',         # Dropdown menu items
            '.sidebar a',               # Sidebar navigation
            '[role="navigation"] a',    # ARIA navigation
            '.menu a',                  # Menu items
            '.navigation a'             # General navigation
        ]
        
        for selector in nav_selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href')
                text = link.get_text(strip=True)
                
                if href and href not in ['#', 'javascript:void(0)', 'javascript:;']:
                    # Convert relative URLs to absolute
                    full_url = urljoin(current_url, href)
                    
                    # Only test internal links
                    if self.is_internal_link(full_url):
                        navigation_links.append({
                            'url': full_url,
                            'text': text,
                            'selector': selector,
                            'source_page': current_url
                        })
        
        return navigation_links
    
    def is_internal_link(self, url):
        """Check if URL is internal to the platform"""
        parsed = urlparse(url)
        base_parsed = urlparse(self.base_url)
        return parsed.netloc == base_parsed.netloc or not parsed.netloc
    
    def test_single_link(self, link_info):
        """Test a single link for accessibility and rendering"""
        url = link_info['url']
        text = link_info['text']
        
        try:
            response = self.session.get(url, timeout=10, allow_redirects=True)
            
            link_result = {
                'url': url,
                'text': text,
                'source_page': link_info['source_page'],
                'selector': link_info['selector'],
                'status_code': response.status_code,
                'final_url': response.url,
                'accessible': False,
                'rendering_ok': False,
                'has_content': False,
                'issues': []
            }
            
            # Check basic accessibility
            if response.status_code == 200:
                link_result['accessible'] = True
                
                # Parse content for rendering issues
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Check for title
                title = soup.title.string if soup.title else None
                link_result['title'] = title
                
                # Check for basic content
                if soup.body and len(soup.body.get_text(strip=True)) > 100:
                    link_result['has_content'] = True
                
                # Check for error indicators
                error_indicators = [
                    '404', '500', 'error', 'not found', 'internal server error',
                    'page not found', 'something went wrong'
                ]
                
                page_text = soup.get_text().lower()
                if any(error in page_text for error in error_indicators):
                    link_result['issues'].append('Error content detected')
                else:
                    link_result['rendering_ok'] = True
                
                # Check for authentication redirect
                if 'login' in response.url.lower() and 'login' not in url.lower():
                    link_result['issues'].append('Redirected to login (authentication required)')
                    self.authentication_issues.append(link_result)
                
                # Check for empty or minimal content
                if not link_result['has_content']:
                    link_result['issues'].append('Insufficient content')
                    self.rendering_issues.append(link_result)
                
                if link_result['accessible'] and link_result['rendering_ok']:
                    self.working_links.append(link_result)
                    
            else:
                link_result['issues'].append(f'HTTP {response.status_code}')
                self.broken_links.append(link_result)
                
            return link_result
            
        except Exception as e:
            error_result = {
                'url': url,
                'text': text,
                'source_page': link_info['source_page'],
                'error': str(e),
                'accessible': False,
                'issues': [f'Connection error: {str(e)}']
            }
            self.broken_links.append(error_result)
            return error_result
    
    def comprehensive_link_test(self):
        """Perform comprehensive link testing across the platform"""
        print("Starting Comprehensive Link Testing")
        print("=" * 60)
        
        # Authenticate first
        if not self.authenticate_as_super_admin():
            print("Cannot proceed without authentication")
            return None
        
        # Start pages to crawl navigation from
        start_pages = [
            f"{self.base_url}/",
            f"{self.base_url}/dashboard",
            f"{self.base_url}/banking",
            f"{self.base_url}/treasury",
            f"{self.base_url}/trading",
            f"{self.base_url}/admin",
            f"{self.base_url}/compliance"
        ]
        
        all_navigation_links = []
        pages_crawled = 0
        
        # Extract navigation links from each start page
        for page_url in start_pages:
            try:
                print(f"Extracting navigation from: {page_url}")
                response = self.session.get(page_url, timeout=10)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    nav_links = self.extract_all_navigation_links(soup, page_url)
                    
                    # Add unique links only
                    for link in nav_links:
                        if link['url'] not in [l['url'] for l in all_navigation_links]:
                            all_navigation_links.append(link)
                    
                    pages_crawled += 1
                    print(f"  Found {len(nav_links)} navigation links")
                
                time.sleep(0.5)  # Be respectful
                
            except Exception as e:
                print(f"  Error extracting from {page_url}: {e}")
        
        print(f"\nTotal unique navigation links found: {len(all_navigation_links)}")
        print("Starting link testing...")
        print("-" * 40)
        
        # Test each navigation link
        results = []
        for i, link_info in enumerate(all_navigation_links, 1):
            print(f"Testing {i}/{len(all_navigation_links)}: {link_info['text'][:30]}...")
            result = self.test_single_link(link_info)
            results.append(result)
            
            # Progress indicator
            if i % 5 == 0:
                print(f"  Progress: {i}/{len(all_navigation_links)} links tested")
            
            time.sleep(0.3)  # Respectful delay
        
        return {
            'total_links_tested': len(all_navigation_links),
            'pages_crawled': pages_crawled,
            'working_links': len(self.working_links),
            'broken_links': len(self.broken_links),
            'rendering_issues': len(self.rendering_issues),
            'authentication_issues': len(self.authentication_issues),
            'results': results,
            'timestamp': datetime.now().isoformat()
        }
    
    def generate_test_report(self, test_results):
        """Generate comprehensive test report"""
        
        report = f"""# NVC Banking Platform - Comprehensive Link Testing Report

**Test Date**: {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}
**Authentication**: Super Admin (uncode)
**Total Links Tested**: {test_results['total_links_tested']}
**Pages Crawled**: {test_results['pages_crawled']}

## Test Summary

- ✅ **Working Links**: {test_results['working_links']}
- ❌ **Broken Links**: {test_results['broken_links']} 
- ⚠️ **Rendering Issues**: {test_results['rendering_issues']}
- 🔒 **Authentication Issues**: {test_results['authentication_issues']}

---

## Working Links ✅

"""
        
        for link in self.working_links:
            report += f"- **{link['text']}** → {link['url']}\n"
            report += f"  - Status: {link['status_code']}\n"
            report += f"  - Title: {link.get('title', 'No title')}\n"
            report += f"  - Source: {link['source_page']}\n\n"
        
        if self.broken_links:
            report += "## Broken Links ❌\n\n"
            for link in self.broken_links:
                report += f"- **{link['text']}** → {link['url']}\n"
                report += f"  - Issues: {', '.join(link['issues'])}\n"
                report += f"  - Source: {link['source_page']}\n\n"
        
        if self.rendering_issues:
            report += "## Rendering Issues ⚠️\n\n"
            for link in self.rendering_issues:
                report += f"- **{link['text']}** → {link['url']}\n"
                report += f"  - Issues: {', '.join(link['issues'])}\n"
                report += f"  - Status: {link['status_code']}\n\n"
        
        if self.authentication_issues:
            report += "## Authentication Issues 🔒\n\n"
            for link in self.authentication_issues:
                report += f"- **{link['text']}** → {link['url']}\n"
                report += f"  - Issues: {', '.join(link['issues'])}\n"
                report += f"  - Redirected to: {link['final_url']}\n\n"
        
        report += """
---

## Recommendations

1. **Fix Broken Links**: Address any HTTP errors or connection issues
2. **Review Authentication**: Check role-based access controls
3. **Improve Rendering**: Fix pages with insufficient content
4. **Update Navigation**: Remove or fix inaccessible menu items

"""
        
        return report

if __name__ == "__main__":
    tester = ComprehensiveLinkTester()
    
    # Run comprehensive testing
    results = tester.comprehensive_link_test()
    
    if results:
        # Generate and save report
        report = tester.generate_test_report(results)
        
        os.makedirs("logs/2025/07/06/system", exist_ok=True)
        
        # Save detailed data
        with open("logs/2025/07/06/system/comprehensive_link_test.json", "w") as f:
            json.dump(results, f, indent=2)
        
        # Save readable report
        with open("docs/LINK_TESTING_REPORT.md", "w") as f:
            f.write(report)
        
        print("\n" + "=" * 60)
        print("Comprehensive Link Testing Complete!")
        print(f"Working Links: {results['working_links']}")
        print(f"Broken Links: {results['broken_links']}")
        print(f"Issues Found: {results['rendering_issues'] + results['authentication_issues']}")
        print(f"Report: docs/LINK_TESTING_REPORT.md")
        print(f"Data: logs/2025/07/06/system/comprehensive_link_test.json")