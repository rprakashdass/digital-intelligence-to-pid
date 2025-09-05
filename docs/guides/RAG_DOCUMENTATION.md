# RAG (Retrieval-Augmented Generation) for P&ID Analysis

## Overview

The RAG system enables natural language queries about P&ID diagrams, providing intelligent answers by combining extracted diagram data with a comprehensive knowledge base of industrial instrumentation and process equipment.

## Features

### 🤖 **Intelligent Q&A**
- Ask natural language questions about P&ID diagrams
- Get contextual answers based on extracted symbols, text, and process logic
- Confidence scoring for response reliability

### 📹 **Video Support**
- Upload video files (MP4, AVI, MOV, MKV, WebM, GIF)
- Automatic frame extraction with quality assessment
- Process best frame through analysis pipeline

### 🧠 **Knowledge Base**
- 50+ ISA-5.1 instrument tags and equipment types
- Process logic and control strategies
- Safety systems and common issues
- Extensible JSON-based knowledge structure

### 🔍 **Smart Retrieval**
- Semantic similarity search using sentence transformers
- Keyword fallback for basic matching
- Context-aware response generation

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Query   │───▶│   RAG Service    │───▶│   LLM Response  │
│                │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │  Knowledge Base  │
                       │   + Embeddings   │
                       └──────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │  P&ID Analysis   │
                       │  (Symbols/Text)  │
                       └──────────────────┘
```

## API Endpoints

### Video Upload
```http
POST /upload/video
Content-Type: multipart/form-data

Body: video file (MP4, AVI, MOV, MKV, WebM, GIF)
```

**Response:**
```json
{
  "video_id": "uuid",
  "filename": "video.mp4",
  "content_type": "video/mp4",
  "frame_extracted": true,
  "frame_path": "/path/to/extracted/frame.png"
}
```

### RAG Query
```http
POST /query
Content-Type: application/json

{
  "image_id": "uuid",
  "query": "What does FIC-101 do?"
}
```

**Response:**
```json
{
  "query": "What does FIC-101 do?",
  "answer": "FIC-101 is a Flow Indicating Controller that measures and controls flow rate...",
  "confidence": 0.85,
  "knowledge_sources": [
    {
      "type": "instrument_tag",
      "key": "FIC",
      "similarity": 0.92
    }
  ],
  "analysis_summary": {
    "symbols_detected": 12,
    "text_elements": 8,
    "issues_found": 2
  }
}
```

### Knowledge Base Info
```http
GET /knowledge-base/info
```

**Response:**
```json
{
  "instrument_tags": 10,
  "equipment": 6,
  "process_logic": 4,
  "safety_systems": 2,
  "common_issues": 4,
  "embedding_model_loaded": true
}
```

## Knowledge Base Structure

The knowledge base is stored in `backend/data/knowledge_base.json` with the following structure:

### Instrument Tags
```json
{
  "instrument_tags": {
    "FIC": {
      "description": "Flow Indicating Controller - Measures and controls flow rate",
      "function": "Flow control loop with indication",
      "typical_use": "Process flow regulation, feed control, product flow control",
      "components": ["Flow transmitter", "Controller", "Control valve"],
      "fault_modes": ["Flow measurement drift", "Valve sticking", "Controller tuning issues"]
    }
  }
}
```

### Equipment
```json
{
  "equipment": {
    "pump": {
      "description": "Centrifugal or positive displacement pump for fluid transfer",
      "function": "Fluid transportation and pressure increase",
      "typical_use": "Process fluid transfer, circulation, boosting",
      "types": ["Centrifugal", "Positive displacement", "Gear", "Screw"],
      "fault_modes": ["Cavitation", "Bearing failure", "Seal leakage", "Motor failure"]
    }
  }
}
```

### Process Logic
```json
{
  "process_logic": {
    "flow_control": {
      "description": "Control system to maintain desired flow rate",
      "components": ["Flow sensor", "Controller", "Control valve"],
      "control_strategy": "Feedback control with flow measurement",
      "tuning_parameters": ["Proportional gain", "Integral time", "Derivative time"],
      "common_issues": ["Oscillation", "Slow response", "Steady-state error"]
    }
  }
}
```

## Usage Examples

### 1. Basic Query
```python
from services.rag import RAGService
from models import Graph

# Initialize RAG service
rag = RAGService()

# Load analyzed P&ID graph
graph = load_analyzed_pid()

# Ask a question
response = rag.answer_query("What does FIC-101 do?", graph)
print(response['answer'])
```

### 2. Video Processing
```python
from services.video import VideoProcessor

# Initialize video processor
processor = VideoProcessor()

# Process video and extract best frame
result = processor.process_video_for_analysis("video.mp4")

if result['success']:
    frame_path = result['frame_path']
    # Process frame through P&ID analysis pipeline
```

### 3. Frontend Integration
```javascript
// Upload video
const formData = new FormData();
formData.append('file', videoFile);
const response = await fetch('/upload/video', {
  method: 'POST',
  body: formData
});

// Ask question
const queryResponse = await fetch('/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    image_id: response.image_id,
    query: "What does FIC-101 do?"
  })
});
```

## Example Queries

### Instrument-Specific Questions
- "What does FIC-101 do?"
- "Explain the function of the pressure controller"
- "What type of instrument is PIC-201?"

### Equipment Questions
- "What is the purpose of the pump in this diagram?"
- "Describe the heat exchanger function"
- "What safety systems are present?"

### Process Questions
- "What type of control system is used?"
- "Describe the process flow"
- "Are there any issues with this P&ID?"

### Troubleshooting Questions
- "What could cause problems with the flow control?"
- "What maintenance issues should I watch for?"
- "Are there any safety concerns?"

## Configuration

### Environment Variables
```bash
# Optional: OpenAI API key for enhanced responses
export OPENAI_API_KEY="your-api-key-here"

# Optional: Custom Tesseract path
export TESSERACT_PATH="/path/to/tesseract"
```

### Dependencies
```bash
pip install sentence-transformers openai
```

## Testing

Run the test suite to verify RAG functionality:

```bash
cd backend
python test_rag.py
```

**Expected Output:**
```
🤖 Testing RAG (Retrieval-Augmented Generation) System
============================================================

📊 Sample P&ID Analysis:
   - Symbols detected: 4
   - Text elements: 3
   - Issues found: 1

❓ Query 1: What does FIC-101 do?
--------------------------------------------------
💡 Answer: FIC-101 is a Flow Indicating Controller that measures and controls flow rate...
🎯 Confidence: 0.85
📚 Knowledge Sources:
   - instrument_tag: FIC (similarity: 0.92)
```

## Performance Optimization

### 1. Embedding Caching
- Embeddings are cached after first computation
- Reduces processing time for repeated queries

### 2. Model Selection
- Uses lightweight `all-MiniLM-L6-v2` model
- Balances accuracy with performance

### 3. Fallback Mechanisms
- Keyword search when embeddings unavailable
- Rule-based responses when LLM unavailable

## Extending the Knowledge Base

### Adding New Instrument Tags
```json
{
  "instrument_tags": {
    "NEW_TAG": {
      "description": "Description of the new instrument",
      "function": "Primary function",
      "typical_use": "Common applications",
      "components": ["Component 1", "Component 2"],
      "fault_modes": ["Common issue 1", "Common issue 2"]
    }
  }
}
```

### Adding New Equipment Types
```json
{
  "equipment": {
    "new_equipment": {
      "description": "Equipment description",
      "function": "Primary function",
      "typical_use": "Common applications",
      "types": ["Type 1", "Type 2"],
      "fault_modes": ["Fault 1", "Fault 2"]
    }
  }
}
```

## Troubleshooting

### Common Issues

1. **No embeddings generated**
   - Check if `sentence-transformers` is installed
   - Verify model download completed successfully

2. **Low confidence responses**
   - Expand knowledge base with more relevant entries
   - Improve query specificity
   - Check if extracted P&ID data is accurate

3. **Video processing fails**
   - Verify video format is supported
   - Check OpenCV installation
   - Ensure sufficient disk space for frame extraction

4. **LLM responses unavailable**
   - Check OpenAI API key configuration
   - Verify internet connectivity
   - System falls back to rule-based responses

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable detailed logging for RAG operations
```

## Future Enhancements

### Planned Features
- [ ] Multi-language support
- [ ] Custom knowledge base upload
- [ ] Advanced video frame selection
- [ ] Real-time query processing
- [ ] Integration with external knowledge sources
- [ ] Voice query support
- [ ] Query history and favorites

### Advanced RAG Features
- [ ] Context-aware follow-up questions
- [ ] Diagram modification suggestions
- [ ] Compliance checking against standards
- [ ] Automated report generation
- [ ] Integration with CAD systems

## Contributing

To contribute to the RAG system:

1. **Expand Knowledge Base**: Add new instrument tags, equipment types, or process logic
2. **Improve Retrieval**: Enhance similarity matching algorithms
3. **Add Languages**: Support for non-English queries and responses
4. **Optimize Performance**: Improve embedding generation and caching
5. **Test Coverage**: Add comprehensive test cases for edge scenarios

## License

This RAG system is part of the P&ID Digital Intelligence Platform and follows the same licensing terms as the main project.
