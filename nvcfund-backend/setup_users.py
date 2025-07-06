#!/usr/bin/env python3
"""
Setup test users for NVC Banking Platform
Creates sample users with different roles for authentication testing
"""

import os
import sys
sys.path.append('.')

from werkzeug.security import generate_password_hash
from datetime import datetime
from main import app
from modules.core.extensions import db
from modules.auth.models import User, UserRole

def create_test_users():
    """Create test users with different roles"""
    
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        
        test_users = [
            {
                'username': 'admin',
                'email': 'admin@nvcbank.com',
                'password': 'admin123',
                'first_name': 'Admin',
                'last_name': 'User',
                'role': UserRole.ADMIN,
                'is_active': True
            },
            {
                'username': 'treasury',
                'email': 'treasury@nvcbank.com',
                'password': 'treasury123',
                'first_name': 'Treasury',
                'last_name': 'Officer',
                'role': UserRole.TREASURY_OFFICER,
                'is_active': True
            },
            {
                'username': 'user',
                'email': 'user@nvcbank.com',
                'password': 'user123',
                'first_name': 'Standard',
                'last_name': 'User',
                'role': UserRole.STANDARD_USER,
                'is_active': True
            },
            {
                'username': 'compliance',
                'email': 'compliance@nvcbank.com',
                'password': 'compliance123',
                'first_name': 'Compliance',
                'last_name': 'Officer',
                'role': UserRole.COMPLIANCE_OFFICER,
                'is_active': True
            }
        ]
        
        print("Creating test users...")
        
        for user_data in test_users:
            # Check if user already exists
            existing_user = User.query.filter_by(username=user_data['username']).first()
            if existing_user:
                print(f"User {user_data['username']} already exists, skipping...")
                continue
            
            # Create new user
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                password_hash=generate_password_hash(user_data['password']),
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                role=user_data['role'],
                is_active=user_data['is_active'],
                created_at=datetime.utcnow(),
                last_login=None,
                login_count=0
            )
            
            db.session.add(user)
            print(f"✓ Created user: {user_data['username']} ({user_data['role'].value})")
        
        # Commit all changes
        db.session.commit()
        print(f"\n✅ Successfully created {len(test_users)} test users!")
        
        print("\n🔐 Login credentials:")
        print("==================")
        for user_data in test_users:
            print(f"Username: {user_data['username']} | Password: {user_data['password']} | Role: {user_data['role'].value}")

if __name__ == '__main__':
    create_test_users()