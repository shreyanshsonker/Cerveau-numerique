import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.models.ticket import Ticket
from src.models.category import Category
from src.models.comment import Comment
from src.models.vote import Vote
from src.routes.auth import auth_bp
from src.routes.tickets import tickets_bp
from src.routes.categories import categories_bp
from src.routes.users import users_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Enable CORS for all routes
CORS(app, origins="*")

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(tickets_bp, url_prefix='/api/tickets')
app.register_blueprint(categories_bp, url_prefix='/api/categories')
app.register_blueprint(users_bp, url_prefix='/api/users')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Create upload directory
upload_dir = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
os.makedirs(upload_dir, exist_ok=True)

with app.app_context():
    db.create_all()
    
    # Create default categories if they don't exist
    from src.models.category import Category
    if Category.query.count() == 0:
        default_categories = [
            {'name': 'Technical Support', 'description': 'Technical issues and bugs', 'color': '#3B82F6'},
            {'name': 'Account Issues', 'description': 'Account related problems', 'color': '#EF4444'},
            {'name': 'Feature Request', 'description': 'New feature suggestions', 'color': '#10B981'},
            {'name': 'General Inquiry', 'description': 'General questions and inquiries', 'color': '#8B5CF6'},
            {'name': 'Billing', 'description': 'Billing and payment issues', 'color': '#F59E0B'}
        ]
        
        for cat_data in default_categories:
            category = Category(**cat_data)
            db.session.add(category)
        
        db.session.commit()
        print("Default categories created")

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
