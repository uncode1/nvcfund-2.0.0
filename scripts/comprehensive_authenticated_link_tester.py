#!/usr/bin/env python3
"""
Comprehensive Authenticated Link Tester for NVC Banking Platform
Uses Playwright to test all navigation links with proper authentication
"""

import asyncio
from playwright.async_api import async_playwright
import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuthenticatedLinkTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.tested_links = set()
        self.working_links = []
        self.broken_links = []
        self.redirected_links = []
        
    async def authenticate(self, page):
        """Authenticate as super admin"""
        try:
            await page.goto(f"{self.base_url}/auth/login")
            await page.wait_for_load_state("networkidle")
            
            # Fill login form
            await page.fill('input[name="username"]', 'uncode')
            await page.fill('input[name="password"]', 'Zx9Wq2@#ComplexCeo')
            await page.click('button[type="submit"]')
            
            # Wait for redirect after login
            await page.wait_for_load_state("networkidle")
            
            # Verify authentication
            current_url = page.url
            if 'login' in current_url:
                logger.error("Authentication failed - still on login page")
                return False
            
            logger.info(f"Successfully authenticated, redirected to: {current_url}")
            return True
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False
    
    async def test_navigation_links(self, page):
        """Test all navigation links including dropdown menus"""
        try:
            # Go to homepage to ensure we're in authenticated state
            await page.goto(self.base_url)
            await page.wait_for_load_state("networkidle")
            
            # Extract all navigation links
            nav_links = await page.locator('nav a, .dropdown-menu a').all()
            
            logger.info(f"Found {len(nav_links)} navigation links to test")
            
            for link in nav_links:
                try:
                    href = await link.get_attribute('href')
                    text = await link.text_content()
                    
                    if not href or href.startswith(('http://', 'https://', 'mailto:', 'tel:', '#')):
                        continue
                        
                    # Skip already tested links
                    if href in self.tested_links:
                        continue
                        
                    self.tested_links.add(href)
                    
                    logger.info(f"Testing link: {text} -> {href}")
                    
                    # Test the link
                    result = await self.test_single_link(page, href, text)
                    
                    if result['status'] == 'working':
                        self.working_links.append(result)
                    elif result['status'] == 'redirected':
                        self.redirected_links.append(result)
                    else:
                        self.broken_links.append(result)
                        
                except Exception as e:
                    logger.error(f"Error testing navigation link: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error extracting navigation links: {e}")
    
    async def test_single_link(self, page, href, text):
        """Test a single link and return detailed results"""
        try:
            # Navigate to the link
            response = await page.goto(f"{self.base_url}{href}")
            await page.wait_for_load_state("networkidle")
            
            current_url = page.url
            status_code = response.status if response else 0
            
            # Check if redirected to homepage
            if current_url == self.base_url or current_url.endswith('/'):
                if href != '/' and href != '':
                    return {
                        'status': 'redirected',
                        'link_text': text,
                        'href': href,
                        'final_url': current_url,
                        'status_code': status_code,
                        'issue': 'REDIRECTED_TO_HOMEPAGE'
                    }
            
            # Check if redirected to login
            if 'login' in current_url:
                return {
                    'status': 'redirected',
                    'link_text': text,
                    'href': href,
                    'final_url': current_url,
                    'status_code': status_code,
                    'issue': 'REDIRECTED_TO_LOGIN'
                }
            
            # Check page title for errors
            title = await page.title()
            if any(error in title.lower() for error in ['error', '404', '500', 'not found']):
                return {
                    'status': 'broken',
                    'link_text': text,
                    'href': href,
                    'final_url': current_url,
                    'status_code': status_code,
                    'issue': f'ERROR_IN_TITLE: {title}'
                }
            
            # Success case
            return {
                'status': 'working',
                'link_text': text,
                'href': href,
                'final_url': current_url,
                'status_code': status_code,
                'page_title': title
            }
            
        except Exception as e:
            return {
                'status': 'broken',
                'link_text': text,
                'href': href,
                'final_url': None,
                'status_code': 0,
                'issue': f'EXCEPTION: {str(e)}'
            }
    
    async def run_comprehensive_test(self):
        """Run the complete authenticated link test"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                # Authenticate
                if not await self.authenticate(page):
                    logger.error("Authentication failed, cannot proceed")
                    return
                
                # Test navigation links
                await self.test_navigation_links(page)
                
                # Generate report
                self.generate_report()
                
            finally:
                await browser.close()
    
    def generate_report(self):
        """Generate comprehensive test report"""
        total_links = len(self.working_links) + len(self.broken_links) + len(self.redirected_links)
        
        print("\n" + "="*80)
        print("COMPREHENSIVE AUTHENTICATED LINK TEST RESULTS")
        print("="*80)
        print(f"Total Links Tested: {total_links}")
        print(f"✅ Working Links: {len(self.working_links)}")
        print(f"🔄 Redirected Links: {len(self.redirected_links)}")
        print(f"❌ Broken Links: {len(self.broken_links)}")
        
        if self.redirected_links:
            print("\n🔄 REDIRECTED LINKS (MAIN ISSUE):")
            print("-" * 40)
            for link in self.redirected_links:
                print(f"❌ {link['link_text']}: {link['href']}")
                print(f"   Issue: {link['issue']}")
                print(f"   Final URL: {link['final_url']}")
                print(f"   Status Code: {link['status_code']}")
                print()
        
        if self.broken_links:
            print("\n❌ BROKEN LINKS:")
            print("-" * 40)
            for link in self.broken_links:
                print(f"❌ {link['link_text']}: {link['href']}")
                print(f"   Issue: {link['issue']}")
                print()
        
        if self.working_links:
            print(f"\n✅ WORKING LINKS ({len(self.working_links)}):")
            print("-" * 40)
            for link in self.working_links:
                print(f"✅ {link['link_text']}: {link['href']}")
        
        # Save detailed report
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'total_links': total_links,
            'working_links': self.working_links,
            'redirected_links': self.redirected_links,
            'broken_links': self.broken_links,
            'summary': {
                'working_count': len(self.working_links),
                'redirected_count': len(self.redirected_links),
                'broken_count': len(self.broken_links)
            }
        }
        
        with open('logs/2025/07/06/system/comprehensive_link_test_report.json', 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: logs/2025/07/06/system/comprehensive_link_test_report.json")

async def main():
    tester = AuthenticatedLinkTester()
    await tester.run_comprehensive_test()

if __name__ == "__main__":
    asyncio.run(main())