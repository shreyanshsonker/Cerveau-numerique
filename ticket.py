from src.models.user import db
from datetime import datetime
from enum import Enum

class TicketStatus(Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

class TicketPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class Ticket(db.Model):
    __tablename__ = 'tickets'
    
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.Enum(TicketStatus), nullable=False, default=TicketStatus.OPEN)
    priority = db.Column(db.Enum(TicketPriority), nullable=False, default=TicketPriority.MEDIUM)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)
    attachment_path = db.Column(db.String(500), nullable=True)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    
    # Relationships
    comments = db.relationship('Comment', backref='ticket', lazy='dynamic', cascade='all, delete-orphan')
    votes = db.relationship('Vote', backref='ticket', lazy='dynamic', cascade='all, delete-orphan')
    
    @property
    def upvotes(self):
        """Get number of upvotes"""
        return self.votes.filter_by(is_upvote=True).count()
    
    @property
    def downvotes(self):
        """Get number of downvotes"""
        return self.votes.filter_by(is_upvote=False).count()
    
    @property
    def comment_count(self):
        """Get number of comments"""
        return self.comments.count()
    
    def to_dict(self, include_comments=False):
        """Convert ticket to dictionary"""
        result = {
            'id': self.id,
            'subject': self.subject,
            'description': self.description,
            'status': self.status.value,
            'priority': self.priority.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'attachment_path': self.attachment_path,
            'user_id': self.user_id,
            'assigned_to': self.assigned_to,
            'category_id': self.category_id,
            'upvotes': self.upvotes,
            'downvotes': self.downvotes,
            'comment_count': self.comment_count,
            'creator': self.creator.to_dict() if self.creator else None,
            'assignee': self.assignee.to_dict() if self.assignee else None,
            'category': self.category.to_dict() if self.category else None
        }
        
        if include_comments:
            result['comments'] = [comment.to_dict() for comment in self.comments.order_by('created_at')]
        
        return result
    
    def __repr__(self):
        return f'<Ticket {self.id}: {self.subject}>'

