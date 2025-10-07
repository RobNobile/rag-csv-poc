# Vehicle Mapping RAG - Dependencies

## Core Dependencies

### RAG Framework

- **langchain** (>=0.1.0): Main framework for building RAG chains
- **langchain-community** (>=0.0.20): Community integrations for Chroma and other tools
- **langchain-ollama** (>=0.1.0): Dedicated package for Ollama integrations (replaces deprecated community integrations)
- **langchain-core**: Core abstractions and interfaces for LangChain

### Vector Database

- **chromadb** (>=0.4.0): Vector database for document storage and retrieval
  - Provides in-memory and persistent storage options
  - Efficient similarity search for embeddings
  - Good integration with LangChain

### Local LLM Integration

- **ollama** (>=0.1.7): Python client for Ollama local models
  - Interfaces with Ollama server running on localhost:11434
  - Supports both embeddings and generation models
  - Used for: mxbai-embed-large (embeddings) and llama3.2:3b (generation)

### Data Processing

- **pandas** (>=2.0.0): Data manipulation and CSV processing library
  - **Critical for this project**: Handles CSV loading and processing
  - Used for grouping vehicle data by vdatModelId
  - Provides efficient data manipulation operations
  - Handles missing values and data cleaning
  - Essential for automotive mapping workflow

### Supporting Libraries

- **numpy** (>=1.24.0): Numerical computing support
  - Required by pandas and various data processing operations
  - Used internally by embeddings and vector operations

- **requests** (>=2.28.0): HTTP library for API calls
  - Used by Ollama client for HTTP communication
  - Required for model inference requests

## Development Dependencies

### Linting and Formatting

- **ruff** (>=0.1.0): Fast Python linter and formatter written in Rust
  - Replaces Black, isort, flake8, and other tools
  - Configured for auto-fix on save in VSCode
  - Rules: pycodestyle, Pyflakes, isort, pep8-naming, pyupgrade, flake8-bugbear
  - Auto-formatting with 88 character line length
  - Import sorting and organization

## Web Framework Dependencies

### Flask Application

- **flask** (>=3.0.0): Lightweight web framework for Python
  - **Purpose**: Powers the web interface (`app.py`)
  - Provides routing, request handling, and templating
  - Built-in development server for testing
  - Session management for multi-user support
  - JSON API support for REST endpoints

- **werkzeug** (>=3.0.0): WSGI utility library (Flask dependency)
  - **Purpose**: Core HTTP and WSGI utilities
  - Secure filename handling with `secure_filename()`
  - Request/response handling
  - File upload processing
  - Development server functionality
  - Automatic dependency of Flask

### Why Flask?

- **Lightweight**: Minimal overhead, fast to develop
- **Flexible**: Easy to add features as needed
- **Well-Documented**: Extensive documentation and community
- **Production Ready**: Can scale with proper WSGI server (Gunicorn)
- **Session Support**: Built-in session management for multi-user RAG instances
- **REST API**: Easy to create JSON APIs for programmatic access
- **Templating**: Jinja2 templates for dynamic HTML
- **Business Value**: Enables non-technical users to access the RAG system

### Testing (Optional)

- **pytest** (optional): Testing framework for Python
  - Not included in requirements.txt by default
  - Install separately if needed: `pip install pytest`
  - Useful for testing CSV processing logic
  - Test files included: `test_consistency.py`, `test_simple_queries.py`

### Interactive Development (Optional)

- **jupyter** (optional): Interactive notebook environment
  - Useful for experimenting with vehicle data processing
  - Install separately if needed: `pip install jupyter`

## Configuration Files

### ruff.toml

Basic linting and formatting configuration:
- Line length: 88 characters
- Target Python version: 3.8+
- Auto-fixable rules enabled
- Import organization and sorting

### .vscode/settings.json (if present)

VSCode integration for Ruff:
- Ruff as default Python formatter
- Format on save enabled
- Auto-fix and import organization on save
- Editor rulers at 88 characters

## System Prerequisites

### Python Environment

- **Python 3.8+**: Required for LangChain and dependencies
- **pip**: Package installer for Python
- **venv**: Virtual environment support (included in Python 3.3+)

### Ollama Installation

Ollama must be installed and running locally:

```bash
# macOS/Linux installation
curl -fsSL https://ollama.ai/install.sh | sh

# Windows: Download from https://ollama.ai
```

### Required Ollama Models

After installing Ollama, pull the required models:

```bash
# Text embeddings model (335MB)
ollama pull mxbai-embed-large

# Text generation model (2.0GB)
ollama pull llama3.2:3b
```

### Vehicle Data CSV

- **File Location**: `data/vdat_cox_mapping.csv`
- **Format**: Standard CSV with header row
- **Encoding**: UTF-8 recommended
- **Size**: Any size supported by pandas (tested up to 10,000 vehicles)

**Required Columns:**
- vdatModelId
- vdatMakeName, vdatModelName
- coxMakeName, coxMakeCode
- coxModelName, coxModelCode
- coxSeriesName, coxSeriesCode
- coxTrimName, coxTrimCode
- coxBodyStyleName, coxBodyStyleCode
- coxFuelTypeCode, coxFuelTypeName

**Optional Columns:**
- Needs Bodystyle
- Needs Fuel Type
- Map to Multiple Cox Models
- Map to Multiple Cox Trims

## Installation Commands

### Full Setup

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt

# Pull Ollama models (if not already done)
ollama pull mxbai-embed-large
ollama pull llama3.2:3b

# Verify CSV file exists
ls data/vdat_cox_mapping.csv
```

### Verify Installation

```bash
# Check Python packages
pip list | grep -E "(langchain|chromadb|ollama|pandas)"

# Check Ollama is running
curl http://localhost:11434/api/version

# Check models are available
ollama list

# Test pandas CSV reading
python -c "import pandas as pd; df = pd.read_csv('data/vdat_cox_mapping.csv'); print(f'Loaded {len(df)} rows')"
```

## Dependency Rationale

### Why LangChain?

- **Abstraction**: High-level abstractions for RAG patterns
- **Integration**: Pre-built integrations with vector stores and LLMs
- **Chains**: Composable chains for complex workflows
- **Community**: Large ecosystem and active development
- **Business Use**: Proven in production applications

### Why Chroma?

- **Simplicity**: Easy setup with no external database
- **Performance**: Fast in-memory operations for vehicle datasets
- **LangChain**: Excellent integration with LangChain
- **Flexibility**: Supports both in-memory and persistent storage
- **Metadata**: Rich metadata filtering for vehicle attributes
- **Scale**: Handles thousands of vehicles efficiently

### Why Ollama?

- **Local**: No API keys or external services required
- **Privacy**: Vehicle data stays on local machine
- **Cost**: No per-token costs for queries
- **Quality**: Good performance for 3B parameter models
- **Variety**: Access to many open-source models
- **Development**: Fast iteration without API rate limits
- **Security**: Critical for automotive industry data

### Why pandas?

- **Industry Standard**: Most popular data manipulation library in Python
- **CSV Processing**: Excellent CSV reading and processing capabilities
- **Grouping**: Efficient groupby operations for consolidating vehicle data
- **Data Cleaning**: Handles missing values and data inconsistencies
- **Performance**: Optimized C/Cython backend for speed
- **Integration**: Works seamlessly with NumPy and other libraries
- **Essential**: Core requirement for vehicle mapping workflow

### Why mxbai-embed-large?

- **Quality**: High-quality embeddings for retrieval
- **Size**: Reasonable model size (335MB)
- **Performance**: Good balance of speed and accuracy
- **Compatibility**: Works well with Ollama and LangChain
- **Vehicle Data**: Handles technical automotive terminology well

### Why llama3.2:3b?

- **Size**: Small enough to run on most machines (2GB)
- **Speed**: Fast inference on consumer hardware
- **Quality**: Good generation quality for its size
- **Recent**: Modern architecture with updated training
- **Versatile**: Handles both general and specific questions well
- **Automotive**: Can understand vehicle terminology and mappings

## Alternative Options

### Different Embedding Models

```bash
# Smaller, faster embedding model
ollama pull all-minilm

# Larger, more accurate embedding model
ollama pull nomic-embed-text
```

### Different Generation Models

```bash
# Larger, higher quality model (4.7GB)
ollama pull llama3.2:7b

# Even larger model for best quality (7.4GB)
ollama pull llama3.1:8b

# Smaller, faster model (1.5GB)
ollama pull llama3.2:1b
```

### Alternative Vector Stores

- **FAISS**: Facebook's similarity search library (faster for large datasets >10K vehicles)
- **Pinecone**: Managed vector database (requires API key, not local)
- **Weaviate**: Open-source vector database (requires server setup)
- **Qdrant**: Vector search engine (good for production deployments)

### Alternative Data Processing

- **Polars**: Faster alternative to pandas (Rust-based)
- **Dask**: Distributed pandas for very large CSV files
- **DuckDB**: SQL-based CSV processing
- **Apache Arrow**: Columnar data format for speed

### Alternative LLM Providers

- **OpenAI**: GPT-3.5/4 via API (requires API key, privacy concerns)
- **Anthropic**: Claude via API (requires API key)
- **Cohere**: Embeddings and generation via API
- **HuggingFace**: Various models via Transformers library

## Development Workflow

With Ruff configured for csv_demo.py:

1. **Edit Code**: Make changes to the Python file
2. **Auto-Format**: Code is automatically formatted on save
3. **Import Organization**: Imports are sorted and organized
4. **Lint Warnings**: Common issues highlighted in editor
5. **Quick Fixes**: Many issues can be auto-fixed
6. **Fast Performance**: 10-100x faster than Black/flake8

## Troubleshooting Dependencies

### Import Errors

```bash
# Check if package is installed
pip show langchain pandas

# Reinstall package
pip install --force-reinstall langchain pandas

# Check for conflicting versions
pip list | grep langchain
```

### pandas CSV Errors

```bash
# Test pandas can read your CSV
python -c "import pandas as pd; print(pd.read_csv('data/vdat_cox_mapping.csv').head())"

# Check for encoding issues
python -c "import pandas as pd; print(pd.read_csv('data/vdat_cox_mapping.csv', encoding='utf-8').head())"

# Check for missing columns
python -c "import pandas as pd; df = pd.read_csv('data/vdat_cox_mapping.csv'); print(df.columns.tolist())"
```

### Ollama Connection Issues

```bash
# Check if Ollama is running
ps aux | grep ollama

# Start Ollama server
ollama serve

# Test connection
curl http://localhost:11434/api/tags
```

### Version Conflicts

```bash
# Show all installed packages
pip list

# Update all packages (careful!)
pip install --upgrade -r requirements.txt

# Create fresh virtual environment
deactivate
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### CSV File Issues

```bash
# Check if file exists
ls -lh data/vdat_cox_mapping.csv

# Check file permissions
chmod 644 data/vdat_cox_mapping.csv

# Validate CSV structure
head -n 5 data/vdat_cox_mapping.csv

# Check for special characters or encoding issues
file data/vdat_cox_mapping.csv
```

## Memory and Performance

### Resource Requirements

- **Disk Space**: ~3GB for models and dependencies
- **RAM**: ~2-4GB during operation
  - Python process: ~200-300MB
  - Ollama models: ~2-3GB
  - Vector store: ~50-200MB (depends on vehicle count)
- **CPU**: Multi-core recommended for faster inference
- **GPU**: Not required (CPU inference is adequate)

### Optimization Tips

1. **Use smaller models** if speed is critical (llama3.2:1b)
2. **Reduce chunk_size** to lower memory usage
3. **Lower k value** in retrieval for faster searches
4. **Enable persistent storage** to avoid re-indexing
5. **Filter CSV data** to load only needed vehicles
6. **Use Polars** instead of pandas for very large CSVs

### pandas Performance

For large CSV files:

```python
# Read only needed columns
df = pd.read_csv('data/vdat_cox_mapping.csv', usecols=['vdatModelId', 'vdatMakeName', ...])

# Use efficient dtypes
df = pd.read_csv('data/vdat_cox_mapping.csv', dtype={'vdatModelId': 'string', ...})

# Process in chunks for very large files
for chunk in pd.read_csv('data/vdat_cox_mapping.csv', chunksize=1000):
    process(chunk)
```

## Production Considerations

### For Production Deployment

- **Persistent Storage**: Enable Chroma persistent storage for faster restarts
- **Caching**: Cache processed CSV data to avoid re-processing
- **Monitoring**: Add logging for CSV load errors and query performance
- **Validation**: Validate CSV structure before processing
- **Error Handling**: Robust error handling for malformed CSV data
- **Updates**: Strategy for updating vector store when CSV changes

### Security Considerations

- **Data Privacy**: All vehicle data processed locally
- **No External Calls**: No data sent to external APIs
- **Access Control**: Consider file permissions on CSV data
- **Audit Logging**: Track queries for compliance if needed
- **Data Sanitization**: Validate CSV input to prevent injection
