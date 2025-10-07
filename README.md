# Vehicle Mapping RAG Chat System

A web-based RAG (Retrieval-Augmented Generation) chat system for querying vehicle mapping data between VDAT and Cox automotive systems. Upload your CSV file and start chatting with AI-powered insights about vehicle mappings.

**🌐 Web Interface** | Built with Flask, LangChain, Chroma, and Ollama

## 🚀 Quick Start

```bash
# 1. Ensure Ollama is running with required models
ollama pull llama3.2:3b
ollama pull mxbai-embed-large
ollama serve  # In separate terminal

# 2. Activate environment and install dependencies
source venv/bin/activate
pip install -r requirements.txt

# 3. Start the web application
python app.py

# 4. Open browser and start chatting!
# → http://localhost:5001
```

Upload your CSV file and start querying your vehicle mapping data.

👉 See [QUICK_START_WEB.md](QUICK_START_WEB.md) for a detailed walkthrough **of the web interface**

👉 See [README_FLASK.md](README_FLASK.md) for complete web documentation **of the API details**

## 🎯 Two Ways to Use This System

This project provides **two interfaces** for the same RAG system:

| Interface      | Best For                          | Quick Start                                  |
| -------------- | --------------------------------- | -------------------------------------------- |
| **🌐 Web App** | Most users, demos, multi-user     | `python app.py` → Open http://localhost:5001 |
| **💻 CLI**     | Developers, automation, scripting | `python cli_app.py`                          |

Both interfaces use the same core RAG logic from `vehicle_rag.py` and provide identical query capabilities.

## Overview

This project implements a specialized RAG chat system that:

- **Web Interface**: Drag-and-drop CSV upload with interactive chat
- **CSV Processing**: Loads and processes vehicle mapping data with pandas
- **Interactive Queries**: Ask questions about VDAT to Cox vehicle mappings
- **Smart Grouping**: Groups vehicle data by model ID with comprehensive metadata
- **Local AI**: Uses Ollama models (no API keys or cloud costs required)
- **Source Citations**: References vehicle model IDs in responses

## Key Features

### Web Application Features

- 📁 **Drag & Drop Upload**: Easy CSV file upload with visual feedback
- 💬 **Real-time Chat**: Interactive chat interface with formatted responses
- 🔄 **Chat Persistence**: Your data stays loaded while Flask is running
- 🚀 **Fast Performance**: 2-5 second initialization, 1-2 second queries

### Core RAG Features

- **CSV-Based Knowledge Base**: Processes vehicle mapping CSV with pandas
- **Interactive Chat**: Continuous conversation without restarting
- **Rich Metadata**: Tracks trim counts, body styles, fuel types, and special requirements
- **Comparison Mode**: Identifies missing trims when provided reference lists
- **Source Citations**: References in responses
- **Error Recovery**: Graceful handling of errors and edge cases

## Prerequisites

Before running this project, ensure you have:

### 1. Python Environment

- Python 3.8 or higher
- pip package manager
- Virtual environment (recommended)

### 2. Ollama Setup

Install Ollama and required models:

```bash
# Install Ollama (macOS/Linux)
curl -fsSL https://ollama.ai/install.sh | sh

# For Windows, download from https://ollama.ai

# Pull required models
ollama pull llama3.2:3b        # Language model
ollama pull mxbai-embed-large  # Embedding model

# Start Ollama service (keep running)
ollama serve
```

### 3. Vehicle Data CSV

The system requires a CSV file with the following structure:

**Required Columns:**

- `vdatModelId` - Unique VDAT model identifier
- `vdatMakeName` - VDAT make name (e.g., "Audi")
- `vdatModelName` - VDAT model name (e.g., "A3 Sportback e-tron")
- `coxMakeName` - Cox make name
- `coxMakeCode` - Cox make code
- `coxModelName` - Cox model name
- `coxModelCode` - Cox model code
- `coxSeriesName` - Cox series name
- `coxSeriesCode` - Cox series code
- `coxTrimName` - Cox trim name
- `coxTrimCode` - Cox trim code
- `coxBodyStyleName` - Cox body style name
- `coxBodyStyleCode` - Cox body style code
- `coxFuelTypeCode` - Cox fuel type code
- `coxFuelTypeName` - Cox fuel type name

**Optional Flag Columns:**

- `Needs Bodystyle` - "Yes" if body style mapping required
- `Needs Fuel Type` - "Yes" if fuel type mapping required
- `Map to Multiple Cox Models` - "Yes" if maps to multiple models
- `Map to Multiple Cox Trims` - "Yes" if maps to multiple trims

## Installation

### 1. Clone and Setup

```bash
# Navigate to project directory
cd rag_poc_csv

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Verify Ollama

```bash
# Check Ollama is running
ollama serve  # Keep this running in a separate terminal

# In another terminal, verify models are available
ollama list
```

You should see `mxbai-embed-large` and `llama3.2:3b` in the list.

### 3. Prepare CSV Data

```bash
# Ensure your CSV file exists (example provided)
ls data/vehicle_mapping_sample.csv

# Verify CSV structure (should have required columns)
head -n 1 data/vehicle_mapping_sample.csv
```

## Using the Web Application

### Starting the Web Server

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Start the Flask application
python app.py
```

You should see:

```
 * Running on http://127.0.0.1:5001
 * Running on http://192.168.1.X:5001
```

### Accessing the Interface

1. Open your browser and navigate to: **http://localhost:5001**
2. You'll see the upload interface

### Uploading a CSV File

1. **Drag and drop** your CSV file onto the upload area, or **click to browse**
2. Click **"Upload & Initialize"**
3. Wait 2-5 seconds for the system to process the file
4. The chat interface will appear automatically

**CSV Requirements:**

- File extension: `.csv`
- Maximum size: 10MB
- Must contain required columns (see Prerequisites section)

### Chatting with Your Data

Once initialized, type your questions in the chat box and press Enter or click Send.

**Example queries:**

```
What is the cox model code for the Integra?
```

```
What trims are mapped to the audi sportback?
```

```
What trims are missing from the bmw_m5-touring in the current mapping based on this separate list of trims: {[{"code":"CS","name":"CS"},{"code":"Competition","name":"Competition"},{"code":"Touring","name":"Touring"}]}
```

```
List all vehicles that are electric
```

**Response Features:**

- Formatted with bullet points for easy reading
- Includes source citations
- Contextually aware (understands comparison vs. simple queries)
- Fast responses (1-2 seconds after initial warm-up)

### Resetting and Uploading New Data

1. Click the **"🔄 Upload New CSV"** button in the chat interface
2. Confirm the reset
3. Upload your new CSV file
4. Start chatting with the new data

### Web Interface Architecture

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

## Using the CLI

For developers and automation, a command-line interface is also available:

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Run the CLI version
python cli_app.py
```

**CLI Features:**

- Terminal-based interactive chat
- Pre-configured CSV path in code
- Built-in commands: `/help`, `/quit`, `/exit`
- Quick testing without browser

**Note:** The CLI version requires the CSV path to be configured in `cli_app.py`. The web version allows dynamic file uploads.

See the code in `cli_app.py` for implementation details.

## Project Structure

```
rag_poc_csv/
├── app.py                      # Flask web application (main entry point)
├── vehicle_rag.py              # Core RAG logic (reusable class)
├── cli_app.py                 # CLI version (alternative interface)
├── requirements.txt            # Python dependencies
├── README.md                   # This file (web-focused)
├── README_FLASK.md             # Detailed web app documentation
├── QUICK_START_WEB.md          # Quick start guide for web interface
├── templates/
│   └── index.html             # Web interface HTML
├── static/
│   ├── styles.css             # Web interface styling
│   └── app.js                 # Frontend JavaScript
├── uploads/                    # Temporary CSV storage (auto-created)
├── data/
│   └── vehicle_mapping_sample.csv   # Example CSV data
├── memory_bank/                # Project documentation
│   ├── project_overview.md    # High-level project context
│   ├── architecture.md        # Technical architecture details
│   ├── dependencies.md        # Dependency information
│   └── usage_examples.md      # Usage examples and customization
├── venv/                      # Python virtual environment
├── .gitignore                 # Git ignore patterns
├── .clinerules                # Cline configuration
└── ruff.toml                  # Linting/formatting config
```

## Technical Details

### Architecture

- **Web Framework**: Flask for local single-user deployment
- **Vector Store**: Chroma (in-memory, persists during Flask runtime)
- **Embeddings**: Ollama mxbai-embed-large
- **Language Model**: Ollama llama3.2:3b
- **RAG Framework**: LangChain
- **Data Processing**: pandas for CSV handling
- **Frontend**: Vanilla JavaScript with REST API

### Key Components

1. **Flask Application** (`app.py`): Web server with REST API endpoints
2. **Vehicle RAG Class** (`vehicle_rag.py`): Reusable RAG implementation
3. **CSV Loader**: Loads and groups vehicle data by vdatModelId
4. **Data Processor**: Groups Cox trims/models per vehicle with metadata
5. **Text Splitter**: Chunks searchable text for processing
6. **Vector Database**: Stores embeddings for similarity search
7. **Retrieval Chain**: Finds relevant vehicle context for questions
8. **Prompt Template**: Specialized for vehicle queries with comparison mode

### Data Processing

The system processes CSV data by:

1. **Loading**: Reads CSV file using pandas
2. **Grouping**: Groups rows by `vdatModelId` to consolidate multiple Cox trim mappings
3. **Text Generation**: Creates rich searchable text with all Cox information
4. **Metadata Extraction**: Captures trim counts, special flags, and requirements
5. **Chunking**: Splits large text into manageable chunks for embeddings
6. **Vectorization**: Converts text chunks to embeddings for semantic search

### Performance Characteristics

- **Initialization**: 2-5 seconds (one-time per Flask startup)
- **Query Response**: 1-2 seconds
- **Memory Usage**: ~2.5-4GB RAM (includes Ollama models)
- **Designed for**: Local single-user deployment

## API Endpoints

The web application provides REST API endpoints for programmatic access:

- `POST /api/upload` - Upload CSV and initialize RAG system
- `POST /api/chat` - Send message and get AI response
- `GET /api/status` - Get current RAG system status
- `POST /api/reset` - Reset RAG system for current session
- `GET /api/health` - Health check endpoint

For complete API documentation, see [README_FLASK.md](README_FLASK.md).

## Customization

### Different Ollama Models

```python
# In vehicle_rag.py, modify the initialization:

# Different embedding model
embeddings = OllamaEmbeddings(model="all-minilm")

# Different LLM
llm = OllamaLLM(model="llama3.1:8b", temperature=0)
```

### Retrieval Parameters

```python
# In vehicle_rag.py, adjust retriever configuration:

# Get more context per query
retriever = vectordb.as_retriever(search_kwargs={"k": 5})
```

### File Upload Limits

```python
# In app.py, modify the configuration:

# Increase max file size to 50MB
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
```

### Port Configuration

```python
# In app.py, change the port:

if __name__ == '__main__':
    app.run(debug=True, port=5002)  # Changed from 5001
```

## Troubleshooting

### Web Application Issues

**Browser shows "Connection refused"**

- Verify Flask server is running: check terminal for "Running on..." message
- Try http://127.0.0.1:5001 instead of localhost
- Check if port 5001 is already in use: `lsof -i :5001`

**CSV upload fails**

- Verify CSV has required columns (see Prerequisites section)
- Check file size is under 10MB (or your configured limit)
- Ensure file extension is `.csv`
- Check for encoding issues in CSV file

**Initialization takes too long**

- First-time initialization is normal (2-5 seconds)
- Check Ollama is responding: `curl http://localhost:11434/api/version`
- Verify CSV file isn't too large (try a subset for testing)

**No responses generated**

- Check browser console for JavaScript errors (F12)
- Verify Ollama is running: `ollama list`
- Check Flask terminal for error messages
- Ensure CSV was processed successfully (check status endpoint)

### Ollama Issues

**"Ollama connection failed"**

- Start Ollama service: `ollama serve`
- Verify it's running: `curl http://localhost:11434/api/version`
- Check models are available: `ollama list`
- Pull models if missing:
  ```bash
  ollama pull mxbai-embed-large
  ollama pull llama3.2:3b
  ```

**Slow first query**

- This is normal (Ollama model warm-up)
- Subsequent queries will be faster
- Consider using a smaller model for testing

### CSV Data Issues

**"Missing required columns"**

- Verify CSV has these columns: `vdatModelId`, `vdatMakeName`, `vdatModelName`, `coxMakeName`, `coxTrimName`
- Check column names match exactly (case-sensitive)
- Ensure no extra spaces in column names

**"CSV file not found" (CLI only)**

- Verify file path in `cli_app.py`
- Check file exists: `ls data/vehicle_mapping_sample.csv`
- Ensure proper relative path from script location

### Verification Commands

```bash
# Check Ollama is running
curl http://localhost:11434/api/version

# Test Ollama models
ollama list

# Check Python packages
pip list | grep -E "(langchain|chromadb|ollama|pandas|flask)"

# Verify CSV structure
head -n 5 data/vehicle_mapping_sample.csv

# Check pandas can read CSV
python -c "import pandas as pd; print(pd.read_csv('data/vehicle_mapping_sample.csv').shape)"

# Test Flask app import
python -c "from app import app; print('Flask app imports successfully')"
```

## Development

### Running in Debug Mode

The application runs in debug mode by default:

```bash
python app.py
```

Debug mode features:

- Auto-reload on code changes
- Detailed error messages
- Request logging in terminal

### Running Tests

```bash
# Run consistency tests
python test_consistency.py

# Run simple query tests
python test_simple_queries.py
```

### Code Formatting

```bash
# Format code with ruff
ruff check --fix .
ruff format .
```

### Memory Bank Documentation

The `memory_bank/` directory contains detailed project documentation:

- `project_overview.md` - High-level project description and use cases
- `architecture.md` - Technical implementation details and design decisions
- `dependencies.md` - Dependency information, rationale, and alternatives
- `usage_examples.md` - Usage patterns, examples, and customization guide

Always check and update these files when making significant changes.

## Use Cases

- **Automotive Industry**: Query vehicle mapping data between systems
- **Data Validation**: Compare trim lists against reference data
- **Mapping Analysis**: Identify vehicles with special requirements
- **Development**: Test and validate vehicle data mappings
- **Support**: Quick lookup of Cox trim information
- **Quality Assurance**: Verify mapping completeness and accuracy
- **Business Users**: Non-technical staff can query data via web interface
- **Demos**: Show RAG capabilities with domain-specific data

## Educational Purpose

This project demonstrates:

- **RAG Architecture**: Retrieval-Augmented Generation with domain-specific data
- **Web Application**: Building a Flask-based AI chat interface
- **LangChain Framework**: Using LangChain for specialized RAG applications
- **Local LLM Integration**: Running AI entirely on-premises with Ollama
- **Contextual Prompting**: Designing prompts for specific business needs

## Comparison: CLI vs Web Interface

| Feature        | Web (`app.py`)        | CLI (`cli_app.py`)  |
| -------------- | --------------------- | ------------------- |
| Interface      | Browser               | Terminal            |
| File Upload    | Drag & drop / browse  | Pre-configured path |
| Multiple Users | No (single global instance) | No              |
| Chat History   | In-browser during chat | Terminal only      |
| Ease of Use    | User-friendly         | Developer-friendly  |
| Deployment     | Server deployable     | Local only          |
| API Access     | Yes (REST endpoints)  | No                  |
| Setup          | Start server          | Run script          |
