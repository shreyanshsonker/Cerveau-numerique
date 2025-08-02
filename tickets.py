from flask import Blueprint, request, jsonify, session, current_app
from werkzeug.utils import secure_filename
from src.models.user import db, User, UserRole
from src.models.ticket import Ticket, TicketStatus, TicketPriority
from src.models.category import Category
from src.models.comment import Comment
from src.models.vote import Vote
from src.routes.auth import login_required, role_required
from datetime import datetime
import os
import uuid

tickets_bp = Blueprint('tickets', __name__)

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@tickets_bp.route('/', methods=['GET'])
@login_required
def get_tickets():
    """Get tickets with filtering and pagination"""
    try:
        user = User.query.get(session['user_id'])
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        
        # Build query based on user role and filters
        query = Ticket.query
        
        # Role-based filtering
        if user.role == UserRole.END_USER:
            # End users can only see their own tickets
            my_tickets_only = request.args.get('my_tickets', 'true').lower() == 'true'
            if my_tickets_only:
                query = query.filter(Ticket.user_id == user.id)
        elif user.role == UserRole.SUPPORT_AGENT:
            # Support agents can see all tickets or filter by assignment
            ticket_queue = request.args.get('queue', 'all')
            if ticket_queue == 'my_tickets':
                query = query.filter(Ticket.assigned_to == user.id)
            elif ticket_queue == 'unassigned':
                query = query.filter(Ticket.assigned_to.is_(None))
        
        # Status filtering
        status = request.args.get('status')
        if status:
            try:
                status_enum = TicketStatus(status)
                query = query.filter(Ticket.status == status_enum)
            except ValueError:
                return jsonify({'error': 'Invalid status'}), 400
        
        # Category filtering
        category_id = request.args.get('category_id', type=int)
        if category_id:
            query = query.filter(Ticket.category_id == category_id)
        
        # Priority filtering
        priority = request.args.get('priority')
        if priority:
            try:
                priority_enum = TicketPriority(priority)
                query = query.filter(Ticket.priority == priority_enum)
            except ValueError:
                return jsonify({'error': 'Invalid priority'}), 400
        
        # Search functionality
        search = request.args.get('search', '').strip()
        if search:
            query = query.filter(
                (Ticket.subject.contains(search)) |
                (Ticket.description.contains(search))
            )
        
        # Sorting
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')
        
        if sort_by == 'most_replied':
            # Sort by comment count
            query = query.outerjoin(Comment).group_by(Ticket.id)
            if sort_order == 'desc':
                query = query.order_by(db.func.count(Comment.id).desc())
            else:
                query = query.order_by(db.func.count(Comment.id).asc())
        elif sort_by == 'updated_at':
            if sort_order == 'desc':
                query = query.order_by(Ticket.updated_at.desc())
            else:
                query = query.order_by(Ticket.updated_at.asc())
        else:  # Default to created_at
            if sort_order == 'desc':
                query = query.order_by(Ticket.created_at.desc())
            else:
                query = query.order_by(Ticket.created_at.asc())
        
        # Pagination
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        tickets = [ticket.to_dict() for ticket in pagination.items]
        
        return jsonify({
            'tickets': tickets,
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
        return jsonify({'error': 'Failed to fetch tickets'}), 500

@tickets_bp.route('/', methods=['POST'])
@login_required
def create_ticket():
    """Create a new ticket"""
    try:
        # Handle file upload
        attachment_path = None
        if 'attachment' in request.files:
            file = request.files['attachment']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Add UUID to prevent filename conflicts
                filename = f"{uuid.uuid4()}_{filename}"
                upload_path = os.path.join(current_app.static_folder, 'uploads', filename)
                file.save(upload_path)
                attachment_path = f"uploads/{filename}"
        
        # Get form data
        subject = request.form.get('subject', '').strip()
        description = request.form.get('description', '').strip()
        category_id = request.form.get('category_id', type=int)
        priority = request.form.get('priority', 'medium')
        
        # Validate required fields
        if not subject:
            return jsonify({'error': 'Subject is required'}), 400
        
        if not description:
            return jsonify({'error': 'Description is required'}), 400
        
        if not category_id:
            return jsonify({'error': 'Category is required'}), 400
        
        # Validate category exists
        category = Category.query.get(category_id)
        if not category or not category.is_active:
            return jsonify({'error': 'Invalid category'}), 400
        
        # Validate priority
        try:
            priority_enum = TicketPriority(priority)
        except ValueError:
            return jsonify({'error': 'Invalid priority'}), 400
        
        # Create ticket
        ticket = Ticket(
            subject=subject,
            description=description,
            category_id=category_id,
            priority=priority_enum,
            user_id=session['user_id'],
            attachment_path=attachment_path
        )
        
        db.session.add(ticket)
        db.session.commit()
        
        return jsonify({
            'message': 'Ticket created successfully',
            'ticket': ticket.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create ticket'}), 500

@tickets_bp.route('/<int:ticket_id>', methods=['GET'])
@login_required
def get_ticket(ticket_id):
    """Get a specific ticket with comments"""
    try:
        user = User.query.get(session['user_id'])
        ticket = Ticket.query.get(ticket_id)
        
        if not ticket:
            return jsonify({'error': 'Ticket not found'}), 404
        
        # Check permissions
        if user.role == UserRole.END_USER and ticket.user_id != user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        return jsonify({'ticket': ticket.to_dict(include_comments=True)}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch ticket'}), 500

@tickets_bp.route('/<int:ticket_id>', methods=['PUT'])
@login_required
def update_ticket(ticket_id):
    """Update a ticket"""
    try:
        user = User.query.get(session['user_id'])
        ticket = Ticket.query.get(ticket_id)
        
        if not ticket:
            return jsonify({'error': 'Ticket not found'}), 404
        
        # Check permissions
        if user.role == UserRole.END_USER and ticket.user_id != user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        
        # Update allowed fields based on user role
        if user.role in [UserRole.SUPPORT_AGENT, UserRole.ADMIN]:
            # Agents and admins can update status and assignment
            if 'status' in data:
                try:
                    ticket.status = TicketStatus(data['status'])
                    if ticket.status == TicketStatus.RESOLVED:
                        ticket.resolved_at = datetime.utcnow()
                except ValueError:
                    return jsonify({'error': 'Invalid status'}), 400
            
            if 'assigned_to' in data:
                if data['assigned_to']:
                    assignee = User.query.get(data['assigned_to'])
                    if not assignee or assignee.role not in [UserRole.SUPPORT_AGENT, UserRole.ADMIN]:
                        return jsonify({'error': 'Invalid assignee'}), 400
                ticket.assigned_to = data['assigned_to']
        
        # All users can update priority if they own the ticket or are agents/admins
        if 'priority' in data and (ticket.user_id == user.id or user.role in [UserRole.SUPPORT_AGENT, UserRole.ADMIN]):
            try:
                ticket.priority = TicketPriority(data['priority'])
            except ValueError:
                return jsonify({'error': 'Invalid priority'}), 400
        
        ticket.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Ticket updated successfully',
            'ticket': ticket.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update ticket'}), 500

@tickets_bp.route('/<int:ticket_id>/comments', methods=['POST'])
@login_required
def add_comment(ticket_id):
    """Add a comment to a ticket"""
    try:
        user = User.query.get(session['user_id'])
        ticket = Ticket.query.get(ticket_id)
        
        if not ticket:
            return jsonify({'error': 'Ticket not found'}), 404
        
        # Check permissions - users can only comment on their own tickets
        if user.role == UserRole.END_USER and ticket.user_id != user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        content = data.get('content', '').strip()
        
        if not content:
            return jsonify({'error': 'Comment content is required'}), 400
        
        # Support agents can mark comments as internal
        is_internal = False
        if user.role in [UserRole.SUPPORT_AGENT, UserRole.ADMIN]:
            is_internal = data.get('is_internal', False)
        
        comment = Comment(
            content=content,
            ticket_id=ticket_id,
            user_id=user.id,
            is_internal=is_internal
        )
        
        db.session.add(comment)
        
        # Update ticket's updated_at timestamp
        ticket.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Comment added successfully',
            'comment': comment.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to add comment'}), 500

@tickets_bp.route('/<int:ticket_id>/vote', methods=['POST'])
@login_required
def vote_ticket(ticket_id):
    """Vote on a ticket (upvote or downvote)"""
    try:
        user_id = session['user_id']
        ticket = Ticket.query.get(ticket_id)
        
        if not ticket:
            return jsonify({'error': 'Ticket not found'}), 404
        
        data = request.get_json()
        is_upvote = data.get('is_upvote', True)
        
        # Check if user already voted
        existing_vote = Vote.query.filter_by(
            ticket_id=ticket_id,
            user_id=user_id
        ).first()
        
        if existing_vote:
            # Update existing vote
            existing_vote.is_upvote = is_upvote
        else:
            # Create new vote
            vote = Vote(
                ticket_id=ticket_id,
                user_id=user_id,
                is_upvote=is_upvote
            )
            db.session.add(vote)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Vote recorded successfully',
            'upvotes': ticket.upvotes,
            'downvotes': ticket.downvotes
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to record vote'}), 500

@tickets_bp.route('/<int:ticket_id>/vote', methods=['DELETE'])
@login_required
def remove_vote(ticket_id):
    """Remove vote from a ticket"""
    try:
        user_id = session['user_id']
        
        vote = Vote.query.filter_by(
            ticket_id=ticket_id,
            user_id=user_id
        ).first()
        
        if not vote:
            return jsonify({'error': 'Vote not found'}), 404
        
        db.session.delete(vote)
        db.session.commit()
        
        ticket = Ticket.query.get(ticket_id)
        
        return jsonify({
            'message': 'Vote removed successfully',
            'upvotes': ticket.upvotes,
            'downvotes': ticket.downvotes
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to remove vote'}), 500

