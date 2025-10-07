# Vehicle Mapping RAG Chat System

An interactive RAG (Retrieval-Augmented Generation) chat system for querying vehicle mapping data between VDAT and Cox automotive systems. Built with LangChain, Chroma, and Ollama for local AI-powered vehicle data queries.

## 🎯 Two Ways to Use This System

This project provides **two interfaces** for the same powerful RAG system:

| Interface      | Best For                          | Quick Start                                  |
| -------------- | --------------------------------- | -------------------------------------------- |
| **🌐 Web App** | Business users, demos, multi-user | `python app.py` → Open http://localhost:5001 |
| **💻 CLI**     | Developers, automation, scripting | `python csv_demo.py`                         |

Both interfaces use the same core RAG logic from `vehicle_rag.py` and provide identical query capabilities.

**👉 For web interface documentation, see [README_FLASK.md](README_FLASK.md)**

**👉 For quick start guide, see [QUICK_START_WEB.md](QUICK_START_WEB.md)**

## Overview

This project implements a specialized RAG chat system that:

- Loads and processes vehicle mapping data from CSV files
- Provides interactive queries about VDAT to Cox vehicle mappings
- Groups vehicle data by model ID with comprehensive metadata
- Supports both simple queries and comparison mode with reference lists
- Uses local LLMs via Ollama (no API keys required)
- Includes intelligent prompting for contextually aware responses
- **Available as both a web application and CLI tool**

## Key Features

- **CSV-Based Knowledge Base**: Processes vehicle mapping CSV with pandas
- **Interactive Chat**: Continuous conversation without restarting
- **Rich Metadata**: Tracks trim counts, body styles, fuel types, and special requirements
- **Comparison Mode**: Identifies missing trims when provided reference lists
- **Source Citations**: References vehicle model IDs in responses
- **Command System**: Built-in commands for help, quit, and more
- **Error Recovery**: Graceful handling of errors and interrupts (Ctrl+C)

## Prerequisites

Before running this project, ensure you have:

### 1. Python Environment

- Python 3.8 or higher
- pip package manager

### 2. Ollama Setup

Install Ollama and required models:

```bash
# Install Ollama (macOS/Linux)
curl -fsSL https://ollama.ai/install.sh | sh

# Pull required models
ollama pull mxbai-embed-large
ollama pull llama3.2:3b
```

For Windows, download from [ollama.ai](https://ollama.ai)

### 3. Vehicle Data CSV

The system requires a CSV file at `data/vdat_cox_mapping.csv` with the following structure:

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
# Ensure Ollama is running
ollama serve

# In another terminal, check models are available
ollama list
```

### 3. Prepare CSV Data

```bash
# Ensure your CSV file exists
ls data/vdat_cox_mapping.csv

# Verify CSV structure (should have required columns)
head -n 1 data/vdat_cox_mapping.csv
```

## Usage

### Running the Interactive Chat

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Run the vehicle mapping RAG chat
python csv_demo.py
```

### Sample Session

```
🔧 Initializing Vehicle Mapping RAG system...
   📚 Loading and processing vehicle mapping CSV...
✅ Processed vehicle models from CSV
   🔗 Setting up RAG chain...
✅ Vehicle Mapping RAG system initialized successfully!

Me: How many Cox trims are mapped to Audi A3 Sportback e-tron?

🤖 Thinking...
Based on [audi_a3-sportback-e-tron], the Audi A3 Sportback e-tron has 2 Cox trims mapped:
• e-tron Premium
• e-tron Premium Plus

──────────────────────────────────────────────────

Me: What Cox trims are available for BMW M5 Touring?

🤖 Thinking...
Based on [bmw_m5-touring], the BMW M5 Touring currently has these Cox trims:
• M5 Competition
• M5 CS

──────────────────────────────────────────────────

Me: /quit

👋 Goodbye! Thanks for using Vehicle Mapping RAG Chat!
```

## Query Types Supported

### 1. Simple Trim Queries

```
"How many Cox trims are mapped to Audi A3 Sportback e-tron?"
"What Cox trims are available for BMW M5 Touring?"
"Show me all trims for Chevrolet Corvette ZR1"
```

**Response Format:**

- Lists current trims in bullet format
- Includes source citation (vdatModelId)
- No mention of "missing" trims

### 2. Comparison Queries

When you provide a reference list (JSON, array, or explicit list):

```
"Here are the trims I have: ['Premium', 'Premium Plus', 'Prestige'].
What's missing for Audi A3 Sportback e-tron?"
```

**Response Format:**

- Shows current trims first
- Then separately lists missing trims
- Activated only when reference data is provided

### 3. Special Requirements Queries

```
"Which models need body style mapping?"
"Show me vehicles that map to multiple Cox models"
"What's the fuel type requirement for this model?"
```

### 4. Search by ID or Name

```
"What trims are mapped to audi_a3-sportback-e-tron?"
"Tell me about Chevrolet Corvette ZR1"
"Show me Dodge models with SRT trims"
```

## Available Commands

- `/help` or `/h` - Display help information
- `/quit` or `/exit` - Exit the chat session
- `q` - Quick exit
- `Ctrl+C` - Graceful shutdown

## Project Structure

```
rag_poc_csv/
├── memory_bank/              # Project documentation
│   ├── project_overview.md   # High-level project description
│   ├── architecture.md       # Technical architecture details
│   ├── dependencies.md       # Dependency information
│   └── usage_examples.md     # Usage examples and customization
├── data/                     # Vehicle mapping data
│   └── vdat_cox_mapping.csv  # Main vehicle mapping CSV
├── venv/                     # Python virtual environment
├── csv_demo.py              # Main vehicle mapping RAG system
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── .gitignore               # Git ignore patterns
├── .clinerules              # Cline configuration
└── ruff.toml                # Linting/formatting config
```

## Technical Details

### Architecture

- **Vector Store**: Chroma (in-memory)
- **Embeddings**: Ollama mxbai-embed-large
- **Language Model**: Ollama llama3.2:3b
- **Framework**: LangChain
- **Data Processing**: pandas for CSV handling
- **Chat Management**: ChatSession class

### Key Components

1. **CSV Loader**: `load_and_process_csv()` - Loads and groups vehicle data by vdatModelId
2. **Data Processor**: Groups Cox trims/models per vehicle with metadata
3. **Text Splitter**: Chunks searchable text for processing
4. **Vector Database**: Stores embeddings for similarity search
5. **Retrieval Chain**: Finds relevant vehicle context for questions
6. **Prompt Template**: Specialized for vehicle queries with comparison mode
7. **ChatSession**: Manages interactive conversation lifecycle

### Data Processing

The system processes CSV data by:

1. **Grouping**: Groups rows by `vdatModelId` to consolidate multiple Cox trim mappings
2. **Text Generation**: Creates rich searchable text with all Cox information
3. **Metadata Extraction**: Captures trim counts, special flags, and requirements
4. **Chunking**: Splits large text into manageable chunks for embeddings
5. **Vectorization**: Converts text chunks to embeddings for semantic search

## Customization

### Different Models

```python
# Different embedding model
embeddings = OllamaEmbeddings(model="all-minilm")

# Different LLM
llm = OllamaLLM(model="llama3.1:8b", temperature=0)
```

### Retrieval Parameters

```python
# Get more context per query
retriever = vectordb.as_retriever(search_kwargs={"k": 5})
```

### Different CSV File

```python
# Load different CSV file
csv_data = load_and_process_csv("data/alternative_mapping.csv")
```

## Troubleshooting

### Common Issues

**Script won't start:**

- Verify Ollama is running: `ollama serve`
- Check models are installed: `ollama list`
- Ensure dependencies are installed: `pip list`
- Verify CSV file exists: `ls data/vdat_cox_mapping.csv`

**CSV loading errors:**

- Check CSV file format and required columns
- Verify pandas is installed: `pip show pandas`
- Check for encoding issues in CSV file
- Ensure vdatModelId column exists

**No responses generated:**

- Check Ollama connection (localhost:11434)
- Verify Python environment is activated
- Check for import errors in terminal
- Ensure CSV was processed successfully

**Poor quality responses:**

- Adjust temperature in LLM configuration
- Modify chunk size or overlap settings
- Try different retrieval parameters (k value)
- Check if CSV data is being loaded correctly

### Verification Commands

```bash
# Check Ollama is running
curl http://localhost:11434/api/version

# Test Ollama models
ollama list

# Check Python packages
pip list | grep -E "(langchain|chromadb|ollama|pandas)"

# Verify CSV structure
head -n 5 data/vdat_cox_mapping.csv

# Check pandas can read CSV
python -c "import pandas as pd; print(pd.read_csv('data/vdat_cox_mapping.csv').shape)"
```

## Development

### Running Tests

```bash
# Install development dependencies
pip install pytest black

# Format code
black csv_demo.py

# Run tests (if available)
pytest test_*.py
```

### Memory Bank

The `memory_bank/` directory contains detailed project documentation:

- Project overview and use cases
- Technical architecture explanation
- Dependency rationale and alternatives
- Usage examples and customization guide

## Use Cases

- **Automotive Industry**: Query vehicle mapping data between systems
- **Data Validation**: Compare trim lists against reference data
- **Mapping Analysis**: Identify vehicles with special requirements
- **Development**: Test and validate vehicle data mappings
- **Support**: Quick lookup of Cox trim information
- **Quality Assurance**: Verify mapping completeness and accuracy

## Educational Purpose

This project demonstrates:

- RAG with domain-specific CSV data
- LangChain framework for specialized applications
- Local LLM integration with Ollama
- Interactive chat system design for business data
- CSV data processing with pandas
- Contextually aware prompting strategies

## License

This project is for educational and business purposes. See individual dependency licenses for usage terms.

## Contributing

This is a specialized business application. For improvements:

- Experiment with different models and parameters
- Add new query patterns
- Implement additional features (history, exports, etc.)
- Share improvements and optimizations

For questions or issues, refer to the memory bank documentation.
