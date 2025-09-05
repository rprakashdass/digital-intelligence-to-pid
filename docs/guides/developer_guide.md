```markdown
# Developer Guide

## Overview

This guide is intended for developers who want to extend, modify, or integrate the P&ID Analyzer system. It covers the codebase organization, development setup, core concepts, and best practices for contributing to the project.

## Project Structure

```
/
├── backend/                # Python FastAPI backend
│   ├── main.py            # API entry point and route definitions
│   ├── models.py          # Pydantic data models
│   ├── setup_yolo.py      # YOLO setup and initialization
│   ├── data/              # Knowledge base and data files
│   ├── models/            # AI model files (YOLO, etc.)
│   └── services/          # Core service modules
│       ├── export.py      # Export functionality
│       ├── graph.py       # Graph construction
│       ├── lines.py       # Line detection 
│       ├── ocr.py         # Text recognition
│       ├── pdf.py         # PDF handling
│       ├── rag.py         # RAG query system
│       ├── symbols.py     # Template-based symbol detection
│       ├── tagging.py     # Tag parsing
│       ├── validate.py    # Validation rules
│       ├── video.py       # Video processing
│       └── yolo_symbols.py # YOLO-based symbol detection
├── frontend/              # React frontend
│   ├── app.js             # Application entry point
│   ├── index.html         # HTML template
│   ├── package.json       # NPM dependencies
│   ├── public/            # Static assets
│   └── src/               # React source code
├── docs/                  # Documentation
├── models/                # Shared model directory
├── data/                  # Shared data directory
│   ├── samples/           # Sample images
│   └── templates/         # Symbol templates
└── temp_images/           # Temporary storage for uploads
```

## Development Environment Setup

### Backend (Python)

1. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Set up YOLO (optional)**:
   ```bash
   python setup_yolo.py
   ```

4. **Run the development server**:
   ```bash
   cd ..
   python -m backend.main
   ```

### Frontend (React)

1. **Install dependencies**:
   ```bash
   cd frontend
   npm install
   # or if using pnpm
   pnpm install
   ```

2. **Run the development server**:
   ```bash
   npm run dev
   # or
   pnpm run dev
   ```

3. **Build for production**:
   ```bash
   npm run build
   # or
   pnpm run build
   ```

## Core Concepts

### Graph Model

The central data structure in the system is the `Graph` model, which represents the P&ID diagram as a network of nodes and edges:

```python
class Graph(BaseModel):
    nodes: List[Node] = []
    edges: List[Edge] = []
    texts: List[Text] = []
    issues: List[Issue] = []
```

- **Nodes**: Symbols in the diagram (equipment, instruments, junctions)
- **Edges**: Connections between nodes (process lines, signal lines)
- **Texts**: Text elements detected in the diagram
- **Issues**: Validation issues or warnings

### Analysis Pipeline

The analysis pipeline consists of these key stages:

1. **Symbol Detection**:
   - YOLO-based detection (`yolo_symbols.py`)
   - Template-based fallback (`symbols.py`)

2. **Text Recognition**:
   - OCR processing (`ocr.py`)
   - Text normalization and cleaning

3. **Line Detection**:
   - Edge detection (`lines.py`)
   - Line extraction and junction identification

4. **Graph Construction**:
   - Assembling nodes and edges (`graph.py`)
   - Text-to-symbol association
   - Tag parsing (`tagging.py`)

5. **Validation**:
   - Issue detection (`validate.py`)
   - Completeness and consistency checks

6. **Export**:
   - Format conversion (`export.py`)
   - DEXPI-lite JSON or CSV generation

### RAG System

The Retrieval-Augmented Generation (RAG) system (`rag.py`) handles natural language queries:

1. **Knowledge Base**: Structured information about P&ID components
2. **Embedding Model**: Converts queries to vector representations
3. **Retrieval**: Finds relevant knowledge items
4. **Context Generation**: Creates context from the diagram and retrieved knowledge
5. **Response Generation**: Produces natural language answers

## Extension Points

### Adding New Symbol Types

1. **Update the detection model**:
   - Train YOLO with new symbol classes, or
   - Add new templates for template matching

2. **Update the knowledge base**:
   - Add entries in `backend/data/knowledge_base.json`
   - Include descriptions and properties

3. **Update UI rendering**:
   - Add icon mapping in the frontend visualization

### Adding New Export Formats

1. Create a new function in `backend/services/export.py`:
   ```python
   def to_new_format(graph: Graph) -> str:
       # Convert graph to your format
       return formatted_output
   ```

2. Add a new case in the `/export` endpoint in `main.py`:
   ```python
   if request.format == "new_format":
       output = export.to_new_format(final_graph)
       return Response(content=output, media_type='application/...')
   ```

### Extending the RAG System

1. **Add knowledge entries**:
   - Extend `backend/data/knowledge_base.json` with new categories or entries

2. **Customize the response generation**:
   - Modify the `generate_response` function in `backend/services/rag.py`

3. **Add new query types**:
   - Implement specialized handlers for specific query categories

## API Integration

### RESTful API

Integrate with the system using its RESTful API:

```python
import requests

# Upload an image
with open('diagram.png', 'rb') as f:
    files = {'file': f}
    upload_response = requests.post('http://localhost:8000/upload', files=files)

image_id = upload_response.json()['image_id']

# Analyze the image
analyze_response = requests.post(
    'http://localhost:8000/analyze',
    json={'image_id': image_id}
)

results = analyze_response.json()

# Query the diagram
query_response = requests.post(
    'http://localhost:8000/query',
    json={'image_id': image_id, 'query': 'What does FIC-101 do?'}
)

answer = query_response.json()
```

### Frontend Integration

To embed the viewer in another application:

1. **Use the React components**:
   ```jsx
   import { DiagramViewer } from 'pid-analyzer/components';
   
   function App() {
     return (
       <DiagramViewer 
         imageUrl="path/to/image.png"
         analysisData={analysisResults}
       />
     );
   }
   ```

2. **Or use the vanilla JS API**:
   ```javascript
   import { renderDiagram } from 'pid-analyzer/vanilla';
   
   renderDiagram(
     document.getElementById('container'),
     'path/to/image.png',
     analysisResults
   );
   ```

## Testing

### Backend Tests

Run the backend tests:

```bash
cd backend
pytest
```

Write new tests:

```python
# test_symbols.py
def test_symbol_detection():
    from backend.services import symbols
    
    result = symbols.detect_symbols("data/samples/sample.png")
    
    assert len(result["nodes"]) > 0
    assert "issues" in result
```

### Frontend Tests

Run the frontend tests:

```bash
cd frontend
npm test
```

Write new component tests:

```jsx
// DiagramViewer.test.jsx
import { render, screen } from '@testing-library/react';
import DiagramViewer from './DiagramViewer';

test('renders diagram with overlays', () => {
  const mockData = {
    nodes: [{ id: 'node1', type: 'pump', bbox: { x: 100, y: 100, w: 50, h: 50 } }]
  };
  
  render(<DiagramViewer data={mockData} />);
  
  expect(screen.getByTestId('diagram-overlay')).toBeInTheDocument();
});
```

## Troubleshooting

### Common Issues

1. **YOLO Import Errors**:
   - Check if PyTorch is installed correctly
   - Verify CUDA compatibility if using GPU
   - The system will fall back to template matching

2. **OCR Quality Issues**:
   - Improve image resolution and contrast
   - Adjust the OCR confidence threshold
   - Add preprocessing steps for specific diagram types

3. **Missing Symbols**:
   - Check if the symbol is in the training data
   - Add templates for uncommon symbols
   - Adjust detection confidence thresholds

### Debugging Tips

1. **Enable Debug Logging**:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **Inspect Intermediate Results**:
   - Use the `/run/{type}` endpoint with specific analysis types
   - Save intermediate images during processing
   - Add visualization helpers for each pipeline stage

3. **Frontend Debugging**:
   - Use React DevTools for component inspection
   - Check browser console for API errors
   - Enable network request logging

## Performance Optimization

### Backend Optimization

1. **Batch Processing**:
   - Process multiple symbols in a single inference
   - Use threading for parallel OCR and detection

2. **Caching**:
   - Add response caching for repeated operations
   - Cache embedding vectors for RAG

3. **Image Processing**:
   - Resize large images before processing
   - Use region proposals to focus detection

### Frontend Optimization

1. **Lazy Loading**:
   - Load components on demand
   - Use React.lazy for code splitting

2. **Rendering Optimization**:
   - Use virtualized lists for large result sets
   - Optimize canvas rendering for large diagrams

3. **API Optimization**:
   - Implement pagination for large results
   - Add websocket support for real-time updates

## Deployment

### Docker Deployment

Build and run with Docker:

```bash
# Build the images
docker-compose build

# Run the services
docker-compose up
```

Configuration via environment variables:

```
YOLO_MODEL_PATH=models/yolov5s.pt
CONFIDENCE_THRESHOLD=0.5
MAX_UPLOAD_SIZE=10
```

### Production Considerations

1. **Security**:
   - Add authentication for API endpoints
   - Implement rate limiting
   - Validate and sanitize all inputs

2. **Scaling**:
   - Use load balancers for multiple instances
   - Separate model serving from API handling
   - Use object storage for uploaded files

3. **Monitoring**:
   - Add health check endpoints
   - Implement request logging
   - Set up alerts for errors and performance issues

## Contributing

### Contribution Guidelines

1. **Code Style**:
   - Follow PEP 8 for Python code
   - Use ESLint and Prettier for JavaScript/React
   - Write docstrings for all functions

2. **Pull Requests**:
   - Create feature branches from `develop`
   - Include tests for new functionality
   - Update documentation as needed
   - Reference related issues

3. **Issue Reporting**:
   - Use descriptive titles
   - Include steps to reproduce
   - Attach sample diagrams when relevant
   - Specify environment details

### Development Workflow

1. Fork the repository
2. Create a feature branch
3. Implement changes with tests
4. Submit a pull request
5. Address review feedback
6. Merge after approval

## Additional Resources

- [API Reference](../api/api_reference.md)
- [System Architecture](../architecture/system_overview.md)
- [RAG Documentation](../RAG_DOCUMENTATION.md)
- [YOLO Integration](../YOLO_INTEGRATION.md)

---

This developer guide provides a comprehensive overview of the P&ID Analyzer system for developers. For more information or assistance, please contact the project maintainers.
```
