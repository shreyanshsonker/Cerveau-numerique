from src.models.user import db
from datetime import datetime

class Vote(db.Model):
    __tablename__ = 'votes'
    
    id = db.Column(db.Integer, primary_key=True)
    is_upvote = db.Column(db.Boolean, nullable=False)  # True for upvote, False for downvote
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Unique constraint to prevent multiple votes from same user on same ticket
    __table_args__ = (db.UniqueConstraint('ticket_id', 'user_id', name='unique_user_ticket_vote'),)
    
    def to_dict(self):
        """Convert vote to dictionary"""
        return {
            'id': self.id,
            'is_upvote': self.is_upvote,
            'created_at': self.created_at.isoformat(),
            'ticket_id': self.ticket_id,
            'user_id': self.user_id
        }
    
    def __repr__(self):
        vote_type = "upvote" if self.is_upvote else "downvote"
        return f'<Vote {self.id}: {vote_type} on Ticket {self.ticket_id}>'

