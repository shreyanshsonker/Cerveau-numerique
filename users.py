from flask import Blueprint, request, jsonify, session
from src.models.user import db, User, UserRole
from src.routes.auth import login_required, role_required

users_bp = Blueprint('users', __name__)

@users_bp.route('/', methods=['GET'])
@role_required([UserRole.ADMIN, UserRole.SUPPORT_AGENT])
def get_users():
    """Get all users (Admin and Support Agent only)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        role_filter = request.args.get('role')
        search = request.args.get('search', '').strip()
        
        query = User.query
        
        # Role filtering
        if role_filter:
            try:
                role_enum = UserRole(role_filter)
                query = query.filter(User.role == role_enum)
            except ValueError:
                return jsonify({'error': 'Invalid role'}), 400
        
        # Search functionality
        if search:
            query = query.filter(
                (User.username.contains(search)) |
                (User.email.contains(search))
            )
        
        # Pagination
        pagination = query.order_by(User.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        users = [user.to_dict() for user in pagination.items]
        
        return jsonify({
            'users': users,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch users'}), 500

@users_bp.route('/agents', methods=['GET'])
@role_required([UserRole.ADMIN, UserRole.SUPPORT_AGENT])
def get_agents():
    """Get all support agents for ticket assignment"""
    try:
        agents = User.query.filter(
            User.role.in_([UserRole.SUPPORT_AGENT, UserRole.ADMIN]),
            User.is_active == True
        ).order_by(User.username).all()
        
        return jsonify({
            'agents': [agent.to_dict() for agent in agents]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch agents'}), 500

@users_bp.route('/<int:user_id>', methods=['GET'])
@login_required
def get_user(user_id):
    """Get a specific user"""
    try:
        current_user = User.query.get(session['user_id'])
        
        # Users can only view their own profile unless they're admin/agent
        if (current_user.role == UserRole.END_USER and 
            current_user.id != user_id):
            return jsonify({'error': 'Access denied'}), 403
        
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({'user': user.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch user'}), 500

@users_bp.route('/<int:user_id>', methods=['PUT'])
@login_required
def update_user(user_id):
    """Update a user"""
    try:
        current_user = User.query.get(session['user_id'])
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Permission check
        if (current_user.role == UserRole.END_USER and 
            current_user.id != user_id):
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        
        # Update email if provided and user is updating their own profile
        if 'email' in data and current_user.id == user_id:
            email = data['email'].strip().lower()
            if email != user.email:
                # Check if email already exists
                if User.query.filter(User.email == email, User.id != user_id).first():
                    return jsonify({'error': 'Email already exists'}), 400
                user.email = email
        
        # Update username if provided and user is updating their own profile
        if 'username' in data and current_user.id == user_id:
            username = data['username'].strip()
            if username != user.username:
                if len(username) < 3:
                    return jsonify({'error': 'Username must be at least 3 characters long'}), 400
                # Check if username already exists
                if User.query.filter(User.username == username, User.id != user_id).first():
                    return jsonify({'error': 'Username already exists'}), 400
                user.username = username
        
        # Only admins can update role and active status
        if current_user.role == UserRole.ADMIN:
            if 'role' in data:
                try:
                    user.role = UserRole(data['role'])
                except ValueError:
                    return jsonify({'error': 'Invalid role'}), 400
            
            if 'is_active' in data:
                user.is_active = bool(data['is_active'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'User updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update user'}), 500

@users_bp.route('/<int:user_id>/deactivate', methods=['POST'])
@role_required([UserRole.ADMIN])
def deactivate_user(user_id):
    """Deactivate a user (Admin only)"""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Prevent admin from deactivating themselves
        if user.id == session['user_id']:
            return jsonify({'error': 'Cannot deactivate your own account'}), 400
        
        user.is_active = False
        db.session.commit()
        
        return jsonify({'message': 'User deactivated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to deactivate user'}), 500

@users_bp.route('/<int:user_id>/activate', methods=['POST'])
@role_required([UserRole.ADMIN])
def activate_user(user_id):
    """Activate a user (Admin only)"""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        user.is_active = True
        db.session.commit()
        
        return jsonify({'message': 'User activated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to activate user'}), 500

@users_bp.route('/stats', methods=['GET'])
@role_required([UserRole.ADMIN])
def get_user_stats():
    """Get user statistics (Admin only)"""
    try:
        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        end_users = User.query.filter_by(role=UserRole.END_USER).count()
        support_agents = User.query.filter_by(role=UserRole.SUPPORT_AGENT).count()
        admins = User.query.filter_by(role=UserRole.ADMIN).count()
        
        return jsonify({
            'stats': {
                'total_users': total_users,
                'active_users': active_users,
                'inactive_users': total_users - active_users,
                'end_users': end_users,
                'support_agents': support_agents,
                'admins': admins
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch user statistics'}), 500

