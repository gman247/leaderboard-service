# XChange Updater

A Flask API service that acts as a proxy to the Outline API, providing enhanced wiki page management capabilities. This service enables creating, reading, updating, and managing table data in Outline wiki pages with advanced operations.

## Features

- **Complete CRUD Operations**: Create, read, and update Outline wiki pages
- **Advanced Update Operations**: Append, prepend, replace, and find/replace content
- **Table Management**: Add rows to markdown tables with automatic column matching
- **Intelligent Table Handling**: Creates new tables or finds existing ones based on column names
- **Request Validation**: Comprehensive input validation with detailed error messages
- **OpenAPI Integration**: Auto-generated OpenAPI specification for easy integration

## Quick Start

### Prerequisites

- Python 3.7+
- Outline API access with valid API key
- pip package manager

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd xchange-updater
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Start the development server:
```bash
python run.py
```

The service will be available at `http://localhost:5000`

## API Operations

All operations use the `/api/pages` endpoint with POST requests. The operation type is specified in the request body.

### 1. Create Document

Creates a new document in an Outline collection.

```json
{
  "operation": "create",
  "api_key": "your_outline_api_key",
  "email": "your_email@example.com",
  "collection_id": "collection_uuid",
  "title": "Document Title",
  "content": "Document content in markdown"
}
```

**Response:**
```json
{
  "success": true,
  "operation": "create",
  "document_id": "new_document_uuid",
  "url": "https://app.getoutline.com/doc/..."
}
```

### 2. Read Document

Retrieves an existing document by ID.

```json
{
  "operation": "read",
  "api_key": "your_outline_api_key",
  "email": "your_email@example.com",
  "document_id": "document_uuid"
}
```

**Response:**
```json
{
  "success": true,
  "operation": "read",
  "document": {
    "id": "document_uuid",
    "title": "Document Title",
    "content": "Document content...",
    "url": "https://app.getoutline.com/doc/...",
    "updated_at": "2024-01-01T00:00:00.000Z"
  }
}
```

### 3. Update Document

Updates document content with various operation types.

```json
{
  "operation": "update",
  "api_key": "your_outline_api_key",
  "email": "your_email@example.com",
  "document_id": "document_uuid",
  "update_type": "append|prepend|replace|find_replace",
  "content": "New content to add",
  "find": "text_to_find"  // Required only for find_replace
}
```

**Update Types:**
- `append`: Adds content to the end of the document
- `prepend`: Adds content to the beginning of the document
- `replace`: Completely replaces the document content
- `find_replace`: Replaces specific text (requires `find` field)

### 4. Update Table

Adds a row to a markdown table or creates a new table if none exists. Optionally sorts the table by a specified column.

```json
{
  "operation": "update_table",
  "api_key": "your_outline_api_key",
  "email": "your_email@example.com",
  "document_id": "document_uuid",
  "table_data": {
    "Column1": "Value1",
    "Column2": "Value2",
    "Column3": "Value3"
  },
  "sort_by": "Column2",
  "sort_order": "desc"
}
```

**Table Behavior:**
- If no tables exist: Creates a new table with the provided columns and data
- If tables exist: Finds a table with matching column names and adds the row
- If no matching table: Returns "Column mismatch" error
- Multiple tables: Automatically finds the correct table based on column names

**Sorting Options:**
- `sort_by` (optional): Column name to sort by
- `sort_order` (optional): "asc" (ascending) or "desc" (descending), defaults to "asc"
- Smart sorting: Automatically detects numeric vs text values
- Empty rows are kept at the bottom after sorting

**Response:**
```json
{
  "success": true,
  "operation": "update_table",
  "document_id": "document_uuid",
  "url": "https://app.getoutline.com/doc/...",
  "table_updated": true
}
```

## Configuration

### Environment Variables

Create a `.env` file or set environment variables:

```env
PORT=5000
FLASK_DEBUG=True
```

### Deployment

The service is configured for Render.com deployment via `render.yaml`. For production deployment:

1. Set environment variables in your hosting platform
2. Ensure `OUTLINE_API_KEY` is available for your application
3. The service runs on the port specified by the `PORT` environment variable

## API Documentation

Access the auto-generated OpenAPI specification:
- **OpenAPI JSON**: `GET /openapi.json`
- **Health Check**: `GET /health`
- **Service Info**: `GET /`

## Error Handling

The API returns appropriate HTTP status codes and error messages:

- `400 Bad Request`: Validation errors, missing fields, column mismatches
- `500 Internal Server Error`: Outline API errors, server errors

**Example Error Response:**
```json
{
  "error": "Column mismatch"
}
```

## Examples

### Creating a Status Table

1. First, create or update a document with table data:
```json
{
  "operation": "update_table",
  "api_key": "your_api_key",
  "email": "user@example.com",
  "document_id": "doc_id",
  "table_data": {
    "Task": "Setup API",
    "Status": "Complete",
    "Assignee": "John Doe"
  }
}
```

2. Add more rows to the same table:
```json
{
  "operation": "update_table",
  "api_key": "your_api_key",
  "email": "user@example.com",
  "document_id": "doc_id",
  "table_data": {
    "Task": "Write Documentation",
    "Status": "In Progress",
    "Assignee": "Jane Smith"
  }
}
```

### Creating a Sorted Leaderboard

Add entries to a leaderboard table and sort by score in descending order:

```json
{
  "operation": "update_table",
  "api_key": "your_api_key",
  "email": "user@example.com",
  "document_id": "leaderboard_doc_id",
  "sort_by": "Score",
  "sort_order": "desc",
  "table_data": {
    "Name": "Alice Johnson",
    "Score": "95",
    "Date": "2025-06-03",
    "Notes": "Excellent performance on all metrics."
  }
}
```

This will add Alice's entry and automatically sort the entire table by Score in descending order, keeping the highest scores at the top.

### Content Updates

Replace specific text in a document:
```json
{
  "operation": "update",
  "api_key": "your_api_key",
  "email": "user@example.com",
  "document_id": "doc_id",
  "update_type": "find_replace",
  "find": "TODO: Update this section",
  "content": "✅ Section completed"
}
```

## Development

### Project Structure

```
├── app.py              # Main Flask application
├── run.py              # Development server with environment support
├── openapi.py          # OpenAPI specification generator
├── requirements.txt    # Python dependencies
├── render.yaml         # Deployment configuration
└── CLAUDE.md          # Development guidelines
```

### Running Tests

```bash
# Install development dependencies
pip install -r requirements.txt

# Run the application
python run.py
```

### Contributing

1. Follow the existing code patterns and validation structure
2. Ensure all operations maintain the stateless design
3. Add appropriate error handling for new features
4. Update this README for any new functionality

## License

This project is available under the MIT License.
