#!/usr/bin/env python3
"""
Vehicle Mapping RAG System - Reusable Core Logic

This module provides a reusable VehicleRAG class
in web applications or CLI applications.
"""

import pandas as pd
from langchain.prompts import ChatPromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_ollama import OllamaEmbeddings, OllamaLLM


class VehicleRAG:
    """
    A reusable RAG system for querying vehicle mapping data.

    This class encapsulates all RAG functionality including CSV processing,
    vector store creation, and query handling.
    """

    def __init__(self):
        """Initialize an empty RAG system."""
        self.vectordb = None
        self.chain = None
        self.csv_filename = None
        self.vehicle_count = 0
        self.csv_data = None
        self.initialized = False

    def load_and_process_csv(self, csv_path):
        """
        Load the vehicle mapping CSV and process it into grouped records by vdatModelId.
        Each record contains rich searchable text and comprehensive metadata.

        Args:
            csv_path (str): Path to the CSV file

        Returns:
            list: List of processed vehicle records

        Raises:
            FileNotFoundError: If CSV file doesn't exist
            ValueError: If CSV is missing required columns
        """
        try:
            # Read the CSV file
            df = pd.read_csv(csv_path)

            # Validate required columns
            required_columns = ['vdatModelId', 'vdatMakeName', 'vdatModelName',
                               'coxMakeName', 'coxTrimName']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"CSV is missing required columns: {', '.join(missing_columns)}")

            # Group by vdatModelId to consolidate multiple Cox trim mappings
            grouped_data = []

            for model_id, group in df.groupby('vdatModelId'):
                # Get unique values for this model
                first_row = group.iloc[0]

                # Build rich searchable text content
                make_model = f"{first_row['vdatMakeName']} {first_row['vdatModelName']}"

                # Collect all Cox information from CSV
                cox_trims = group['coxTrimName'].dropna().unique().tolist()
                cox_trim_codes = group['coxTrimCode'].dropna().unique().tolist() if 'coxTrimCode' in group.columns else []
                cox_models = group['coxModelName'].dropna().unique().tolist() if 'coxModelName' in group.columns else []
                cox_model_codes = group['coxModelCode'].dropna().unique().tolist() if 'coxModelCode' in group.columns else []
                cox_make = first_row['coxMakeName']
                cox_make_code = first_row.get('coxMakeCode', '')
                cox_series = group['coxSeriesName'].dropna().unique().tolist() if 'coxSeriesName' in group.columns else []
                cox_series_codes = group['coxSeriesCode'].dropna().unique().tolist() if 'coxSeriesCode' in group.columns else []
                cox_fuel_type_codes = group['coxFuelTypeCode'].dropna().unique().tolist() if 'coxFuelTypeCode' in group.columns else []
                cox_body_styles = group['coxBodyStyleName'].dropna().unique().tolist() if 'coxBodyStyleName' in group.columns else []
                cox_body_style_codes = group['coxBodyStyleCode'].dropna().unique().tolist() if 'coxBodyStyleCode' in group.columns else []

                # Get fuel type names for display
                fuel_types = group['coxFuelTypeName'].dropna().unique().tolist() if 'coxFuelTypeName' in group.columns else []

                # Build comprehensive searchable text with ALL CSV columns
                # Put fuel type information early and prominently for better retrieval
                fuel_type_info = ""
                if cox_fuel_type_codes:
                    fuel_type_info = f"FUEL TYPE: {', '.join(cox_fuel_type_codes)}"
                    if fuel_types:
                        fuel_type_info += f" ({', '.join(fuel_types)})"

                searchable_text = f"""
                    Model ID: {model_id}
                    Vehicle: {make_model}
                    {fuel_type_info}
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
                """

                # Add special requirements if they exist
                special_flags = []
                if 'Needs Bodystyle' in group.columns and group['Needs Bodystyle'].any() and group['Needs Bodystyle'].iloc[0] == 'Yes':
                    special_flags.append("Requires Body Style mapping")
                if 'Needs Fuel Type' in group.columns and group['Needs Fuel Type'].any() and group['Needs Fuel Type'].iloc[0] == 'Yes':
                    special_flags.append("Requires Fuel Type mapping")
                if 'Map to Multiple Cox Models' in group.columns and group['Map to Multiple Cox Models'].any() and group['Map to Multiple Cox Models'].iloc[0] == 'Yes':
                    special_flags.append("Maps to multiple Cox models")
                if 'Map to Multiple Cox Trims' in group.columns and group['Map to Multiple Cox Trims'].any() and group['Map to Multiple Cox Trims'].iloc[0] == 'Yes':
                    special_flags.append("Maps to multiple Cox trims")

                if special_flags:
                    searchable_text += f"\nSpecial Requirements: {', '.join(special_flags)}"

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
                    "needs_bodystyle": group['Needs Bodystyle'].iloc[0] == 'Yes' if 'Needs Bodystyle' in group.columns and pd.notna(group['Needs Bodystyle'].iloc[0]) else False,
                    "needs_fuel_type": group['Needs Fuel Type'].iloc[0] == 'Yes' if 'Needs Fuel Type' in group.columns and pd.notna(group['Needs Fuel Type'].iloc[0]) else False,
                    "multiple_cox_models": group['Map to Multiple Cox Models'].iloc[0] == 'Yes' if 'Map to Multiple Cox Models' in group.columns and pd.notna(group['Map to Multiple Cox Models'].iloc[0]) else False,
                    "multiple_cox_trims": group['Map to Multiple Cox Trims'].iloc[0] == 'Yes' if 'Map to Multiple Cox Trims' in group.columns and pd.notna(group['Map to Multiple Cox Trims'].iloc[0]) else False,
                    "trim_count": len(cox_trims)
                }

                grouped_data.append({
                    "text": searchable_text.strip(),
                    "metadata": metadata
                })

            return grouped_data

        except FileNotFoundError:
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        except Exception as e:
            raise Exception(f"Error processing CSV: {str(e)}")

    def build_vectorstore(self, csv_data):
        """
        Build a vector store from the CSV data.

        Args:
            csv_data (list): Processed vehicle records

        Returns:
            Chroma: Vector database instance
        """
        # Handle empty knowledge base
        if not csv_data:
            csv_data = [{
                "text": "This is a placeholder document for an empty vehicle mapping knowledge base.",
                "metadata": {"source": "placeholder", "trim_count": 0}
            }]

        # Split into chunks
        splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
        chunks, metas = [], []

        for item in csv_data:
            text_content = item["text"]
            metadata = item["metadata"]

            # Split the text content into chunks
            text_chunks = splitter.split_text(text_content)

            for chunk in text_chunks:
                chunks.append(chunk)
                metas.append(metadata)

        # Convert to embeddings
        embeddings = OllamaEmbeddings(model="mxbai-embed-large")

        # Store in vector DB
        vectordb = Chroma.from_texts(texts=chunks, embedding=embeddings, metadatas=metas)
        return vectordb

    def format_docs(self, docs):
        """
        Format retrieved documents with source citations.

        Args:
            docs (list): Retrieved documents

        Returns:
            str: Formatted context string
        """
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

    def build_chain(self):
        """
        Build the RAG chain for query processing.

        Returns:
            Chain: LangChain RAG chain
        """
        # Retrieve: Embed question & search Chroma
        retriever = self.vectordb.as_retriever(search_kwargs={"k": 5})

        # Prompt: Pass context + question into LLM
        system = """
        You are a helpful AI assistant specializing in vehicle data and Cox automotive mapping information.
        You have access to a comprehensive vehicle mapping knowledge base.

        RESPONSE GUIDELINES:
        - Extract ALL relevant information from the provided CONTEXT before responding
        - Cite sources using their [source] tags (which represent vdatModelId values)
        - Use clean, bullet-point formatting for trim lists
        - Be contextually aware of what the user is asking

        SOURCE CITATION RULES:
        - Each document in the context has a [source] tag at the beginning (e.g., [audi_a3-sportback-e-tron])
        - You MUST use the [source] tag from the SAME document that contains the answer to the question
        - NEVER use a [source] tag from a different document than the one containing the information
        - The source ID should logically match the vehicle you're discussing (e.g., [audi_*] for Audi vehicles, [bmw_*] for BMW)
        - If answering about "Audi Sportback", the source MUST be an audi_* identifier, NOT ram_* or any other make
        - CRITICAL: Match each piece of information to its correct source document before citing
        - When you see trim information in the context, use the [source] from THAT specific document

        FUEL TYPE QUERIES:
        - When users ask about vehicle fuel types (electric, hybrid, gas, diesel, etc.), you MUST filter based on the coxFuelTypeCode field found in the context
        - Electric vehicles have coxFuelTypeCode = "ELE" (look for "FUEL TYPE: ELE" in the context)
        - STRICT RULE: ONLY list vehicles that explicitly show "FUEL TYPE: ELE" in their context. Do NOT include vehicles just because they have "electric" in their name or trim name
        - If a vehicle's context does NOT contain "FUEL TYPE: ELE", it is NOT an electric vehicle, even if "electric" appears in the vehicle name
        - The vdatModelId and vehicle names are just identifiers - NEVER use them for filtering fuel types
        - Example: "Show me all electric vehicles" should return ONLY vehicles where the context explicitly shows "FUEL TYPE: ELE"

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

        # Chain wiring
        chain = (
            {
                "context": retriever | self.format_docs,
                "question": RunnablePassthrough(),
            }
            | prompt
            | llm
            | StrOutputParser()
        )
        return chain

    def initialize_from_csv(self, csv_path):
        """
        Initialize the RAG system from a CSV file.

        Args:
            csv_path (str): Path to the CSV file

        Returns:
            dict: Initialization result with success status and metadata
        """
        try:
            # Load and process CSV data
            self.csv_data = self.load_and_process_csv(csv_path)
            self.vehicle_count = len(self.csv_data)

            # Build vector store
            self.vectordb = self.build_vectorstore(self.csv_data)

            # Build RAG chain
            self.chain = self.build_chain()

            # Store metadata
            import os
            self.csv_filename = os.path.basename(csv_path)
            self.initialized = True

            return {
                "success": True,
                "vehicle_count": self.vehicle_count,
                "filename": self.csv_filename,
                "message": f"Successfully initialized RAG system with {self.vehicle_count} vehicles"
            }

        except Exception as e:
            self.initialized = False
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to initialize RAG system: {str(e)}"
            }

    def query(self, question):
        """
        Process a query through the RAG pipeline.

        Args:
            question (str): User's question

        Returns:
            dict: Query result with response and metadata
        """
        if not self.initialized or self.chain is None:
            return {
                "success": False,
                "error": "RAG system not initialized",
                "response": "Please upload a CSV file first to initialize the system."
            }

        try:
            # Generate response using RAG chain
            response = self.chain.invoke(question)

            return {
                "success": True,
                "response": response.strip(),
                "question": question
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response": f"Error processing query: {str(e)}"
            }

    def get_stats(self):
        """
        Get statistics about the loaded data.

        Returns:
            dict: Statistics including vehicle count, filename, etc.
        """
        return {
            "initialized": self.initialized,
            "vehicle_count": self.vehicle_count,
            "filename": self.csv_filename,
            "has_vectordb": self.vectordb is not None,
            "has_chain": self.chain is not None
        }

    def reset(self):
        """Reset the RAG system, clearing all data."""
        self.vectordb = None
        self.chain = None
        self.csv_filename = None
        self.vehicle_count = 0
        self.csv_data = None
        self.initialized = False
