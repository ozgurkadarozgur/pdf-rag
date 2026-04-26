# PDF RAG Pipeline

A simple PDF semantic search API. The project allows users to upload PDF files, extracts text from uploaded PDFs, generates embeddings, stores them in PostgreSQL, and provides semantic search over the uploaded documents.

## Tech Stack

- Python
- FastAPI
- Pydantic
- FastEmbed
- PostgreSQL
- Docker Compose

## Features

- Upload PDF files
- Extract text content from PDF files
- Generate embeddings for extracted text
- Store document chunks and embeddings in PostgreSQL
- Perform semantic search over uploaded PDF content

## Requirements

- Docker
- Docker Compose

## Getting Started

Start the project with:

```bash
docker compose up -d
```

This command starts the API and PostgreSQL services.

## Startup Note

When the project starts for the first time, the embedding model is downloaded automatically.

Because of this, the API may not be available immediately after running `docker compose up -d`.

You can follow the API container logs with:

```bash
docker compose logs -f <your-api-container-name>
```

Wait until you see the following log:

```text
INFO:     Application startup complete.
```

After this message appears, the API is ready to use.

## API Base URL

```text
http://localhost:8000
```

## Endpoints

The project has two main endpoints:

- `upload`
- `search`

## Upload PDF

Uploads a PDF file, extracts the text content, generates embeddings, and stores the data in PostgreSQL.

### Request

```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@example.pdf"
```

## Search

Performs semantic search over the uploaded PDF files.

### Request

```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "your search query"
  }'
```

## File Storage

Uploaded PDF files are stored locally in the `uploads` directory.

```text
uploads/
```
