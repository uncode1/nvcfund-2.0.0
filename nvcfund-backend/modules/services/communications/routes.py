"""
Communications Routes
NVC Banking Platform - Communications Management Web Routes

This module provides web endpoints for communication functionality:
- Communication preferences management
- Email template administration
- Communication logs and analytics
- Test messaging capabilities
"""

from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from modules.services.communications import communications_bp
from modules.services.communications.services import EmailService, PersonalizedMessageService, CommunicationScheduler
from modules.services.communications.models import CommunicationLog, CommunicationPreference, EmailTemplate
from modules.core.security_enforcement import secure_banking_route
from modules.core.extensions import db
import logging
import time

logger = logging.getLogger(__name__)


@communications_bp.route('/')
@login_required
@secure_banking_route(
    required_permissions=['communications_access'],
    rate_limit=10,
    validation_rules={
        'required_fields': [],
        'optional_fields': []
    }
)
def communications_dashboard():
    """Communications management dashboard"""
    try:
        # Get communication statistics for current user
        user_logs = CommunicationLog.query.filter_by(
            recipient_user_id=current_user.id
        ).order_by(CommunicationLog.sent_at.desc()).limit(10).all()
        
        # Get user's communication preferences
        preferences = CommunicationPreference.get_or_create_preferences(current_user.id)
        
        # Get communication statistics
        total_sent = CommunicationLog.query.filter_by(
            recipient_user_id=current_user.id
        ).count()
        
        successful_sent = CommunicationLog.query.filter_by(
            recipient_user_id=current_user.id,
            status='sent'
        ).count()
        
        return render_template('communications/dashboard.html',
                             recent_communications=user_logs,
                             preferences=preferences,
                             total_sent=total_sent,
                             successful_sent=successful_sent)
        
    except Exception as e:
        logger.error(f"Error loading communications dashboard for user {current_user.id}: {str(e)}")
        flash('Error loading communications dashboard. Please try again.', 'error')
        return redirect(url_for('dashboard.dashboard_home'))


@communications_bp.route('/preferences', methods=['GET', 'POST'])
@login_required
@secure_banking_route(
    required_permissions=['communications_preferences'],
    rate_limit=5,
    validation_rules={
        'required_fields': [],
        'optional_fields': ['email_enabled', 'marketing_emails', 'transaction_alerts', 
                           'security_alerts', 'account_statements', 'birthday_messages', 
                           'holiday_messages']
    }
)
def communication_preferences():
    """Manage communication preferences"""
    try:
        preferences = CommunicationPreference.get_or_create_preferences(current_user.id)
        
        if request.method == 'POST':
            # Update preferences based on form data
            preferences.email_enabled = bool(request.form.get('email_enabled'))
            preferences.marketing_emails = bool(request.form.get('marketing_emails'))
            preferences.transaction_alerts = bool(request.form.get('transaction_alerts'))
            preferences.security_alerts = bool(request.form.get('security_alerts'))
            preferences.account_statements = bool(request.form.get('account_statements'))
            preferences.birthday_messages = bool(request.form.get('birthday_messages'))
            preferences.holiday_messages = bool(request.form.get('holiday_messages'))
            preferences.weekly_summary = bool(request.form.get('weekly_summary'))
            preferences.monthly_statements = bool(request.form.get('monthly_statements'))
            
            db.session.commit()
            flash('Communication preferences updated successfully!', 'success')
            return redirect(url_for('communications.communications_dashboard'))
        
        return render_template('communications/preferences.html', preferences=preferences)
        
    except Exception as e:
        logger.error(f"Error managing communication preferences for user {current_user.id}: {str(e)}")
        flash('Error updating preferences. Please try again.', 'error')
        return redirect(url_for('communications.communications_dashboard'))


@communications_bp.route('/send-test-email', methods=['POST'])
@login_required
@secure_banking_route(
    required_permissions=['communications_test'],
    rate_limit=2,
    validation_rules={
        'required_fields': ['template_name'],
        'optional_fields': ['subject']
    }
)
def send_test_email():
    """Send a test email to current user"""
    try:
        template_name = request.form.get('template_name', 'welcome_email')
        subject = request.form.get('subject', 'Test Email from NVC Banking')
        
        email_service = EmailService()
        message_service = PersonalizedMessageService()
        
        # Generate context based on template type
        if template_name == 'welcome_email':
            context = message_service.generate_welcome_email_context(current_user)
        elif template_name == 'login_notification':
            context = message_service.generate_login_notification_context(
                current_user, request.remote_addr
            )
        elif template_name == 'birthday_message':
            context = message_service.generate_birthday_message_context(current_user)
        elif template_name == 'holiday_message':
            context = message_service.generate_holiday_message_context(
                current_user, 'Test Holiday'
            )
        else:
            context = {'first_name': getattr(current_user, 'first_name', 'Valued Customer')}
        
        # Send test email
        success = email_service.send_email(
            to_email=current_user.email,
            subject=f"[TEST] {subject}",
            template_name=template_name,
            context=context
        )
        
        if success:
            flash(f'Test email sent successfully to {current_user.email}!', 'success')
        else:
            flash('Failed to send test email. Please check your email configuration.', 'error')
        
        return redirect(url_for('communications.communications_dashboard'))
        
    except Exception as e:
        logger.error(f"Error sending test email for user {current_user.id}: {str(e)}")
        flash('Error sending test email. Please try again.', 'error')
        return redirect(url_for('communications.communications_dashboard'))


@communications_bp.route('/history')
@login_required
@secure_banking_route(
    required_permissions=['communications_history'],
    rate_limit=10,
    validation_rules={
        'required_fields': [],
        'optional_fields': ['page', 'per_page']
    }
)
def communication_history():
    """View communication history for current user"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        # Get paginated communication logs
        logs = CommunicationLog.query.filter_by(
            recipient_user_id=current_user.id
        ).order_by(CommunicationLog.sent_at.desc()).paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return render_template('communications/history.html', logs=logs)
        
    except Exception as e:
        logger.error(f"Error loading communication history for user {current_user.id}: {str(e)}")
        flash('Error loading communication history. Please try again.', 'error')
        return redirect(url_for('communications.communications_dashboard'))


@communications_bp.route('/message-center')
@login_required
@secure_banking_route(
    required_permissions=['communications_messages'],
    rate_limit=10,
    validation_rules={
        'required_fields': [],
        'optional_fields': ['page', 'filter_type']
    }
)
def message_center():
    """Message center interface"""
    try:
        page = request.args.get('page', 1, type=int)
        filter_type = request.args.get('filter_type', 'all')
        
        return render_template('communications/message_center.html',
                             user=current_user,
                             page_title='Message Center',
                             current_page=page,
                             filter_type=filter_type)
    except Exception as e:
        logger.error(f"Error loading message center for user {current_user.id}: {str(e)}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('communications.communications_dashboard'))


@communications_bp.route('/notification-settings')
@login_required
@secure_banking_route(
    required_permissions=['communications_notifications'],
    rate_limit=5,
    validation_rules={
        'required_fields': [],
        'optional_fields': ['notification_type', 'channel_type']
    }
)
def notification_settings():
    """Notification settings management"""
    try:
        return render_template('communications/notification_settings.html',
                             user=current_user,
                             page_title='Notification Settings')
    except Exception as e:
        logger.error(f"Error loading notification settings for user {current_user.id}: {str(e)}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('communications.communications_dashboard'))


@communications_bp.route('/admin')
@login_required
@secure_banking_route(
    required_permissions=['communications_admin'],
    rate_limit=10,
    validation_rules={
        'required_fields': [],
        'optional_fields': []
    }
)
def admin_dashboard():
    """Communications administration dashboard (admin only)"""
    try:
        # Get communication statistics
        total_logs = CommunicationLog.query.count()
        successful_logs = CommunicationLog.query.filter_by(status='sent').count()
        failed_logs = CommunicationLog.query.filter_by(status='failed').count()
        
        # Get recent logs
        recent_logs = CommunicationLog.query.order_by(
            CommunicationLog.sent_at.desc()
        ).limit(20).all()
        
        # Get email templates
        templates = EmailTemplate.query.filter_by(is_active=True).all()
        
        return render_template('communications/admin_dashboard.html',
                             total_logs=total_logs,
                             successful_logs=successful_logs,
                             failed_logs=failed_logs,
                             recent_logs=recent_logs,
                             templates=templates)
        
    except Exception as e:
        logger.error(f"Error loading communications admin dashboard: {str(e)}")
        flash('Error loading admin dashboard. Please try again.', 'error')
        return redirect(url_for('communications.communications_dashboard'))


@communications_bp.route('/admin/send-bulk', methods=['POST'])
@login_required
@secure_banking_route(
    required_permissions=['communications_bulk_send'],
    rate_limit=1,
    validation_rules={
        'required_fields': ['template_name', 'subject', 'recipient_type'],
        'optional_fields': ['target_users']
    }
)
def send_bulk_communication():
    """Send bulk communications (admin only)"""
    try:
        template_name = request.form.get('template_name')
        subject = request.form.get('subject')
        recipient_type = request.form.get('recipient_type')  # 'all', 'active', 'specific'
        
        email_service = EmailService()
        message_service = PersonalizedMessageService()
        
        # Determine recipients
        from modules.auth.models import User
        
        if recipient_type == 'all':
            recipients = User.query.all()
        elif recipient_type == 'active':
            recipients = User.query.filter_by(is_active=True).all()
        elif recipient_type == 'specific':
            user_ids = request.form.getlist('target_users')
            recipients = User.query.filter(User.id.in_(user_ids)).all()
        else:
            flash('Invalid recipient type selected.', 'error')
            return redirect(url_for('communications.admin_dashboard'))
        
        # Send emails
        sent_count = 0
        failed_count = 0
        
        for user in recipients:
            try:
                # Check user's communication preferences
                preferences = CommunicationPreference.get_or_create_preferences(user.id)
                if not preferences.email_enabled:
                    continue  # Skip if user has disabled emails
                
                # Generate context based on template
                if template_name == 'welcome_email':
                    context = message_service.generate_welcome_email_context(user)
                elif template_name == 'birthday_message':
                    context = message_service.generate_birthday_message_context(user)
                elif template_name == 'holiday_message':
                    context = message_service.generate_holiday_message_context(user, 'Holiday')
                else:
                    context = {'first_name': getattr(user, 'first_name', 'Valued Customer')}
                
                success = email_service.send_email(
                    to_email=user.email,
                    subject=subject,
                    template_name=template_name,
                    context=context
                )
                
                if success:
                    sent_count += 1
                else:
                    failed_count += 1
                    
            except Exception as e:
                logger.error(f"Error sending bulk email to user {user.id}: {str(e)}")
                failed_count += 1
        
        flash(f'Bulk communication completed. Sent: {sent_count}, Failed: {failed_count}', 'info')
        return redirect(url_for('communications.admin_dashboard'))
        
    except Exception as e:
        logger.error(f"Error sending bulk communication: {str(e)}")
        flash('Error sending bulk communication. Please try again.', 'error')
        return redirect(url_for('communications.admin_dashboard'))


@communications_bp.route('/api/status')
@login_required
def api_status():
    """Get communication service status as JSON"""
    try:
        email_service = EmailService()
        
        # Check SendGrid configuration
        sendgrid_configured = email_service.client is not None
        
        # Get recent communication stats
        total_today = CommunicationLog.query.filter(
            CommunicationLog.sent_at >= db.func.current_date()
        ).count()
        
        successful_today = CommunicationLog.query.filter(
            CommunicationLog.sent_at >= db.func.current_date(),
            CommunicationLog.status == 'sent'
        ).count()
        
        return jsonify({
            'success': True,
            'status': {
                'sendgrid_configured': sendgrid_configured,
                'emails_sent_today': total_today,
                'successful_today': successful_today,
                'success_rate': (successful_today / total_today * 100) if total_today > 0 else 0
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting communication status: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error getting communication status'
        }), 500


@communications_bp.route('/health')
def health_check():
    """Communications module health check"""
    try:
        # Test database connectivity
        db.session.execute(db.text('SELECT 1'))
        
        # Test SendGrid configuration
        email_service = EmailService()
        sendgrid_healthy = email_service.client is not None
        
        return jsonify({
            'status': 'healthy',
            'app_module': 'communications',
            'features': {
                'email_sending': sendgrid_healthy,
                'database_connectivity': True,
                'template_rendering': True,
                'audit_logging': True,
                'bulk_messaging': True,
                'personalization': True
            },
            'sendgrid_configured': sendgrid_healthy
        })
        
    except Exception as e:
        logger.error(f"Communications health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'app_module': 'communications',
            'error': str(e)
        }), 500


# Error handlers for Communications module
@communications_bp.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors within Communications module"""
    return render_template('communications/error.html', 
                         error_code=404,
                         error_message="Communications page not found"), 404


@communications_bp.route('/send-welcome-email/<int:user_id>')
@login_required
@secure_banking_route(
    required_permissions=['communications_admin'],
    rate_limit=5,
    validation_rules={'required_fields': [], 'optional_fields': []}
)
def send_welcome_email(user_id):
    """Send welcome email using orphaned template"""
    try:
        from modules.auth.models import User
        target_user = User.query.get_or_404(user_id)
        
        email_service = EmailService()
        message_service = PersonalizedMessageService()
        context = message_service.generate_welcome_email_context(target_user)
        
        success = email_service.send_email_from_template(
            to_email=target_user.email,
            template_path='communications/email/welcome_email.html',
            context=context
        )
        
        if success:
            flash(f'Welcome email sent to {target_user.email}', 'success')
        else:
            flash('Failed to send welcome email', 'error')
            
        return redirect(url_for('communications.admin_dashboard'))
        
    except Exception as e:
        logger.error(f"Error sending welcome email: {e}")
        flash('Error sending welcome email', 'error')
        return redirect(url_for('communications.admin_dashboard'))

@communications_bp.route('/send-verification-email/<int:user_id>')
@login_required
@secure_banking_route(
    required_permissions=['communications_admin'],
    rate_limit=3,
    validation_rules={'required_fields': [], 'optional_fields': []}
)
def send_verification_email(user_id):
    """Send signup verification email using orphaned template"""
    try:
        from modules.auth.models import User
        target_user = User.query.get_or_404(user_id)
        
        email_service = EmailService()
        verification_token = f"verify_{user_id}_{int(time.time())}"
        
        context = {
            'user': target_user,
            'verification_link': url_for('auth.verify_email', token=verification_token, _external=True),
            'company_name': 'NVC Banking Platform'
        }
        
        success = email_service.send_email_from_template(
            to_email=target_user.email,
            template_path='communications/email/signup_verification.html',
            context=context
        )
        
        if success:
            flash(f'Verification email sent to {target_user.email}', 'success')
        else:
            flash('Failed to send verification email', 'error')
            
        return redirect(url_for('communications.admin_dashboard'))
        
    except Exception as e:
        logger.error(f"Error sending verification email: {e}")
        flash('Error sending verification email', 'error')
        return redirect(url_for('communications.admin_dashboard'))

@communications_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors within Communications module"""
    logger.error(f"Communications module internal error: {str(error)}")
    return render_template('communications/error.html',
                         error_code=500,
                         error_message="Internal server error in Communications module"), 500