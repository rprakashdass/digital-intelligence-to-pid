# RAG System Dependencies Guide

The Retrieval-Augmented Generation (RAG) system in the P&ID Analyzer requires additional dependencies beyond the core application. This guide helps you ensure all necessary components are properly installed.

## Required Dependencies

The RAG system requires the following Python packages:

1. **sentence-transformers**: For embedding text and enabling semantic search
   ```bash
   pip install sentence-transformers
   ```

2. **numpy**: For numerical operations (usually installed with other packages)
   ```bash
   pip install numpy
   ```

3. **openai**: Optional, for enhanced responses using OpenAI models
   ```bash
   pip install openai
   ```

## Verifying Installations

You can verify all dependencies are correctly installed by running:

```bash
python backend/check_dependencies.py
```

This script will:
- Check for all required dependencies
- Offer to install any missing packages
- Verify PyTorch installation (for YOLO detection)
- Check external dependencies like Tesseract OCR

## Testing the RAG System

To test the RAG system without starting the full server:

```bash
python backend/test_minimal_rag.py
```

This script creates a simple test image, processes it through the analysis pipeline, and tests the RAG query functionality.

## Troubleshooting

### Common Issues

1. **Missing PyTorch**:
   - Error: `No module named 'torch'`
   - Solution: `pip install torch torchvision`

2. **Missing sentence-transformers**:
   - Error: `No module named 'sentence_transformers'`
   - Solution: `pip install sentence-transformers`

3. **Model Download Failures**:
   If you're behind a firewall or have limited internet access, the sentence-transformers library might fail to download its model. In this case:
   - The system will fall back to keyword-based search
   - You'll see a warning about the embedding model not being available

### Fallback Mechanisms

The RAG system includes multiple fallback mechanisms:

1. If sentence-transformers fails to load, it falls back to keyword-based search
2. If OpenAI API is not configured, it uses a rule-based response generator
3. If all else fails, it provides a simple summary of the diagram contents

## OpenAI Integration (Optional)

To enable enhanced responses using OpenAI models:

1. Set your API key:
   ```bash
   # Windows
   set OPENAI_API_KEY=your-api-key-here

   # Linux/Mac
   export OPENAI_API_KEY=your-api-key-here
   ```

2. The system will automatically use OpenAI when available, falling back to local processing when not available.

## Custom Knowledge Base

The knowledge base file is located at:
```
backend/data/knowledge_base.json
```

You can customize this file with domain-specific knowledge about:
- Instrument tags
- Equipment
- Process logic
- Safety systems
- Common issues

The system will automatically use this knowledge to answer queries about the P&ID diagrams.
