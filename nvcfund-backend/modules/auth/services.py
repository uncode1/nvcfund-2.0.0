"""
Auth Module Services - Business Logic and Authentication Services
Comprehensive authentication services for the modular auth system
"""

import re
import logging
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from flask import current_app
from typing import Dict, List, Any

from .models import User, UserRole
from modules.core.extensions import db
from .config import AuthConfig

logger = logging.getLogger(__name__)

class AuthService:
    """Authentication Service - Core business logic for auth module"""
    
    def __init__(self):
        self.config = AuthConfig()
    
    def determine_dashboard_redirect(self, username: str, user_role: str) -> str:
        """
        Advanced Role-Based Dashboard Redirection Logic
        
        Args:
            username: User's login username
            user_role: User's assigned role from UserRole enum
            
        Returns:
            str: Dashboard URL path for redirection
        """
        logger.info("🔍 Auth Service: Parsing dashboard redirect for user: %s with role: %s", username, user_role)
        
        # Special username-based overrides (for testing/demo accounts)
        username_overrides = {
            'demo_user': '/dashboard/',           # Always use modular dashboard for demo
            'testapi': '/dashboard/',             # API test user gets standard dashboard  
            'regular_user': '/dashboard/',        # Regular test user
            'uncode': '/admin/dashboard'          # Superadmin override
        }
        
        if username.lower() in username_overrides:
            override_path = username_overrides[username.lower()]
            logger.info("🔧 Auth Service: Username override applied: %s -> %s", username, override_path)
            return override_path
        
        # Administrative and System Roles
        if user_role in [UserRole.SUPER_ADMIN.value, UserRole.ADMIN.value]:
            logger.info("👑 Auth Service: Admin user detected - redirecting to admin dashboard")
            return '/admin/dashboard'
        
        # Executive Level (Sovereign Banking Access)
        elif user_role in [UserRole.SOVEREIGN_BANKER.value, UserRole.CENTRAL_BANK_GOVERNOR.value]:
            logger.info("🏛️ Auth Service: Sovereign banking user detected - redirecting to sovereign dashboard")
            return '/sovereign/dashboard'
        
        # Treasury Operations
        elif user_role in [UserRole.TREASURY_OFFICER.value]:
            logger.info("💰 Auth Service: Treasury officer detected - redirecting to treasury dashboard")
            return '/treasury/dashboard'
        
        # Institutional Banking
        elif user_role in [UserRole.CORRESPONDENT_BANKER.value, UserRole.INSTITUTIONAL_BANKER.value]:
            logger.info("🏦 Auth Service: Institutional banker detected - redirecting to institutional dashboard")
            return '/institutional/dashboard'
            
        # Risk and Compliance Management
        elif user_role in [UserRole.RISK_MANAGER.value, UserRole.COMPLIANCE_OFFICER.value]:
            logger.info("⚖️ Auth Service: Risk/Compliance user detected - redirecting to compliance dashboard")
            return '/compliance/dashboard'
            
        # Branch and Customer Management
        elif user_role in [UserRole.BRANCH_MANAGER.value, UserRole.CUSTOMER_SERVICE.value]:
            logger.info("🏪 Auth Service: Branch management user detected - redirecting to branch dashboard")
            return '/branch/dashboard'
            
        # Business Account Holders
        elif user_role == UserRole.BUSINESS_USER.value:
            logger.info("💼 Auth Service: Business user detected - redirecting to business dashboard")
            return '/business/dashboard'
            
        # Standard Users and Default
        else:
            logger.info("👤 Auth Service: Standard user detected - redirecting to modular dashboard")
            return '/dashboard/'  # Modular Dashboard Module
    
    def validate_registration(self, registration_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate user registration data
        
        Args:
            registration_data: Dictionary containing registration form data
            
        Returns:
            Dict with validation results
        """
        errors = []
        
        # Required field validation
        required_fields = ['username', 'email', 'password', 'confirm_password', 'first_name', 'last_name']
        for field in required_fields:
            if not registration_data.get(field):
                errors.append(f"{field.replace('_', ' ').title()} is required")
        
        # Username validation
        username = registration_data.get('username', '')
        if len(username) < 3:
            errors.append("Username must be at least 3 characters long")
        elif User.query.filter_by(username=username).first():
            errors.append("Username already exists")
        
        # Email validation
        email = registration_data.get('email', '')
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            errors.append("Invalid email address format")
        elif User.query.filter_by(email=email).first():
            errors.append("Email address already registered")
        
        # Password validation - Banking-Grade Security
        password = registration_data.get('password', '')
        confirm_password = registration_data.get('confirm_password', '')
        
        password_errors = self.validate_password_complexity(password)
        errors.extend(password_errors)
        
        if password != confirm_password:
            errors.append("Passwords do not match")
        
        # Age validation
        date_of_birth = registration_data.get('date_of_birth')
        if date_of_birth:
            try:
                birth_date = datetime.strptime(date_of_birth, '%Y-%m-%d')
                age = (datetime.now() - birth_date).days // 365
                if age < self.config.MIN_AGE_REQUIREMENT:
                    errors.append(f"You must be at least {self.config.MIN_AGE_REQUIREMENT} years old to register")
            except ValueError:
                errors.append("Invalid date of birth format")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def validate_password_complexity(self, password: str) -> List[str]:
        """
        Comprehensive password complexity validation for banking-grade security
        
        Args:
            password: Password to validate
            
        Returns:
            List of validation error messages
        """
        errors = []
        
        # Length validation
        if len(password) < self.config.MIN_PASSWORD_LENGTH:
            errors.append(f"Password must be at least {self.config.MIN_PASSWORD_LENGTH} characters long")
        
        # Character type validation with counts
        uppercase_count = len(re.findall(r'[A-Z]', password))
        lowercase_count = len(re.findall(r'[a-z]', password))
        numbers_count = len(re.findall(r'\d', password))
        special_count = len(re.findall(r'[!@#$%^&*(),.?":{}|<>]', password))
        
        if self.config.REQUIRE_UPPERCASE and uppercase_count < self.config.MIN_UPPERCASE_COUNT:
            errors.append(f"Password must contain at least {self.config.MIN_UPPERCASE_COUNT} uppercase letters")
        
        if self.config.REQUIRE_LOWERCASE and lowercase_count < self.config.MIN_LOWERCASE_COUNT:
            errors.append(f"Password must contain at least {self.config.MIN_LOWERCASE_COUNT} lowercase letters")
        
        if self.config.REQUIRE_NUMBERS and numbers_count < self.config.MIN_NUMBERS_COUNT:
            errors.append(f"Password must contain at least {self.config.MIN_NUMBERS_COUNT} numbers")
        
        if self.config.REQUIRE_SPECIAL_CHARS and special_count < self.config.MIN_SPECIAL_CHARS_COUNT:
            errors.append(f"Password must contain at least {self.config.MIN_SPECIAL_CHARS_COUNT} special characters (!@#$%^&*(),.?\":{{}}|<>)")
        
        # Forbidden patterns validation
        password_lower = password.lower()
        for pattern in self.config.FORBIDDEN_PATTERNS:
            if pattern.lower() in password_lower:
                errors.append(f"Password cannot contain common patterns like '{pattern}'")
        
        # Additional security checks
        if len(set(password)) < 8:
            errors.append("Password must contain at least 8 unique characters")
        
        # Check for consecutive characters
        consecutive_count = 0
        for i in range(len(password) - 1):
            if ord(password[i+1]) == ord(password[i]) + 1:
                consecutive_count += 1
                if consecutive_count >= 2:
                    errors.append("Password cannot contain 3 or more consecutive characters")
                    break
            else:
                consecutive_count = 0
        
        # Check for repeated characters
        for char in password:
            if password.count(char) > 2:
                errors.append("Password cannot have the same character repeated more than twice")
                break
        
        return errors
    
    def create_user(self, registration_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create new user account
        
        Args:
            registration_data: Validated registration data
            
        Returns:
            Dict with creation results
        """
        try:
            # Create new user
            user = User()
            user.username = registration_data['username']
            user.email = registration_data['email']
            user.set_password(registration_data['password'])  # Use the set_password method
            user.first_name = registration_data.get('first_name', '')
            user.last_name = registration_data.get('last_name', '')
            user.phone_number = registration_data.get('phone_number')
            user.date_of_birth = datetime.strptime(registration_data['date_of_birth'], '%Y-%m-%d') if registration_data.get('date_of_birth') else None
            user.role = registration_data.get('account_type', 'standard_user')
            user.account_type = registration_data.get('account_type', 'individual')
            user.is_active = True
            user.is_verified = False  # Requires email verification
            user.created_at = datetime.utcnow()
            user.updated_at = datetime.utcnow()
            
            db.session.add(user)
            db.session.commit()
            
            logger.info("✅ Auth Service: New user created: %s", registration_data['username'])
            
            return {
                'success': True,
                'user_id': user.id,
                'message': 'User account created successfully'
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error("❌ Auth Service: User creation error: %s", str(e))
            return {
                'success': False,
                'error': 'Failed to create user account. Please try again.'
            }
    
    def initiate_password_reset(self, email: str) -> Dict[str, Any]:
        """
        Initiate password reset process
        
        Args:
            email: User's email address
            
        Returns:
            Dict with reset initiation results
        """
        try:
            user = User.query.filter_by(email=email).first()
            if not user:
                # Don't reveal if email exists for security
                return {
                    'success': True,
                    'message': 'Password reset instructions sent if email exists'
                }
            
            # Generate reset token (simplified for now)
            reset_token = f"reset_{user.id}_{datetime.utcnow().timestamp()}"
            
            # In production, you would:
            # 1. Store token in database with expiration
            # 2. Send email with reset link
            # 3. Implement token validation
            
            logger.info("✅ Auth Service: Password reset initiated for user: %s", user.username)
            
            return {
                'success': True,
                'message': 'Password reset instructions have been sent to your email'
            }
            
        except Exception as e:
            logger.error("❌ Auth Service: Password reset error: %s", str(e))
            return {
                'success': False,
                'error': 'Password reset service unavailable. Please try again later.'
            }
    
    def authenticate_user(self, username: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user with username and password
        
        Args:
            username: User's username or email
            password: User's password
            
        Returns:
            Dict with authentication results
        """
        try:
            # Find user by username or email
            user = User.query.filter(
                (User.username == username) | (User.email == username)
            ).first()
            
            if not user:
                logger.warning("❌ Auth Service: Authentication failed - user not found: %s", username)
                return {
                    'success': False,
                    'error': 'Invalid username or password'
                }
            
            # Check if account is locked
            if user.is_account_locked():
                logger.warning("❌ Auth Service: Authentication failed - account locked: %s", username)
                return {
                    'success': False,
                    'error': 'Account is temporarily locked. Please try again later.'
                }
            
            # Check password
            if not user.check_password(password):
                # Increment failed login attempts
                user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
                user.last_failed_login = datetime.utcnow()
                
                # Lock account after 5 failed attempts
                if user.failed_login_attempts >= 5:
                    user.account_locked_until = datetime.utcnow() + timedelta(minutes=30)
                
                db.session.commit()
                
                logger.warning("❌ Auth Service: Authentication failed - invalid password: %s", username)
                return {
                    'success': False,
                    'error': 'Invalid username or password'
                }
            
            # Check if account is active
            if not user.is_active:
                logger.warning("❌ Auth Service: Authentication failed - account inactive: %s", username)
                return {
                    'success': False,
                    'error': 'Account is deactivated. Please contact support.'
                }
            
            # Successful authentication
            user.failed_login_attempts = 0
            user.last_login = datetime.utcnow()
            user.last_activity = datetime.utcnow()
            db.session.commit()
            
            logger.info("✅ Auth Service: Authentication successful: %s", username)
            
            return {
                'success': True,
                'user': user,
                'user_id': user.id,
                'username': user.username,
                'role': user.role,
                'account_type': user.account_type
            }
            
        except Exception as e:
            logger.error("❌ Auth Service: Authentication error: %s", str(e))
            return {
                'success': False,
                'error': 'Authentication service unavailable. Please try again later.'
            }
    
    def reset_password_with_token(self, token: str, new_password: str) -> Dict[str, Any]:
        """
        Reset password using token
        
        Args:
            token: Password reset token
            new_password: New password
            
        Returns:
            Dict with reset results
        """
        try:
            # Token validation (simplified for now)
            if not token.startswith('reset_'):
                return {
                    'success': False,
                    'error': 'Invalid or expired reset token'
                }
            
            # Extract user ID from token (in production, use proper token validation)
            try:
                user_id = int(token.split('_')[1])
                user = User.query.get(user_id)
                if not user:
                    return {
                        'success': False,
                        'error': 'Invalid or expired reset token'
                    }
            except (ValueError, IndexError):
                return {
                    'success': False,
                    'error': 'Invalid or expired reset token'
                }
            
            # Update password
            user.password_hash = generate_password_hash(new_password)
            user.updated_at = datetime.utcnow()
            db.session.commit()
            
            logger.info("✅ Auth Service: Password reset completed for user: %s", user.username)
            
            return {
                'success': True,
                'message': 'Password successfully reset'
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error("❌ Auth Service: Password reset error: %s", str(e))
            return {
                'success': False,
                'error': 'Password reset failed. Please try again.'
            }