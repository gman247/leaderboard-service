# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Flask API service that acts as a proxy to the Outline API, providing enhanced wiki page management capabilities. It enables creating, reading, and updating Outline wiki pages with advanced update operations like append, prepend, and find/replace.

## Architecture

- **Single-file Flask application** (`app.py`) with all core logic
- **OutlineClient** class (in `app.py`) handles HTTP communication with Outline's REST API
- **Marshmallow validation** for request data with operation-specific field requirements
- **Unified endpoint pattern** - single `/api/pages` POST endpoint handles all CRUD operations via `operation` field
- **Stateless design** - no session management, users provide API key per request
- **Read-Process-Write workflow** for updates that modify existing content
- **OpenAPI specification** generated dynamically in `openapi.py` for ChatGPT integration

## Development Commands

- `python -m venv venv` - Create virtual environment
- `source venv/bin/activate` (macOS/Linux) - Activate virtual environment  
- `pip install -r requirements.txt` - Install dependencies
- `python run.py` - Start development server with environment variable support
- `python app.py` - Direct Flask app start (debug mode on port 5000)

## Core Components

### Request Validation (`validate_request` function)
- Uses Marshmallow schema for type validation
- Operation-specific field validation (create needs collection_id/title/content, update needs document_id/update_type/content)
- Special handling for find_replace operations requiring both `find` and `content` fields

### OutlineClient Class
- Manages Outline API authentication headers
- Three main methods: `get_document()`, `create_document()`, `update_document()`
- Uses Outline's POST-based API endpoints (not REST-style GET/PUT)

### Update Operations Processing
- Read current document content first
- Apply transformation based on `update_type`:
  - `append`: concatenate new content to end
  - `prepend`: add new content to beginning  
  - `replace`: completely replace content
  - `find_replace`: string replacement operation
- Write back the processed content

## Environment Configuration

The service supports environment variables via `run.py`:
- `PORT` - Server port (default: 5000)
- `FLASK_DEBUG` - Debug mode (default: True)

## Deployment

Configured for Render.com deployment via `render.yaml`:
- Python environment with pip install build step
- Expects `OUTLINE_API_KEY` and `OUTLINE_DOCUMENT_ID` environment variables