# Vehicle Mapping RAG - Technical Architecture

## Overview

This project provides **two interfaces** sharing the same core RAG logic:

1. **CLI Application** (`csv_demo.py`) - Terminal-based interactive chat
2. **Flask Web Application** (`app.py`) - Browser-based interface with REST API
3. **Shared Core** (`vehicle_rag.py`) - Reusable RAG system class

## CLI Application Architecture

```
CSV File → Data Loader → Grouped Records → Text Splitter → Embeddings → Vector DB
                                                                            ↓
User Input → Command Processing → RAG Chain → Retriever → Context → LLM → Response
     ↓              ↓                  ↓                      ↓         ↓
ChatSession → Lifecycle Management → Query Mode Detection → Format → Output
     ↓
  Init, Chat Loop, Cleanup, Signals
```

## Flask Web Application Architecture

```
User Browser
    ↓
┌───────────────────────────────────────────┐
│  Flask Web Server (app.py)                │
│  ├── Routes: /, /api/upload, /api/chat   │
│  ├── Session Management (in-memory)      │
│  └── File Upload Handling                │
└───────────────────────────────────────────┘
    ↓
┌───────────────────────────────────────────┐
│  VehicleRAG Class (vehicle_rag.py)        │
│  ├── initialize_from_csv()                │
│  ├── query()                              │
│  ├── get_stats()                          │
│  └── reset()                              │
└───────────────────────────────────────────┘
    ↓
┌───────────────────────────────────────────┐
│  Core RAG Components                      │
│  ├── CSV Processing (pandas)             │
│  ├── Vector Store (Chroma)               │
│  ├── Embeddings (Ollama)                 │
│  └── LLM Chain (LangChain)               │
└───────────────────────────────────────────┘
```

### Web Request Flow

**Upload Flow:**
```
1. User uploads CSV file via browser
2. POST /api/upload → Flask receives file
3. File saved to session-specific directory
4. VehicleRAG.initialize_from_csv(filepath)
5. CSV processed, vector store created
6. Session ID stored, RAG instance cached
7. JSON response: {success, vehicle_count, filename}
8. Frontend switches to chat interface
```

**Chat Flow:**
```
1. User types question in chat
2. POST /api/chat with {message: "question"}
3. Flask retrieves RAG instance by session ID
4. VehicleRAG.query(question)
5. RAG chain: retrieval → context → LLM → response
6. JSON response: {success, response, question}
7. Frontend displays formatted response
```

**Session Management:**
```python
# In-memory dictionary storing RAG instances
rag_sessions = {
    "session_id_1": VehicleRAG(),  # User 1's instance
    "session_id_2": VehicleRAG(),  # User 2's instance
    ...
}
```

## High-Level Flow

1. **Initialization**: ChatSession loads CSV, processes data, builds vector store
2. **Chat Loop**: Continuous conversation with command processing
3. **Query Processing**: User input → retrieval → context formatting → LLM generation
4. **Cleanup**: Graceful shutdown on exit or Ctrl+C

## Component Details

### 1. CSV Data Loader (`load_and_process_csv()`)

The foundation of the system - processes vehicle mapping CSV into searchable records.

#### Function Signature
```python
def load_and_process_csv(csv_path="data/vdat_cox_mapping.csv"):
    """
    Load the vehicle mapping CSV and process it into grouped records by vdatModelId.
    Each record contains rich searchable text and comprehensive metadata.
    """
```

#### Processing Pipeline

**Step 1: Load CSV with pandas**
```python
df = pd.read_csv(csv_path)
```

**Step 2: Group by vdatModelId**
```python
for model_id, group in df.groupby('vdatModelId'):
```
- Each vdatModelId represents one VDAT vehicle model
- Multiple CSV rows (different Cox trims) are consolidated per vehicle
- Handles one-to-many relationships (1 VDAT model → N Cox trims)

**Step 3: Extract Unique Values**

For each vehicle group, extract unique values across all rows:
- Cox trim names and codes (multiple values expected)
- Cox model names and codes (usually one, sometimes multiple)
- Cox series names and codes
- Cox body style names and codes
- Cox fuel type codes and names
- Special requirement flags

**Step 4: Build Rich Searchable Text**

Creates comprehensive text content including:
```
Model ID: {vdatModelId}
Vehicle: {vdatMakeName} {vdatModelName}
Cox Make: {coxMakeName}
Cox Make Code: {coxMakeCode}
Cox Series: {all unique series names}
Cox Series Codes: {all unique series codes}
Cox Models: {all unique model names}
Cox Model Codes: {all unique model codes}
Cox Trims: {all unique trim names}
Cox Trim Codes: {all unique trim codes}
Cox Body Styles: {all unique body style names}
Cox Body Style Codes: {all unique body style codes}
Cox Fuel Type Codes: {all unique fuel type codes}
```

**Step 5: Add Special Requirements**

Identifies and includes special flags:
- "Requires Body Style mapping" (if Needs Bodystyle = Yes)
- "Requires Fuel Type mapping" (if Needs Fuel Type = Yes)
- "Maps to multiple Cox models" (if Map to Multiple Cox Models = Yes)
- "Maps to multiple Cox trims" (if Map to Multiple Cox Trims = Yes)

**Step 6: Build Comprehensive Metadata**

Creates metadata dictionary for Chroma:
```python
metadata = {
    "source": model_id,  # Used for citations
    "vdat_make_name": vdatMakeName,
    "vdat_model_name": vdatModelName,
    "cox_make_name": coxMakeName,
    "cox_models_str": ", ".join(cox_models),  # Lists converted to strings
    "cox_trims_str": ", ".join(cox_trims),
    "cox_trim_codes_str": ", ".join(cox_trim_codes),
    "fuel_types_str": ", ".join(fuel_types),
    "needs_bodystyle": boolean,
    "needs_fuel_type": boolean,
    "multiple_cox_models": boolean,
    "multiple_cox_trims": boolean,
    "trim_count": len(cox_trims)
}
```

**Step 7: Return Structured Data**

Returns list of dictionaries:
```python
[
    {
        "text": searchable_text,
        "metadata": metadata_dict
    },
    # ... one per vdatModelId
]
```

#### Error Handling

- **FileNotFoundError**: Returns empty list, displays error message
- **General Exceptions**: Catches all errors, returns empty list with error message
- **Empty CSV**: Handled by placeholder in `build_vectorstore()`

### 2. Vector Store Builder (`build_vectorstore()`)

Converts processed CSV data into a searchable vector database.

#### Function Signature
```python
def build_vectorstore(csv_data=None):
```

#### Processing Steps

**Step 1: Load CSV Data**
```python
if csv_data is None:
    csv_data = load_and_process_csv()
```

**Step 2: Handle Empty Knowledge Base**
```python
if not csv_data:
    csv_data = [{
        "text": "This is a placeholder document for an empty vehicle mapping knowledge base.",
        "metadata": {"source": "placeholder", "trim_count": 0}
    }]
```

**Step 3: Text Splitting**
```python
splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
```
- **Chunk Size**: 800 characters (larger than basic demo to preserve vehicle context)
- **Overlap**: 100 characters (ensures continuity across chunks)
- Each vehicle record may be split into multiple chunks if text is long

**Step 4: Chunk Generation**
```python
for item in csv_data:
    text_content = item["text"]
    metadata = item["metadata"]

    text_chunks = splitter.split_text(text_content)

    for chunk in text_chunks:
        chunks.append(chunk)
        metas.append(metadata)  # Same metadata for all chunks of a vehicle
```

**Step 5: Generate Embeddings**
```python
embeddings = OllamaEmbeddings(model="mxbai-embed-large")
```
- Model: mxbai-embed-large (335MB)
- Dimensions: 1024 (embedding vector size)
- Local execution via Ollama

**Step 6: Create Vector Store**
```python
vectordb = Chroma.from_texts(
    texts=chunks,
    embedding=embeddings,
    metadatas=metas
)
```
- Storage: In-memory (ephemeral)
- One vector per chunk
- Metadata attached to each vector

### 3. Document Formatter (`format_docs()`)

Formats retrieved documents with source citations and metadata enhancement.

#### Function Signature
```python
def format_docs(docs):
```

#### Processing

**Step 1: Extract Source and Content**
```python
for d in docs:
    src = d.metadata.get("source", "kb")
    content = d.page_content.strip()
```

**Step 2: Add Metadata Context**
```python
if hasattr(d, 'metadata') and d.metadata:
    trim_count = d.metadata.get('trim_count', 0)
    if trim_count > 0:
        content += f"\n(This vehicle has {trim_count} Cox trim(s) mapped)"
```
- Enhances retrieval quality by adding trim count
- Helps LLM understand vehicle completeness

**Step 3: Format with Citations**
```python
lines.append(f"[{src}] {content}")
```

**Output Format:**
```
[audi_a3-sportback-e-tron] Model ID: audi_a3-sportback-e-tron
Vehicle: Audi A3 Sportback e-tron
Cox Trims: e-tron Premium, e-tron Premium Plus
(This vehicle has 2 Cox trim(s) mapped)

[bmw_m5-touring] Model ID: bmw_m5-touring
Vehicle: BMW M5 Touring
Cox Trims: M5 Competition, M5 CS
(This vehicle has 2 Cox trim(s) mapped)
```

### 4. RAG Chain Builder (`build_chain()`)

Constructs the retrieval-augmented generation pipeline.

#### Components

**Retriever Configuration**
```python
retriever = vectordb.as_retriever(search_kwargs={"k": 5})
```
- **k=5**: Retrieves top 5 most relevant chunks
- **Search Type**: Similarity search (default)
- **Distance Metric**: Cosine similarity

**Specialized Prompt Template**

```python
system = """
You are a helpful AI assistant specializing in vehicle data and Cox automotive mapping information.
You have access to a comprehensive vehicle mapping knowledge base.

RESPONSE GUIDELINES:
- Extract ALL relevant information from the provided CONTEXT before responding
- Cite sources using their [source] tags (which represent vdatModelId values)
- Use clean, bullet-point formatting for trim lists
- Be contextually aware of what the user is asking

RESPONSE PATTERNS:

FOR SIMPLE TRIM QUERIES (no reference list provided):
Format: "Based on [source], the [Vehicle Name] has these Cox trims:
• Trim 1
• Trim 2
• Trim 3"

FOR COMPARISON QUERIES (when user provides a reference list/JSON/array):
Only when the user explicitly provides a list to compare against:
1. Show current trims in bullet format
2. Then show missing trims separately in bullet format

Format: "Based on [source], the [Vehicle Name] currently has these Cox trims:
• Current Trim 1
• Current Trim 2

Comparing against your reference list, the missing trims are:
• Missing Trim 1
• Missing Trim 2"

KEY RULES:
- Never mention "missing trims" unless the user provided a reference list to compare against
- Never repeat the same trim list twice in different formats
- Use bullet points (•) for all trim listings
- Be concise and avoid redundancy
- Only activate comparison mode when reference data is explicitly provided

NOTE: Sources like [ram_power-wagon] represent vehicle model mappings in the database.
"""
```

**Key Prompt Features:**
- **Mode Detection**: Automatically distinguishes simple vs. comparison queries
- **Formatting Rules**: Consistent bullet-point formatting
- **Citation Requirements**: Must include source tags
- **Anti-Redundancy**: Prevents repeating trim lists
- **Contextual Awareness**: Responds appropriately to query type

**LLM Configuration**
```python
llm = OllamaLLM(model="llama3.2:3b", temperature=0)
```
- **Model**: llama3.2:3b (2GB, fast inference)
- **Temperature**: 0 (deterministic responses)
- **Local**: Runs via Ollama on localhost:11434

**Chain Wiring**
```python
chain = (
    {
        "context": retriever | format_docs,   # Retrieval + formatting
        "question": RunnablePassthrough(),    # Forward original question
    }
    | prompt
    | llm
    | StrOutputParser()
)
```

**Data Flow:**
1. Question comes in as string
2. Retriever finds top-k relevant chunks
3. format_docs() formats chunks with citations
4. Prompt template receives context + question
5. LLM generates response
6. StrOutputParser() extracts text from response

### 5. ChatSession Class

Manages the interactive conversation lifecycle.

#### Class Attributes
```python
class ChatSession:
    def __init__(self):
        self.vectordb = None      # Chroma vector store
        self.chain = None          # RAG chain
        self.running = True        # Loop control flag
        signal.signal(signal.SIGINT, self._signal_handler)  # Ctrl+C handler
```

#### Key Methods

**`initialize_rag_system()`**

One-time initialization at startup:

```python
def initialize_rag_system(self):
    print("\n🔧 Initializing Vehicle Mapping RAG system...")

    try:
        print("   📚 Loading and processing vehicle mapping CSV...")
        self.vectordb = build_vectorstore()  # Load CSV, build vector DB

        print("   🔗 Setting up RAG chain...")
        self.chain = build_chain(self.vectordb)  # Create RAG pipeline

        print("✅ Vehicle Mapping RAG system initialized successfully!\n")
        return True

    except Exception as e:
        print(f"❌ Failed to initialize RAG system: {str(e)}")
        # Error messages for common issues
        return False
```

**Performance:**
- Runs once at startup
- Takes ~2-5 seconds depending on CSV size
- Subsequent queries are fast (~1-2 seconds)

**`run_chat()`**

Main interactive loop:

```python
def run_chat(self):
    # Initialize system
    if not self.initialize_rag_system():
        return

    # Main chat loop
    while self.running:
        try:
            user_input = self.get_user_input()

            if not user_input:
                continue

            # Process commands (/help, /quit, etc.)
            command_result = self.process_command(user_input)
            if command_result == "quit":
                break
            elif command_result in ["help", "clear"]:
                continue

            # Generate response
            response = self.generate_response(user_input)
            print(response)

            print("\n" + "─" * 50)  # Separator

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\n❌ Unexpected error: {str(e)}")
            print("The chat will continue. Try your question again.")

    self.cleanup()
```

**`generate_response()`**

Generates responses using RAG chain:

```python
def generate_response(self, question):
    try:
        print("\n🤖 Thinking...")

        # Invoke RAG chain
        response = self.chain.invoke(question)

        return response.strip()

    except Exception as e:
        error_msg = f"❌ Error generating response: {str(e)}"
        print(error_msg)
        return "Sorry, I encountered an error while processing your question. Please try again."
```

**`process_command()`**

Handles special commands:

```python
def process_command(self, user_input):
    user_input = user_input.lower().strip()

    if user_input in ["/quit", "/exit", "q"]:
        print("\n👋 Goodbye! Thanks for using Vehicle Mapping RAG Chat!")
        return "quit"

    elif user_input in ["/help", "/h"]:
        self.display_help()
        return "help"

    elif user_input in ["/clear", "/cls"]:
        import os
        os.system("cls" if os.name == "nt" else "clear")
        return "clear"

    return None  # Not a command
```

**`display_help()`**

Shows detailed help information with vehicle-specific examples.

**`_signal_handler()`**

Handles Ctrl+C gracefully:

```python
def _signal_handler(self, signum, frame):
    print("\n\n👋 Goodbye! Chat session ended.")
    self.running = False
    sys.exit(0)
```

## Data Flow Diagrams

### Initialization Phase

```
1. User runs: python csv_demo.py
2. main() creates ChatSession()
3. ChatSession sets up signal handler
4. initialize_rag_system() called:
   a. load_and_process_csv() reads CSV
   b. Groups by vdatModelId
   c. Creates rich searchable text
   d. Extracts metadata
   e. Returns structured data
   f. build_vectorstore() creates vector DB
   g. Splits text into chunks
   h. Generates embeddings
   i. Stores in Chroma
   j. build_chain() creates RAG pipeline
5. System ready for queries
```

### Query Processing Phase

```
1. User enters question: "How many Cox trims for Audi A3?"
2. get_user_input() captures input
3. process_command() checks (not a command)
4. generate_response() called:
   a. Question embedded by retriever
   b. Top-5 similar chunks retrieved from Chroma
   c. format_docs() adds citations and metadata
   d. Prompt constructed with context + question
   e. LLM analyzes context and question
   f. Determines query mode (simple vs. comparison)
   g. Generates formatted response
   h. StrOutputParser extracts text
5. Response printed to user
6. Loop continues
```

### Comparison Query Flow

```
User provides reference list in question
    ↓
Retriever finds relevant vehicle data
    ↓
LLM receives:
  - Current trims from database (via context)
  - User's reference list (from question)
    ↓
LLM compares and identifies:
  1. Current trims (from database)
  2. Missing trims (in reference but not in database)
    ↓
Formats response with both sections
    ↓
Returns structured comparison
```

## Key Design Decisions

### Why Group by vdatModelId?

**Problem**: CSV has one row per Cox trim mapping
- Example: Audi A3 with 3 trims = 3 rows in CSV
- Searching returns 3 separate chunks for same vehicle
- Redundant information and poor user experience

**Solution**: Group rows by vdatModelId
- Consolidates all trims for a vehicle into one record
- Single comprehensive searchable text per vehicle
- Better retrieval quality and cleaner responses

### Why Rich Searchable Text?

**Advantages:**
- Includes all Cox information (trims, models, series, body styles, fuel types)
- Enables flexible searches (by name, code, ID, feature)
- Better semantic matching for diverse queries
- Maintains context for special requirements

### Why Chunk Size 800?

**Rationale:**
- Vehicles with many trims need more space
- Preserves complete vehicle context in single chunk (usually)
- Reduces chunk fragmentation
- Better than default 500 for structured data

### Why k=5 for Retrieval?

**Benefits:**
- Retrieves multiple vehicles for comparison
- Handles cases where query matches multiple vehicles
- Provides context for follow-up questions
- Better than k=3 for comprehensive responses

### Why Temperature 0?

**Consistency:**
- Deterministic responses for data queries
- No creative variation needed
- Accurate citation of sources
- Reliable for business use

### Why In-Memory Storage?

**Advantages:**
- Fast initialization (no disk I/O)
- Simple development and testing
- Good for datasets under 10,000 vehicles
- Easy cleanup on exit

**Trade-off:**
- Must re-index on each run (~2-5 seconds)
- For persistent storage, add `persist_directory` parameter

## Error Handling

### CSV Loading Errors

```python
try:
    df = pd.read_csv(csv_path)
    # Process data...
except FileNotFoundError:
    print(f"❌ CSV file not found: {csv_path}")
    return []
except Exception as e:
    print(f"❌ Error processing CSV: {str(e)}")
    return []
```

### Empty CSV Handling

```python
if not csv_data:
    print("No vehicle data found, creating placeholder")
    csv_data = [{
        "text": "This is a placeholder document for an empty vehicle mapping knowledge base.",
        "metadata": {"source": "placeholder", "trim_count": 0}
    }]
```

### Runtime Errors

```python
try:
    response = self.chain.invoke(question)
    return response.strip()
except Exception as e:
    error_msg = f"❌ Error generating response: {str(e)}"
    print(error_msg)
    return "Sorry, I encountered an error while processing your question. Please try again."
```

### Signal Handling

```python
signal.signal(signal.SIGINT, self._signal_handler)

def _signal_handler(self, signum, frame):
    print("\n\n👋 Goodbye! Chat session ended.")
    self.running = False
    sys.exit(0)
```

## Performance Characteristics

### Initialization

- **CSV Loading**: ~100-500ms depending on size
- **Grouping**: ~50-200ms depending on row count
- **Text Processing**: ~100-300ms
- **Embedding Generation**: ~1-3 seconds depending on vehicle count
- **Total**: ~2-5 seconds for typical dataset

### Query Processing

- **First Query**: ~2-3 seconds (Ollama warm-up)
- **Subsequent Queries**: ~1-2 seconds
- **Retrieval**: ~50-100ms
- **LLM Generation**: ~1-2 seconds (most of the time)

### Memory Usage

- **Python Process**: ~200-300MB
- **Ollama Models**: ~2-3GB (mxbai-embed-large + llama3.2:3b)
- **Vector Store**: ~50-200MB depending on vehicle count
- **Total System**: ~2.5-4GB RAM

### Scalability

**Good Performance:**
- Up to 1,000 vehicles: <3 seconds initialization
- Up to 10,000 vehicles: <10 seconds initialization
- Query speed unaffected by dataset size (k=5 retrieval)

**Consider Optimization:**
- 10,000+ vehicles: Use persistent storage
- 50,000+ vehicles: Consider FAISS or other optimized vector stores
- Very large datasets: Batch processing or server deployment

## Extensibility Points

### Adding Persistent Storage

```python
def build_vectorstore(csv_data=None):
    # ... processing ...

    vectordb = Chroma.from_texts(
        texts=chunks,
        embedding=embeddings,
        metadatas=metas,
        persist_directory="./chroma_db"  # Add this
    )
    return vectordb
```

### Adding Metadata Filtering

```python
retriever = vectordb.as_retriever(
    search_kwargs={
        "k": 5,
        "filter": {"vdat_make_name": "Audi"}  # Filter by make
    }
)
```

### Adding Chat History

```python
class ChatSession:
    def __init__(self):
        self.chat_history = []  # Add this
        # ... rest of init ...

    def generate_response(self, question):
        # Include history in prompt
        # Append Q&A to history
```

### Adding Export Functionality

```python
def export_results(self, query, response, filename="results.json"):
    import json
    data = {
        "query": query,
        "response": response,
        "timestamp": datetime.now().isoformat()
    }
    with open(filename, 'a') as f:
        json.dump(data, f)
        f.write('\n')
