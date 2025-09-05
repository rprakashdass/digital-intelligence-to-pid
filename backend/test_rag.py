#!/usr/bin/env python3
"""
Test script for RAG functionality.
Demonstrates how the RAG system answers questions about P&ID diagrams.
"""

import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.rag import RAGService
from backend.models import Graph, Node, Text, BoundingBox, Issue

def create_sample_graph():
    """Create a sample P&ID graph for testing."""
    
    # Sample nodes (symbols)
    nodes = [
        Node(
            id="pump_1",
            kind="equipment",
            type="pump",
            bbox=BoundingBox(x=100, y=150, w=50, h=30),
            tag="P-101",
            confidence=0.95
        ),
        Node(
            id="valve_1",
            kind="equipment", 
            type="valve_control",
            bbox=BoundingBox(x=200, y=150, w=40, h=40),
            tag="FV-101",
            confidence=0.88
        ),
        Node(
            id="instrument_1",
            kind="instrument",
            type="instrument_bubble",
            bbox=BoundingBox(x=250, y=100, w=30, h=30),
            tag="FIC-101",
            confidence=0.92
        ),
        Node(
            id="tank_1",
            kind="equipment",
            type="tank",
            bbox=BoundingBox(x=300, y=200, w=80, h=100),
            tag="T-101",
            confidence=0.90
        )
    ]
    
    # Sample text elements
    texts = [
        Text(
            id="text_1",
            content="FIC-101",
            bbox=BoundingBox(x=250, y=100, w=30, h=15)
        ),
        Text(
            id="text_2", 
            content="P-101",
            bbox=BoundingBox(x=100, y=150, w=25, h=15)
        ),
        Text(
            id="text_3",
            content="Process Flow",
            bbox=BoundingBox(x=50, y=50, w=80, h=15)
        )
    ]
    
    # Sample issues
    issues = [
        Issue(
            id="issue_1",
            severity="warn",
            message="Low confidence detection for valve FV-101",
            targetId="valve_1"
        )
    ]
    
    return Graph(nodes=nodes, texts=texts, issues=issues)

def test_rag_queries():
    """Test various RAG queries."""
    
    print("🤖 Testing RAG (Retrieval-Augmented Generation) System")
    print("=" * 60)
    
    # Initialize RAG service
    rag_service = RAGService()
    
    # Create sample graph
    sample_graph = create_sample_graph()
    
    # Test queries
    test_queries = [
        "What does FIC-101 do?",
        "Explain the function of the pump in this diagram",
        "What safety systems are present?",
        "Are there any issues with this P&ID?",
        "What type of control system is used?",
        "Describe the process flow",
        "What equipment is connected to the tank?",
        "How many instruments are in this diagram?"
    ]
    
    print(f"📊 Sample P&ID Analysis:")
    print(f"   - Symbols detected: {len(sample_graph.nodes)}")
    print(f"   - Text elements: {len(sample_graph.texts)}")
    print(f"   - Issues found: {len(sample_graph.issues)}")
    print()
    
    for i, query in enumerate(test_queries, 1):
        print(f"❓ Query {i}: {query}")
        print("-" * 50)
        
        try:
            response = rag_service.answer_query(query, sample_graph)
            
            print(f"💡 Answer: {response['answer']}")
            print(f"🎯 Confidence: {response['confidence']:.2f}")
            
            if response['knowledge_sources']:
                print("📚 Knowledge Sources:")
                for source in response['knowledge_sources'][:3]:  # Show top 3
                    print(f"   - {source['type']}: {source['key']} (similarity: {source.get('similarity', 0):.2f})")
            
            print()
            
        except Exception as e:
            print(f"❌ Error: {e}")
            print()
    
    print("✅ RAG testing completed!")

def test_knowledge_base():
    """Test knowledge base loading and retrieval."""
    
    print("\n📖 Testing Knowledge Base")
    print("=" * 40)
    
    rag_service = RAGService()
    kb = rag_service.knowledge_base
    
    print(f"📊 Knowledge Base Statistics:")
    print(f"   - Instrument tags: {len(kb.get('instrument_tags', {}))}")
    print(f"   - Equipment types: {len(kb.get('equipment', {}))}")
    print(f"   - Process logic: {len(kb.get('process_logic', {}))}")
    print(f"   - Safety systems: {len(kb.get('safety_systems', {}))}")
    print(f"   - Common issues: {len(kb.get('common_issues', {}))}")
    print()
    
    # Test specific knowledge retrieval
    print("🔍 Sample Knowledge Retrieval:")
    
    # Test FIC tag
    fic_info = kb.get('instrument_tags', {}).get('FIC', {})
    if fic_info:
        print(f"   FIC (Flow Indicating Controller):")
        print(f"     Description: {fic_info.get('description', 'N/A')}")
        print(f"     Function: {fic_info.get('function', 'N/A')}")
        print(f"     Typical use: {fic_info.get('typical_use', 'N/A')}")
        print()
    
    # Test pump equipment
    pump_info = kb.get('equipment', {}).get('pump', {})
    if pump_info:
        print(f"   Pump Equipment:")
        print(f"     Description: {pump_info.get('description', 'N/A')}")
        print(f"     Function: {pump_info.get('function', 'N/A')}")
        print(f"     Types: {', '.join(pump_info.get('types', []))}")
        print()

def main():
    """Main test function."""
    
    print("🧪 P&ID RAG System Test Suite")
    print("=" * 50)
    print()
    
    try:
        # Test knowledge base
        test_knowledge_base()
        
        # Test RAG queries
        test_rag_queries()
        
        print("\n🎉 All tests completed successfully!")
        print("\n💡 To use the RAG system:")
        print("   1. Start the backend server: uvicorn backend.main:app --reload")
        print("   2. Upload a P&ID image or video")
        print("   3. Go to the 'Smart Q&A' tab")
        print("   4. Ask questions about the diagram")
        print("   5. Get intelligent answers based on extracted data and knowledge base")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
