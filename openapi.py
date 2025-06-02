from flask import jsonify
from app import app

def generate_openapi_spec():
    """Generate OpenAPI 3.0 specification for the API"""
    spec = {
        "openapi": "3.0.0",
        "info": {
            "title": "XChange Updater",
            "description": "API service for creating, reading, and updating Outline wiki pages. This service acts as a proxy to the Outline API with enhanced update capabilities including append, prepend, and find/replace operations.",
            "version": "1.0.0",
            "contact": {
                "name": "API Support"
            }
        },
        "servers": [
            {
                "url": "http://localhost:5000",
                "description": "Local development server"
            }
        ],
        "paths": {
            "/api/pages": {
                "post": {
                    "summary": "Manage Outline wiki pages",
                    "description": "Unified endpoint for creating, reading, and updating Outline wiki pages. Supports various update operations including append, prepend, replace, and find/replace.",
                    "operationId": "managePage",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "oneOf": [
                                        {"$ref": "#/components/schemas/CreatePageRequest"},
                                        {"$ref": "#/components/schemas/ReadPageRequest"},
                                        {"$ref": "#/components/schemas/UpdatePageRequest"}
                                    ]
                                },
                                "examples": {
                                    "create_page": {
                                        "summary": "Create a new page",
                                        "value": {
                                            "operation": "create",
                                            "collection_id": "01234567-89ab-cdef-0123-456789abcdef",
                                            "title": "New Page Title",
                                            "content": "# New Page\n\nThis is the content of the new page.",
                                            "api_key": "outline_api_key_here",
                                            "email": "user@example.com"
                                        }
                                    },
                                    "read_page": {
                                        "summary": "Read an existing page",
                                        "value": {
                                            "operation": "read",
                                            "document_id": "01234567-89ab-cdef-0123-456789abcdef",
                                            "api_key": "outline_api_key_here",
                                            "email": "user@example.com"
                                        }
                                    },
                                    "append_to_page": {
                                        "summary": "Append content to a page",
                                        "value": {
                                            "operation": "update",
                                            "document_id": "01234567-89ab-cdef-0123-456789abcdef",
                                            "update_type": "append",
                                            "content": "\n\n## New Section\nAdditional content added to the end.",
                                            "api_key": "outline_api_key_here",
                                            "email": "user@example.com"
                                        }
                                    },
                                    "find_replace": {
                                        "summary": "Find and replace text in a page",
                                        "value": {
                                            "operation": "update",
                                            "document_id": "01234567-89ab-cdef-0123-456789abcdef",
                                            "update_type": "find_replace",
                                            "find": "Old text to replace",
                                            "content": "New replacement text",
                                            "api_key": "outline_api_key_here",
                                            "email": "user@example.com"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Operation successful",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "oneOf": [
                                            {"$ref": "#/components/schemas/CreatePageResponse"},
                                            {"$ref": "#/components/schemas/ReadPageResponse"},
                                            {"$ref": "#/components/schemas/UpdatePageResponse"}
                                        ]
                                    }
                                }
                            }
                        },
                        "400": {
                            "description": "Bad request - validation error",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                                }
                            }
                        },
                        "500": {
                            "description": "Internal server error or Outline API error",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                                }
                            }
                        }
                    }
                }
            },
            "/health": {
                "get": {
                    "summary": "Health check",
                    "description": "Check if the service is running",
                    "responses": {
                        "200": {
                            "description": "Service is healthy",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string", "example": "healthy"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "components": {
            "schemas": {
                "CreatePageRequest": {
                    "type": "object",
                    "required": ["operation", "collection_id", "title", "content", "api_key", "email"],
                    "properties": {
                        "operation": {"type": "string", "enum": ["create"]},
                        "collection_id": {"type": "string", "format": "uuid", "description": "UUID of the Outline collection to create the page in"},
                        "title": {"type": "string", "description": "Title of the new page"},
                        "content": {"type": "string", "description": "Markdown content of the new page"},
                        "api_key": {"type": "string", "description": "User's Outline API key"},
                        "email": {"type": "string", "format": "email", "description": "User's email address"}
                    }
                },
                "ReadPageRequest": {
                    "type": "object", 
                    "required": ["operation", "document_id", "api_key", "email"],
                    "properties": {
                        "operation": {"type": "string", "enum": ["read"]},
                        "document_id": {"type": "string", "format": "uuid", "description": "UUID of the document to read"},
                        "api_key": {"type": "string", "description": "User's Outline API key"},
                        "email": {"type": "string", "format": "email", "description": "User's email address"}
                    }
                },
                "UpdatePageRequest": {
                    "type": "object",
                    "required": ["operation", "document_id", "update_type", "content", "api_key", "email"],
                    "properties": {
                        "operation": {"type": "string", "enum": ["update"]},
                        "document_id": {"type": "string", "format": "uuid", "description": "UUID of the document to update"},
                        "update_type": {
                            "type": "string", 
                            "enum": ["append", "prepend", "replace", "find_replace"],
                            "description": "Type of update operation to perform"
                        },
                        "content": {"type": "string", "description": "Content to add or replace"},
                        "find": {"type": "string", "description": "Text to find (required for find_replace operation)"},
                        "api_key": {"type": "string", "description": "User's Outline API key"},
                        "email": {"type": "string", "format": "email", "description": "User's email address"}
                    }
                },
                "CreatePageResponse": {
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean", "example": True},
                        "operation": {"type": "string", "example": "create"},
                        "document_id": {"type": "string", "format": "uuid"},
                        "url": {"type": "string", "format": "uri", "description": "URL to the created page"}
                    }
                },
                "ReadPageResponse": {
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean", "example": True},
                        "operation": {"type": "string", "example": "read"},
                        "document": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string", "format": "uuid"},
                                "title": {"type": "string"},
                                "content": {"type": "string", "description": "Markdown content of the page"},
                                "url": {"type": "string", "format": "uri"},
                                "updated_at": {"type": "string", "format": "date-time"}
                            }
                        }
                    }
                },
                "UpdatePageResponse": {
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean", "example": True},
                        "operation": {"type": "string", "example": "update"},
                        "update_type": {"type": "string", "enum": ["append", "prepend", "replace", "find_replace"]},
                        "document_id": {"type": "string", "format": "uuid"},
                        "url": {"type": "string", "format": "uri", "description": "URL to the updated page"}
                    }
                },
                "ErrorResponse": {
                    "type": "object",
                    "properties": {
                        "error": {"type": "string", "description": "Error message describing what went wrong"}
                    }
                }
            }
        }
    }
    return spec

@app.route('/openapi.json', methods=['GET'])
def openapi_spec():
    """Serve OpenAPI specification"""
    return jsonify(generate_openapi_spec())