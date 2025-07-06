#!/usr/bin/env python3
"""
Quick Interface Capture for NVC Banking Platform
Captures key accessible interfaces and generates visual documentation
"""

import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

def capture_key_interfaces():
    """Capture the most accessible and important interfaces"""
    base_url = "http://localhost:5000"
    
    # Focus on accessible interfaces without authentication
    key_urls = {
        "homepage": "/",
        "dashboard": "/dashboard", 
        "login": "/auth/login",
        "register": "/auth/register",
        "contact": "/contact",
        "about": "/about",
        "api_docs": "/api-documentation"
    }
    
    interface_data = {}
    
    print("Capturing NVC Banking Platform Interfaces")
    print("=" * 50)
    
    for name, url in key_urls.items():
        try:
            full_url = f"{base_url}{url}"
            response = requests.get(full_url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract key interface elements
                interface_info = {
                    "url": full_url,
                    "title": soup.title.string if soup.title else "No Title",
                    "main_content": extract_content_structure(soup),
                    "navigation": extract_navigation_simple(soup),
                    "forms": extract_forms_simple(soup),
                    "key_elements": extract_key_elements(soup)
                }
                
                interface_data[name] = interface_info
                print(f"✓ Captured: {name} - {interface_info['title']}")
                
            else:
                print(f"✗ Failed: {name} - HTTP {response.status_code}")
                
        except Exception as e:
            print(f"✗ Error: {name} - {str(e)}")
    
    return interface_data

def extract_content_structure(soup):
    """Extract main content structure"""
    content = {
        "headings": [],
        "sections": [],
        "key_text": []
    }
    
    # Extract headings
    for level in ['h1', 'h2', 'h3']:
        headings = soup.find_all(level)
        for h in headings:
            content["headings"].append({
                "level": level,
                "text": h.get_text(strip=True)
            })
    
    # Extract sections with meaningful content
    sections = soup.find_all(['section', 'div'])
    for section in sections:
        classes = section.get('class', [])
        if any(keyword in str(classes) for keyword in ['hero', 'dashboard', 'main', 'content', 'feature']):
            content["sections"].append({
                "class": classes,
                "text_preview": section.get_text(strip=True)[:200] + "..."
            })
    
    return content

def extract_navigation_simple(soup):
    """Extract navigation in simple format"""
    nav_items = []
    
    # Look for navigation links
    nav_elements = soup.find_all(['nav', 'header'])
    for nav in nav_elements:
        links = nav.find_all('a')
        for link in links:
            text = link.get_text(strip=True)
            href = link.get('href', '')
            if text and len(text) < 50:  # Filter out very long text
                nav_items.append(f"{text} → {href}")
    
    return nav_items

def extract_forms_simple(soup):
    """Extract forms in simple format"""
    forms = []
    form_elements = soup.find_all('form')
    
    for form in form_elements:
        form_info = {
            "action": form.get('action', ''),
            "method": form.get('method', 'GET'),
            "inputs": []
        }
        
        inputs = form.find_all(['input', 'select', 'textarea'])
        for inp in inputs:
            if inp.get('type') != 'hidden':
                form_info["inputs"].append({
                    "type": inp.get('type', inp.name),
                    "name": inp.get('name', ''),
                    "placeholder": inp.get('placeholder', '')
                })
        
        forms.append(form_info)
    
    return forms

def extract_key_elements(soup):
    """Extract key visual elements"""
    elements = {
        "buttons": [],
        "cards": 0,
        "tables": 0,
        "widgets": 0
    }
    
    # Count buttons
    buttons = soup.find_all(['button', 'input'])
    for btn in buttons:
        if btn.name == 'button' or btn.get('type') in ['submit', 'button']:
            text = btn.get_text(strip=True) or btn.get('value', '')
            if text:
                elements["buttons"].append(text)
    
    # Count interface components
    elements["cards"] = len(soup.find_all('div', class_=lambda x: x and ('card' in str(x) or 'widget' in str(x))))
    elements["tables"] = len(soup.find_all('table'))
    elements["widgets"] = len(soup.find_all('div', class_=lambda x: x and 'metric' in str(x)))
    
    return elements

def generate_interface_documentation(interface_data):
    """Generate visual documentation from captured interfaces"""
    
    doc = "# NVC Banking Platform - Live Interface Capture\n\n"
    doc += f"**Capture Date**: {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}\n"
    doc += f"**Interfaces Captured**: {len(interface_data)}\n\n"
    doc += "This documentation is generated from live interface crawling of accessible pages.\n\n"
    doc += "---\n\n"
    
    for name, data in interface_data.items():
        doc += f"## {data['title']}\n\n"
        doc += f"**Interface**: {name.title()}\n"
        doc += f"**URL**: {data['url']}\n\n"
        
        # Main content structure
        if data['main_content']['headings']:
            doc += "### Page Structure\n\n"
            for heading in data['main_content']['headings']:
                doc += f"- **{heading['level'].upper()}**: {heading['text']}\n"
            doc += "\n"
        
        # Navigation
        if data['navigation']:
            doc += "### Navigation Elements\n\n"
            for nav_item in data['navigation'][:10]:  # Limit to avoid clutter
                doc += f"- {nav_item}\n"
            doc += "\n"
        
        # Forms
        if data['forms']:
            doc += "### Forms\n\n"
            for i, form in enumerate(data['forms'], 1):
                doc += f"**Form {i}** ({form['method']} → {form['action']}):\n"
                for inp in form['inputs']:
                    doc += f"- {inp['type']}: {inp['name']} ({inp['placeholder']})\n"
                doc += "\n"
        
        # Interface elements
        elements = data['key_elements']
        if any([elements['buttons'], elements['cards'], elements['tables'], elements['widgets']]):
            doc += "### Interface Components\n\n"
            if elements['cards']:
                doc += f"- **Cards/Widgets**: {elements['cards']} components\n"
            if elements['tables']:
                doc += f"- **Data Tables**: {elements['tables']} tables\n"
            if elements['widgets']:
                doc += f"- **Metric Widgets**: {elements['widgets']} widgets\n"
            if elements['buttons']:
                doc += f"- **Action Buttons**: {', '.join(elements['buttons'][:5])}\n"
            doc += "\n"
        
        doc += "---\n\n"
    
    return doc

if __name__ == "__main__":
    # Capture interfaces
    interface_data = capture_key_interfaces()
    
    # Generate documentation
    documentation = generate_interface_documentation(interface_data)
    
    # Save files
    os.makedirs("logs/2025/07/06/system", exist_ok=True)
    
    with open("logs/2025/07/06/system/live_interface_data.json", "w") as f:
        json.dump(interface_data, f, indent=2)
    
    with open("docs/LIVE_WEB_INTERFACES.md", "w") as f:
        f.write(documentation)
    
    print("\n" + "=" * 50)
    print("Interface capture completed!")
    print(f"Documentation: docs/LIVE_WEB_INTERFACES.md")
    print(f"Data: logs/2025/07/06/system/live_interface_data.json")