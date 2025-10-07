# Quick Start Guide - Flask Web Application

## 🚀 Getting Started in 3 Steps

### 1. Start the Server

**Prerequisites:**

- Python 3.8+ with virtual environment
- Ollama installed and running locally:
  1. Pull required models:
     ```bash
     ollama pull mxbai-embed-large
     ollama pull llama3.2:3b
     ```
  2. Start Ollama service:
     ```bash
     ollama serve
     ```
     (Keep this running in a separate terminal)

**Installation & Startup:**

1. **Activate virtual environment** (if not already activated):

   ```bash
   source venv/bin/activate
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Start the Flask server**:

   ```bash
   python app.py
   ```

4. **Verify it's running** - You should see:
   ```
    * Running on http://127.0.0.1:5001
    * Running on http://192.168.1.246:5001
   ```

### 2. Open in Browser

Navigate to: **http://localhost:5001**

### 3. Upload CSV & Chat

1. **Upload your CSV file**:

   - Drag and drop `data/vehicle_mapping_sample.csv` onto the upload area
   - Or click to browse and select the file
   - Click "Upload & Initialize"
   - Wait 2-5 seconds for processing

2. **Start chatting**:
   - Type your question in the chat box
   - Press Enter or click "Send"
   - Get instant AI-powered responses!

## 📝 Example Questions to Try

Once your CSV is uploaded, try these queries:

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

## 🎨 Features You'll See

- **Drag & Drop Upload**: Just drag your CSV file onto the upload area
- **Real-time Chat**: Instant responses with formatted bullet points
- **Easy Reset**: Upload a new CSV anytime with the reset button
- **Loading Indicators**: Visual feedback during processing
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Local Single-User**: Simplified architecture for personal use

## 🔄 Uploading a Different CSV

1. Click the **"🔄 Upload New CSV"** button in the chat interface
2. Confirm the reset
3. Upload your new CSV file
4. Start chatting with the new data

## ⚠️ Important Notes

- **CSV Requirements**: Your CSV must have these columns:

  - `vdatModelId`, `vdatMakeName`, `vdatModelName`
  - `coxMakeName`, `coxTrimName`

- **File Size Limit**: Maximum 10MB

- **Ollama Required**: Make sure Ollama is running with:
  - `mxbai-embed-large` (embeddings)
  - `llama3.2:3b` (LLM)

## 🛑 Stopping the Server

To stop the server, press **Ctrl+C** in the terminal.

## 📚 More Information

- Full documentation: See `README_FLASK.md`
- API documentation: See `README_FLASK.md` → API Endpoints section
- Original CLI version: Run `python cli_app.py`

## 🐛 Troubleshooting

**Browser shows "Connection refused"**

- Make sure the server is running (check terminal)
- Try http://127.0.0.1:5001 instead of localhost

**Upload fails**

- Check that your CSV has the required columns
- Verify file size is under 10MB
- Make sure file extension is `.csv`

**Slow responses**

- First query may take 2-3 seconds (Ollama warm-up)
- Subsequent queries should be faster (1-2 seconds)
- Initialization takes 2-5 seconds (one-time per upload)

**Ollama errors**

- Verify Ollama is running: `ollama list`
- Check models are available:
  ```bash
  ollama pull mxbai-embed-large
  ollama pull llama3.2:3b
  ```

## 🎯 What's Next?

After testing the web interface:

1. Try different types of queries
2. Compare responses with the CLI version (`python cli_app.py`)
3. Test with your own vehicle mapping CSV files
4. Explore the API endpoints for programmatic access

Enjoy your Vehicle Mapping RAG Web Application! 🚗✨
