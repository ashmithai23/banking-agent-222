# FastAPI Endpoint Documentation

## Health & System
### `GET /`
- **Description**: Verifies service status and API version.
- **Response**: `{"status": "online", "system": "VectraBank Multi-Agent Engine", "version": "2.0.0"}`

## Agent Operations
### `POST /api/chat`
- **Description**: Standard synchronous multi-agent chat interface.
- **Body**: `{"query": string, "customer_id": string, "history": list}`
- **Response**: `{"response": string, "agent_path": list, "citations": list}`

### `POST /api/chat/stream`
- **Description**: Real-time SSE token stream.
- **Body**: `{"query": string, "customer_id": string}`
- **Output**: `text/event-stream`

## Knowledge Base
### `POST /api/documents/upload`
- **Description**: Uploads and indexes knowledge documents.
- **Body**: `multipart/form-data` with `file: UploadFile`
- **Response**: `{"status": "indexed", "filename": string, "chunks": integer}`
