# RAG Pipeline for Audio and Document Summarization

Complete RAG (Retrieval-Augmented Generation) pipeline using LangChain and Microsoft Azure for extracting summaries from audio files and documents.

## Features

✅ **Multiple Document Types**: PDF, DOCX, XLSX, PPTX, TXT  
✅ **Audio Processing**: MP3, WAV, M4A with streaming support  
✅ **Batch Processing**: Process multiple files at once  
✅ **Error Handling**: Comprehensive error handling and logging  
✅ **Flexible Storage**: Azure AI Search or FAISS vector store  
✅ **Multiple Summary Types**: Concise, detailed, or bullet points  
✅ **Query Support**: Search for specific information  
✅ **CLI Tool**: Easy command-line interface  

## Prerequisites

- Python 3.8+
- Azure OpenAI account with deployed models
- Azure Speech Services account
- (Optional) Azure AI Search account

## Installation

1. **Clone or download this folder**

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**:
```bash
# Copy the example file
copy .env.example .env

# Edit .env with your Azure credentials
```

## Azure Setup

### 1. Azure OpenAI
- Create Azure OpenAI resource
- Deploy models:
  - `text-embedding-ada-002` (for embeddings)
  - `gpt-4` or `gpt-35-turbo` (for summarization)
- Copy endpoint and key to `.env`

### 2. Azure Speech Services
- Create Speech Services resource
- Copy key and region to `.env`

### 3. Azure AI Search (Optional)
- Create Azure AI Search resource
- Copy endpoint and key to `.env`
- Or use FAISS (local, no setup needed)

## Quick Start

### Python API

```python
from rag_summarizer import RAGSummarizer

# Initialize
summarizer = RAGSummarizer(use_azure_search=False)

# Process a single file
text = summarizer.process_file("document.pdf")
summarizer.add_to_vectorstore(text, metadata={"source": "document.pdf"})

# Generate summary
summary = summarizer.generate_summary(summary_type="concise")
print(summary)
```

### Command Line

```bash
# Process single file
python cli.py document.pdf

# Process multiple files
python cli.py report.pdf meeting.mp3 data.xlsx

# Query specific information
python cli.py document.pdf --query "What are the key findings?"

# Generate detailed summary
python cli.py document.pdf --summary-type detailed

# Save index for later use
python cli.py document.pdf --save-index my_index

# Load existing index
python cli.py --load-index my_index --query "Summary please"
```

## Usage Examples

### 1. Single File Processing

```python
from rag_summarizer import RAGSummarizer

summarizer = RAGSummarizer(use_azure_search=False)

# Process PDF
text = summarizer.process_file("report.pdf")
summarizer.add_to_vectorstore(text, metadata={"source": "report.pdf"})

# Generate summary
summary = summarizer.generate_summary(summary_type="bullet_points")
print(summary)
```

### 2. Batch Processing

```python
files = [
    "documents/report1.pdf",
    "documents/report2.docx",
    "audio/meeting.mp3"
]

# Process all files
results = summarizer.batch_process_files(files)
summarizer.batch_add_to_vectorstore(results)

# Generate summary
summary = summarizer.generate_summary(summary_type="detailed")
```

### 3. Audio Transcription

```python
# Transcribe audio with streaming (for long files)
transcription = summarizer.transcribe_audio_streaming("meeting.mp3")

# Add to vector store
summarizer.add_to_vectorstore(
    transcription,
    metadata={"source": "meeting.mp3", "type": "audio"}
)

# Summarize
summary = summarizer.generate_summary(
    query="What were the action items?",
    summary_type="bullet_points"
)
```

### 4. Query Specific Information

```python
# Add documents
results = summarizer.batch_process_files(["doc1.pdf", "doc2.pdf"])
summarizer.batch_add_to_vectorstore(results)

# Query for specific topic
summary = summarizer.generate_summary(
    query="What are the financial projections?",
    k=5
)

# Get raw relevant documents
docs = summarizer.query_documents("financial projections", k=3)
for doc in docs:
    print(doc.page_content)
```

### 5. Save and Load Index

```python
# Process and save
summarizer.process_file("document.pdf")
summarizer.save_vectorstore("my_index")

# Later, load and use
new_summarizer = RAGSummarizer(use_azure_search=False)
new_summarizer.load_vectorstore("my_index")
summary = new_summarizer.generate_summary()
```

### 6. Use Azure AI Search

```python
# Use Azure AI Search instead of FAISS
summarizer = RAGSummarizer(use_azure_search=True)

# Everything else works the same
results = summarizer.batch_process_files(files)
summarizer.batch_add_to_vectorstore(results)
summary = summarizer.generate_summary()
```

## CLI Examples

```bash
# Basic usage
python cli.py document.pdf

# Multiple files with query
python cli.py doc1.pdf doc2.docx audio.mp3 --query "key findings"

# Detailed bullet point summary
python cli.py report.pdf --summary-type bullet_points

# Process and save index
python cli.py doc1.pdf doc2.pdf --save-index project_docs

# Use saved index
python cli.py --load-index project_docs --query "summary"

# Use Azure Search
python cli.py document.pdf --azure-search

# Retrieve more chunks
python cli.py document.pdf --top-k 10
```

## Supported File Types

| Type | Extensions | Notes |
|------|-----------|-------|
| PDF | .pdf | Text extraction |
| Word | .docx, .doc | Full text support |
| Excel | .xlsx, .xls | All sheets extracted |
| PowerPoint | .pptx, .ppt | Slide text extraction |
| Audio | .mp3, .wav, .m4a | Streaming transcription |
| Text | .txt | Direct reading |

## Summary Types

- **concise**: Short, high-level summary
- **detailed**: Comprehensive summary with details
- **bullet_points**: Key points in bullet format

## Architecture

```
User Files (PDF, Audio, etc.)
    ↓
Text Extraction / Transcription
    ↓
Text Chunking (1000 chars, 200 overlap)
    ↓
Azure OpenAI Embeddings
    ↓
Vector Store (FAISS or Azure AI Search)
    ↓
Similarity Search
    ↓
Azure OpenAI Summarization
    ↓
Final Summary
```

## Error Handling

The pipeline includes comprehensive error handling:
- File processing errors are logged but don't stop batch processing
- Empty or invalid files are skipped
- Network errors are caught and reported
- All operations are logged for debugging

## Performance Tips

1. **Batch Processing**: Process multiple files at once for efficiency
2. **Save Indexes**: Save vector stores to avoid reprocessing
3. **Adjust Chunk Size**: Modify `chunk_size` for your use case
4. **Use Azure Search**: For production/large-scale deployments
5. **Streaming Audio**: Automatically handles long audio files

## Troubleshooting

### "No module named 'langchain'"
```bash
pip install -r requirements.txt
```

### "Azure OpenAI authentication failed"
- Check your `.env` file has correct credentials
- Verify endpoint URL format
- Ensure API key is valid

### "Audio transcription failed"
- Check audio file format is supported
- Verify Azure Speech key and region
- Ensure audio file is not corrupted

### "Vector store is empty"
- Make sure to add documents before generating summary
- Check if file processing succeeded (check logs)

## Advanced Configuration

### Custom Chunk Size

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

summarizer.text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1500,
    chunk_overlap=300
)
```

### Custom Prompts

```python
from langchain.prompts import PromptTemplate

custom_prompt = PromptTemplate(
    template="Summarize this for executives:\n\n{text}\n\nSUMMARY:",
    input_variables=["text"]
)
```

### Different Languages

```python
# For audio transcription
summarizer.speech_config.speech_recognition_language = "es-ES"  # Spanish
```

## License

MIT License - feel free to use in your projects!

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review Azure service status
3. Check logs for detailed error messages
