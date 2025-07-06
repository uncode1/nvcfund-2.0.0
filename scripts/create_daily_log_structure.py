#!/usr/bin/env python3
"""
Daily Log Structure Creation Script
Automatically creates nested year/month/date log structure for current date
"""

import os
from datetime import datetime
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_daily_log_structure():
    """Create nested log directory structure for current date"""
    
    # Get current date
    now = datetime.now()
    year = now.strftime("%Y")
    month = now.strftime("%m") 
    date = now.strftime("%d")
    
    # Create base logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Create nested directory structure
    current_date_dir = logs_dir / year / month / date
    current_date_dir.mkdir(parents=True, exist_ok=True)
    
    # Create category subdirectories
    categories = [
        "security_reports",    # Security audit reports and assessments
        "application",         # General application logs
        "banking",            # Banking operation logs  
        "compliance",         # AML, KYC, regulatory compliance logs
        "admin",              # Administrative and management logs
        "errors",             # Error logs and exception reports
        "audit",              # Audit trail logs
        "system",             # System health and monitoring logs
        "transactions",       # Transaction processing logs
        "auth",               # Authentication and authorization logs
        "api"                 # API access and integration logs
    ]
    
    created_dirs = []
    
    for category in categories:
        category_dir = current_date_dir / category
        if not category_dir.exists():
            category_dir.mkdir(exist_ok=True)
            created_dirs.append(category)
            logger.info(f"Created category directory: {year}/{month}/{date}/{category}")
    
    if created_dirs:
        logger.info(f"Created {len(created_dirs)} new log directories for {year}-{month}-{date}")
    else:
        logger.info(f"Log structure for {year}-{month}-{date} already exists")
    
    return current_date_dir

def get_current_log_path(category="application"):
    """Get the current log path for a specific category"""
    now = datetime.now()
    year = now.strftime("%Y")
    month = now.strftime("%m")
    date = now.strftime("%d")
    
    logs_dir = Path("logs") / year / month / date / category
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    return logs_dir

def get_log_file_path(filename, category="application"):
    """Get full path for a log file in the appropriate category"""
    log_dir = get_current_log_path(category)
    return log_dir / filename

if __name__ == "__main__":
    logger.info("Creating daily log structure...")
    current_dir = create_daily_log_structure()
    logger.info(f"Daily log structure ready: {current_dir}")