from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from marshmallow import Schema, fields, ValidationError
from typing import Dict, Any, Optional

app = Flask(__name__)
CORS(app)

class OutlineClient:
    def __init__(self, api_key: str, base_url: str = "https://app.getoutline.com"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    def get_document(self, document_id: str) -> Dict[str, Any]:
        """Retrieve a document by ID"""
        response = requests.post(
            f"{self.base_url}/api/documents.info",
            headers=self.headers,
            json={"id": document_id}
        )
        response.raise_for_status()
        return response.json()
    
    def create_document(self, title: str, text: str, collection_id: str, publish: bool = True) -> Dict[str, Any]:
        """Create a new document"""
        response = requests.post(
            f"{self.base_url}/api/documents.create",
            headers=self.headers,
            json={
                "title": title,
                "text": text,
                "collectionId": collection_id,
                "publish": publish
            }
        )
        response.raise_for_status()
        return response.json()
    
    def update_document(self, document_id: str, title: Optional[str] = None, text: Optional[str] = None) -> Dict[str, Any]:
        """Update an existing document"""
        payload = {"id": document_id}
        if title:
            payload["title"] = title
        if text:
            payload["text"] = text
            
        response = requests.post(
            f"{self.base_url}/api/documents.update",
            headers=self.headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()

class PageRequestSchema(Schema):
    operation = fields.Str(required=True, validate=lambda x: x in ['create', 'read', 'update'])
    api_key = fields.Str(required=True)
    email = fields.Email(required=True)
    
    # Create operation fields
    collection_id = fields.Str(required=False)
    title = fields.Str(required=False)
    content = fields.Str(required=False)
    
    # Read/Update operation fields  
    document_id = fields.Str(required=False)
    
    # Update operation fields
    update_type = fields.Str(required=False, validate=lambda x: x in ['append', 'prepend', 'replace', 'find_replace'])
    find = fields.Str(required=False)

def validate_request(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate request data based on operation type"""
    schema = PageRequestSchema()
    
    try:
        result = schema.load(data)
    except ValidationError as err:
        raise ValueError(f"Validation error: {err.messages}")
    
    operation = result['operation']
    
    if operation == 'create':
        required_fields = ['collection_id', 'title', 'content']
        missing = [field for field in required_fields if not result.get(field)]
        if missing:
            raise ValueError(f"Create operation missing required fields: {missing}")
    
    elif operation in ['read', 'update']:
        if not result.get('document_id'):
            raise ValueError(f"{operation.title()} operation requires document_id")
        
        if operation == 'update':
            if not result.get('update_type'):
                raise ValueError("Update operation requires update_type")
            if not result.get('content'):
                raise ValueError("Update operation requires content")
            if result.get('update_type') == 'find_replace' and not result.get('find'):
                raise ValueError("find_replace update_type requires 'find' field")
    
    return result

@app.route('/api/pages', methods=['POST'])
def handle_page_operation():
    """Unified endpoint for all page operations"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        # Validate request
        validated_data = validate_request(data)
        
        # Initialize Outline client
        outline = OutlineClient(validated_data['api_key'])
        
        operation = validated_data['operation']
        
        if operation == 'create':
            result = outline.create_document(
                title=validated_data['title'],
                text=validated_data['content'],
                collection_id=validated_data['collection_id']
            )
            return jsonify({
                "success": True,
                "operation": "create",
                "document_id": result['data']['id'],
                "url": result['data']['url']
            })
        
        elif operation == 'read':
            result = outline.get_document(validated_data['document_id'])
            return jsonify({
                "success": True,
                "operation": "read",
                "document": {
                    "id": result['data']['id'],
                    "title": result['data']['title'],
                    "content": result['data']['text'],
                    "url": result['data']['url'],
                    "updated_at": result['data']['updatedAt']
                }
            })
        
        elif operation == 'update':
            # Read current document
            current_doc = outline.get_document(validated_data['document_id'])
            current_content = current_doc['data']['text']
            
            # Process content based on update_type
            update_type = validated_data['update_type']
            new_content = validated_data['content']
            
            if update_type == 'append':
                processed_content = current_content + new_content
            elif update_type == 'prepend':
                processed_content = new_content + current_content
            elif update_type == 'replace':
                processed_content = new_content
            elif update_type == 'find_replace':
                find_text = validated_data['find']
                processed_content = current_content.replace(find_text, new_content)
            
            # Update document
            result = outline.update_document(
                document_id=validated_data['document_id'],
                text=processed_content
            )
            
            return jsonify({
                "success": True,
                "operation": "update",
                "update_type": update_type,
                "document_id": result['data']['id'],
                "url": result['data']['url']
            })
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except requests.exceptions.HTTPError as e:
        return jsonify({"error": f"Outline API error: {e.response.status_code}"}), 500
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"})

@app.route('/', methods=['GET'])
def root():
    """Root endpoint with API information"""
    return jsonify({
        "service": "XChange Updater",
        "description": "API for creating, reading, and updating Outline wiki pages",
        "endpoints": {
            "pages": "/api/pages (POST)",
            "health": "/health (GET)",
            "openapi": "/openapi.json (GET)"
        }
    })

# Import OpenAPI specification
from openapi import openapi_spec

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)