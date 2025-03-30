import json
import os
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from models import Form, FormResponse
from services.form.form_service import extract_form_structure, validate_form_submission
from services.form.pdf_service import generate_pdf_from_form
from services.email_service import send_form_email

form_bp = Blueprint('form', __name__, url_prefix='/forms')

@form_bp.route('/')
@login_required
def form_list():
    forms = Form.query.all()
    
    # Get user's in-progress forms
    user_responses = FormResponse.query.filter_by(
        user_id=current_user.id,
        is_complete=False
    ).all()
    
    in_progress_forms = []
    for response in user_responses:
        in_progress_forms.append({
            'form_id': response.form_id,
            'form_title': response.form.title,
            'response_id': response.id,
            'updated_at': response.updated_at
        })
    
    return render_template('forms/form_list.html', forms=forms, in_progress_forms=in_progress_forms)

@form_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_form():
    if not current_user.is_admin:
        flash('Only administrators can upload forms', 'danger')
        return redirect(url_for('form.form_list'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        file = request.files.get('form_file')
        
        if not title or not file:
            flash('Title and form file are required', 'danger')
            return render_template('forms/form_upload.html')
        
        # Check file extension
        if file.filename == '':
            flash('No file selected', 'danger')
            return render_template('forms/form_upload.html')
        
        allowed_extensions = {'pdf', 'doc', 'docx', 'txt'}
        if not '.' in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
            flash('File type not allowed', 'danger')
            return render_template('forms/form_upload.html')
        
        # Save the file
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['FORM_UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        try:
            # Extract form structure using OpenAI
            form_structure = extract_form_structure(file_path)
            
            # Create form record
            new_form = Form(
                title=title,
                description=description,
                file_path=file_path,
                structure=json.dumps(form_structure)
            )
            
            db.session.add(new_form)
            db.session.commit()
            
            flash('Form uploaded successfully', 'success')
            return redirect(url_for('form.form_list'))
            
        except Exception as e:
            flash(f'Error processing form: {str(e)}', 'danger')
            return render_template('forms/form_upload.html')
    
    return render_template('forms/form_upload.html')

@form_bp.route('/<int:form_id>/fill', methods=['GET'])
@login_required
def fill_form(form_id):
    form = Form.query.get_or_404(form_id)
    
    # Check if there's an existing in-progress response
    existing_response = FormResponse.query.filter_by(
        form_id=form_id,
        user_id=current_user.id,
        is_complete=False
    ).first()
    
    if existing_response:
        response_id = existing_response.id
        form_data = json.loads(form.structure)
        answers = json.loads(existing_response.answers) if existing_response.answers else {}
    else:
        # Create new form response
        new_response = FormResponse(
            form_id=form_id,
            user_id=current_user.id,
            answers=json.dumps({})
        )
        db.session.add(new_response)
        db.session.commit()
        
        response_id = new_response.id
        form_data = json.loads(form.structure)
        answers = {}
    
    return render_template('forms/form_fill.html', 
                          form=form, 
                          form_data=form_data, 
                          answers=answers, 
                          response_id=response_id)

@form_bp.route('/response/<int:response_id>/save', methods=['POST'])
@login_required
def save_form_progress(response_id):
    response = FormResponse.query.get_or_404(response_id)
    
    # Ensure user owns this response
    if response.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    data = request.json
    current_question = data.get('currentQuestion')
    answers = data.get('answers', {})
    
    # Update response
    response.answers = json.dumps(answers)
    response.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'success': True})

@form_bp.route('/response/<int:response_id>/submit', methods=['POST'])
@login_required
def submit_form(response_id):
    response = FormResponse.query.get_or_404(response_id)
    
    # Ensure user owns this response
    if response.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    form = Form.query.get(response.form_id)
    data = request.json
    answers = data.get('answers', {})
    
    # Validate submission
    form_structure = json.loads(form.structure)
    validation_result = validate_form_submission(form_structure, answers)
    
    if not validation_result['valid']:
        return jsonify({
            'success': False, 
            'message': 'Form has incomplete or invalid fields',
            'missing_fields': validation_result['missing_fields']
        }), 400
    
    # Generate PDF
    try:
        pdf_filename = f"form_{form.id}_user_{current_user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        pdf_path = os.path.join(current_app.config['PDF_OUTPUT_FOLDER'], pdf_filename)
        
        generate_pdf_from_form(form.title, form_structure, answers, pdf_path)
        
        # Update response
        response.answers = json.dumps(answers)
        response.is_complete = True
        response.pdf_path = pdf_path
        response.submitted_at = datetime.utcnow()
        db.session.commit()
        
        # Send email with PDF to both the user and Minto Disability Services
        try:
            # Send to the user
            send_form_email(
                recipient_email=current_user.email,
                form_title=form.title,
                pdf_path=pdf_path
            )
            
            # Also ensure it goes to Minto Disability Services
            minto_email = "hello@mintodisabilityservices.com.au"
            if current_user.email.lower() != minto_email.lower():
                send_form_email(
                    recipient_email=minto_email,
                    form_title=f"{form.title} - Submitted by {current_user.username}",
                    pdf_path=pdf_path
                )
            
            email_sent = True
        except Exception as e:
            email_sent = False
            current_app.logger.error(f"Email sending failed: {str(e)}")
        
        return jsonify({
            'success': True,
            'message': 'Form submitted successfully',
            'email_sent': email_sent
        })
        
    except Exception as e:
        current_app.logger.error(f"Form submission error: {str(e)}")
        return jsonify({'success': False, 'message': f'Error submitting form: {str(e)}'}), 500
