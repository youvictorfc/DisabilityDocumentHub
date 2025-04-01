import os
import json
import logging
import numpy as np
import faiss
from flask import current_app
from app import db
from models import DocumentChunk
from services.ai.openai_service import generate_embeddings

# Paths for vector database files
VECTOR_DB_PATH = os.environ.get('VECTOR_DB_PATH', 'vector_db')
VECTOR_INDEX_PATH = os.path.join(VECTOR_DB_PATH, 'index.faiss')
VECTOR_MAPPING_PATH = os.path.join(VECTOR_DB_PATH, 'id_mapping.json')

# Make sure the vector DB directory exists
os.makedirs(VECTOR_DB_PATH, exist_ok=True)

# Global variables for index and mapping
index = None
id_mapping = {}

def initialize_vector_db():
    """
    Initialize or load the vector database.
    """
    global index, id_mapping
    
    try:
        # Check if index exists
        if os.path.exists(VECTOR_INDEX_PATH) and os.path.exists(VECTOR_MAPPING_PATH):
            # Load existing index
            index = faiss.read_index(VECTOR_INDEX_PATH)
            
            # Load ID mapping
            with open(VECTOR_MAPPING_PATH, 'r') as f:
                id_mapping = json.load(f)
        else:
            # Create new index (using 1536 dimensions for OpenAI embeddings)
            index = faiss.IndexFlatL2(1536)
            id_mapping = {}
            
            # Save the empty index and mapping
            faiss.write_index(index, VECTOR_INDEX_PATH)
            with open(VECTOR_MAPPING_PATH, 'w') as f:
                json.dump(id_mapping, f)
    
    except Exception as e:
        logging.error(f"Error initializing vector database: {str(e)}")
        # Create new index if loading fails
        index = faiss.IndexFlatL2(1536)
        id_mapping = {}

# Function to rebuild the vector database from scratch
def rebuild_vector_db():
    """
    Rebuild the vector database from scratch using the document chunks in the database.
    This should be used when there's a mismatch between the vector database and the actual data.
    """
    global index, id_mapping
    
    try:
        from app import db
        from models import DocumentChunk
        
        # Create a new index
        index = faiss.IndexFlatL2(1536)
        id_mapping = {}
        
        # Get all document chunks from the database
        chunks = DocumentChunk.query.all()
        
        if not chunks:
            logging.warning("No document chunks found in the database to rebuild vector DB")
            # Save the empty index and mapping
            faiss.write_index(index, VECTOR_INDEX_PATH)
            with open(VECTOR_MAPPING_PATH, 'w') as f:
                json.dump(id_mapping, f)
            return False
            
        # Add each chunk to the vector database
        for chunk in chunks:
            try:
                # Skip if there's no content to embed
                if not chunk.content:
                    logging.warning(f"Skipping chunk {chunk.id} with no content")
                    continue
                    
                # Generate embedding
                embedding = generate_embeddings(chunk.content)
                
                # Convert to numpy array and reshape
                vector = np.array(embedding).astype('float32').reshape(1, -1)
                
                # Add to index
                index_id = index.ntotal  # Get the next available ID
                index.add(vector)
                
                # Map Faiss index ID to chunk ID
                id_mapping[str(index_id)] = chunk.id
                
                # Update the chunk's embedding_id in the database
                chunk.embedding_id = str(index_id)
                
                logging.info(f"Successfully rebuilt vector embedding for chunk {chunk.id}")
                
            except Exception as e:
                logging.error(f"Error rebuilding vector DB for chunk {chunk.id}: {str(e)}")
                continue
        
        # Save the index and mapping
        faiss.write_index(index, VECTOR_INDEX_PATH)
        with open(VECTOR_MAPPING_PATH, 'w') as f:
            json.dump(id_mapping, f)
            
        # Commit the changes to the database
        db.session.commit()
        
        logging.info(f"Successfully rebuilt vector database with {index.ntotal} embeddings")
        return True
        
    except Exception as e:
        logging.error(f"Error rebuilding vector database: {str(e)}")
        if 'db' in locals():
            db.session.rollback()
        return False

# Initialize on import
initialize_vector_db()

def add_to_vector_db(chunk_id, text):
    """
    Generate embedding for text and add to vector database.
    """
    global index, id_mapping
    
    try:
        # Generate embedding
        embedding = generate_embeddings(text)
        
        # Convert to numpy array and reshape
        vector = np.array(embedding).astype('float32').reshape(1, -1)
        
        # Add to index
        index_id = index.ntotal  # Get the next available ID
        index.add(vector)
        
        # Map Faiss index ID to chunk ID
        id_mapping[str(index_id)] = chunk_id
        
        # Save updated index and mapping
        faiss.write_index(index, VECTOR_INDEX_PATH)
        with open(VECTOR_MAPPING_PATH, 'w') as f:
            json.dump(id_mapping, f)
        
        # Return the index ID as the embedding identifier
        return str(index_id)
    
    except Exception as e:
        logging.error(f"Error adding to vector database: {str(e)}")
        raise Exception(f"Failed to add to vector database: {str(e)}")

def search_documents(query, top_k=5):
    """
    Search for documents relevant to a query.
    """
    global index, id_mapping
    
    try:
        # Generate embedding for query
        query_embedding = generate_embeddings(query)
        
        # Convert to numpy array and reshape
        vector = np.array(query_embedding).astype('float32').reshape(1, -1)
        
        # Search the index
        if index.ntotal == 0:
            return []  # No documents in the index
        
        distances, indices = index.search(vector, min(top_k, index.ntotal))
        
        # Map results to chunk IDs and add distances as scores
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1:  # Valid index
                chunk_id = id_mapping.get(str(idx))
                if chunk_id:
                    results.append({
                        'chunk_id': chunk_id,
                        'score': float(1.0 / (1.0 + distances[0][i]))  # Convert distance to similarity score
                    })
        
        return results
    
    except Exception as e:
        logging.error(f"Error searching vector database: {str(e)}")
        raise Exception(f"Failed to search vector database: {str(e)}")
