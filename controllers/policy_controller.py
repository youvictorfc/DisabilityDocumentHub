import os
import json
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from models import Document, DocumentChunk
from services.document.document_service import process_document, extract_text_from_file
from services.document.vector_service import search_documents
from services.ai.openai_service import generate_answer_with_context

policy_bp = Blueprint('policy', __name__, url_prefix='/policies')

@policy_bp.route('/')
@login_required
def policy_list():
    documents = Document.query.all()
    return render_template('policies/policy_list.html', documents=documents)

@policy_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_policy():
    if not current_user.is_admin:
        flash('Only administrators can upload policy documents', 'danger')
        return redirect(url_for('policy.policy_list'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        document_type = request.form.get('document_type')
        file = request.files.get('document_file')
        
        if not title or not document_type or not file:
            flash('Title, document type, and file are required', 'danger')
            return render_template('policies/policy_upload.html')
        
        # Check file extension
        if file.filename == '':
            flash('No file selected', 'danger')
            return render_template('policies/policy_upload.html')
        
        allowed_extensions = {'pdf', 'doc', 'docx', 'txt'}
        if not '.' in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
            flash('File type not allowed', 'danger')
            return render_template('policies/policy_upload.html')
        
        # Save the file
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['DOCUMENT_UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        try:
            # Extract text from document
            document_text = extract_text_from_file(file_path)
            
            # Create document record
            new_document = Document(
                title=title,
                document_type=document_type,
                file_path=file_path,
                content=document_text
            )
            
            db.session.add(new_document)
            db.session.commit()
            
            # Process document for vector search (chunking and embeddings)
            process_document(new_document.id)
            
            flash('Document uploaded and processed successfully', 'success')
            return redirect(url_for('policy.policy_list'))
            
        except Exception as e:
            current_app.logger.error(f"Document processing error: {str(e)}")
            flash(f'Error processing document: {str(e)}', 'danger')
            return render_template('policies/policy_upload.html')
    
    return render_template('policies/policy_upload.html')

@policy_bp.route('/assistant')
@login_required
def policy_assistant():
    return render_template('policies/policy_assistant.html')

@policy_bp.route('/assistant/query', methods=['POST'])
@login_required
def query_assistant():
    data = request.json
    query = data.get('query')
    
    if not query:
        return jsonify({'success': False, 'message': 'Query is required'}), 400
    
    try:
        # Search for relevant document chunks
        search_results = search_documents(query, top_k=5)
        
        if not search_results:
            return jsonify({
                'success': True, 
                'answer': "I couldn't find any relevant information in the policy documents.",
                'sources': []
            })
        
        # Extract contexts and document references
        contexts = []
        sources = []
        
        for result in search_results:
            chunk = DocumentChunk.query.get(result['chunk_id'])
            document = Document.query.get(chunk.document_id)
            
            contexts.append(chunk.content)
            sources.append({
                'document_id': document.id,
                'document_title': document.title,
                'document_type': document.document_type,
                'relevance_score': result['score']
            })
        
        # Generate answer with context
        answer = generate_answer_with_context(query, contexts)
        
        return jsonify({
            'success': True,
            'answer': answer,
            'sources': sources
        })
        
    except Exception as e:
        current_app.logger.error(f"Policy assistant error: {str(e)}")
        return jsonify({'success': False, 'message': f'Error processing query: {str(e)}'}), 500
