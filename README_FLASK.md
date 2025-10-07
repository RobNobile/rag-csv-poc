# Vehicle Mapping RAG - Flask Web Application

A web-based interface for the Vehicle Mapping RAG system, providing CSV file upload and interactive chat functionality for querying VDAT to Cox automotive mapping data.

## Features

- 📁 **CSV File Upload**: Drag-and-drop or browse to upload vehicle mapping CSV files
- 💬 **Interactive Chat**: Real-time chat interface for querying vehicle data
- 🔄 **Session Management**: Each user gets their own RAG instance
- 🎨 **Modern UI**: Clean, responsive design with loading indicators
- 🚀 **Fast Queries**: Powered by local Ollama models (no API costs)

## Architecture

```
User Browser
    ↓
Flask Web Server (app.py)
    ↓
Vehicle RAG System (vehicle_rag.py)
    ↓
├── CSV Processing (pandas)
├── Vector Store (Chroma)
├── Embeddings (Ollama - mxbai-embed-large)
└── LLM (Ollama - llama3.2:3b)
```

## Prerequisites

1. **Python 3.8+** with virtual environment
2. **Ollama** installed and running locally:
   - Pull required models:
     ```bash
     ollama pull mxbai-embed-large
     ollama pull llama3.2:3b
     ```
   - Start Ollama service:
     ```bash
     ollama serve
     ```
     (Keep this running in a separate terminal)

## Installation

1. **Activate virtual environment** (if not already activated):

   ```bash
   source venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. **Start the Flask server**:

   ```bash
   python app.py
   ```

2. **Open your browser**:
   Navigate to `http://localhost:5001`

3. **Upload CSV and start chatting**:
   - Upload your vehicle mapping CSV file
   - Wait for initialization (2-5 seconds)
   - Start asking questions!

## Usage

### Uploading a CSV File

1. Drag and drop your CSV file onto the upload area, or click to browse
2. Click "Upload & Initialize"
3. Wait for the system to process the file
4. The chat interface will appear automatically

**CSV Requirements:**

- Must be a `.csv` file
- Maximum size: 10MB
- Required columns: `vdatModelId`, `vdatMakeName`, `vdatModelName`, `coxMakeName`, `coxTrimName`

### Asking Questions

Example queries:

- "How many Cox trims are mapped to Audi A3 Sportback e-tron?"
- "What Cox trims are available for BMW M5?"
- "Which vehicles need body style mapping?"
- "Show me vehicles with fuel type requirements"
- "What's the Cox model code for Bentley Continental GT?"

### Resetting

Click the "🔄 Upload New CSV" button to:

- Clear the current session
- Upload a different CSV file
- Start a fresh chat

## API Endpoints

The Flask application provides the following REST API endpoints:

### `POST /api/upload`

Upload and initialize RAG system with CSV file.

**Request:** multipart/form-data with `file` field

**Response:**

```json
{
  "success": true,
  "vehicle_count": 150,
  "filename": "vdat_cox_mapping.csv",
  "message": "Successfully initialized RAG system with 150 vehicles"
}
```

### `POST /api/chat`

Send a chat message and get AI response.

**Request:**

```json
{
  "message": "How many Cox trims for Audi A3?"
}
```

**Response:**

```json
{
  "success": true,
  "response": "Based on [audi_a3-sportback-e-tron], the Audi A3 Sportback e-tron has these Cox trims:\n• e-tron Premium\n• e-tron Premium Plus",
  "question": "How many Cox trims for Audi A3?"
}
```

### `GET /api/status`

Get current RAG system status.

**Response:**

```json
{
  "success": true,
  "status": {
    "initialized": true,
    "vehicle_count": 150,
    "filename": "vdat_cox_mapping.csv",
    "has_vectordb": true,
    "has_chain": true
  }
}
```

### `POST /api/reset`

Reset the RAG system for current session.

**Response:**

```json
{
  "success": true,
  "message": "RAG system reset successfully"
}
```

### `GET /api/health`

Health check endpoint.

**Response:**

```json
{
  "success": true,
  "status": "healthy",
  "message": "Vehicle Mapping RAG service is running"
}
```

## File Structure

```
rag_poc_csv/
├── app.py                      # Flask application & API routes
├── vehicle_rag.py              # Core RAG logic (reusable class)
├── csv_demo.py                 # Original CLI version (still works!)
├── requirements.txt            # Python dependencies
├── templates/
│   └── index.html             # Main web interface
├── static/
│   ├── styles.css             # Styling
│   └── app.js                 # Frontend JavaScript
├── uploads/                    # Temporary CSV storage (auto-created, gitignored)
├── data/
│   └── vdat_cox_mapping.csv   # Example CSV data
└── memory_bank/
    └── ... (project documentation)
```

## Session Management

The application uses **in-memory session management** with Flask sessions:

- Each user gets a unique session ID
- RAG instances are stored per session in a dictionary
- Sessions persist during server runtime
- Uploaded files are stored in session-specific directories

**Note:** Sessions are cleared when the server restarts. For production use with multiple workers, consider implementing Redis-based session storage.

## Development

### Running in Debug Mode

The application runs in debug mode by default:

```bash
python app.py
```

Debug mode features:

- Auto-reload on code changes
- Detailed error messages
- Request logging

### Running in Production

For production deployment:

1. **Disable debug mode** in `app.py`:

   ```python
   app.run(debug=False, host='0.0.0.0', port=5001)
   ```

2. **Use a production WSGI server** (e.g., Gunicorn):

   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5001 app:app
   ```

3. **Consider using a reverse proxy** (e.g., Nginx) for better performance and security

## Troubleshooting

### "Ollama connection failed"

- Ensure Ollama is running: `ollama list`
- Check if models are available: `ollama pull mxbai-embed-large` and `ollama pull llama3.2:3b`

### "CSV file not found" or "Missing required columns"

- Verify your CSV has the required columns: `vdatModelId`, `vdatMakeName`, `vdatModelName`, `coxMakeName`, `coxTrimName`
- Check CSV is properly formatted (no extra commas, quotes, etc.)

### "File size exceeds maximum limit"

- The application has a 10MB file size limit
- For larger files, consider splitting them or increasing `MAX_CONTENT_LENGTH` in `app.py`

### Slow initialization

- First-time initialization takes 2-5 seconds depending on CSV size
- This is normal as the system needs to generate embeddings for all vehicles
- Subsequent queries are much faster (~1-2 seconds)

### Port 5001 already in use

- Change the port in `app.py`: `app.run(debug=True, port=5001)`
- Or kill the process using port 5001

## Comparison: CLI vs Web Interface

| Feature        | CLI (`csv_demo.py`) | Web (`app.py`)            |
| -------------- | ------------------- | ------------------------- |
| Interface      | Terminal            | Browser                   |
| File Upload    | Pre-configured path | Drag & drop / browse      |
| Multiple Users | No                  | Yes (sessions)            |
| Chat History   | Terminal only       | Persistent during session |
| Ease of Use    | Developer-friendly  | User-friendly             |
| Deployment     | Local only          | Can be deployed to server |

Both versions use the same core RAG logic from `vehicle_rag.py`.

## Security Considerations

- File uploads are validated (extension, size)
- Filenames are sanitized with `secure_filename()`
- Files are stored in session-specific directories
- Input validation on all API endpoints
- Session cookies are secure (generated with `secrets.token_hex()`)

For production:

- Add HTTPS/TLS
- Implement rate limiting
- Add authentication/authorization
- Use environment variables for secrets
- Enable CORS only for trusted origins

## Performance

- **Initialization:** ~2-5 seconds (one-time per session)
- **Query Response:** ~1-2 seconds
- **Memory Usage:** ~2.5-4GB RAM (includes Ollama models)
- **Concurrent Users:** Depends on server resources and Ollama capacity

## Future Enhancements

Potential improvements:

- [ ] Persistent vector store (save embeddings to disk)
- [ ] Redis-based session storage for multi-worker deployments
- [ ] Chat history export (JSON/CSV)
- [ ] User authentication
- [ ] Multiple CSV file support (merge datasets)
- [ ] Advanced filtering (by make, model, special requirements)
- [ ] Query history and favorites
- [ ] Batch query processing
- [ ] API key authentication for programmatic access

## License

Same as the parent project.

## Support

For issues or questions:

1. Check the troubleshooting section
2. Review memory_bank documentation
3. Check original CLI app (`csv_demo.py`) to isolate web-specific issues
