# Quick Start Guide

## Initial Setup

1. **Activate Virtual Environment** (if not already activated):
   ```bash
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

2. **Install Dependencies** (if not already installed):
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify Configuration**:
   - Check that `.env` file exists (copy from `config.env` if needed)
   - Verify `OLLAMA_BASE_URL=http://47.129.127.169` is set

## Running the Application

### Start Backend (Terminal 1)
```bash
uvicorn backend.main:app --reload --port 8000
```

The API will be available at: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

### Start Frontend (Terminal 2)
```bash
streamlit run frontend/app.py
```

The UI will open automatically in your browser at: `http://localhost:8501`

## Usage Workflow

1. **Create Knowledge Base**: Go to "Knowledge Bases" page and create a new KB
2. **Upload Documents**: Go to "Upload Documents" page and upload PDF/DOCX/TXT files
3. **Index Documents**: Go to "Index Documents" page and index uploaded files into a KB
4. **Chat**: Go to "Chat" page and ask questions about your indexed documents

## Project Structure

```
ollama_rag/
├── core/                    # Shared core logic
│   ├── adapters/           # Ollama API adapter
│   ├── services/           # Business logic (RAG, documents, vector store)
│   └── utils/              # Config, document processing
├── backend/                # FastAPI application
│   └── main.py            # API endpoints
├── frontend/              # Streamlit application
│   └── app.py            # UI pages
└── data/                  # Data storage
    ├── uploads/          # Uploaded documents
    ├── chunks/           # Document chunks
    └── temp/             # Temporary files
```

## Troubleshooting

- **Backend won't start**: Check if port 8000 is available
- **Frontend can't connect**: Ensure backend is running first
- **Ollama errors**: Verify the remote server at http://47.129.127.169 is accessible
- **Import errors**: Make sure virtual environment is activated and dependencies are installed

