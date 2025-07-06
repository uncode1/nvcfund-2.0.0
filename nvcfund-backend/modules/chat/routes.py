"""
Live Chat Module - Routes
NVC Banking Platform - Interactive Multi-Agent Chat System

Features:
- Real-time chat with multiple specialized agents
- Business question handling with domain expertise
- WebSocket integration for live communication
- Agent routing based on question type
- Chat history and session management
"""

from flask import Blueprint, render_template, request, jsonify, session
from flask_login import login_required, current_user
from flask_socketio import emit, join_room, leave_room
from datetime import datetime
import json
import uuid
from typing import Dict, List, Any

try:
    from app.decorators import banking_security_required, rate_limit
except ImportError:
    # Fallback decorators if main decorators not available
    def banking_security_required(f):
        return f
    def rate_limit(*args, **kwargs):
        def chat_rate_limit_decorator(f):
            return f
        return chat_rate_limit_decorator

try:
    from ..core.logging import BankingLogger
except ImportError:
    import logging
    BankingLogger = logging.getLogger
from .services import ChatService, AgentService
from .models import ChatSession, ChatMessage, Agent

# Initialize module components
chat_bp = Blueprint('chat', __name__, url_prefix='/chat', template_folder='templates')
logger = BankingLogger('chat')
chat_service = ChatService()
agent_service = AgentService()

@chat_bp.route('/')
@login_required
@banking_security_required
def chat_home():
    """Main chat interface"""
    try:
        # Get available agents for user
        available_agents = agent_service.get_available_agents(current_user.role)
        
        # Get recent chat sessions
        recent_sessions = chat_service.get_recent_sessions(current_user.id)
        
        return render_template('chat/chat_home.html', 
                             available_agents=available_agents,
                             recent_sessions=recent_sessions)
    except Exception as e:
        logger.error(f"Error loading chat home: {e}")
        return render_template('error.html', error="Chat system temporarily unavailable")

@chat_bp.route('/session/<session_id>')
@login_required
@banking_security_required
def chat_session(session_id):
    """Individual chat session view"""
    try:
        # Validate session access
        chat_session = chat_service.get_session(session_id, current_user.id)
        if not chat_session:
            return render_template('error.html', error="Chat session not found")
        
        # Get chat history
        messages = chat_service.get_session_messages(session_id)
        
        return render_template('chat_session.html',
                             session=chat_session,
                             messages=messages)
    except Exception as e:
        logger.error(f"Error loading chat session {session_id}: {e}")
        return render_template('error.html', error="Chat session unavailable")

@chat_bp.route('/api/start-session', methods=['POST'])
@login_required
@banking_security_required
@rate_limit(requests_per_minute=10)
def start_chat_session():
    """Start new chat session with agent"""
    try:
        data = request.get_json()
        agent_type = data.get('agent_type')
        initial_question = data.get('initial_question', '')
        
        # Create new chat session
        session_id = chat_service.create_session(
            user_id=current_user.id,
            agent_type=agent_type,
            initial_question=initial_question
        )
        
        # Log session creation
        logger.info(f"Chat session created: {session_id} for user {current_user.id}")
        
        return jsonify({
            'status': 'success',
            'session_id': session_id,
            'redirect_url': f'/chat/session/{session_id}'
        })
        
    except Exception as e:
        logger.error(f"Error starting chat session: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to start chat session'
        }), 500

@chat_bp.route('/api/send-message', methods=['POST'])
@login_required
@banking_security_required
@rate_limit(requests_per_minute=30)
def send_message():
    """Send message in chat session"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        message_text = data.get('message')
        
        # Validate session
        if not chat_service.validate_session_access(session_id, current_user.id):
            return jsonify({'status': 'error', 'message': 'Invalid session'}), 403
        
        # Send message and get agent response
        message_id = chat_service.send_message(
            session_id=session_id,
            user_id=current_user.id,
            message=message_text
        )
        
        # Get agent response
        agent_response = chat_service.get_agent_response(session_id, message_text)
        
        return jsonify({
            'status': 'success',
            'message_id': message_id,
            'agent_response': agent_response
        })
        
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to send message'
        }), 500

@chat_bp.route('/api/get-messages/<session_id>')
@login_required
@banking_security_required
@rate_limit(requests_per_minute=60)
def get_messages(session_id):
    """Get messages for chat session"""
    try:
        # Validate session access
        if not chat_service.validate_session_access(session_id, current_user.id):
            return jsonify({'status': 'error', 'message': 'Invalid session'}), 403
        
        messages = chat_service.get_session_messages(session_id)
        
        return jsonify({
            'status': 'success',
            'messages': [msg.to_dict() for msg in messages]
        })
        
    except Exception as e:
        logger.error(f"Error getting messages: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve messages'
        }), 500

@chat_bp.route('/api/agents')
@login_required
@banking_security_required
@rate_limit(requests_per_minute=20)
def get_agents():
    """Get available agents for user"""
    try:
        agents = agent_service.get_available_agents(current_user.role)
        
        return jsonify({
            'status': 'success',
            'agents': [agent.to_dict() for agent in agents]
        })
        
    except Exception as e:
        logger.error(f"Error getting agents: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve agents'
        }), 500

@chat_bp.route('/api/transfer-session', methods=['POST'])
@login_required
@banking_security_required
@rate_limit(requests_per_minute=5)
def transfer_session():
    """Transfer chat session to different agent"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        new_agent_type = data.get('new_agent_type')
        transfer_reason = data.get('transfer_reason', '')
        
        # Validate session access
        if not chat_service.validate_session_access(session_id, current_user.id):
            return jsonify({'status': 'error', 'message': 'Invalid session'}), 403
        
        # Transfer session
        success = chat_service.transfer_session(
            session_id=session_id,
            new_agent_type=new_agent_type,
            transfer_reason=transfer_reason
        )
        
        if success:
            return jsonify({
                'status': 'success',
                'message': 'Session transferred successfully'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to transfer session'
            }), 500
            
    except Exception as e:
        logger.error(f"Error transferring session: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to transfer session'
        }), 500

@chat_bp.route('/api/end-session', methods=['POST'])
@login_required
@banking_security_required
@rate_limit(requests_per_minute=10)
def end_session():
    """End chat session"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        satisfaction_rating = data.get('satisfaction_rating')
        feedback = data.get('feedback', '')
        
        # Validate session access
        if not chat_service.validate_session_access(session_id, current_user.id):
            return jsonify({'status': 'error', 'message': 'Invalid session'}), 403
        
        # End session
        success = chat_service.end_session(
            session_id=session_id,
            satisfaction_rating=satisfaction_rating,
            feedback=feedback
        )
        
        if success:
            return jsonify({
                'status': 'success',
                'message': 'Session ended successfully'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to end session'
            }), 500
            
    except Exception as e:
        logger.error(f"Error ending session: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to end session'
        }), 500

@chat_bp.route('/support')
@login_required
@banking_security_required
def support_chat():
    """Support chat interface"""
    try:
        return render_template('chat/support_chat.html',
                             user=current_user,
                             page_title='Support Chat')
    except Exception as e:
        logger.error(f"Error loading support chat: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('chat.chat_home'))

@chat_bp.route('/api/health')
@rate_limit(requests_per_minute=100)
def health_check():
    """Chat module health check"""
    return jsonify({
        'status': 'healthy',
        'app_module': 'chat',
        'timestamp': datetime.utcnow().isoformat(),
        'agents_available': len(agent_service.get_all_agents()),
        'active_sessions': chat_service.get_active_session_count()
    })

# WebSocket event handlers
def init_socketio_handlers(socketio):
    """Initialize WebSocket handlers for real-time chat"""
    
    @socketio.on('join_chat')
    def handle_join_chat(data):
        """User joins chat room"""
        if not current_user.is_authenticated:
            return False
        
        session_id = data.get('session_id')
        if chat_service.validate_session_access(session_id, current_user.id):
            join_room(session_id)
            emit('joined_chat', {'session_id': session_id})
            logger.info(f"User {current_user.id} joined chat {session_id}")
        else:
            emit('error', {'message': 'Invalid session'})
    
    @socketio.on('leave_chat')
    def handle_leave_chat(data):
        """User leaves chat room"""
        if not current_user.is_authenticated:
            return False
        
        session_id = data.get('session_id')
        leave_room(session_id)
        emit('left_chat', {'session_id': session_id})
        logger.info(f"User {current_user.id} left chat {session_id}")
    
    @socketio.on('typing')
    def handle_typing(data):
        """Handle typing indicators"""
        if not current_user.is_authenticated:
            return False
        
        session_id = data.get('session_id')
        if chat_service.validate_session_access(session_id, current_user.id):
            emit('user_typing', {
                'user_id': current_user.id,
                'username': current_user.username,
                'typing': data.get('typing', False)
            }, room=session_id, include_self=False)
    
    @socketio.on('message')
    def handle_message(data):
        """Handle real-time message sending"""
        if not current_user.is_authenticated:
            return False
        
        session_id = data.get('session_id')
        message_text = data.get('message')
        
        if chat_service.validate_session_access(session_id, current_user.id):
            # Send message
            message_id = chat_service.send_message(
                session_id=session_id,
                user_id=current_user.id,
                message=message_text
            )
            
            # Emit to room
            emit('new_message', {
                'message_id': message_id,
                'user_id': current_user.id,
                'username': current_user.username,
                'message': message_text,
                'timestamp': datetime.utcnow().isoformat()
            }, room=session_id)
            
            # Get agent response
            agent_response = chat_service.get_agent_response(session_id, message_text)
            if agent_response:
                emit('agent_response', agent_response, room=session_id)
        else:
            emit('error', {'message': 'Invalid session'})

# Register route collection
CHAT_ROUTES = [
    '/',
    '/session/<session_id>',
    '/api/start-session',
    '/api/send-message',
    '/api/get-messages/<session_id>',
    '/api/agents',
    '/api/transfer-session',
    '/api/end-session',
    '/api/health'
]