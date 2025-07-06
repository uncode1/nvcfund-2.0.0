"""
Core Database Models for NVC Banking Platform
Reusable models with proper relationships to avoid conflicts
"""

from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Optional, Dict, Any
import uuid

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Numeric, Index
from sqlalchemy.orm import relationship, validates, declarative_base
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.dialects.postgresql import UUID, JSONB
from flask_login import UserMixin

from .extensions import db

# === BASE MIXINS FOR REUSABILITY ===

class TimestampMixin:
    """Reusable timestamp mixin"""
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

class AuditMixin:
    """Reusable audit trail mixin"""
    @declared_attr
    def created_by(cls):
        return Column(Integer, ForeignKey('users.id'), nullable=True)
    
    @declared_attr
    def updated_by(cls):
        return Column(Integer, ForeignKey('users.id'), nullable=True)

# === FORM SUBMISSION TRACKING ===

class FormSubmissionStatus(Enum):
    """Form submission status tracking"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REJECTED = "rejected"

class FormSubmission(TimestampMixin, db.Model):
    """Track all form submissions across the banking platform"""
    __tablename__ = 'form_submissions'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    submission_id = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # Form metadata
    form_type = Column(String(100), nullable=False)
    module_name = Column(String(50), nullable=False)
    
    # User tracking with proper relationship
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    user_ip = Column(String(45), nullable=False)
    user_agent = Column(Text, nullable=True)
    
    # Security
    csrf_token = Column(String(128), nullable=False)
    session_id = Column(String(128), nullable=False)
    
    # Form data (encrypted in production)
    form_data = Column(Text, nullable=False)
    
    # Processing status
    status = Column(String(20), nullable=False, default=FormSubmissionStatus.PENDING.value)
    error_message = Column(Text, nullable=True)
    
    # Processing timestamps
    submitted_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    
    # Audit trail
    processing_notes = Column(Text, nullable=True)
    approved_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], backref="form_submissions")
    approved_by_user = relationship("User", foreign_keys=[approved_by], backref="approved_submissions")
    
    def __repr__(self):
        return f'<FormSubmission {self.submission_id}: {self.form_type}>'

# === BANKING TRANSACTIONS ===

class TransactionType(Enum):
    """Banking transaction types"""
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"
    PAYMENT = "payment"
    FEE = "fee"
    INTEREST = "interest"
    LOAN_PAYMENT = "loan_payment"
    WIRE_TRANSFER = "wire_transfer"
    ACH_TRANSFER = "ach_transfer"
    CARD_PAYMENT = "card_payment"

class TransactionStatus(Enum):
    """Transaction processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REVERSED = "reversed"

class BankingTransaction(TimestampMixin, AuditMixin, db.Model):
    """Core banking transactions table"""
    __tablename__ = 'banking_transactions'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    transaction_id = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # Transaction details
    transaction_type = Column(String(20), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), nullable=False, default='USD')
    
    # Account information with proper relationships
    from_account_id = Column(Integer, nullable=True)  # References banking.BankAccount
    to_account_id = Column(Integer, nullable=True)    # References banking.BankAccount
    
    # External accounts
    external_account_number = Column(String(50), nullable=True)
    routing_number = Column(String(20), nullable=True)
    
    # Processing
    status = Column(String(20), nullable=False, default=TransactionStatus.PENDING.value)
    reference_number = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    
    # Form submission reference
    form_submission_id = Column(Integer, ForeignKey('form_submissions.id'), nullable=True)
    
    # User tracking
    initiated_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Processing timestamps
    initiated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships - handled by banking module to avoid circular imports
    form_submission = relationship("FormSubmission", backref="banking_transactions")
    initiated_by_user = relationship("User", foreign_keys=[initiated_by], backref="initiated_transactions")
    
    def __repr__(self):
        return f'<Transaction {self.transaction_id}: {self.transaction_type} ${self.amount}>'

# === BANK ACCOUNTS ===

class AccountType(Enum):
    """Bank account types"""
    CHECKING = "checking"
    SAVINGS = "savings"
    BUSINESS = "business"
    INVESTMENT = "investment"
    MONEY_MARKET = "money_market"
    CERTIFICATE_DEPOSIT = "cd"

# === TREASURY OPERATIONS ===

class TreasuryOperation(TimestampMixin, AuditMixin, db.Model):
    """Treasury operations and settings"""
    __tablename__ = 'treasury_operations'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    operation_id = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # Operation details
    operation_type = Column(String(50), nullable=False)
    operation_data = Column(Text, nullable=False)
    
    # Form submission reference with proper relationship
    form_submission_id = Column(Integer, ForeignKey('form_submissions.id'), nullable=False)
    
    # Authorization with proper relationship
    authorized_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    authorization_level = Column(String(20), nullable=False)
    
    # Status
    status = Column(String(20), nullable=False, default='pending_approval')
    
    # Processing timestamps
    submitted_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    approved_at = Column(DateTime, nullable=True)
    implemented_at = Column(DateTime, nullable=True)
    
    # Relationships
    form_submission = relationship("FormSubmission", backref="treasury_operations")
    authorized_by_user = relationship("User", foreign_keys=[authorized_by], backref="authorized_treasury_operations")
    
    def __repr__(self):
        return f'<TreasuryOperation {self.operation_id}: {self.operation_type}>'

# === AUDIT TRAIL ===

class AuditLog(db.Model):
    """Comprehensive audit logging for all form submissions and transactions"""
    __tablename__ = 'audit_logs'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    log_id = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # Event details
    event_type = Column(String(50), nullable=False)
    event_description = Column(Text, nullable=False)
    
    # User and session with proper relationships
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    session_id = Column(String(128), nullable=False)
    user_ip = Column(String(45), nullable=False)
    
    # Related records with proper relationships
    form_submission_id = Column(Integer, ForeignKey('form_submissions.id'), nullable=True)
    transaction_id = Column(Integer, ForeignKey('banking_transactions.id'), nullable=True)
    
    # Additional data
    additional_data = Column(Text, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], backref="audit_logs")
    form_submission = relationship("FormSubmission", backref="audit_logs")
    transaction = relationship("BankingTransaction", backref="audit_logs")
    
    def __repr__(self):
        return f'<AuditLog {self.log_id}: {self.event_type}>'

# === ADDITIONAL MODELS FOR COMPATIBILITY ===

# Account alias for backwards compatibility - will be set by banking module
Account = None

# Transaction alias for API module compatibility
Transaction = BankingTransaction

# Add indexes for performance
Index('idx_form_submissions_user_id', FormSubmission.user_id)
Index('idx_form_submissions_status', FormSubmission.status)
Index('idx_form_submissions_submitted_at', FormSubmission.submitted_at)
Index('idx_banking_transactions_user_id', BankingTransaction.initiated_by)
Index('idx_banking_transactions_status', BankingTransaction.status)
Index('idx_banking_transactions_initiated_at', BankingTransaction.initiated_at)
Index('idx_audit_logs_user_id', AuditLog.user_id)
Index('idx_audit_logs_created_at', AuditLog.created_at)