# RAG Service Troubleshooting Guide

## Common Issues and Solutions

### 1. "500 Internal Server Error" on `/query` Endpoint

This error occurs when the RAG service encounters an exception during processing.

#### Solutions:

1. **Check Dependencies**
   ```bash
   cd backend
   pip install sentence-transformers openai numpy
   ```

2. **Verify Knowledge Base**
   Make sure the knowledge base file exists and is valid:
   ```
   backend/data/knowledge_base.json
   ```

3. **Use Fallback Mode**
   The RAG service now includes a fallback mode that provides basic responses even when the full RAG system fails.

4. **Check Model Availability**
   If the sentence-transformers model fails to load, the service will fall back to keyword-based retrieval.

### 2. "Image with ID X not found" Error

This error occurs when the specified image_id does not exist in the temp_images directory.

#### Solutions:

1. **Upload a New Image**
   Use the `/upload` endpoint to upload a new image before using `/query`.

2. **Check Image ID**
   Ensure you're using the correct image_id returned from the upload endpoint.

### 3. Frontend "Loading..." Issues

If the frontend gets stuck in a loading state while querying:

#### Solutions:

1. **Check CORS Headers**
   The backend includes CORS headers to allow cross-origin requests.

2. **Verify Frontend Configuration**
   Ensure the frontend is configured to use the correct backend URL:
   ```
   http://localhost:8000
   ```

3. **Check Browser Console**
   Look for network errors or JavaScript exceptions in the browser console.

### 4. Sentence Transformer Model Issues

If you see errors related to the sentence-transformers model:

#### Solutions:

1. **Install Specific Version**
   ```bash
   pip install sentence-transformers==2.2.2
   ```

2. **Check for PyTorch**
   ```bash
   pip install torch
   ```

3. **Download Model Manually**
   The model 'all-MiniLM-L6-v2' should be downloaded automatically, but can be manually downloaded if needed.

### 5. OpenAI API Integration

If using the OpenAI integration for enhanced responses:

#### Solutions:

1. **Set API Key**
   ```bash
   # Windows
   set OPENAI_API_KEY=your-api-key

   # Linux/Mac
   export OPENAI_API_KEY=your-api-key
   ```

2. **Use Fallback Mode**
   If no API key is set, the service will use its built-in fallback response generator.

## Testing and Debugging

### Test Scripts

1. **Test RAG Dependencies**
   ```bash
   python backend/test_rag_deps.py
   ```

2. **Test RAG Query**
   ```bash
   python backend/test_rag_query.py
   ```

### Debug Logging

Enhanced logging has been added to the RAG service to provide better debugging information. Check the server logs for details about:

- Model loading
- Knowledge base access
- Query processing
- Error tracebacks

## Advanced Configurations

### Knowledge Base Customization

You can customize the knowledge base by editing:
```
backend/data/knowledge_base.json
```

The structure includes:
- instrument_tags
- equipment
- process_logic
- safety_systems
- common_issues

### Embedding Model Selection

You can change the embedding model in the RAG service:

```python
# backend/services/rag.py
self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
```

Smaller models will load faster but may provide less accurate semantic search results.
