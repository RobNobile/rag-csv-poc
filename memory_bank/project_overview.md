# Vehicle Mapping RAG - Project Overview

## Purpose

This project implements an interactive RAG (Retrieval-Augmented Generation) chat system specifically designed for querying vehicle mapping data between VDAT and Cox automotive systems. It serves as both a practical business tool and a demonstration of domain-specific RAG applications with CSV data sources.

## Available Interfaces

The system provides **two interfaces** to suit different user needs:

### 🌐 Web Application (`app.py`)
- **Purpose**: User-friendly interface for business users and demos
- **Features**:
  - Drag-and-drop CSV upload
  - Interactive chat interface
  - Session-based multi-user support
  - Real-time responses with loading indicators
  - Mobile-responsive design
- **Best For**: Business analysts, QA teams, demos, non-technical users
- **Technology**: Flask web framework with REST API

### 💻 Command Line Interface (`csv_demo.py`)
- **Purpose**: Developer-friendly interface for automation and scripting
- **Features**:
  - Terminal-based interaction
  - Pre-configured CSV path
  - Command system (/help, /quit, etc.)
  - Signal handling (Ctrl+C)
- **Best For**: Developers, automation, testing, power users
- **Technology**: Python interactive console

### Shared Core Logic (`vehicle_rag.py`)
Both interfaces use the same underlying RAG system:
- Identical CSV processing and grouping logic
- Same vector store and retrieval chain
- Consistent query capabilities and response formats
- Shared prompt engineering and LLM integration

## What is This System?

A specialized RAG application that combines:

1. **CSV Data Processing**: Loads and processes vehicle mapping data from structured CSV files
2. **Semantic Search**: Stores vehicle information in a vector database for intelligent retrieval
3. **Interactive Queries**: Provides a conversational interface for vehicle data lookups
4. **Contextual Responses**: Uses retrieved context to generate accurate, cited answers about vehicle mappings

## Business Context

### VDAT to Cox Mapping

The system manages mappings between two automotive data systems:

- **VDAT**: Vehicle data system (source system)
- **Cox Automotive**: Industry-standard vehicle classification system (target system)

Each VDAT vehicle model may map to:
- Multiple Cox trims
- Multiple Cox models (in some cases)
- Different body styles and fuel types
- Special configuration requirements

### Data Structure

Vehicle data is organized by **vdatModelId**, with each vehicle containing:

- **Make/Model Information**: VDAT and Cox make/model names and codes
- **Trim Mappings**: One or more Cox trims per VDAT model
- **Body Styles**: Cox body style names and codes
- **Fuel Types**: Cox fuel type names and codes
- **Series Information**: Cox series names and codes
- **Special Requirements**: Flags for body style needs, fuel type needs, multiple model mappings, etc.

## Core Components

### 1. CSV Data Loader (`load_and_process_csv()`)

Processes vehicle mapping CSV files by:

- Reading CSV with pandas
- Grouping rows by `vdatModelId` to consolidate multiple Cox trim mappings
- Extracting unique Cox information (trims, models, series, body styles, fuel types)
- Building rich searchable text with all vehicle details
- Creating comprehensive metadata for each vehicle
- Handling special requirement flags

### 2. Vector Store

- **Technology**: Chroma (in-memory)
- **Embeddings**: Ollama mxbai-embed-large
- **Storage**: Vehicle records grouped by model ID
- **Metadata**: Trim counts, special flags, make/model information

### 3. RAG Chain

- **Retriever**: Top-k similarity search (k=5)
- **Prompt**: Specialized for vehicle queries with two modes:
  - **Simple Mode**: Lists current trims for a vehicle
  - **Comparison Mode**: Identifies missing trims when user provides reference list
- **LLM**: Ollama llama3.2:3b
- **Output**: Formatted responses with source citations

### 4. ChatSession Class

Manages the interactive conversation lifecycle:

- One-time initialization of RAG system
- Continuous chat loop
- Command processing (/help, /quit, etc.)
- Error handling and graceful shutdown
- Signal handling for Ctrl+C

## Use Cases

### Automotive Industry Applications

1. **Data Validation**: Verify trim completeness by comparing against reference lists
2. **Mapping Lookup**: Quick queries for Cox trim information by vehicle
3. **Gap Analysis**: Identify vehicles missing expected trims
4. **Special Requirements**: Find vehicles needing body style or fuel type mappings
5. **Development Support**: Test and validate mapping changes
6. **Quality Assurance**: Ensure mapping consistency and accuracy

### Example Queries

**Simple Lookups:**
- "How many Cox trims are mapped to Audi A3 Sportback e-tron?"
- "What Cox trims are available for BMW M5 Touring?"
- "Show me the Cox model codes for Chevrolet Corvette ZR1"

**Special Requirements:**
- "Which vehicles need body style mapping?"
- "Show me models that map to multiple Cox trims"
- "What fuel types are available for electric vehicles?"

**Comparison Queries:**
- "I have these trims: [list]. What's missing for this vehicle?"
- "Compare my trim list against the database for BMW M5"

**Search Patterns:**
- Search by make: "Show me all Audi models"
- Search by ID: "What's in audi_a3-sportback-e-tron?"
- Search by feature: "Which Dodge models have SRT trims?"

## Key Features

### Data Processing Features

- **Intelligent Grouping**: Consolidates multiple CSV rows per vehicle model
- **Rich Text Generation**: Creates comprehensive searchable text with all vehicle details
- **Metadata Extraction**: Captures trim counts, special flags, and requirements
- **Flexible CSV Support**: Handles optional columns gracefully
- **Error Handling**: Graceful handling of missing files or malformed data

### Query Features

- **Contextual Prompting**: Automatically detects simple vs. comparison queries
- **Source Citations**: References vdatModelId in responses (e.g., [audi_a3-sportback-e-tron])
- **Bullet Formatting**: Clean, readable trim lists
- **Trim Counting**: Automatic display of trim counts
- **Special Flags**: Highlights vehicles with special requirements

### User Experience Features

- **Interactive Chat**: Continuous conversation without restarting
- **Fast Responses**: One-time initialization, then quick queries
- **Command System**: Built-in commands for help and navigation
- **Error Recovery**: Continues running after errors
- **Graceful Shutdown**: Clean exit with Ctrl+C or commands

## Query Modes

### Simple Query Mode (Default)

Activated when user asks straightforward questions without providing reference data.

**Characteristics:**
- Lists current Cox trims in bullet format
- Includes source citation
- Shows trim count if relevant
- No mention of "missing" trims

**Example:**
```
User: "What Cox trims are mapped to BMW M5 Touring?"

System: "Based on [bmw_m5-touring], the BMW M5 Touring has these Cox trims:
• M5 Competition
• M5 CS"
```

### Comparison Query Mode

Activated when user explicitly provides a reference list to compare against.

**Characteristics:**
- Shows current trims first
- Then separately lists missing trims
- Uses bullet format for both sections
- Only activates when reference data is provided

**Example:**
```
User: "I have ['M5 Competition', 'M5 CS', 'M5 Base']. What's missing for BMW M5 Touring?"

System: "Based on [bmw_m5-touring], the BMW M5 Touring currently has these Cox trims:
• M5 Competition
• M5 CS

Comparing against your reference list, the missing trim is:
• M5 Base"
```

## Prerequisites

### Technical Requirements

- **Python 3.8+**: Core runtime environment
- **Ollama**: Local LLM server with models:
  - `mxbai-embed-large` (335MB) - Text embeddings
  - `llama3.2:3b` (2.0GB) - Text generation
- **Virtual Environment**: Isolated Python environment (recommended)

### Data Requirements

- **CSV File**: `data/vdat_cox_mapping.csv`
- **Required Columns**: vdatModelId, make/model names, Cox trim/model information
- **Optional Columns**: Special requirement flags
- **Format**: Standard CSV with header row

### System Resources

- **Disk Space**: ~3GB for models and dependencies
- **RAM**: 2-4GB during operation
- **CPU**: Multi-core recommended for faster inference
- **Network**: None required (fully local operation)

## Target Audience

### Primary Users

**For Web Interface:**
- **Business Analysts**: Query vehicle data without technical setup
- **QA Engineers**: Interactive testing of mapping completeness
- **Support Teams**: Quick customer-facing data lookups
- **Product Managers**: Data exploration and gap analysis
- **Non-Technical Stakeholders**: Self-service data queries

**For CLI Interface:**
- **Developers**: Automation and scripting integration
- **Data Engineers**: Batch processing and testing
- **DevOps**: Integration with CI/CD pipelines
- **Power Users**: Advanced queries and customization

### Secondary Users

- **Students**: Learn RAG with domain-specific CSV data
- **Engineers**: Understand LangChain and local LLM integration
- **Researchers**: Explore conversational AI for business data
- **Developers**: Build similar systems for other domains

## Project Philosophy

This project prioritizes:

1. **Business Value**: Practical tool for real automotive data queries
2. **Accuracy**: Source citations and data-driven responses
3. **Usability**: Interactive, user-friendly chat interface
4. **Performance**: Fast queries after one-time initialization
5. **Privacy**: Local operation with no external API calls
6. **Flexibility**: Easy customization for different CSV sources
7. **Reliability**: Error handling and graceful degradation

## Data Privacy & Security

- **Fully Local**: All processing happens on local machine
- **No External APIs**: No data sent to cloud services
- **No Network Required**: Operates offline after Ollama model download
- **Data Control**: CSV data never leaves local environment
- **Audit Trail**: Source citations allow verification

## Future Enhancements

Potential improvements:

1. **Chat History**: Maintain conversation context across queries
2. **Export Functionality**: Save query results to files
3. **Batch Processing**: Process multiple queries at once
4. **Web Interface**: Add Flask/Streamlit UI
5. **Persistent Storage**: Save vector database for faster restarts
6. **Advanced Filtering**: Metadata-based search refinement
7. **Analytics Dashboard**: Visualize mapping statistics
8. **Multi-CSV Support**: Compare multiple mapping versions

## Success Metrics

The system is successful when it:

- Accurately retrieves vehicle mapping information
- Provides fast, responsive queries (<2 seconds)
- Handles edge cases gracefully (missing data, special requirements)
- Maintains source citations for verification
- Enables efficient data validation workflows
- Reduces manual CSV lookups significantly
