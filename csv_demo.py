#!/usr/bin/env python3
import signal
import sys
import pandas as pd

from langchain.prompts import ChatPromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_ollama import OllamaEmbeddings, OllamaLLM

# ---------------- Knowledge base from CSV ---------------- #
def load_and_process_csv(csv_path="data/vdat_cox_mapping.csv"):
    """
    Load the vehicle mapping CSV and process it into grouped records by vdatModelId.
    Each record contains rich searchable text and comprehensive metadata.
    """
    try:
        # Read the CSV file
        df = pd.read_csv(csv_path)

        # Group by vdatModelId to consolidate multiple Cox trim mappings
        grouped_data = []

        for model_id, group in df.groupby('vdatModelId'):
            # Get unique values for this model
            first_row = group.iloc[0]

            # Build rich searchable text content
            make_model = f"{first_row['vdatMakeName']} {first_row['vdatModelName']}"

            # Collect all Cox information from CSV
            cox_trims = group['coxTrimName'].dropna().unique().tolist()
            cox_trim_codes = group['coxTrimCode'].dropna().unique().tolist()
            cox_models = group['coxModelName'].dropna().unique().tolist()
            cox_model_codes = group['coxModelCode'].dropna().unique().tolist()
            cox_make = first_row['coxMakeName']
            cox_make_code = first_row.get('coxMakeCode', '')
            cox_series = group['coxSeriesName'].dropna().unique().tolist()
            cox_series_codes = group['coxSeriesCode'].dropna().unique().tolist()
            cox_fuel_type_codes = group['coxFuelTypeCode'].dropna().unique().tolist()
            cox_body_styles = group['coxBodyStyleName'].dropna().unique().tolist()
            cox_body_style_codes = group['coxBodyStyleCode'].dropna().unique().tolist()

            # Build comprehensive searchable text with ALL CSV columns
            searchable_text = f"""
                Model ID: {model_id}
                Vehicle: {make_model}
                Cox Make: {cox_make}
                Cox Make Code: {cox_make_code}
                Cox Series: {', '.join(cox_series) if cox_series else ''}
                Cox Series Codes: {', '.join(cox_series_codes) if cox_series_codes else ''}
                Cox Models: {', '.join(cox_models)}
                Cox Model Codes: {', '.join(cox_model_codes)}
                Cox Trims: {', '.join(cox_trims)}
                Cox Trim Codes: {', '.join(cox_trim_codes)}
                Cox Body Styles: {', '.join(cox_body_styles) if cox_body_styles else ''}
                Cox Body Style Codes: {', '.join(cox_body_style_codes) if cox_body_style_codes else ''}
                Cox Fuel Type Codes: {', '.join(cox_fuel_type_codes) if cox_fuel_type_codes else ''}
            """

            # Add special requirements if they exist
            special_flags = []
            if group['Needs Bodystyle'].any() and group['Needs Bodystyle'].iloc[0] == 'Yes':
                special_flags.append("Requires Body Style mapping")
            if group['Needs Fuel Type'].any() and group['Needs Fuel Type'].iloc[0] == 'Yes':
                special_flags.append("Requires Fuel Type mapping")
            if group['Map to Multiple Cox Models'].any() and group['Map to Multiple Cox Models'].iloc[0] == 'Yes':
                special_flags.append("Maps to multiple Cox models")
            if group['Map to Multiple Cox Trims'].any() and group['Map to Multiple Cox Trims'].iloc[0] == 'Yes':
                special_flags.append("Maps to multiple Cox trims")

            if special_flags:
                searchable_text += f"\nSpecial Requirements: {', '.join(special_flags)}"

            # Add fuel type information if available
            fuel_types = group['coxFuelTypeName'].dropna().unique().tolist()
            if fuel_types:
                searchable_text += f"\nFuel Types: {', '.join(fuel_types)}"

            # Build comprehensive metadata (convert lists to strings for Chroma compatibility)
            metadata = {
                "source": model_id,
                "vdat_make_name": first_row['vdatMakeName'],
                "vdat_model_name": first_row['vdatModelName'],
                "cox_make_name": cox_make,
                "cox_models_str": ", ".join(cox_models) if cox_models else "",
                "cox_trims_str": ", ".join(cox_trims) if cox_trims else "",
                "cox_trim_codes_str": ", ".join(cox_trim_codes) if cox_trim_codes else "",
                "fuel_types_str": ", ".join(fuel_types) if fuel_types else "",
                "needs_bodystyle": group['Needs Bodystyle'].iloc[0] == 'Yes' if pd.notna(group['Needs Bodystyle'].iloc[0]) else False,
                "needs_fuel_type": group['Needs Fuel Type'].iloc[0] == 'Yes' if pd.notna(group['Needs Fuel Type'].iloc[0]) else False,
                "multiple_cox_models": group['Map to Multiple Cox Models'].iloc[0] == 'Yes' if pd.notna(group['Map to Multiple Cox Models'].iloc[0]) else False,
                "multiple_cox_trims": group['Map to Multiple Cox Trims'].iloc[0] == 'Yes' if pd.notna(group['Map to Multiple Cox Trims'].iloc[0]) else False,
                "trim_count": len(cox_trims)
            }

            grouped_data.append({
                "text": searchable_text.strip(),
                "metadata": metadata
            })

        print(f"✅ Processed vehicle models from CSV")
        return grouped_data

    except FileNotFoundError:
        print(f"❌ CSV file not found: {csv_path}")
        return []
    except Exception as e:
        print(f"❌ Error processing CSV: {str(e)}")
        return []

# ---------------- Ingestion ---------------- #
# Build avector store from the CSV data
def build_vectorstore(csv_data=None):
    # Load CSV data if not provided
    if csv_data is None:
        csv_data = load_and_process_csv()

    # Handle empty knowledge base
    if not csv_data:
        print("No vehicle data found, creating placeholder")
        csv_data = [{
            "text": "This is a placeholder document for an empty vehicle mapping knowledge base.",
            "metadata": {"source": "placeholder", "trim_count": 0}
        }]

    # --- Split into chunks ---
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    chunks, metas = [], []

    for item in csv_data:
        text_content = item["text"]
        metadata = item["metadata"]

        # Split the text content into chunks
        text_chunks = splitter.split_text(text_content)

        for chunk in text_chunks:
            chunks.append(chunk)
            # Include the original metadata for each chunk
            metas.append(metadata)

    # --- Convert to embeddings ---
    embeddings = OllamaEmbeddings(model="mxbai-embed-large")

    # --- Store in vector DB ---
    vectordb = Chroma.from_texts(texts=chunks, embedding=embeddings, metadatas=metas)
    return vectordb


def format_docs(docs):
# retrieved documents with source citations
    lines = []
    for d in docs:
        src = d.metadata.get("source", "kb")
        content = d.page_content.strip()

        # Add metadata context for better retrieval quality
        if hasattr(d, 'metadata') and d.metadata:
            trim_count = d.metadata.get('trim_count', 0)
            if trim_count > 0:
                content += f"\n(This vehicle has {trim_count} Cox trim(s) mapped)"

        lines.append(f"[{src}] {content}")
    return "\n\n".join(lines)

# ---------------- Query ---------------- #
def build_chain(vectordb):
    # --- Retrieve: Embed question & search Chroma) ---
    retriever = vectordb.as_retriever(search_kwargs={"k": 5})

    # --- Prompt: Pass context + question into LLM ---
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

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", "CONTEXT:\n{context}\n\nQUESTION: {question}"),
        ]
    )

    llm = OllamaLLM(model="llama3.2:3b", temperature=0)

    # --- Chain wiring ---
    # 1) Take the user question
    # 2) Retrieve docs → format into a context string
    # 3) Fill the prompt
    # 4) Generate with LLM → parse to string
    chain = (
        {
            "context": retriever | format_docs,   # retrieval + citations
            "question": RunnablePassthrough(),    # forward original question
        }
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain


# ---------------- Interactive Chat Session Class ---------------- #
class ChatSession:
    """Manages an interactive RAG chat session."""

    def __init__(self):
        self.vectordb = None
        self.chain = None
        self.running = True

        # Set up signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully."""
        print("\n\n👋 Goodbye! Chat session ended.")
        self.running = False
        sys.exit(0)

    def initialize_rag_system(self):
        """Initialize the vector store and RAG chain once at startup."""
        print("\n🔧 Initializing Vehicle Mapping RAG system...")

        try:
            # Build vector store from CSV data (this can take a moment)
            print("   📚 Loading and processing vehicle mapping CSV...")
            self.vectordb = build_vectorstore()

            # Build the RAG chain
            print("   🔗 Setting up RAG chain...")
            self.chain = build_chain(self.vectordb)

            print("✅ Vehicle Mapping RAG system initialized successfully!\n")
            return True

        except Exception as e:
            print(f"❌ Failed to initialize RAG system: {str(e)}")
            print(
                "   Make sure Ollama is running with models: mxbai-embed-large, llama3.2:3b"
            )
            print("   Also ensure data/vdat_cox_mapping.csv exists and pandas is installed")
            return False

    def display_welcome(self):
        """Display welcome message and instructions."""
        welcome_msg = """
🚗 Vehicle Mapping RAG Chat
=====================================

Welcome to the Vehicle Mapping RAG system! This system can answer:
• Questions about vehicle Cox mapping data from the knowledge base
• Cox trim counts and details for specific vehicle models
• Mapping requirements (body style, fuel type, etc.)
• General automotive questions using LLM knowledge

💡 Available Commands:
   /help    - Show this help message
   /quit    - Exit the chat (or use Ctrl+C)
   /exit    - Same as /quit
   q        - Quick exit

🚀 Just type your question and press Enter to get started!
📝 The system will cite sources using vehicle model IDs like [audi_a3-sportback-e-tron].

=====================================
"""
        print(welcome_msg)

    def display_help(self):
        """Display help information."""
        help_msg = """
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
"""
        print(help_msg)

    def process_command(self, user_input):
        """Process special commands. Returns True if command was handled."""
        user_input = user_input.lower().strip()

        if user_input in ["/quit", "/exit", "q"]:
            print("\n👋 Goodbye! Thanks for using Vehicle Mapping RAG Chat!")
            return "quit"

        elif user_input in ["/help", "/h"]:
            self.display_help()
            return "help"

        elif user_input in ["/clear", "/cls"]:
            # Clear screen (works on most terminals)
            import os

            os.system("cls" if os.name == "nt" else "clear")
            return "clear"

        return None

    def get_user_input(self):
        """Get user input with a nice prompt."""
        try:
            prompt = "Me: "
            user_input = input(prompt).strip()
            return user_input

        except (EOFError, KeyboardInterrupt):
            # Handle Ctrl+C or Ctrl+D
            return "/quit"

    def generate_response(self, question):
        """Generate a response using the RAG chain."""
        try:
            print("\n🤖 Thinking...")

            # Get response from RAG chain
            response = self.chain.invoke(question)

            return response.strip()

        except Exception as e:
            error_msg = f"❌ Error generating response: {str(e)}"
            print(error_msg)
            return "Sorry, I encountered an error while processing your question. Please try again."

    def run_chat(self):
        """Main interactive chat loop."""
        # Initialize system
        if not self.initialize_rag_system():
            return

        # # Show welcome message
        # self.display_welcome()

        # Main chat loop
        while self.running:
            try:
                # Get user input
                print()  # Add spacing
                user_input = self.get_user_input()

                if not user_input:
                    continue

                # Process commands
                command_result = self.process_command(user_input)
                if command_result == "quit":
                    break
                elif command_result in ["help", "clear"]:
                    continue

                response = self.generate_response(user_input)
                print(response)

                # Add separator for readability
                print("\n" + "─" * 50)

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"\n❌ Unexpected error: {str(e)}")
                print("The chat will continue. Try your question again.")

        self.cleanup()

    def cleanup(self):
        """Perform cleanup before exit."""
        print("\n🧹 Cleaning up...")
        # Could add cleanup logic here if needed (e.g., saving chat history)
        print("✨ Chat session ended")


# ---------------- Main execution ---------------- #
def main():
    """Main entry point for the interactive RAG chat."""
    chat_session = ChatSession()
    chat_session.run_chat()


if __name__ == "__main__":
    main()
