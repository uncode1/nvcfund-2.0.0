#!/usr/bin/env python3
"""
NVC Banking Platform Web Interface Crawler
Uses Beautiful Soup to crawl all accessible pages and extract interface structures
"""

import requests
from bs4 import BeautifulSoup
import json
import os
from urllib.parse import urljoin, urlparse
from datetime import datetime
import time

class WebInterfaceCrawler:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.crawled_urls = set()
        self.interface_data = {}
        self.session = requests.Session()
        
        # Known banking platform URLs from the actual running system
        self.platform_urls = [
            "/",  # Homepage
            "/dashboard",  # Main dashboard
            "/banking",  # Banking operations
            "/banking/accounts",  # Account management
            "/banking/transfers",  # Money transfers
            "/banking/cards",  # Card management
            "/treasury",  # Treasury management
            "/treasury/liquidity",  # Liquidity management
            "/treasury/reserves",  # Reserve management
            "/trading",  # Trading platform
            "/trading/portfolio",  # Portfolio management
            "/investments/portfolio",  # Investment portfolio
            "/admin",  # Admin dashboard
            "/admin/users",  # User management
            "/admin/system",  # System configuration
            "/compliance",  # Compliance dashboard
            "/compliance/reports",  # Compliance reporting
            "/security_center",  # Security center
            "/security_center/threats",  # Threat analysis
            "/cards_payments",  # Cards and payments
            "/sovereign",  # Sovereign banking
            "/institutional",  # Institutional banking
            "/analytics",  # Analytics dashboard
            "/blockchain_analytics",  # Blockchain analytics
            "/smart_contracts",  # Smart contracts
            "/nvct_stablecoin",  # NVCT stablecoin
            "/islamic_banking",  # Islamic banking
            "/interest_rate_management",  # Interest rate management
            "/insurance",  # Insurance module
            "/chat",  # Banking chat system
            "/binance_integration",  # Binance integration
            "/auth/login",  # Login page
            "/auth/register",  # Registration page
            "/contact",  # Contact page
            "/about",  # About page
            "/api-documentation"  # API documentation
        ]
        
    def crawl_page(self, url):
        """Crawl a single page and extract interface structure"""
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                return self.extract_interface_structure(soup, url)
            else:
                return {"error": f"HTTP {response.status_code}", "url": url}
        except Exception as e:
            return {"error": str(e), "url": url}
    
    def extract_interface_structure(self, soup, url):
        """Extract key interface elements from a page"""
        structure = {
            "url": url,
            "title": soup.title.string if soup.title else "No Title",
            "navigation": self.extract_navigation(soup),
            "main_content": self.extract_main_content(soup),
            "forms": self.extract_forms(soup),
            "buttons": self.extract_buttons(soup),
            "cards": self.extract_cards(soup),
            "tables": self.extract_tables(soup),
            "widgets": self.extract_widgets(soup),
            "links": self.extract_internal_links(soup)
        }
        return structure
    
    def extract_navigation(self, soup):
        """Extract navigation elements"""
        nav_elements = []
        
        # Look for nav tags, navigation menus, sidebars
        navs = soup.find_all(['nav', 'header'])
        for nav in navs:
            nav_data = {
                "type": nav.name,
                "class": nav.get('class', []),
                "links": []
            }
            
            # Extract navigation links
            links = nav.find_all('a')
            for link in links:
                nav_data["links"].append({
                    "text": link.get_text(strip=True),
                    "href": link.get('href', ''),
                    "class": link.get('class', [])
                })
            
            nav_elements.append(nav_data)
        
        return nav_elements
    
    def extract_main_content(self, soup):
        """Extract main content structure"""
        main_content = []
        
        # Look for main content areas
        main_areas = soup.find_all(['main', 'div']) 
        for area in main_areas:
            if any(cls in str(area.get('class', [])) for cls in ['content', 'main', 'dashboard', 'container']):
                content_data = {
                    "type": area.name,
                    "class": area.get('class', []),
                    "text_preview": area.get_text(strip=True)[:200] + "..." if len(area.get_text(strip=True)) > 200 else area.get_text(strip=True)
                }
                main_content.append(content_data)
        
        return main_content
    
    def extract_forms(self, soup):
        """Extract form structures"""
        forms = []
        form_elements = soup.find_all('form')
        
        for form in form_elements:
            form_data = {
                "action": form.get('action', ''),
                "method": form.get('method', 'GET'),
                "class": form.get('class', []),
                "fields": []
            }
            
            # Extract form fields
            inputs = form.find_all(['input', 'select', 'textarea'])
            for inp in inputs:
                field_data = {
                    "type": inp.get('type', inp.name),
                    "name": inp.get('name', ''),
                    "placeholder": inp.get('placeholder', ''),
                    "class": inp.get('class', [])
                }
                form_data["fields"].append(field_data)
            
            forms.append(form_data)
        
        return forms
    
    def extract_buttons(self, soup):
        """Extract button elements"""
        buttons = []
        button_elements = soup.find_all(['button', 'input'])
        
        for btn in button_elements:
            if btn.name == 'input' and btn.get('type') not in ['button', 'submit']:
                continue
                
            button_data = {
                "text": btn.get_text(strip=True) or btn.get('value', ''),
                "type": btn.get('type', 'button'),
                "class": btn.get('class', []),
                "onclick": btn.get('onclick', '')
            }
            buttons.append(button_data)
        
        return buttons
    
    def extract_cards(self, soup):
        """Extract card-like interface components"""
        cards = []
        card_elements = soup.find_all('div')
        
        for div in card_elements:
            classes = div.get('class', [])
            if any(cls in str(classes) for cls in ['card', 'widget', 'panel', 'metric']):
                card_data = {
                    "class": classes,
                    "content": div.get_text(strip=True)[:100] + "..." if len(div.get_text(strip=True)) > 100 else div.get_text(strip=True)
                }
                cards.append(card_data)
        
        return cards
    
    def extract_tables(self, soup):
        """Extract table structures"""
        tables = []
        table_elements = soup.find_all('table')
        
        for table in table_elements:
            table_data = {
                "class": table.get('class', []),
                "headers": [],
                "rows_count": 0
            }
            
            # Extract headers
            headers = table.find_all('th')
            for header in headers:
                table_data["headers"].append(header.get_text(strip=True))
            
            # Count rows
            rows = table.find_all('tr')
            table_data["rows_count"] = len(rows)
            
            tables.append(table_data)
        
        return tables
    
    def extract_widgets(self, soup):
        """Extract dashboard widgets and components"""
        widgets = []
        
        # Look for common widget patterns
        widget_selectors = [
            {'class': 'stat-card'}, {'class': 'metric-card'}, 
            {'class': 'dashboard-widget'}, {'class': 'summary-card'}
        ]
        
        for selector in widget_selectors:
            elements = soup.find_all('div', class_=selector['class'])
            for element in elements:
                widget_data = {
                    "type": selector['class'],
                    "content": element.get_text(strip=True)[:150] + "..." if len(element.get_text(strip=True)) > 150 else element.get_text(strip=True)
                }
                widgets.append(widget_data)
        
        return widgets
    
    def extract_internal_links(self, soup):
        """Extract internal links for crawling"""
        links = []
        link_elements = soup.find_all('a', href=True)
        
        for link in link_elements:
            href = link['href']
            # Filter for internal links
            if href.startswith('/') or self.base_url in href:
                full_url = urljoin(self.base_url, href)
                if full_url not in self.crawled_urls:
                    links.append({
                        "text": link.get_text(strip=True),
                        "url": full_url,
                        "href": href
                    })
        
        return links
    
    def crawl_banking_platform(self):
        """Crawl the NVC Banking Platform systematically using all known URLs"""
        print(f"Starting comprehensive web crawl of NVC Banking Platform at {self.base_url}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Total URLs to crawl: {len(self.platform_urls)}")
        print("=" * 80)
        
        # Convert relative URLs to absolute URLs
        urls_to_crawl = [f"{self.base_url}{url}" for url in self.platform_urls]
        
        while urls_to_crawl:
            current_url = urls_to_crawl.pop(0)
            
            if current_url in self.crawled_urls:
                continue
                
            print(f"Crawling: {current_url}")
            self.crawled_urls.add(current_url)
            
            # Crawl the page
            page_data = self.crawl_page(current_url)
            
            if "error" not in page_data:
                self.interface_data[current_url] = page_data
                
                # Add newly discovered internal links (limited to prevent infinite loops)
                for link_data in page_data.get("links", []):
                    new_url = link_data["url"]
                    if (new_url not in self.crawled_urls and 
                        new_url not in urls_to_crawl and 
                        len(urls_to_crawl) < 50):  # Increased limit for comprehensive crawl
                        urls_to_crawl.append(new_url)
                
                print(f"✓ Successfully crawled: {current_url}")
                print(f"  Title: {page_data['title']}")
                print(f"  Navigation items: {len(page_data['navigation'])}")
                print(f"  Forms: {len(page_data['forms'])}")
                print(f"  Cards/Widgets: {len(page_data['cards']) + len(page_data['widgets'])}")
                print(f"  Tables: {len(page_data['tables'])}")
                
            else:
                print(f"✗ Error crawling {current_url}: {page_data['error']}")
            
            # Small delay to be respectful
            time.sleep(0.5)
        
        print("=" * 60)
        print(f"Crawl completed. Total pages: {len(self.interface_data)}")
        
        return self.interface_data
    
    def generate_interface_documentation(self):
        """Generate comprehensive interface documentation"""
        crawl_data = self.crawl_banking_platform()
        
        # Save raw data
        os.makedirs("logs/2025/07/06/system", exist_ok=True)
        with open("logs/2025/07/06/system/web_crawl_data.json", "w") as f:
            json.dump(crawl_data, f, indent=2)
        
        # Generate structured documentation
        doc_content = self.create_interface_documentation(crawl_data)
        
        with open("docs/ACTUAL_WEB_INTERFACES.md", "w") as f:
            f.write(doc_content)
        
        print(f"Documentation saved to: docs/ACTUAL_WEB_INTERFACES.md")
        print(f"Raw data saved to: logs/2025/07/06/system/web_crawl_data.json")
        
        return crawl_data
    
    def create_interface_documentation(self, crawl_data):
        """Create formatted documentation from crawl data"""
        doc = "# NVC Banking Platform - Actual Web Interfaces\n\n"
        doc += "## Based on Live Platform Crawl\n\n"
        doc += f"**Crawl Date**: {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}\n"
        doc += f"**Pages Analyzed**: {len(crawl_data)}\n\n"
        doc += "This documentation is generated from actual web interface crawling using Beautiful Soup.\n\n"
        doc += "---\n\n"
        
        for url, data in crawl_data.items():
            doc += f"## {data['title']}\n\n"
            doc += f"**URL**: {url}\n\n"
            
            # Navigation
            if data['navigation']:
                doc += "### Navigation Structure\n\n"
                for nav in data['navigation']:
                    doc += f"**{nav['type'].title()} Navigation**:\n"
                    for link in nav['links']:
                        doc += f"- {link['text']} → {link['href']}\n"
                    doc += "\n"
            
            # Forms
            if data['forms']:
                doc += "### Forms\n\n"
                for i, form in enumerate(data['forms'], 1):
                    doc += f"**Form {i}** ({form['method']} → {form['action']}):\n"
                    for field in form['fields']:
                        doc += f"- {field['type']}: {field['name']} ({field['placeholder']})\n"
                    doc += "\n"
            
            # Cards and Widgets
            if data['cards'] or data['widgets']:
                doc += "### Dashboard Components\n\n"
                all_components = data['cards'] + data['widgets']
                for component in all_components:
                    doc += f"- **{component.get('type', 'Component')}**: {component['content'][:100]}...\n"
                doc += "\n"
            
            # Tables
            if data['tables']:
                doc += "### Data Tables\n\n"
                for table in data['tables']:
                    doc += f"**Table** ({table['rows_count']} rows):\n"
                    if table['headers']:
                        doc += f"Columns: {', '.join(table['headers'])}\n"
                    doc += "\n"
            
            # Buttons
            if data['buttons']:
                doc += "### Action Buttons\n\n"
                for button in data['buttons']:
                    if button['text']:
                        doc += f"- {button['text']} ({button['type']})\n"
                doc += "\n"
            
            doc += "---\n\n"
        
        return doc

if __name__ == "__main__":
    crawler = WebInterfaceCrawler()
    crawler.generate_interface_documentation()