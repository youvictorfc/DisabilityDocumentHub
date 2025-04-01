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
    # Get all policy documents for reference
    documents = Document.query.all()
    
    # Allow admins to rebuild vector DB if needed
    rebuild_option = current_user.is_admin
    
    return render_template('policies/policy_assistant.html', documents=documents, rebuild_option=rebuild_option)

@policy_bp.route('/assistant/rebuild-vector-db', methods=['POST'])
@login_required
def rebuild_vector_database():
    """Rebuild the vector database from scratch using existing document chunks"""
    # Only administrators can rebuild the vector database
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Only administrators can rebuild the vector database'}), 403
    
    try:
        from services.document.vector_service import rebuild_vector_db
        
        # Rebuild the vector database
        success = rebuild_vector_db()
        
        if success:
            current_app.logger.info("Vector database rebuilt successfully")
            return jsonify({'success': True, 'message': 'Vector database rebuilt successfully'})
        else:
            current_app.logger.warning("Failed to rebuild vector database")
            return jsonify({'success': False, 'message': 'Failed to rebuild vector database'}), 500
            
    except Exception as e:
        current_app.logger.error(f"Error rebuilding vector database: {str(e)}")
        return jsonify({'success': False, 'message': f'Error rebuilding vector database: {str(e)}'}), 500

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
            if chunk is None:
                current_app.logger.warning(f"Could not find chunk with ID {result['chunk_id']}")
                continue
                
            document = Document.query.get(chunk.document_id)
            if document is None:
                current_app.logger.warning(f"Could not find document with ID {chunk.document_id}")
                continue
            
            contexts.append(chunk.content)
            sources.append({
                'document_id': document.id,
                'document_title': document.title,
                'document_type': document.document_type,
                'relevance_score': result['score']
            })
        
        # Check if we have any valid contexts to work with
        if not contexts:
            return jsonify({
                'success': True, 
                'answer': "I couldn't find any valid information in the policy documents related to your query.",
                'sources': []
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

@policy_bp.route('/<int:document_id>/delete', methods=['POST'])
@login_required
def delete_policy(document_id):
    """Delete a policy document and its associated file and chunks"""
    if not current_user.is_admin:
        flash('Only administrators can delete policy documents', 'danger')
        return redirect(url_for('policy.policy_list'))
    
    document = Document.query.get_or_404(document_id)
    
    try:
        # Delete document file if it exists
        if document.file_path and os.path.exists(document.file_path):
            os.remove(document.file_path)
            current_app.logger.info(f"Deleted document file: {document.file_path}")
        
        # Delete all document chunks (the document chunks will be automatically deleted due to cascade="all, delete-orphan")
        
        # Delete document from database
        db.session.delete(document)
        db.session.commit()
        
        current_app.logger.info(f"Document ID {document_id} deleted successfully")
        
        # Check if this is an AJAX request
        is_ajax_request = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        if is_ajax_request:
            return jsonify({
                'success': True,
                'message': f'Document "{document.title}" deleted successfully'
            })
        else:
            flash(f'Document "{document.title}" has been deleted', 'success')
            return redirect(url_for('policy.policy_list'))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting document: {str(e)}")
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': False,
                'message': f'Error deleting document: {str(e)}'
            }), 500
        else:
            flash(f'Error deleting document: {str(e)}', 'danger')
            return redirect(url_for('policy.policy_list'))
