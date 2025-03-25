import datetime
from flask import Blueprint, request, jsonify
from bson.objectid import ObjectId
from utils.auth_utils import token_required
from app_instance import mongo

document_bp = Blueprint('document', __name__)

@document_bp.route('/store', methods=['POST'])
@token_required
def store_final_data(current_user):
    """Stores the final confirmed data after user review and editing."""
    try:
        db = mongo.db
        data = request.get_json()
        user_id = str(current_user["_id"])  # Get the user_id from the token

        document_id = data.get("document_id")
        final_data = data.get("final_data", {})

        if not document_id or not final_data:
            return jsonify({"error": "Missing document_id or final_data"}), 400

        result = db.documents.update_one(
            {"_id": ObjectId(document_id), "user_id": user_id},  # Ensure ownership
            {"$set": {"final_data": final_data}}
        )

        if result.matched_count == 0:
            return jsonify({"error": "Document not found or unauthorized"}), 404

        return jsonify({"message": "Final data saved successfully"}), 200

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

@document_bp.route('/documents/<document_id>', methods=['GET'])
@token_required
def get_document_by_id(document_id, current_user):
    """Retrieves a specific document by its ID."""
    try:
        db = mongo.db
        user_id = str(current_user["_id"])  # Get the user_id from the token

        document = db.documents.find_one(
            {"_id": ObjectId(document_id), "user_id": user_id},
            {"_id": 1, "document_type": 1, "extracted_data": 1, "final_data": 1, "created_at": 1}
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
