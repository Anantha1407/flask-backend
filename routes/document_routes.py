import datetime
from flask import Blueprint, request, jsonify
from bson.objectid import ObjectId
from utils.auth_utils import token_required
from app_instance import mongo
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

from .Connecting_LLM_VectorDB.vectordb import store_text_doc

document_bp = Blueprint('document', __name__)

# Load SentenceTransformer model
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

load_dotenv()

Pinecone_api=os.getenv("PINECONE_API_KEY")
# Initialize Pinecone
pc = Pinecone(api_key=Pinecone_api)  # Replace with your actual API key
index_name = "text-search"

def embed_text(text):
    """Generate embeddings using the SentenceTransformer model."""
    return model.encode(text).tolist()

# def store_text(user_id, text, document_id):
#     """Store embedded text into Pinecone under the user's namespace."""
#     namespace = user_id
#     embedding = embed_text(text)
    
#     vectors = [(document_id, embedding, {"text": text})]
    
#     index = pc.Index(index_name)
#     index.upsert(vectors=vectors, namespace=namespace)
#     print(f"Stored text in namespace '{namespace}': {vectors}")

# def extract_text_from_final_data(final_data):
#     """Convert final_data dictionary into a formatted text string."""
#     if not isinstance(final_data, dict):
#         return ""

#     # Join all key-value pairs into a single text string
#     return " ".join([f"{key}: {value}" for key, value in final_data.items() if isinstance(value, (str, int, float))])

@document_bp.route('/store', methods=['POST'])
@token_required
def store_final_data(current_user):
    """Stores the final confirmed data after user review and editing."""
    try:
        db = mongo.db
        data = request.get_json()
        user_id = str(current_user["_id"])  

        document_id = data.get("document_id")
        final_data = data.get("final_data", {})
        relationship = data.get("relationship", "")  
        document_type = data.get("document_type", "")

        if not document_id or not final_data:
            return jsonify({"error": "Missing document_id or final_data"}), 400

        # Update MongoDB
        result = db.documents.update_one(
            {"_id": ObjectId(document_id), "user_id": user_id},  
            {"$set": {"final_data": final_data}}  
        )

        if result.matched_count == 0:
            return jsonify({"error": "Document not found or unauthorized"}), 404
        
        print(final_data.items())

        for key, value in final_data.items():
            key = document_type + " " + key
            if relationship=="myself":
                store_text_doc(user_id, key, value)
            else:
                store_text_doc(user_id, key, value, relationship)
        
        return jsonify({"message": "Final data saved and stored successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@document_bp.route('/documents', methods=['GET'])
@token_required
def get_documents(current_user):
    """Retrieves all documents uploaded by the authenticated user."""
    try:
        db = mongo.db
        user_id = str(current_user["_id"])  # Get the user_id from the token

        documents = list(db.documents.find({"user_id": user_id}, {"_id": 1, "document_type": 1, "created_at": 1, "final_data": 1}))
        
        for document in documents:
            document["document_id"] = str(document["_id"])
            del document["_id"]
            document["created_at"] = document["created_at"].isoformat()

        return jsonify({"documents": documents}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@document_bp.route('/<document_id>', methods=['GET'])
@token_required
def get_document_by_id(current_user, document_id):  # Accept document_id from URL
    """Retrieves a specific document by its ID."""
    try:
        db = mongo.db
        user_id = str(current_user["_id"])  # Get the user_id from the token

        document = db.documents.find_one(
            {"_id": ObjectId(document_id), "user_id": user_id},
            {"_id": 1, "user_id": 1, "relationship": 1, "document_type": 1, "final_data": 1, "created_at": 1}
        )

        if not document:
            return jsonify({"error": "Document not found or unauthorized"}), 404

        document["document_id"] = str(document["_id"])
        del document["_id"]
        document["created_at"] = document["created_at"].isoformat()

        return jsonify(document), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@document_bp.route('/delete/<document_id>', methods=['DELETE'])
@token_required
def delete_document(document_id, current_user):
    """Deletes a document if the user is the owner."""
    try:
        db = mongo.db
        user_id = str(current_user["_id"])  # Get the user_id from the token

        result = db.documents.delete_one({"_id": ObjectId(document_id), "user_id": user_id})

        if result.deleted_count == 0:
            return jsonify({"error": "Document not found or unauthorized"}), 404

        return jsonify({"message": "Document deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
