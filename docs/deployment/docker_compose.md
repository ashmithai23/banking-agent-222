# Docker Compose Production Deployment

## Architecture
VectraBank is containerized into two independent microservices:
1. `backend`: Python 3.11 with FastAPI, Semantic Kernel, and ChromaDB.
2. `frontend`: Node 20 with React, Tailwind CSS, and Vite.

## Example `docker-compose.yml`
```yaml
version: '3.8'
services:
  vectrabank-backend:
    build: ./backend
    ports:
      - "8000:8000"
    env_file:
      - ./backend/.env
    volumes:
      - chroma_data:/app/chroma_db
    restart: unless-stopped

  vectrabank-frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    environment:
      - VITE_API_URL=http://localhost:8000
    depends_on:
      - vectrabank-backend
    restart: unless-stopped

volumes:
  chroma_data:
```
