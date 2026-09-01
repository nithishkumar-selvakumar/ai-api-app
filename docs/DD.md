# Detailed Design Document

## 1. API Design

The system provides REST endpoints separated into three distinct router modules:
- Files router (`/api/files`)
- Chat router (`/api/chat`)
- Conversations router (`/api/conversations`)

## 2. Request Models

### `ChatRequest`
- `question`: `str` (required)
- `top_k`: `int` (default: `5`)
- `score_threshold`: `float` (default: `0.3`)
- `conversation_id`: `int | None` (default: `None`)

## 3. Response Models

### `Source`
- `filename`: `str`
- `page`: `int | None`
- `chunk_index`: `int`
- `score`: `float`

### `ChatResponse`
- `conversation_id`: `int`
- `question`: `str`
- `answer`: `str`
- `sources`: `list[Source]`

### `UploadedFile`
- `filename`: `str`
- `path`: `str`
- `size`: `int`

### `UploadResponse`
- `message`: `str`
- `project_name`: `str`
- `files`: `list[UploadedFile]`

### `ConversationResponse`
- `id`: `int`
- `project_name`: `str`
- `title`: `str | None`
- `created_at`: `str`
- `updated_at`: `str`

### `MessageResponse`
- `id`: `int`
- `conversation_id`: `int`
- `role`: `str`
- `content`: `str`
- `created_at`: `str`

### `ConversationDetailResponse`
- `id`: `int`
- `project_name`: `str`
- `title`: `str | None`
- `messages`: `list[MessageResponse]`

## 4. Route Details

- **`POST /api/files/upload`**
  - Form inputs: `project_name` (`str`), `files` (`list[UploadFile]`)
  - Handler: `upload_routes.upload`

- **`GET /api/files/upload/{project_name}`**
  - Path param: `project_name` (`str`)
  - Handler: `upload_routes.get_files_by_project`

- **`GET /api/files/upload/{project_name}/{filename}`**
  - Path params: `project_name` (`str`), `filename` (`str`)
  - Handler: `upload_routes.download_project_file`

- **`GET /api/chat/test-documentation`**
  - Handler: `chat_routes.test_documentation`

- **`POST /api/chat/{project_name}/ask`**
  - Path param: `project_name` (`str`)
  - Body: `ChatRequest`
  - Handler: `chat_routes.chat`

- **`GET /api/conversations/{project_name}`**
  - Path param: `project_name` (`str`)
  - Handler: `conversation_routes.conversations`

- **`GET /api/conversations/detail/{conversation_id}`**
  - Path param: `conversation_id` (`int`)
  - Handler: `conversation_routes.conversation`

- **`DELETE /api/conversations/{conversation_id}`**
  - Path param: `conversation_id` (`int`)
  - Handler: `conversation_routes.delete`

## 5. Controller Logic

- `app/controllers/upload_controller.py`:
  - `upload_files`: Delegated to `upload_service.save_files`.
  - `retrieve_project_files`: Invokes `upload_service.get_project_files`.
  - `retrieve_project_file`: Invokes `upload_service.get_project_file`.

- `app/controllers/chat_controller.py`:
  - `ask`: Passes parameters directly to `chat_service.ask_project`.

- `app/controllers/conversation_controller.py`:
  - `get_project_conversations`: Invokes `conversation_service.list_conversations`.
  - `get_conversation`: Invokes `conversation_service.get_conversation_detail`.
  - `delete_conversation`: Invokes `conversation_service.remove_conversation`.

## 6. Service Logic

- **`upload_service`**:
  - Validates project names for traversal characters (`/`, `\`, `..`).
  - Filters upload candidates against allowed file extensions (`.pdf`, `.csv`, `.xlsx`, `.xls`, `.json`).
  - Saves streams to `uploaded-docs/<project_name>/<filename>`.
  - Processes saved files using `load_document` and `create_chunks`.
  - Attaches metadata (`project_name`, `filename`, `file_type`, `chunk_index`) to chunks.
  - Stores embeddings into Chroma via `create_vector_store`.

- **`chat_service`**:
  - Validates or creates a `Conversation` record (using the first 100 characters of the question as title).
  - Formats up to the last 10 messages as conversation history.
  - Executes `search_vectors` against Chroma DB collection `project_<project_name>` using `top_k` and `score_threshold`.
  - Returns default response if no context matches search threshold without invoking LLM.
  - Assembles prompt context, calls `generate_answer` using Ollama `llama3.2`, saves both user and assistant messages, and returns standard response dictionary.

- **`conversation_service`**:
  - Fetches project conversations ordered by updated timestamp descending.
  - Fetches conversation detail and messages ordered by created timestamp.
  - Removes conversation record by ID.

## 7. Repository Logic

- `app/repositories/chat_repository.py`:
  - `create_conversation`: Inserts new `Conversation` row.
  - `add_message`: Inserts new `Message` row associated with conversation.
  - `get_conversation`: Queries `Conversation` by primary key.
  - `get_messages`: Queries `Message` records by `conversation_id` ordered by `created_at` ascending.
  - `get_project_conversations`: Queries `Conversation` records by `project_name` ordered by `updated_at` descending.
  - `delete_conversation`: Deletes `Conversation` record if found.

## 8. Database Design

### Entity: `Conversation` (`conversations` table)
- `id`: `Integer` (Primary Key, Indexed)
- `project_name`: `String(255)` (Not Null, Indexed)
- `title`: `String(500)` (Nullable)
- `created_at`: `DateTime` (Default: `datetime.now`)
- `updated_at`: `DateTime` (Default: `datetime.now`, OnUpdate: `datetime.now`)
- Relationship: `messages` (`Message` list, cascade: `all, delete-orphan`)

### Entity: `Message` (`messages` table)
- `id`: `Integer` (Primary Key, Indexed)
- `conversation_id`: `Integer` (ForeignKey `conversations.id` ON DELETE CASCADE, Not Null, Indexed)
- `role`: `String(50)` (Not Null)
- `content`: `Text` (Not Null)
- `created_at`: `DateTime` (Default: `datetime.utcnow`)
- Relationship: `conversation` (`Conversation` instance)

## 9. File Processing

- Supported extensions: `.pdf`, `.csv`, `.xlsx`, `.xls`, `.json`, `.docx`.
- File loaders utilized (`app/utils/document_loader.py`):
  - PDF -> `PyPDFLoader`
  - CSV -> `CSVLoader`
  - Excel -> `UnstructuredExcelLoader`
  - JSON -> `JSONLoader` (`jq_schema="."`, `text_content=False`)
  - DOCX -> `_load_docx` custom paragraph extraction
- Text splitting strategy (`app/utils/chunker.py`):
  - `RecursiveCharacterTextSplitter` (`chunk_size=1000`, `chunk_overlap=200`).

## 10. AI / RAG Processing

- **Embeddings**:
  - Model: `nomic-embed-text` via `OllamaEmbeddings` at `http://localhost:11434`.
  - Store: Chroma DB persisted in directory `chroma-data`.
  - Collection Naming: `project_<project_name>`.
  - Vector ID Format: `<project_name>:<filename>:<chunk_index>`.
- **Vector Search**:
  - Similarity search with relevance scores.
  - Filters results below `score_threshold` (default 0.3).
- **LLM Context Synthesis**:
  - Model: `llama3.2` via `ChatOllama` at `http://localhost:11434` with `temperature=0`.
  - Prompt restricts answers strictly to document context.

## 11. Conversation Management

- Implicit conversation initialization upon submission of a query without `conversation_id`.
- Contextual memory tracks up to 10 recent messages in linear prompt format.
- Foreign key constraints ensure conversation deletion automatically purges all associated messages.

## 12. Error Handling

- Raises `HTTPException(status_code=400)` for invalid project names, missing files, or unsupported file formats.
- Raises `HTTPException(status_code=404)` for missing projects, conversations, or files.
- Throws `ValueError` in `chat_service` if conversation is invalid or mismatched across projects.

## 13. Configuration and Environment Variables

- Database connection string defined in `app/database/connection.py` targeting PostgreSQL.
- Local filesystem storage configured at `uploaded-docs` and `chroma-data`.
- Ollama base URL defaulting to `http://localhost:11434`.

## 14. Sequence / Data Flow

1. Client issues `POST` to `/api/chat/{project_name}/ask` with `ChatRequest` JSON.
2. `chat_routes.chat` invokes `chat_controller.ask` -> `chat_service.ask_project`.
3. `chat_service` looks up or creates `Conversation` entity via `chat_repository`.
4. `chat_service` loads past conversation messages via `get_messages`.
5. `chat_service` searches Chroma collection `project_<project_name>` using query string and parameters.
6. Formatted context and history are passed into `generate_answer` prompt -> Ollama LLM execution.
7. User question and assistant generated response saved as `Message` entities.
8. `ChatResponse` payload returned to client.

## 15. Change History

- Added `GET /api/chat/test-documentation` endpoint detail.
- Route path updated: `POST /api/chat/{project_name}` changed to `POST /api/chat/{project_name}/ask`.
- Initial creation of Detailed Design Document based on code analysis.
