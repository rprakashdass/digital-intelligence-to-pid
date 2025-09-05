"""
Test script to verify all imports work correctly.
"""

print("Testing imports...")

# Test main models
print("Importing from backend.models...")
try:
    from backend.models import Graph, Node, Edge, Text, BoundingBox, Issue
    print("✅ Successfully imported models!")
except Exception as e:
    print(f"❌ Error importing models: {e}")

# Test services
services = [
    "ocr", "symbols", "lines", "graph", "tagging", 
    "validate", "export", "rag", "video", "pdf", "yolo_symbols"
]

for service in services:
    print(f"Importing from backend.services.{service}...")
    try:
        module = __import__(f"backend.services.{service}", fromlist=["*"])
        print(f"✅ Successfully imported {service}!")
    except Exception as e:
        print(f"❌ Error importing {service}: {e}")

print("\nImport testing complete.")
