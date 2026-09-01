# Software Design Document

## 1. System Overview

The AI Defect Analyzer is a document question-answering system using Retrieval-Augmented Generation (RAG). It enables users to upload project-related files (PDF, CSV, Excel, JSON, DOCX), automatically parses and chunks document content, indexes embeddings into a Chroma vector store, and provides conversational Q&A capability using Ollama LLM and local vector search.

## 2. Architecture

The application follows a standard layered architecture pattern powered by FastAPI:

- **API Router Layer**: Exposes HTTP REST endpoints for files, chat queries, and conversation management.
- **Controller Layer**: Delegates API requests to appropriate service components.
- **Service Layer**: Implements core domain workflows for document ingestion, chunking, vector indexing, conversation tracking, and context-aware query processing.
- **Repository Layer**: Encapsulates database CRUD operations using SQLAlchemy.
- **Database Layer**: Handles PostgreSQL connectivity and session management.
- **Utility Layer**: Provides document loading, text splitting, vector storage operations, vector similarity searching, and LLM text generation interfaces.

## 3. Components

### 3.1 API Layer
- `app.routes.upload_routes`: Handles file upload, metadata listing, and file retrieval endpoints.
- `app.routes.chat_routes`: Exposes the RAG query endpoint and test endpoint.
- `app.routes.conversation_routes`: Provides endpoints for listing, viewing, and deleting conversation histories.

### 3.2 Controller Layer
- `app.controllers.upload_controller`: Coordinates file upload and document retrieval actions.
- `app.controllers.chat_controller`: Coordinates chat processing requests.
- `app.controllers.conversation_controller`: Coordinates retrieval and deletion of stored conversations.

### 3.3 Service Layer
- `app.services.upload_service`: Manages path validation, physical file storage, parsing, chunking, and embedding creation.
- `app.services.chat_service`: Manages conversation persistence, context assembly, similarity searching, and LLM answer generation.
- `app.services.conversation_service`: Manages conversation lists, detailed histories, and deletion logic.

### 3.4 Repository Layer
- `app.repositories.chat_repository`: Encapsulates database queries for `Conversation` and `Message` entities.

### 3.5 Database Layer
- `app.database.connection`: Sets up SQLAlchemy engine, session maker, and standard `get_db` dependency.
- `app.database.base`: Declarative Base class for ORM models.

### 3.6 Utility Layer
- `app.utils.document_loader`: Parses multi-format documents into standard LangChain Document instances.
- `app.utils.chunker`: Splits documents into manageable text chunks using recursive character splitting.
- `app.utils.vector_store`: Manages Chroma collections and embedding persistence.
- `app.utils.vector_search`: Performs vector similarity searching with relevance threshold filtering.
- `app.utils.llm`: Interacts with Ollama Chat API (`llama3.2`) to generate answers based strictly on context.

## 4. API Interfaces

- **Files Endpoints** (`/api/files`):
  - `POST /upload`: Upload project documents.
  - `GET /upload/{project_name}`: Retrieve metadata and download URLs for a project's files.
  - `GET /upload/{project_name}/{filename}`: Download a specific uploaded project file.

- **Chat Endpoints** (`/api/chat`):
  - `GET /test-documentation`: Returns a simple documentation test message.
  - `POST /{project_name}/ask`: Process user questions for a specific project using RAG.

- **Conversation Endpoints** (`/api/conversations`):
  - `GET /{project_name}`: List all conversations for a project.
  - `GET /detail/{conversation_id}`: Retrieve messages for a specific conversation.
  - `DELETE /{conversation_id}`: Delete a conversation and its messages.

## 5. Data Flow

1. **Document Processing**: Uploaded documents -> `upload_routes` -> `upload_service` -> File saved under `uploaded-docs/<project_name>` -> Parsed by `document_loader` -> Chunked by `chunker` -> Embedded with `OllamaEmbeddings` -> Saved in Chroma vector collection `project_<project_name>`.
2. **RAG Chat Query**: Request sent to `POST /api/chat/{project_name}/ask` -> `chat_service` gets or creates `Conversation` -> Retrieves conversation history -> Runs vector similarity search in Chroma DB -> Assembles history and context -> Calls ChatOllama (`llama3.2`) -> Saves user & assistant messages to PostgreSQL -> Returns answer with source references.

## 6. External Dependencies

- **FastAPI / Uvicorn**: Framework and server implementation.
- **SQLAlchemy / psycopg**: Database ORM and PostgreSQL database adapter.
- **LangChain Core & Community**: Document loaders, splitters, and standard abstractions.
- **LangChain Chroma & Ollama**: Vector store integration and Ollama LLM/Embedding bindings.
- **Ollama**: Local instance running `llama3.2` and `nomic-embed-text` models.
- **python-docx**: DOCX file format processing.

## 7. Configuration

- **Database**: PostgreSQL connection established via SQLAlchemy engine in `app/database/connection.py`.
- **Ollama Host**: Default `http://localhost:11434`.
- **LLM Model**: `llama3.2` with temperature set to `0`.
- **Embedding Model**: `nomic-embed-text`.
- **Vector Storage Directory**: `chroma-data`.
- **File Storage Directory**: `uploaded-docs`.

## 8. Error Handling

- Unsafe project names or missing files raise HTTP 400 Bad Request.
- Unsupported file extensions raise HTTP 400 Bad Request.
- Missing conversations or files raise HTTP 404 Not Found.
- If vector search finds no matching chunks above `score_threshold`, the system returns standard fallback answer: "The information is not available in the uploaded documents."

## 9. Security Considerations

- Path traversal defense in file uploads and file downloads via strict path validation.
- SQL parameter binding through SQLAlchemy ORM.
- DB passwords and credentials must be injected via external environment configuration in production environments.

## 10. Deployment Considerations

- Local or server deployment requires a running PostgreSQL database instance and an Ollama instance with pre-downloaded `llama3.2` and `nomic-embed-text` models.
- Local filesystem write access required for `uploaded-docs/` and `chroma-data/` directories.

## 11. Change History

- Added `GET /api/chat/test-documentation` test endpoint.
- Updated chat endpoint route path from `/api/chat/{project_name}` to `/api/chat/{project_name}/ask`.
- Initial generation of Software Design Document from application source code.
