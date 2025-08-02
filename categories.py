from flask import Blueprint, request, jsonify, session
from src.models.user import db, User, UserRole
from src.models.category import Category
from src.routes.auth import login_required, role_required

categories_bp = Blueprint('categories', __name__)

@categories_bp.route('/', methods=['GET'])
@login_required
def get_categories():
    """Get all active categories"""
    try:
        categories = Category.query.filter_by(is_active=True).order_by(Category.name).all()
        return jsonify({
            'categories': [category.to_dict() for category in categories]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch categories'}), 500

@categories_bp.route('/', methods=['POST'])
@role_required([UserRole.ADMIN])
def create_category():
    """Create a new category (Admin only)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        name = data.get('name', '').strip()
        if not name:
            return jsonify({'error': 'Category name is required'}), 400
        
        # Check if category already exists
        if Category.query.filter_by(name=name).first():
            return jsonify({'error': 'Category already exists'}), 400
        
        description = data.get('description', '').strip()
        color = data.get('color', '#6B7280').strip()
        
        # Validate color format (basic hex color validation)
        if not color.startswith('#') or len(color) != 7:
            return jsonify({'error': 'Invalid color format. Use hex format like #FF0000'}), 400
        
        category = Category(
            name=name,
            description=description,
            color=color
        )
        
        db.session.add(category)
        db.session.commit()
        
        return jsonify({
            'message': 'Category created successfully',
            'category': category.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create category'}), 500

@categories_bp.route('/<int:category_id>', methods=['GET'])
@login_required
def get_category(category_id):
    """Get a specific category"""
    try:
        category = Category.query.get(category_id)
        
        if not category:
            return jsonify({'error': 'Category not found'}), 404
        
        return jsonify({'category': category.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch category'}), 500

@categories_bp.route('/<int:category_id>', methods=['PUT'])
@role_required([UserRole.ADMIN])
def update_category(category_id):
    """Update a category (Admin only)"""
    try:
        category = Category.query.get(category_id)
        
        if not category:
            return jsonify({'error': 'Category not found'}), 404
        
        data = request.get_json()
        
        # Update name if provided
        if 'name' in data:
            name = data['name'].strip()
            if not name:
                return jsonify({'error': 'Category name cannot be empty'}), 400
            
            # Check if another category with this name exists
            existing = Category.query.filter(
                Category.name == name,
                Category.id != category_id
            ).first()
            
            if existing:
                return jsonify({'error': 'Category name already exists'}), 400
            
            category.name = name
        
        # Update description if provided
        if 'description' in data:
            category.description = data['description'].strip()
        
        # Update color if provided
        if 'color' in data:
            color = data['color'].strip()
            if not color.startswith('#') or len(color) != 7:
                return jsonify({'error': 'Invalid color format. Use hex format like #FF0000'}), 400
            category.color = color
        
        # Update active status if provided
        if 'is_active' in data:
            category.is_active = bool(data['is_active'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Category updated successfully',
            'category': category.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update category'}), 500

@categories_bp.route('/<int:category_id>', methods=['DELETE'])
@role_required([UserRole.ADMIN])
def delete_category(category_id):
    """Soft delete a category (Admin only)"""
    try:
        category = Category.query.get(category_id)
        
        if not category:
            return jsonify({'error': 'Category not found'}), 404
        
        # Check if category has tickets
        if category.tickets.count() > 0:
            # Soft delete - just deactivate
            category.is_active = False
            db.session.commit()
            return jsonify({'message': 'Category deactivated successfully'}), 200
        else:
            # Hard delete if no tickets
            db.session.delete(category)
            db.session.commit()
            return jsonify({'message': 'Category deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete category'}), 500

