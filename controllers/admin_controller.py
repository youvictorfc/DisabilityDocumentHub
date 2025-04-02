from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, send_file
from flask_login import login_required, current_user
from datetime import datetime
import os
from app import db
from models import User, Form, FormResponse

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

@admin_bp.route('/submissions', methods=['GET'])
@login_required
def form_submissions():
    """View all form submissions across the system"""
    if not current_user.is_admin:
        flash('You do not have permission to access the admin panel', 'danger')
        return redirect(url_for('index'))
    
    # Filter parameters
    form_id = request.args.get('form_id', type=int)
    user_id = request.args.get('user_id', type=int)
    status = request.args.get('status')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Base query
    query = FormResponse.query
    
    # Apply filters
    if form_id:
        query = query.filter(FormResponse.form_id == form_id)
    if user_id:
        query = query.filter(FormResponse.user_id == user_id)
    if status == 'complete':
        query = query.filter(FormResponse.is_complete == True)
    elif status == 'incomplete':
        query = query.filter(FormResponse.is_complete == False)
    
    # Add option to filter by deleted forms
    deleted_status = request.args.get('deleted_status')
    if deleted_status == 'only_active':
        query = query.join(Form).filter(Form.is_deleted == False)
    elif deleted_status == 'only_deleted':
        query = query.join(Form).filter(Form.is_deleted == True)
    
    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(FormResponse.created_at >= start_date_obj)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
            query = query.filter(FormResponse.created_at <= end_date_obj)
        except ValueError:
            pass
    
    # Get all form submissions with related form and user data
    submissions = query.order_by(FormResponse.submitted_at.desc().nulls_last(), 
                               FormResponse.updated_at.desc()).all()
    
    # Get lists for filter dropdowns
    forms = Form.query.order_by(Form.title).all()
    users = User.query.order_by(User.username).all()
    
    return render_template('admin/form_submissions.html', 
                          submissions=submissions, 
                          forms=forms,
                          users=users,
                          selected_filters={
                              'form_id': form_id,
                              'user_id': user_id,
                              'status': status,
                              'start_date': start_date,
                              'end_date': end_date,
                              'deleted_status': deleted_status
                          })

@admin_bp.route('/submissions/<int:response_id>/download-pdf', methods=['GET'])
@login_required
def download_submission_pdf(response_id):
    """Download the PDF for a form submission"""
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    
    response = FormResponse.query.get_or_404(response_id)
    
    if not response.pdf_path or not os.path.exists(response.pdf_path):
        flash('PDF file not found for this submission', 'danger')
        return redirect(url_for('admin.form_submissions'))
    
    form = Form.query.get(response.form_id)
    user = User.query.get(response.user_id)
    
    # Create a more descriptive filename
    form_title = form.title if form else 'Unknown Form'
    username = user.username if user else f'User_{response.user_id}'
    safe_form_title = ''.join(c if c.isalnum() else '_' for c in form_title)
    
    return send_file(
        response.pdf_path,
        as_attachment=True,
        download_name=f"{safe_form_title}_{username}_{response.id}.pdf"
    )