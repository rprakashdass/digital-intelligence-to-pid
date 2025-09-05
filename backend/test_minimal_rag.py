"""
Minimal working example for P&ID Analyzer RAG functionality

This script creates a simple test image, processes it, and tests the RAG functionality
without requiring the full FastAPI server to be running.
"""

import os
import sys
import json
import uuid
from PIL import Image, ImageDraw

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_test_image():
    """Create a simple test image with a tank and valve."""
    print("Creating test image...")
    
    # Create a blank image
    width, height = 800, 600
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # Draw a tank (rectangle)
    draw.rectangle([(100, 100), (300, 400)], outline='black', width=3)
    
    # Draw a valve (circle)
    draw.ellipse([(500, 200), (600, 300)], outline='black', width=3)
    
    # Draw a line connecting them
    draw.line([(300, 250), (500, 250)], fill='black', width=3)
    
    # Add some text
    draw.text((150, 250), "TANK-101", fill='black')
    draw.text((520, 250), "V-102", fill='black')
    
    # Save the image
    temp_dir = "temp_images"
    os.makedirs(temp_dir, exist_ok=True)
    
    image_id = str(uuid.uuid4())
    image_path = os.path.join(temp_dir, f"{image_id}.png")
    
    image.save(image_path)
    print(f"Test image saved as {image_path}")
    
    return image_path, image_id

def run_minimal_rag_example():
    """Run a minimal working example for the RAG functionality."""
    try:
        print("=" * 50)
        print("P&ID Analyzer RAG Minimal Working Example")
        print("=" * 50)
        
        # Check for required dependencies
        try:
            import cv2
            import numpy as np
            from backend.models import Graph, Node, Edge, Text, BoundingBox
            from backend.services import symbols, ocr, lines, graph, rag
            print("✅ All basic dependencies imported successfully")
        except ImportError as e:
            print(f"❌ Error importing required dependencies: {e}")
            print("Please run check_dependencies.py to install missing dependencies.")
            return False
        
        # Create a test image
        image_path, image_id = create_test_image()
        
        print("\nProcessing image...")
        # Detect symbols
        print("Detecting symbols...")
        try:
            # Try YOLO first
            try:
                import torch
                from backend.services import yolo_symbols
                detection_result = yolo_symbols.detect_symbols_yolo(image_path)
                print("✅ YOLO symbol detection completed")
            except (ImportError, Exception) as e:
                print(f"⚠️ YOLO detection failed: {e}")
                print("Falling back to template matching...")
                detection_result = symbols.detect_symbols(image_path)
                print("✅ Template matching completed")
        except Exception as e:
            print(f"❌ Symbol detection failed: {e}")
            return False
        
        detected_symbols = detection_result["nodes"]
        symbol_issues = detection_result["issues"]
        
        print(f"Detected {len(detected_symbols)} symbols")
        
        # Perform OCR
        print("\nPerforming OCR...")
        try:
            texts = ocr.ocr_image(image_path)
            print(f"✅ OCR completed, found {len(texts)} text elements")
        except Exception as e:
            print(f"❌ OCR failed: {e}")
            return False
        
        # Extract lines and junctions
        print("\nExtracting lines and junctions...")
        try:
            line_edges, junction_nodes = lines.extract_lines_and_junctions(image_path)
            print(f"✅ Line extraction completed, found {len(line_edges)} lines and {len(junction_nodes)} junctions")
        except Exception as e:
            print(f"❌ Line extraction failed: {e}")
            return False
        
        # Assemble graph
        print("\nAssembling graph...")
        try:
            analysis_graph = graph.assemble_graph(detected_symbols, line_edges, junction_nodes, texts)
            print(f"✅ Graph assembled with {len(analysis_graph.nodes)} nodes, {len(analysis_graph.edges)} edges, and {len(analysis_graph.texts)} texts")
        except Exception as e:
            print(f"❌ Graph assembly failed: {e}")
            return False
        
        # Test RAG query
        print("\nTesting RAG query...")
        test_query = "What equipment is shown in this diagram?"
        
        try:
            # Test sentence-transformers
            try:
                from sentence_transformers import SentenceTransformer
                print("✅ sentence-transformers imported successfully")
            except ImportError:
                print("⚠️ sentence-transformers not installed, RAG will use fallback mode")
            
            # Process query
            try:
                rag_response = rag.answer_pid_query(test_query, analysis_graph)
                print("✅ RAG query processed successfully")
                print(f"\nQuery: {test_query}")
                print(f"Answer: {rag_response['answer']}")
                print(f"Confidence: {rag_response.get('confidence', 'N/A')}")
                
                if 'knowledge_sources' in rag_response and rag_response['knowledge_sources']:
                    print("\nKnowledge sources used:")
                    for source in rag_response['knowledge_sources']:
                        print(f"  - {source.get('type', 'unknown')}: {source.get('key', 'unknown')}")
                
                return True
            except Exception as e:
                print(f"❌ RAG query processing failed: {e}")
                import traceback
                traceback.print_exc()
                return False
            
        except Exception as e:
            print(f"❌ RAG functionality failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_minimal_rag_example()
    
    if success:
        print("\n" + "=" * 50)
        print("✅ RAG minimal example completed successfully!")
        print("The system appears to be working correctly.")
    else:
        print("\n" + "=" * 50)
        print("❌ RAG minimal example failed.")
        print("Please check the error messages above and install any missing dependencies.")
        print("You can run check_dependencies.py to verify all dependencies are installed.")
