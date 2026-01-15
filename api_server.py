from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import tempfile
from openai import AzureOpenAI
import numpy as np
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize Azure OpenAI client
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version="2023-05-15",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

# Simple in-memory vector store
documents = []

def get_embedding(text):
    """Get embedding for text"""
    response = client.embeddings.create(
        model=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
        input=text
    )
    return response.data[0].embedding

def cosine_similarity(a, b):
    """Calculate cosine similarity"""
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "RAG Pipeline"}), 200

@app.route('/process', methods=['POST'])
def process_file():
    """Process uploaded file and return summary"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        summary_type = request.form.get('summary_type', 'concise')
        query = request.form.get('query', None)
        
        print(f"Processing file: {file.filename}")
        
        # Save and read file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
            file.save(tmp.name)
            tmp_path = tmp.name
        
        # Process based on file type
        from rag_summarizer import RAGSummarizer
        print("Initializing summarizer...")
        summarizer = RAGSummarizer(use_azure_search=False)
        print(f"Processing file with extension: {os.path.splitext(file.filename)[1]}")
        text = summarizer.process_file(tmp_path)
        print(f"Extracted text length: {len(text) if text else 0}")
        
        if not text:
            os.unlink(tmp_path)
            return jsonify({"error": f"Could not extract text from {file.filename}. Check server logs."}), 200
        
        print(f"Text extracted: {len(text)} chars")
        
        # Split into chunks
        chunk_size = 1000
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        
        print(f"Creating embeddings for {len(chunks)} chunks...")
        # Store chunks with embeddings
        for chunk in chunks:
            embedding = get_embedding(chunk)
            documents.append({
                "text": chunk,
                "embedding": embedding,
                "source": file.filename
            })
        
        print("Generating summary...")
        # Get relevant chunks
        if query:
            query_embedding = get_embedding(query)
            similarities = [cosine_similarity(query_embedding, doc["embedding"]) for doc in documents]
            top_indices = np.argsort(similarities)[-3:][::-1]
            relevant_text = "\n\n".join([documents[i]["text"] for i in top_indices])
            prompt = f"Answer this question based on the text: {query}\n\nText:\n{relevant_text}\n\nANSWER:"
        else:
            relevant_text = "\n\n".join([doc["text"] for doc in documents[-3:]])
            prompts = {
                "concise": f"Write a concise summary:\n\n{relevant_text}\n\nSUMMARY:",
                "detailed": f"Write a detailed summary:\n\n{relevant_text}\n\nSUMMARY:",
                "bullet_points": f"Summarize in bullet points:\n\n{relevant_text}\n\nSUMMARY:"
            }
            prompt = prompts.get(summary_type, prompts["concise"])
        
        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT"),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        summary = response.choices[0].message.content
        
        os.unlink(tmp_path)
        
        print("Success!")
        return jsonify({
            "filename": file.filename,
            "summary": summary,
            "summary_type": summary_type
        })
    
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 200

@app.route('/query', methods=['POST'])
def query_documents():
    """Query existing documents"""
    try:
        data = request.json
        query = data.get('query', '')
        k = data.get('k', 5)
        
        if not documents:
            return jsonify({"error": "No documents in store"}), 200
        
        query_embedding = get_embedding(query)
        similarities = [cosine_similarity(query_embedding, doc["embedding"]) for doc in documents]
        top_indices = np.argsort(similarities)[-k:][::-1]
        
        results = [{
            "content": documents[i]["text"],
            "metadata": {"source": documents[i]["source"]}
        } for i in top_indices]
        
        return jsonify({"results": results})
    
    except Exception as e:
        print(f"ERROR: {e}")
        return jsonify({"error": str(e)}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
