#!/usr/bin/env python3
"""
Operations Dropdown Menu Link Tester
Tests all operations dropdown menu links specifically
"""

import requests
from datetime import datetime

def test_operations_dropdown_links():
    """Test all the operations dropdown menu links"""
    base_url = "http://localhost:5000"
    
    # Login as super admin first
    session = requests.Session()
    
    # Login
    login_data = {
        'username': 'uncode',
        'password': 'Zx9Wq2@#ComplexCeo'
    }
    
    login_response = session.post(f"{base_url}/auth/login", data=login_data)
    
    # Operations dropdown menu links from the navbar
    operations_links = [
        # Branch & Operations
        ("/admin/branches", "Branch Management"),
        ("/admin/teller-operations", "Teller Operations"),
        ("/admin/branch-reports", "Branch Reports"),
        ("/settlement/dashboard", "Settlement Operations"),
        
        # System Operations
        ("/admin/", "Admin Dashboard"),
        ("/system/dashboard", "System Health"),
        ("/admin/maintenance", "Maintenance Mode"),
        ("/admin/backups", "Database Backups"),
        
        # Security Operations (if accessible)
        ("/security/", "Security Dashboard"),
        ("/security/investigation", "Investigation Tools"),
        ("/security/threat-monitoring", "Threat Monitoring"),
        ("/security/incident-response", "Incident Response")
    ]
    
    working_links = []
    broken_links = []
    
    print("Testing Operations Dropdown Menu Links")
    print("=" * 50)
    
    for endpoint, name in operations_links:
        try:
            response = session.get(f"{base_url}{endpoint}", timeout=10)
            
            status = response.status_code
            
            if status == 200:
                working_links.append({'endpoint': endpoint, 'name': name, 'status': status})
                print(f"✅ {name}: {endpoint} - HTTP {status}")
                
            elif status in [302, 308]:
                # Check where it redirects
                final_url = response.url
                if 'login' in final_url:
                    print(f"🔒 {name}: {endpoint} - Redirects to login (needs auth)")
                else:
                    working_links.append({'endpoint': endpoint, 'name': name, 'status': status})
                    print(f"🔄 {name}: {endpoint} - HTTP {status} (redirect)")
                    
            elif status == 404:
                broken_links.append({'endpoint': endpoint, 'name': name, 'status': status})
                print(f"❌ {name}: {endpoint} - HTTP 404 (NOT FOUND)")
                
            elif status == 403:
                print(f"🔒 {name}: {endpoint} - HTTP 403 (FORBIDDEN)")
                
            else:
                broken_links.append({'endpoint': endpoint, 'name': name, 'status': status})
                print(f"⚠️ {name}: {endpoint} - HTTP {status}")
                
        except Exception as e:
            broken_links.append({'endpoint': endpoint, 'name': name, 'error': str(e)})
            print(f"💥 {name}: {endpoint} - ERROR: {str(e)}")
    
    print("\n" + "=" * 50)
    print("OPERATIONS DROPDOWN TESTING SUMMARY")
    print("=" * 50)
    print(f"✅ Working Links: {len(working_links)}")
    print(f"❌ Broken Links: {len(broken_links)}")
    
    if broken_links:
        print("\nBroken Links Details:")
        for link in broken_links:
            print(f"  - {link['name']}: {link['endpoint']}")
    
    return {
        'working_links': working_links,
        'broken_links': broken_links,
        'total_tested': len(operations_links)
    }

if __name__ == "__main__":
    results = test_operations_dropdown_links()
    
    # Save quick summary
    with open("logs/2025/07/06/system/operations_dropdown_test.txt", "w") as f:
        f.write(f"Operations Dropdown Test Results - {datetime.now()}\n")
        f.write(f"Total Links Tested: {results['total_tested']}\n")
        f.write(f"Working Links: {len(results['working_links'])}\n")
        f.write(f"Broken Links: {len(results['broken_links'])}\n\n")
        
        if results['broken_links']:
            f.write("BROKEN LINKS:\n")
            for link in results['broken_links']:
                f.write(f"  - {link['name']}: {link['endpoint']}\n")
        else:
            f.write("ALL OPERATIONS DROPDOWN LINKS WORKING!\n")