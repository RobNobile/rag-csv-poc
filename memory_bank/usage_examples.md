# Vehicle Mapping RAG - Usage Examples

## Available Interfaces

This system provides two ways to interact with the Vehicle Mapping RAG:

### 🌐 Web Interface (Flask)
- **Start**: `python app.py` → Open http://localhost:5001
- **Features**: Drag-and-drop CSV upload, browser-based chat, session management
- **Best For**: Business users, demos, non-technical stakeholders
- **Documentation**: See `README_FLASK.md` for detailed web interface usage

### 💻 CLI Interface (Terminal)
- **Start**: `python csv_demo.py`
- **Features**: Terminal-based chat, command system, pre-configured CSV path
- **Best For**: Developers, automation, scripting
- **Documentation**: Examples below focus on CLI usage

## Running the CLI Interactive Chat

### Basic Execution

```bash
# Navigate to project directory
cd rag_poc_csv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run the vehicle mapping RAG chat
python csv_demo.py
```

### Expected Startup Output

```
🔧 Initializing Vehicle Mapping RAG system...
   📚 Loading and processing vehicle mapping CSV...
✅ Processed vehicle models from CSV
   🔗 Setting up RAG chain...
✅ Vehicle Mapping RAG system initialized successfully!
```

The system initializes once (loading and processing the CSV) and then enters interactive mode. You can now type questions and receive responses continuously.

## Example Chat Sessions

### Session 1: Simple Trim Queries

```
Me: How many Cox trims are mapped to Audi A3 Sportback e-tron?

🤖 Thinking...
Based on [audi_a3-sportback-e-tron], the Audi A3 Sportback e-tron has 2 Cox trims:
• e-tron Premium
• e-tron Premium Plus

──────────────────────────────────────────────────

Me: What Cox trims are available for BMW M5 Touring?

🤖 Thinking...
Based on [bmw_m5-touring], the BMW M5 Touring has these Cox trims:
• M5 Competition
• M5 CS

──────────────────────────────────────────────────

Me: Show me all trims for Chevrolet Corvette ZR1

🤖 Thinking...
Based on [chevrolet_corvette-zr1], the Chevrolet Corvette ZR1 has these Cox trims:
• ZR1 Coupe
• ZR1 Convertible

──────────────────────────────────────────────────

Me: /quit

👋 Goodbye! Thanks for using Vehicle Mapping RAG Chat!
```

### Session 2: Using the Help Command

```
Me: /help

📖 Help & Commands
==================

Available Commands:
  /help, /h     - Show this help message
  /quit, /exit  - Exit the chat session
  q             - Quick exit

Example Questions:

🚗 Vehicle Mapping Queries:
  • "How many Cox trims are mapped to Audi A3 Sportback e-tron?"
  • "What Cox trims are available for BMW M5 Touring?"
  • "Which models need body style mapping?"
  • "Show me all electric vehicles in the database"
  • "What's the Cox model code for Bentley Continental GT?"

🔍 Search by ID or Name:
  • "What trims are mapped to audi_a3-sportback-e-tron?"
  • "Tell me about Chevrolet Corvette ZR1"
  • "Which Dodge models have SRT trims?"

💡 Tips:
  - Sources like [audi_a3-sportback-e-tron] refer to vehicle model IDs
  - You can search by make/model name or technical vdatModelId
  - Ask follow-up questions in the same session!

==================

Me: Thanks!

🤖 Thinking...
You're welcome! Feel free to ask me about any vehicle mappings.
```

### Session 3: Special Requirements Queries

```
Me: Which vehicles need body style mapping?

🤖 Thinking...
Based on the database, the following vehicles require body style mapping:
• [toyota_camry] Toyota Camry
• [honda_accord] Honda Accord
• [ford_f-150] Ford F-150

These vehicles have the "Requires Body Style mapping" flag set.

──────────────────────────────────────────────────

Me: Show me vehicles that map to multiple Cox models

🤖 Thinking...
The following vehicles map to multiple Cox models:
• [ram_power-wagon] Ram Power Wagon - Maps to 2 Cox models
• [jeep_wrangler] Jeep Wrangler - Maps to 3 Cox models

──────────────────────────────────────────────────

Me: What fuel types are available for electric vehicles?

🤖 Thinking...
Based on the electric vehicles in the database:
• [audi_a3-sportback-e-tron] Audi A3 Sportback e-tron - Fuel Type: Electric
• [bmw_i3] BMW i3 - Fuel Type: Electric
• [tesla_model-s] Tesla Model S - Fuel Type: Electric

All are coded as "Electric" in the Cox fuel type classification.
```

### Session 4: Comparison Mode (with Reference List)

```
Me: I have these trims: ['e-tron Premium', 'e-tron Premium Plus', 'e-tron Prestige']. What's missing for Audi A3 Sportback e-tron?

🤖 Thinking...
Based on [audi_a3-sportback-e-tron], the Audi A3 Sportback e-tron currently has these Cox trims:
• e-tron Premium
• e-tron Premium Plus

Comparing against your reference list, the missing trim is:
• e-tron Prestige

──────────────────────────────────────────────────

Me: Here's a JSON array: ["M5 Base", "M5 Competition", "M5 CS", "M5 Competition xDrive"]. What trims does BMW M5 Touring have vs. this list?

🤖 Thinking...
Based on [bmw_m5-touring], the BMW M5 Touring currently has these Cox trims:
• M5 Competition
• M5 CS

Comparing against your reference list, the missing trims are:
• M5 Base
• M5 Competition xDrive

──────────────────────────────────────────────────
```

### Session 5: Search by Vehicle ID

```
Me: What trims are mapped to audi_a3-sportback-e-tron?

🤖 Thinking...
Based on [audi_a3-sportback-e-tron], this vehicle has 2 Cox trims:
• e-tron Premium
• e-tron Premium Plus

Vehicle Details:
- VDAT Make: Audi
- VDAT Model: A3 Sportback e-tron
- Cox Make: Audi
- Cox Model: A3 Sportback e-tron

──────────────────────────────────────────────────

Me: Tell me about ram_power-wagon

🤖 Thinking...
Based on [ram_power-wagon], here's the information:

Vehicle: Ram Power Wagon
Cox Trims:
• Power Wagon Crew Cab
• Power Wagon Mega Cab

Special Requirements:
- Maps to multiple Cox models
- Requires body style mapping

Cox Body Styles:
• Crew Cab Pickup
• Mega Cab Pickup
```

## Available Commands

### Help Commands

```bash
/help    # Show full help information
/h       # Short form of help
```

### Exit Commands

```bash
/quit    # Exit gracefully
/exit    # Same as /quit
q        # Quick exit
Ctrl+C   # Signal-based graceful shutdown
```

### Screen Commands

```bash
/clear   # Clear the terminal screen
/cls     # Same as /clear
```

## Query Patterns

### 1. Trim Count Queries

**Pattern**: "How many [trims/mappings] for [Vehicle]?"

```
"How many Cox trims are mapped to Audi A3 Sportback e-tron?"
"How many trims does the BMW M5 Touring have?"
"Count of Cox mappings for Chevrolet Corvette ZR1"
```

**Expected Response Format:**
```
Based on [source], the [Vehicle] has X Cox trims:
• Trim 1
• Trim 2
• ...
```

### 2. Trim List Queries

**Pattern**: "What trims [are available/does X have/are mapped]?"

```
"What Cox trims are available for BMW M5 Touring?"
"Show me all trims for Chevrolet Corvette ZR1"
"List the Cox trims mapped to Audi A3"
```

### 3. Model Code Queries

**Pattern**: "What [code/model code] for [Vehicle]?"

```
"What's the Cox model code for Bentley Continental GT?"
"Show me Cox codes for Ram Power Wagon"
"What are the trim codes for BMW M5?"
```

### 4. Special Requirements Queries

**Pattern**: "Which [vehicles/models] [need/require/have] [requirement]?"

```
"Which vehicles need body style mapping?"
"Show me models that require fuel type mapping"
"Which vehicles map to multiple Cox models?"
"What models have multiple trim mappings?"
```

### 5. Search by Make

**Pattern**: "Show me [all/list] [Make] [models/vehicles]"

```
"Show me all Audi models"
"List all Chevrolet vehicles"
"What BMW models are in the database?"
```

### 6. Search by Feature

**Pattern**: "[Vehicles/Models] with [feature/attribute]"

```
"Which Dodge models have SRT trims?"
"Show me vehicles with electric fuel type"
"Models with convertible body style"
```

### 7. Search by ID

**Pattern**: Direct vdatModelId lookup

```
"What's in audi_a3-sportback-e-tron?"
"Tell me about bmw_m5-touring"
"Information for chevrolet_corvette-zr1"
```

### 8. Comparison Queries

**Pattern**: Provide reference list + ask for comparison

```
"I have ['Trim1', 'Trim2', 'Trim3']. What's missing for [Vehicle]?"
"Here's my list: [array]. Compare against [Vehicle]"
"My trims are X, Y, Z. What does [Vehicle] have vs. this?"
```

**Key**: Must explicitly provide a reference list for comparison mode to activate.

## Customization Examples

### 1. Using a Different CSV File

Edit `csv_demo.py`:

```python
def load_and_process_csv(csv_path="data/alternative_mapping.csv"):
    # Rest of function remains the same
```

Or call directly:

```python
csv_data = load_and_process_csv("data/my_custom_mapping.csv")
vectordb = build_vectorstore(csv_data)
```

### 2. Adjusting Retrieval Parameters

Edit the `build_chain()` function:

```python
# Get more context per query (default is k=5)
retriever = vectordb.as_retriever(search_kwargs={"k": 10})

# Or use similarity score threshold
retriever = vectordb.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"score_threshold": 0.7, "k": 5}
)
```

### 3. Filtering by Metadata

```python
# Only retrieve Audi vehicles
retriever = vectordb.as_retriever(
    search_kwargs={
        "k": 5,
        "filter": {"vdat_make_name": "Audi"}
    }
)

# Only vehicles needing body style
retriever = vectordb.as_retriever(
    search_kwargs={
        "k": 5,
        "filter": {"needs_bodystyle": True}
    }
)
```

### 4. Changing LLM Temperature

Edit the `build_chain()` function:

```python
# More varied responses (higher temperature)
llm = OllamaLLM(model="llama3.2:3b", temperature=0.3)

# Completely deterministic (lower temperature)
llm = OllamaLLM(model="llama3.2:3b", temperature=0)
```

### 5. Using Different Models

```python
# Different embedding model in build_vectorstore()
embeddings = OllamaEmbeddings(model="all-minilm")

# Larger generation model in build_chain()
llm = OllamaLLM(model="llama3.1:8b", temperature=0)

# Smaller, faster model
llm = OllamaLLM(model="llama3.2:1b", temperature=0)
```

### 6. Adding Persistent Storage

Edit the `build_vectorstore()` function:

```python
# Save database to disk
vectordb = Chroma.from_texts(
    texts=chunks,
    embedding=embeddings,
    metadatas=metas,
    persist_directory="./chroma_db"  # Add this line
)

return vectordb
```

To load an existing database:

```python
from langchain_community.vectorstores import Chroma

# Load existing database instead of creating new one
def build_vectorstore(csv_data=None):
    embeddings = OllamaEmbeddings(model="mxbai-embed-large")

    # Check if database exists
    import os
    if os.path.exists("./chroma_db"):
        print("Loading existing vector database...")
        vectordb = Chroma(
            persist_directory="./chroma_db",
            embedding_function=embeddings
        )
    else:
        # Create new database as before
        csv_data = load_and_process_csv()
        # ... rest of processing ...
        vectordb = Chroma.from_texts(
            texts=chunks,
            embedding=embeddings,
            metadatas=metas,
            persist_directory="./chroma_db"
        )

    return vectordb
```

### 7. Customizing Text Splitting

Edit the `build_vectorstore()` function:

```python
# Larger chunks for more context
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1200,  # Increased from 800
    chunk_overlap=150  # Increased from 100
)

# Smaller chunks for finer granularity
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)
```

### 8. Adding Custom Metadata Processing

Edit the `load_and_process_csv()` function:

```python
# Add custom metadata fields
metadata = {
    "source": model_id,
    "vdat_make_name": first_row['vdatMakeName'],
    "vdat_model_name": first_row['vdatModelName'],
    # ... existing fields ...

    # Add custom fields
    "year": first_row.get('modelYear', ''),
    "category": first_row.get('vehicleCategory', ''),
    "market_segment": first_row.get('marketSegment', ''),
}
```

## Advanced Usage Patterns

### Batch Processing Queries

Create a script to process multiple queries:

```python
#!/usr/bin/env python3
from csv_demo import ChatSession

def batch_process_queries(queries):
    """Process a list of queries and return results."""
    chat_session = ChatSession()

    if not chat_session.initialize_rag_system():
        return []

    results = []
    for query in queries:
        print(f"\nProcessing: {query}")
        response = chat_session.generate_response(query)
        results.append({
            "query": query,
            "response": response
        })

    return results

# Usage
queries = [
    "How many Cox trims are mapped to Audi A3 Sportback e-tron?",
    "What Cox trims are available for BMW M5 Touring?",
    "Which vehicles need body style mapping?"
]

results = batch_process_queries(queries)

# Save results
import json
with open('query_results.json', 'w') as f:
    json.dump(results, indent=2, fp=f)
```

### Export Query Results

Add export functionality to ChatSession:

```python
class ChatSession:
    def __init__(self):
        # ... existing init ...
        self.query_history = []  # Add this

    def generate_response(self, question):
        # ... existing code ...

        # Store in history
        self.query_history.append({
            "timestamp": datetime.now().isoformat(),
            "query": question,
            "response": response
        })

        return response

    def export_history(self, filename="query_history.json"):
        """Export query history to JSON file."""
        import json
        with open(filename, 'w') as f:
            json.dump(self.query_history, f, indent=2)
        print(f"✅ Query history exported to {filename}")
```

### Filter CSV Before Loading

```python
def load_and_process_csv(csv_path="data/vdat_cox_mapping.csv", filter_make=None):
    """Load CSV with optional filtering."""
    df = pd.read_csv(csv_path)

    # Apply filter if specified
    if filter_make:
        df = df[df['vdatMakeName'] == filter_make]
        print(f"Filtered to {len(df)} rows for make: {filter_make}")

    # Continue with grouping...
```

### Add Validation Before Processing

```python
def validate_csv_structure(csv_path):
    """Validate CSV has required columns."""
    required_columns = [
        'vdatModelId', 'vdatMakeName', 'vdatModelName',
        'coxMakeName', 'coxModelName', 'coxTrimName'
    ]

    df = pd.read_csv(csv_path, nrows=1)
    missing = [col for col in required_columns if col not in df.columns]

    if missing:
        raise ValueError(f"CSV missing required columns: {missing}")

    return True

# Use before processing
try:
    validate_csv_structure("data/vdat_cox_mapping.csv")
    csv_data = load_and_process_csv()
except ValueError as e:
    print(f"❌ CSV validation failed: {e}")
```

## Debugging and Troubleshooting

### Enable Verbose Output

Add debugging to functions:

```python
def format_docs(docs):
    print(f"\n[DEBUG] Retrieved {len(docs)} documents")
    lines = []
    for d in docs:
        src = d.metadata.get("source", "kb")
        content = d.page_content.strip()
        print(f"[DEBUG] [{src}] {content[:100]}...")
        # ... rest of function
```

### Check Retrieved Context

```python
def generate_response(self, question):
    try:
        print("\n🤖 Thinking...")

        # Debug: Show what was retrieved
        docs = self.vectordb.similarity_search(question, k=5)
        print(f"\n[DEBUG] Retrieved {len(docs)} documents:")
        for doc in docs:
            print(f"  - [{doc.metadata['source']}]")

        response = self.chain.invoke(question)
        return response.strip()
```

### Test CSV Processing

```python
# Test CSV loading independently
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--test-csv":
        print("Testing CSV processing...")
        csv_data = load_and_process_csv()
        print(f"Loaded {len(csv_data)} vehicle records")

        # Show first record
        if csv_data:
            print("\nFirst record:")
            print(f"Text: {csv_data[0]['text'][:200]}...")
            print(f"Metadata: {csv_data[0]['metadata']}")

        sys.exit(0)

    # Normal execution
    main()
```

Run with: `python csv_demo.py --test-csv`

### Verify Vector Store

```python
def initialize_rag_system(self):
    # ... existing code ...

    # Add verification
    print(f"   📊 Vector store statistics:")
    collection = self.vectordb._collection
    print(f"      - Total documents: {collection.count()}")

    # Sample query
    test_results = self.vectordb.similarity_search("Audi", k=1)
    if test_results:
        print(f"      - Sample retrieval: {test_results[0].metadata['source']}")
```

## Common Issues and Solutions

### Issue: No results for certain queries

**Solution 1**: Increase k value
```python
retriever = vectordb.as_retriever(search_kwargs={"k": 10})
```

**Solution 2**: Check if vehicle exists in CSV
```python
df = pd.read_csv('data/vdat_cox_mapping.csv')
print(df[df['vdatMakeName'].str.contains('Audi', case=False)])
```

### Issue: Slow initialization

**Solution**: Enable persistent storage
```python
vectordb = Chroma.from_texts(
    texts=chunks,
    embedding=embeddings,
    metadatas=metas,
    persist_directory="./chroma_db"
)
```

### Issue: Out of memory with large CSV

**Solution**: Process CSV in chunks
```python
def load_and_process_csv_chunked(csv_path, chunk_size=1000):
    """Process large CSV in chunks."""
    all_data = []
    for chunk in pd.read_csv(csv_path, chunksize=chunk_size):
        # Process chunk
        for model_id, group in chunk.groupby('vdatModelId'):
            # ... processing logic ...
            all_data.append(processed_record)
    return all_data
```

### Issue: Inconsistent responses

**Solution**: Set temperature to 0
```python
llm = OllamaLLM(model="llama3.2:3b", temperature=0)
```

## Performance Optimization Tips

1. **Use persistent storage** for large datasets (>1000 vehicles)
2. **Filter CSV data** before processing if only subset needed
3. **Increase chunk size** to reduce number of chunks
4. **Use smaller models** for faster inference (llama3.2:1b)
5. **Reduce k value** if getting too much irrelevant context
6. **Cache processed CSV** data to avoid re-processing

## Next Steps

After mastering basic usage, explore:

1. **Web Interface**: Add Flask or Streamlit UI for easier access
2. **API Endpoint**: Create REST API for programmatic access
3. **Chat History**: Implement conversation memory for context
4. **Analytics**: Track most common queries and performance metrics
5. **Validation Tools**: Build tools to validate mapping completeness
6. **Export Features**: Export query results in various formats
7. **Batch Operations**: Process multiple vehicles at once
8. **Integration**: Integrate with existing automotive systems
