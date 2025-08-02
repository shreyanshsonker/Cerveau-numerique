from src.models.user import db
from datetime import datetime

class Comment(db.Model):
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_internal = db.Column(db.Boolean, default=False)  # Internal notes for agents
    
    # Foreign Keys
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    def to_dict(self):
        """Convert comment to dictionary"""
        return {
            'id': self.id,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_internal': self.is_internal,
            'ticket_id': self.ticket_id,
            'user_id': self.user_id,
            'author': self.author.to_dict() if self.author else None
        }
    
    def __repr__(self):
        return f'<Comment {self.id} on Ticket {self.ticket_id}>'

