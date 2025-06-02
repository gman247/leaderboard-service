# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Flask API service that acts as a proxy to the Outline API, providing enhanced wiki page management capabilities. It enables creating, reading, and updating Outline wiki pages with advanced update operations like append, prepend, and find/replace.

## Architecture

- **Flask API** with a unified `/api/pages` endpoint for all operations
- **OutlineClient** class handles communication with Outline's API
- **Stateless authentication** - users provide their Outline API key with each request
- **Read-Process-Write workflow** for update operations that need to modify existing content

## Development Commands

- `python -m venv venv` - Create virtual environment
- `source venv/bin/activate` (macOS/Linux) - Activate virtual environment  
- `pip install -r requirements.txt` - Install dependencies
- `python run.py` - Start development server on port 5000
- `python app.py` - Alternative way to start the server

## API Endpoints

- `POST /api/pages` - Unified endpoint for create/read/update operations
- `GET /health` - Health check
- `GET /openapi.json` - OpenAPI specification for ChatGPT integration
- `GET /` - API information and available endpoints

## Key Features

- **Create**: New pages in specified collections
- **Read**: Retrieve existing page content
- **Update Types**: 
  - `append` - Add content to end of page
  - `prepend` - Add content to beginning of page  
  - `replace` - Replace entire page content
  - `find_replace` - Find and replace specific text

## Request Authentication

All requests require:
- `api_key` - User's Outline API key
- `email` - User's email address

## Testing

The service can be tested with curl or any HTTP client:

```bash
curl -X POST http://localhost:5000/api/pages \
  -H "Content-Type: application/json" \
  -d '{"operation": "read", "document_id": "uuid-here", "api_key": "key", "email": "user@example.com"}'
```