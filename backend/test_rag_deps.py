"""
Test script to check if all necessary dependencies for the RAG service are installed
"""

print("Testing RAG dependencies...")

try:
    import numpy as np
    print("✅ numpy is installed")
except ImportError:
    print("❌ numpy is not installed. Run: pip install numpy")

try:
    from sentence_transformers import SentenceTransformer
    print("✅ sentence_transformers is installed")
except ImportError:
    print("❌ sentence_transformers is not installed. Run: pip install sentence-transformers")

try:
    import openai
    print("✅ openai is installed")
except ImportError:
    print("❌ openai is not installed. Run: pip install openai")

# Check specific version of sentence_transformers
try:
    import sentence_transformers
    print(f"sentence_transformers version: {sentence_transformers.__version__}")
except Exception as e:
    print(f"Error checking sentence_transformers version: {e}")

# Check if the model can be loaded
try:
    print("Attempting to load sentence transformer model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("✅ SentenceTransformer model loaded successfully")
    
    # Test encoding
    test_text = "This is a test sentence for encoding"
    print(f"Encoding test text: '{test_text}'")
    embedding = model.encode(test_text)
    print(f"✅ Encoding successful. Embedding shape: {embedding.shape}")
except Exception as e:
    print(f"❌ Error loading or using SentenceTransformer model: {e}")
    import traceback
    traceback.print_exc()

print("\nTesting Knowledge Base...")
import os
import json

kb_path = "backend/data/knowledge_base.json"
print(f"Looking for knowledge base at: {kb_path}")

if os.path.exists(kb_path):
    print(f"✅ Knowledge base file found at {kb_path}")
    try:
        with open(kb_path, 'r', encoding='utf-8') as f:
            kb_data = json.load(f)
            print(f"✅ Knowledge base loaded successfully")
            print(f"Knowledge base contains:")
            for key, value in kb_data.items():
                print(f"  - {key}: {len(value)} entries")
    except Exception as e:
        print(f"❌ Error loading knowledge base: {e}")
else:
    print(f"❌ Knowledge base file not found at {kb_path}")
