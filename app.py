from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from marshmallow import Schema, fields, ValidationError
from typing import Dict, Any, Optional, List, Tuple
import re

app = Flask(__name__)
CORS(app)

class OutlineClient:
    def __init__(self, api_key: str, base_url: str = "https://app.getoutline.com", verify_ssl: bool = True):
        self.api_key = api_key
        self.base_url = base_url
        self.verify_ssl = verify_ssl
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    def get_document(self, document_id: str) -> Dict[str, Any]:
        """Retrieve a document by ID"""
        response = requests.post(
            f"{self.base_url}/api/documents.info",
            headers=self.headers,
            json={"id": document_id},
            verify=self.verify_ssl
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
            },
            verify=self.verify_ssl
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
            json=payload,
            verify=self.verify_ssl
        )
        response.raise_for_status()
        return response.json()

class PageRequestSchema(Schema):
    operation = fields.Str(required=True, validate=lambda x: x in ['create', 'read', 'update', 'update_table'])
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
    
    # Update table operation fields
    table_data = fields.Dict(required=False)
    
    # Optional custom Outline server URL
    outline_url = fields.Str(required=False)
    
    # Optional SSL verification disable for self-hosted instances
    verify_ssl = fields.Bool(required=False, missing=True)

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
    
    elif operation in ['read', 'update', 'update_table']:
        if not result.get('document_id'):
            raise ValueError(f"{operation.title()} operation requires document_id")
        
        if operation == 'update':
            if not result.get('update_type'):
                raise ValueError("Update operation requires update_type")
            if not result.get('content'):
                raise ValueError("Update operation requires content")
            if result.get('update_type') == 'find_replace' and not result.get('find'):
                raise ValueError("find_replace update_type requires 'find' field")
        
        elif operation == 'update_table':
            if not result.get('table_data'):
                raise ValueError("update_table operation requires table_data")
            if not isinstance(result.get('table_data'), dict):
                raise ValueError("table_data must be a dictionary")
    
    return result

def parse_markdown_tables(content: str) -> List[Tuple[List[str], List[List[str]], int, int]]:
    """
    Parse markdown tables from content and return table data with positions.
    Returns list of tuples: (headers, rows, start_pos, end_pos)
    """
    tables = []
    lines = content.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        if '|' in line and line.startswith('|') and line.endswith('|'):
            # Found potential table header
            header_line = line
            if i + 1 < len(lines) and '|' in lines[i + 1] and '-' in lines[i + 1]:
                # Found separator line, this is a table
                separator_line = lines[i + 1]
                headers = [h.strip() for h in header_line.split('|')[1:-1]]
                
                start_line = i
                rows = []
                i += 2  # Skip header and separator
                
                # Read table rows
                while i < len(lines) and '|' in lines[i] and lines[i].strip().startswith('|'):
                    row_line = lines[i].strip()
                    row = [cell.strip() for cell in row_line.split('|')[1:-1]]
                    rows.append(row)
                    i += 1
                
                end_line = i - 1
                # Calculate character positions
                start_pos = sum(len(lines[j]) + 1 for j in range(start_line))
                end_pos = sum(len(lines[j]) + 1 for j in range(end_line + 1)) - 1
                
                tables.append((headers, rows, start_pos, end_pos))
                continue
        i += 1
    
    return tables

def generate_markdown_table(headers: List[str], rows: List[List[str]]) -> str:
    """Generate markdown table from headers and rows"""
    if not headers:
        return ""
    
    # Create header row
    header_row = "| " + " | ".join(headers) + " |"
    
    # Create separator row
    separator_row = "|" + "|".join([" --- " for _ in headers]) + "|"
    
    # Create data rows
    data_rows = []
    for row in rows:
        # Pad row to match header length
        padded_row = row + [""] * (len(headers) - len(row))
        data_rows.append("| " + " | ".join(padded_row[:len(headers)]) + " |")
    
    return "\n".join([header_row, separator_row] + data_rows)

def find_matching_table(tables: List[Tuple[List[str], List[List[str]], int, int]], 
                       target_columns: List[str]) -> Tuple[int, Tuple[List[str], List[List[str]], int, int], List[str]]:
    """
    Find table with matching column names and return the correct column order.
    Returns (index, table_data, ordered_columns) or (-1, None, None) if not found.
    """
    for i, (headers, rows, start_pos, end_pos) in enumerate(tables):
        if set(headers) == set(target_columns):
            return i, (headers, rows, start_pos, end_pos), headers
    return -1, None, None

@app.route('/api/pages', methods=['POST'])
def handle_page_operation():
    """Unified endpoint for all page operations"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        # Validate request
        validated_data = validate_request(data)
        
        # Initialize Outline client with custom URL if provided
        outline_url = validated_data.get('outline_url', 'https://app.getoutline.com')
        verify_ssl = validated_data.get('verify_ssl', True)
        outline = OutlineClient(validated_data['api_key'], base_url=outline_url, verify_ssl=verify_ssl)
        
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
        
        elif operation == 'update_table':
            # Read current document
            current_doc = outline.get_document(validated_data['document_id'])
            current_content = current_doc['data']['text']
            table_data = validated_data['table_data']
            
            # Extract column names and values from table_data
            column_names = list(table_data.keys())
            
            # Parse existing tables
            tables = parse_markdown_tables(current_content)
            
            if not tables:
                # No tables exist, create new table
                new_row_values = [str(table_data[col]) for col in column_names]
                new_table = generate_markdown_table(column_names, [new_row_values])
                processed_content = current_content + "\n\n" + new_table
            else:
                # Find table with matching columns
                table_index, matching_table, table_column_order = find_matching_table(tables, column_names)
                
                if matching_table is None:
                    return jsonify({"error": "Column mismatch"}), 400
                
                headers, rows, start_pos, end_pos = matching_table
                
                # Order the new row values according to the existing table's column order
                new_row_values = [str(table_data[col]) for col in table_column_order]
                
                # Add new row to existing table
                updated_rows = rows + [new_row_values]
                updated_table = generate_markdown_table(headers, updated_rows)
                
                # Replace the table in content
                processed_content = current_content[:start_pos] + updated_table + current_content[end_pos:]
            
            # Update document
            result = outline.update_document(
                document_id=validated_data['document_id'],
                text=processed_content
            )
            
            return jsonify({
                "success": True,
                "operation": "update_table",
                "document_id": result['data']['id'],
                "url": result['data']['url'],
                "table_updated": True
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