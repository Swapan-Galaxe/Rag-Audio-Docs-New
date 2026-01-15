import os
import logging
from typing import List, Dict, Optional
from pathlib import Path
from dotenv import load_dotenv

from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
from langchain_community.vectorstores import FAISS, AzureSearch
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

import azure.cognitiveservices.speech as speechsdk
from pypdf import PdfReader
from docx import Document as DocxDocument
from openpyxl import load_workbook
from pptx import Presentation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


class RAGSummarizer:
    """Complete RAG pipeline for extracting summaries from audio and documents."""
    
    def __init__(self, use_azure_search: bool = False):
        """
        Initialize RAG Summarizer.
        
        Args:
            use_azure_search: If True, uses Azure AI Search; if False, uses FAISS
        """
        try:
            # Azure OpenAI setup
            self.embeddings = AzureOpenAIEmbeddings(
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                api_key=os.getenv("AZURE_OPENAI_KEY"),
                azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
                api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
                openai_api_type="azure"
            )
            
            self.llm = AzureChatOpenAI(
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                api_key=os.getenv("AZURE_OPENAI_KEY"),
                azure_deployment=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT"),
                api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
                temperature=0
            )
            
            # Vector store setup
            self.use_azure_search = use_azure_search
            if use_azure_search:
                self.vector_store = AzureSearch(
                    azure_search_endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
                    azure_search_key=os.getenv("AZURE_SEARCH_KEY"),
                    index_name=os.getenv("AZURE_SEARCH_INDEX_NAME"),
                    embedding_function=self.embeddings.embed_query
                )
            else:
                self.vector_store = None  # Will be initialized when adding documents
            
            # Azure Speech setup
            self.speech_config = speechsdk.SpeechConfig(
                subscription=os.getenv("AZURE_SPEECH_KEY"),
                region=os.getenv("AZURE_SPEECH_REGION")
            )
            self.speech_config.speech_recognition_language = "en-US"
            
            # Text splitter
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len
            )
            
            logger.info("RAG Summarizer initialized successfully")
            
        except Exception as e:
            logger.error(f"Initialization error: {e}")
            raise
    
    def transcribe_audio_streaming(self, audio_path: str) -> str:
        """
        Transcribe audio file with streaming support for long files.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Transcribed text
        """
        try:
            audio_config = speechsdk.audio.AudioConfig(filename=audio_path)
            speech_recognizer = speechsdk.SpeechRecognizer(
                speech_config=self.speech_config,
                audio_config=audio_config
            )
            
            all_results = []
            done = False
            error_occurred = False
            
            def stop_cb(evt):
                nonlocal done
                done = True
            
            def recognized_cb(evt):
                if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
                    all_results.append(evt.result.text)
            
            def canceled_cb(evt):
                nonlocal done, error_occurred
                if evt.reason == speechsdk.CancellationReason.Error:
                    logger.error(f"Speech recognition error: {evt.error_details}")
                    error_occurred = True
                done = True
            
            speech_recognizer.recognized.connect(recognized_cb)
            speech_recognizer.session_stopped.connect(stop_cb)
            speech_recognizer.canceled.connect(canceled_cb)
            
            speech_recognizer.start_continuous_recognition()
            
            import time
            timeout = 60
            elapsed = 0
            while not done and elapsed < timeout:
                time.sleep(0.5)
                elapsed += 0.5
            
            speech_recognizer.stop_continuous_recognition()
            
            if error_occurred or not all_results:
                return "Audio transcription failed. Please use WAV format (16kHz, mono, 16-bit PCM)."
            
            transcription = " ".join(all_results)
            logger.info(f"Audio transcribed: {len(transcription)} characters")
            return transcription
            
        except Exception as e:
            logger.error(f"Audio transcription error for {audio_path}: {e}")
            return "Audio transcription failed. Please use WAV format (16kHz, mono, 16-bit PCM)."
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF file."""
        try:
            reader = PdfReader(pdf_path)
            text = " ".join([page.extract_text() for page in reader.pages])
            logger.info(f"PDF extracted: {len(text)} characters")
            return text
        except Exception as e:
            logger.error(f"PDF extraction error for {pdf_path}: {e}")
            return ""
    
    def extract_text_from_docx(self, docx_path: str) -> str:
        """Extract text from DOCX file."""
        try:
            doc = DocxDocument(docx_path)
            text = " ".join([para.text for para in doc.paragraphs])
            logger.info(f"DOCX extracted: {len(text)} characters")
            return text
        except Exception as e:
            logger.error(f"DOCX extraction error for {docx_path}: {e}")
            return ""
    
    def extract_text_from_excel(self, excel_path: str) -> str:
        """Extract text from Excel file."""
        try:
            wb = load_workbook(excel_path, data_only=True)
            text_parts = []
            
            for sheet in wb.worksheets:
                text_parts.append(f"Sheet: {sheet.title}")
                for row in sheet.iter_rows(values_only=True):
                    row_text = " ".join([str(cell) for cell in row if cell is not None])
                    if row_text.strip():
                        text_parts.append(row_text)
            
            text = " ".join(text_parts)
            logger.info(f"Excel extracted: {len(text)} characters")
            return text
        except Exception as e:
            logger.error(f"Excel extraction error for {excel_path}: {e}")
            return ""
    
    def extract_text_from_pptx(self, pptx_path: str) -> str:
        """Extract text from PowerPoint file."""
        try:
            prs = Presentation(pptx_path)
            text_parts = []
            
            for slide_num, slide in enumerate(prs.slides, 1):
                text_parts.append(f"Slide {slide_num}:")
                for shape in slide.shapes:
                    if hasattr(shape, "text"):
                        text_parts.append(shape.text)
            
            text = " ".join(text_parts)
            logger.info(f"PPTX extracted: {len(text)} characters")
            return text
        except Exception as e:
            logger.error(f"PPTX extraction error for {pptx_path}: {e}")
            return ""
    
    def process_file(self, file_path: str) -> str:
        """
        Process any supported file type and extract text.
        
        Args:
            file_path: Path to file
            
        Returns:
            Extracted text
        """
        file_path = str(file_path)
        ext = Path(file_path).suffix.lower()
        
        extractors = {
            '.pdf': self.extract_text_from_pdf,
            '.docx': self.extract_text_from_docx,
            '.doc': self.extract_text_from_docx,
            '.xlsx': self.extract_text_from_excel,
            '.xls': self.extract_text_from_excel,
            '.pptx': self.extract_text_from_pptx,
            '.ppt': self.extract_text_from_pptx,
            '.mp3': self.transcribe_audio_streaming,
            '.wav': self.transcribe_audio_streaming,
            '.m4a': self.transcribe_audio_streaming,
            '.txt': lambda p: open(p, 'r', encoding='utf-8').read()
        }
        
        extractor = extractors.get(ext)
        if extractor:
            return extractor(file_path)
        else:
            logger.warning(f"Unsupported file type: {ext}")
            return ""
    
    def batch_process_files(self, file_paths: List[str]) -> List[Dict[str, str]]:
        """
        Process multiple files in batch.
        
        Args:
            file_paths: List of file paths
            
        Returns:
            List of dicts with file path and extracted text
        """
        results = []
        for file_path in file_paths:
            logger.info(f"Processing: {file_path}")
            text = self.process_file(file_path)
            results.append({
                'file_path': file_path,
                'text': text,
                'success': bool(text)
            })
        return results
    
    def add_to_vectorstore(self, text: str, metadata: Optional[Dict] = None):
        """
        Add text to vector store.
        
        Args:
            text: Text to add
            metadata: Optional metadata
        """
        try:
            if not text.strip():
                logger.warning("Empty text, skipping vectorstore addition")
                return
            
            chunks = self.text_splitter.split_text(text)
            documents = [
                Document(page_content=chunk, metadata=metadata or {})
                for chunk in chunks
            ]
            
            if self.use_azure_search:
                self.vector_store.add_documents(documents)
            else:
                if self.vector_store is None:
                    self.vector_store = FAISS.from_documents(documents, self.embeddings)
                else:
                    self.vector_store.add_documents(documents)
            
            logger.info(f"Added {len(documents)} chunks to vector store")
            
        except Exception as e:
            logger.error(f"Error adding to vector store: {e}")
            raise
    
    def batch_add_to_vectorstore(self, results: List[Dict[str, str]]):
        """
        Add multiple processed files to vector store.
        
        Args:
            results: List of processing results from batch_process_files
        """
        for result in results:
            if result['success']:
                metadata = {
                    'source': result['file_path'],
                    'filename': Path(result['file_path']).name
                }
                self.add_to_vectorstore(result['text'], metadata)
    
    def generate_summary(
        self,
        query: Optional[str] = None,
        k: int = 4,
        summary_type: str = "concise"
    ) -> str:
        """
        Generate summary from vector store.
        
        Args:
            query: Optional query to filter relevant documents
            k: Number of documents to retrieve
            summary_type: Type of summary ('concise', 'detailed', 'bullet_points')
            
        Returns:
            Generated summary
        """
        try:
            if self.vector_store is None:
                raise ValueError("Vector store is empty. Add documents first.")
            
            # Retrieve relevant documents
            if query:
                docs = self.vector_store.similarity_search(query, k=k)
            else:
                docs = self.vector_store.similarity_search("summary", k=k)
            
            if not docs:
                return "No relevant documents found."
            
            # Combine document content
            combined_text = "\n\n".join([doc.page_content for doc in docs])
            
            # Custom prompts based on summary type
            prompts = {
                "concise": "Write a concise summary of the following:\n\n{text}\n\nCONCISE SUMMARY:",
                "detailed": "Write a comprehensive and detailed summary of the following:\n\n{text}\n\nDETAILED SUMMARY:",
                "bullet_points": "Summarize the following in bullet points:\n\n{text}\n\nBULLET POINT SUMMARY:"
            }
            
            prompt_text = prompts.get(summary_type, prompts["concise"]).format(text=combined_text)
            
            # Generate summary using LLM
            response = self.llm.invoke(prompt_text)
            summary = response.content if hasattr(response, 'content') else str(response)
            
            logger.info("Summary generated successfully")
            return summary
            
        except Exception as e:
            logger.error(f"Summary generation error: {e}")
            raise
    
    def query_documents(self, query: str, k: int = 4) -> List[Document]:
        """
        Query vector store for relevant documents.
        
        Args:
            query: Search query
            k: Number of results
            
        Returns:
            List of relevant documents
        """
        try:
            if self.vector_store is None:
                raise ValueError("Vector store is empty. Add documents first.")
            
            docs = self.vector_store.similarity_search(query, k=k)
            logger.info(f"Found {len(docs)} relevant documents")
            return docs
            
        except Exception as e:
            logger.error(f"Query error: {e}")
            raise
    
    def save_vectorstore(self, path: str = "faiss_index"):
        """Save FAISS vector store to disk."""
        if not self.use_azure_search and self.vector_store:
            self.vector_store.save_local(path)
            logger.info(f"Vector store saved to {path}")
        else:
            logger.warning("Save only available for FAISS vector store")
    
    def load_vectorstore(self, path: str = "faiss_index"):
        """Load FAISS vector store from disk."""
        if not self.use_azure_search:
            self.vector_store = FAISS.load_local(
                path,
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            logger.info(f"Vector store loaded from {path}")
        else:
            logger.warning("Load only available for FAISS vector store")
