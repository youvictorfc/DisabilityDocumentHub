from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from models import User

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/users', methods=['GET'])
@login_required
def user_list():
    """View all users and manage admin status"""
    if not current_user.is_admin:
        flash('You do not have permission to access the admin panel', 'danger')
        return redirect(url_for('index'))
    
    users = User.query.order_by(User.id).all()
    return render_template('admin/user_list.html', users=users)

@admin_bp.route('/users/<int:user_id>/toggle-admin', methods=['POST'])
@login_required
def toggle_admin(user_id):
    """Toggle admin status for a user"""
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    
    # Cannot change your own admin status
    if user_id == current_user.id:
        return jsonify({'success': False, 'message': 'You cannot change your own admin status'}), 400
    
    user = User.query.get_or_404(user_id)
    
    try:
        # Toggle admin status
        user.is_admin = not user.is_admin
        db.session.commit()
        
        status = 'added' if user.is_admin else 'removed'
        return jsonify({
            'success': True, 
            'message': f'Admin privileges {status} for {user.username}',
            'is_admin': user.is_admin
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500