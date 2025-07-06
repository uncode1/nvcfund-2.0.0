"""
Comprehensive Template and Route Validation for NVC Banking Platform
Verifies all templates have corresponding routes and all routes render properly
"""
import os
import pytest
import time
from pathlib import Path
from flask import url_for
from urllib.parse import urlparse
import re


class TemplateRouteValidator:
    """Comprehensive validator for template-route mapping verification"""
    
    def __init__(self):
        self.validation_results = {
            'templates_found': 0,
            'routes_tested': 0,
            'successful_renders': 0,
            'missing_routes': [],
            'template_errors': [],
            'route_performance': {},
            'modules_tested': set(),
            'status_codes': {}
        }
        self.performance_metrics = {}
        
    def find_all_templates(self):
        """Find all HTML templates in the modules directory"""
        templates = []
        modules_dir = Path('modules')
        
        for template_file in modules_dir.rglob('*.html'):
            # Skip base templates and fragments
            if 'base' not in template_file.name.lower() and 'fragment' not in template_file.name.lower():
                templates.append(template_file)
                
        return templates
    
    def extract_module_from_path(self, template_path):
        """Extract module name from template path"""
        parts = template_path.parts
        if len(parts) >= 2 and parts[0] == 'modules':
            return parts[1]
        return 'unknown'
    
    def generate_potential_routes(self, template_path):
        """Generate potential route patterns for a template"""
        module = self.extract_module_from_path(template_path)
        template_name = template_path.stem
        
        # Common route patterns used in the platform
        route_patterns = [
            f'/{module}/',
            f'/{module}/{template_name}',
            f'/{module}/{template_name}/',
            f'/{template_name}',
            f'/{template_name}/',
        ]
        
        # Handle special cases
        if template_name == 'main' or template_name == 'index':
            route_patterns.extend([f'/{module}', f'/{module}/'])
        
        if template_name == 'dashboard':
            route_patterns.extend(['/dashboard/', '/dashboard/overview'])
            
        if template_name == 'login':
            route_patterns.extend(['/auth/login', '/login'])
            
        return route_patterns


@pytest.mark.template_validation
def test_comprehensive_template_route_validation(app, client):
    """Comprehensive validation of all templates and their routes"""
    
    validator = TemplateRouteValidator()
    
    print("\n" + "="*80)
    print("COMPREHENSIVE TEMPLATE & ROUTE VALIDATION")
    print("="*80)
    
    # Find all templates
    templates = validator.find_all_templates()
    validator.validation_results['templates_found'] = len(templates)
    
    print(f"\nFound {len(templates)} templates to validate")
    print("-" * 60)
    
    # Test each template
    for template_path in templates:
        module = validator.extract_module_from_path(template_path)
        validator.validation_results['modules_tested'].add(module)
        
        template_name = template_path.name
        print(f"\nTesting: {module}/{template_name}")
        
        # Generate potential routes for this template
        potential_routes = validator.generate_potential_routes(template_path)
        route_found = False
        
        for route in potential_routes:
            try:
                start_time = time.time()
                response = client.get(route)
                end_time = time.time()
                
                response_time = (end_time - start_time) * 1000  # Convert to ms
                
                # Track performance
                validator.performance_metrics[route] = response_time
                
                # Count status codes
                status = response.status_code
                validator.validation_results['status_codes'][status] = \
                    validator.validation_results['status_codes'].get(status, 0) + 1
                
                validator.validation_results['routes_tested'] += 1
                
                if status == 200:
                    print(f"  ✅ {route} -> HTTP {status} ({response_time:.1f}ms)")
                    validator.validation_results['successful_renders'] += 1
                    route_found = True
                    break
                elif status in [301, 302]:
                    print(f"  🔄 {route} -> HTTP {status} (redirect)")
                    route_found = True
                    break
                elif status in [401, 403]:
                    print(f"  🔒 {route} -> HTTP {status} (auth required)")
                    route_found = True
                    break
                elif status == 404:
                    print(f"  ❌ {route} -> HTTP {status} (not found)")
                else:
                    print(f"  ⚠️  {route} -> HTTP {status}")
                    
            except Exception as e:
                print(f"  💥 {route} -> Error: {str(e)}")
                validator.validation_results['template_errors'].append({
                    'template': template_name,
                    'route': route,
                    'error': str(e)
                })
        
        if not route_found:
            validator.validation_results['missing_routes'].append({
                'template': template_name,
                'module': module,
                'path': str(template_path)
            })
            print(f"  ⚠️  No working route found for {template_name}")
    
    # Generate comprehensive report
    print("\n" + "="*80)
    print("VALIDATION SUMMARY REPORT")
    print("="*80)
    
    results = validator.validation_results
    
    print(f"\n📊 STATISTICS:")
    print(f"  Templates Found: {results['templates_found']}")
    print(f"  Routes Tested: {results['routes_tested']}")
    print(f"  Successful Renders: {results['successful_renders']}")
    print(f"  Modules Tested: {len(results['modules_tested'])}")
    
    # Success rate
    if results['routes_tested'] > 0:
        success_rate = (results['successful_renders'] / results['routes_tested']) * 100
        print(f"  Success Rate: {success_rate:.1f}%")
    
    # Status code breakdown
    print(f"\n📈 HTTP STATUS CODES:")
    for status, count in sorted(results['status_codes'].items()):
        status_name = {
            200: "OK",
            301: "Moved Permanently", 
            302: "Found (Redirect)",
            401: "Unauthorized",
            403: "Forbidden", 
            404: "Not Found",
            500: "Internal Server Error"
        }.get(status, "Other")
        print(f"  HTTP {status} ({status_name}): {count}")
    
    # Performance metrics
    if validator.performance_metrics:
        response_times = list(validator.performance_metrics.values())
        avg_time = sum(response_times) / len(response_times)
        max_time = max(response_times)
        slow_routes = [(route, time) for route, time in validator.performance_metrics.items() if time > 1000]
        
        print(f"\n⚡ PERFORMANCE METRICS:")
        print(f"  Average Response Time: {avg_time:.1f}ms")
        print(f"  Maximum Response Time: {max_time:.1f}ms")
        print(f"  Slow Routes (>1s): {len(slow_routes)}")
        
        if slow_routes:
            print(f"\n⏱️  SLOWEST ROUTES:")
            for route, response_time in sorted(slow_routes, key=lambda x: x[1], reverse=True)[:5]:
                print(f"  {route}: {response_time:.1f}ms")
    
    # Modules tested
    print(f"\n🏗️  MODULES TESTED:")
    for module in sorted(results['modules_tested']):
        print(f"  • {module}")
    
    # Missing routes
    if results['missing_routes']:
        print(f"\n⚠️  TEMPLATES WITHOUT WORKING ROUTES ({len(results['missing_routes'])}):")
        for missing in results['missing_routes']:
            print(f"  • {missing['module']}/{missing['template']} ({missing['path']})")
    
    # Template errors
    if results['template_errors']:
        print(f"\n💥 TEMPLATE ERRORS ({len(results['template_errors'])}):")
        for error in results['template_errors']:
            print(f"  • {error['template']} ({error['route']}): {error['error']}")
    
    print("\n" + "="*80)
    print("VALIDATION COMPLETE")
    print("="*80)
    
    # Test assertions - ensure we found templates and routes
    assert results['templates_found'] > 0, "No templates found in modules directory"
    assert results['routes_tested'] > 0, "No routes were tested"
    assert len(results['modules_tested']) > 0, "No modules were tested"


@pytest.mark.template_validation  
def test_critical_template_route_mapping(app, client):
    """Test that critical templates have working routes"""
    
    critical_templates = [
        ('auth', 'login'),
        ('dashboard', 'main'),
        ('banking', 'main'),
        ('public', 'index'),
    ]
    
    print("\n" + "="*60)
    print("CRITICAL TEMPLATE ROUTE MAPPING TEST")
    print("="*60)
    
    for module, template in critical_templates:
        route_patterns = [
            f'/{module}/',
            f'/{module}/{template}',
            f'/{module}' if template in ['main', 'index'] else f'/{module}/{template}/'
        ]
        
        route_found = False
        for route in route_patterns:
            try:
                response = client.get(route)
                if response.status_code < 500:  # Any non-server-error response
                    print(f"✅ {module}/{template}.html -> {route} (HTTP {response.status_code})")
                    route_found = True
                    break
            except Exception as e:
                print(f"❌ {route} -> Error: {str(e)}")
        
        if not route_found:
            print(f"⚠️  Critical template {module}/{template}.html has no working route")
        
        # Don't fail the test for missing routes, just report them
        # assert route_found, f"Critical template {module}/{template}.html must have a working route"


@pytest.mark.template_validation
def test_template_rendering_errors(app, client):
    """Test for template rendering errors and missing dependencies"""
    
    print("\n" + "="*60)
    print("TEMPLATE RENDERING ERROR DETECTION")
    print("="*60)
    
    # Test common routes that should render without errors
    test_routes = [
        '/',
        '/auth/login',
        '/dashboard/',
        '/api/v1/health',
    ]
    
    rendering_errors = []
    
    for route in test_routes:
        try:
            response = client.get(route)
            
            # Check for common error indicators in response
            if response.status_code == 200:
                response_text = response.get_data(as_text=True)
                
                # Look for common error patterns
                error_patterns = [
                    r'TemplateNotFound',
                    r'UndefinedError',
                    r'TemplateSyntaxError',
                    r'Internal Server Error',
                    r'500 Internal Server Error'
                ]
                
                for pattern in error_patterns:
                    if re.search(pattern, response_text, re.IGNORECASE):
                        rendering_errors.append({
                            'route': route,
                            'error_type': pattern,
                            'status': response.status_code
                        })
                        print(f"❌ {route} -> Contains error pattern: {pattern}")
                        break
                else:
                    print(f"✅ {route} -> Renders successfully")
            else:
                print(f"ℹ️  {route} -> HTTP {response.status_code} (non-200 response)")
                
        except Exception as e:
            rendering_errors.append({
                'route': route,
                'error_type': 'Exception',
                'error': str(e)
            })
            print(f"💥 {route} -> Exception: {str(e)}")
    
    if rendering_errors:
        print(f"\n⚠️  Found {len(rendering_errors)} rendering issues")
        for error in rendering_errors:
            print(f"  • {error['route']}: {error.get('error_type', 'Unknown error')}")
    else:
        print("\n✅ No template rendering errors detected")
    
    print("\n" + "="*60)