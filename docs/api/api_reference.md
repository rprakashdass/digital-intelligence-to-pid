```markdown
# P&ID Analyzer API Reference

This document provides comprehensive documentation for the P&ID Analyzer API endpoints, request/response formats, and usage examples.

## Base URL

All API endpoints are relative to:

```
http://localhost:8000/
```

## Authentication

> **Note**: The current implementation does not include authentication. In a production environment, appropriate authentication mechanisms should be implemented.

## API Endpoints

### Health Check

```http
GET /health
```

Check if the API server is running.

**Response**:
```json
{
  "status": "ok"
}
```

### Upload Image

```http
POST /upload
Content-Type: multipart/form-data
```

Upload a P&ID image for analysis.

**Parameters**:
- `file`: The image file to upload (PNG, JPG, PDF)

**Response**:
```json
{
  "image_id": "606449c3-90db-41f2-8e5c-265c7d854ba2",
  "filename": "sample.png",
  "content_type": "image/png"
}
```

### Upload Video

```http
POST /upload/video
Content-Type: multipart/form-data
```

Upload a video file containing P&ID footage.

**Parameters**:
- `file`: The video file to upload (MP4, AVI, MOV, etc.)

**Response**:
```json
{
  "video_id": "7ec90ac3-b3ac-4b44-9ff3-0638eb870e1f",
  "filename": "pid_video.mp4",
  "content_type": "video/mp4",
  "frame_extracted": true,
  "frame_path": "/temp_images/7ec90ac3-b3ac-4b44-9ff3-0638eb870e1f.png"
}
```

### Analyze Image

```http
POST /analyze
Content-Type: application/json
```

Trigger full analysis on a previously uploaded image.

**Request**:
```json
{
  "image_id": "606449c3-90db-41f2-8e5c-265c7d854ba2",
  "options": {
    "detect_symbols": true,
    "detect_lines": true,
    "run_ocr": true,
    "validate": true
  }
}
```

**Response**:
```json
{
  "nodes": [
    {
      "id": "node_1",
      "kind": "equipment",
      "type": "pump",
      "bbox": {
        "x": 150,
        "y": 200,
        "w": 50,
        "h": 50
      },
      "confidence": 0.92,
      "tag": "P-101"
    },
    // More nodes...
  ],
  "edges": [
    {
      "id": "edge_1",
      "kind": "process",
      "from_node": "node_1",
      "to_node": "node_2",
      "polyline": [
        [150, 225],
        [300, 225]
      ]
    },
    // More edges...
  ],
  "texts": [
    {
      "id": "text_1",
      "content": "P-101",
      "bbox": {
        "x": 140,
        "y": 170,
        "w": 40,
        "h": 20
      }
    },
    // More texts...
  ],
  "issues": [
    {
      "id": "issue_1",
      "severity": "warning",
      "message": "Unlabeled equipment detected",
      "node_id": "node_3"
    },
    // More issues...
  ]
}
```

### Run Specific Analysis

```http
POST /run/{type}
Content-Type: application/json
```

Run a specific type of analysis on a previously uploaded image.

**Path Parameters**:
- `type`: Analysis type ("validate", "ocr", or "graph")

**Request**:
```json
{
  "image_id": "606449c3-90db-41f2-8e5c-265c7d854ba2"
}
```

**Response**: Same format as `/analyze` endpoint, but with only the relevant sections populated.

### Export Results

```http
POST /export
Content-Type: application/json
```

Export analysis results in the specified format.

**Request**:
```json
{
  "image_id": "606449c3-90db-41f2-8e5c-265c7d854ba2",
  "format": "json"  // or "csv"
}
```

**Response**: 
- For JSON: A JSON file with the analysis results in DEXPI-lite format
- For CSV: A ZIP file containing multiple CSV files for nodes, edges, and issues

### RAG Query

```http
POST /query
Content-Type: application/json
```

Submit a natural language query about a previously analyzed P&ID diagram.

**Request**:
```json
{
  "image_id": "606449c3-90db-41f2-8e5c-265c7d854ba2",
  "query": "What does FIC-101 do?"
}
```

**Response**:
```json
{
  "query": "What does FIC-101 do?",
  "answer": "FIC-101 is a Flow Indicating Controller that measures and controls the flow rate of the process fluid. In this diagram, it is connected to the control valve CV-101 which regulates the flow to the tank T-101.",
  "context_used": "Detected symbols and equipment:\n- pump (ID: node_1) with tag: P-101\n- control valve (ID: node_2) with tag: CV-101...",
  "knowledge_sources": [
    {
      "type": "instrument_tag",
      "key": "FIC",
      "similarity": 0.92
    }
  ],
  "confidence": 0.85
}
```

### YOLO Model Info

```http
GET /models/info
```

Get information about the currently loaded YOLO model for symbol detection.

**Response**:
```json
{
  "model_path": "models/yolov5s.pt",
  "conf_threshold": 0.5,
  "iou_threshold": 0.45,
  "loaded": true,
  "classes": ["pump", "valve_manual", "valve_control", "instrument_bubble", "tank"],
  "input_size": [640, 640],
  "device": "cpu"
}
```

### Load YOLO Model

```http
POST /models/load
Content-Type: application/json
```

Load a custom YOLO model for symbol detection.

**Request**:
```json
{
  "model_path": "models/custom_pid_model.pt",
  "conf_threshold": 0.6
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Model loaded from models/custom_pid_model.pt"
}
```

### Knowledge Base Info

```http
GET /knowledge-base/info
```

Get information about the RAG knowledge base.

**Response**:
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

## Error Handling

All API endpoints return appropriate HTTP status codes:

- `200 OK`: Request succeeded
- `400 Bad Request`: Invalid parameters or request format
- `404 Not Found`: Resource not found (e.g., image_id doesn't exist)
- `415 Unsupported Media Type`: Unsupported file format
- `500 Internal Server Error`: Server-side error

Error responses include a detail message:

```json
{
  "detail": "Error message describing the issue"
}
```

## Usage Examples

### Complete Analysis Pipeline

```bash
# 1. Upload an image
curl -X POST -F "file=@sample.png" http://localhost:8000/upload

# 2. Analyze the image
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"image_id":"606449c3-90db-41f2-8e5c-265c7d854ba2"}' \
  http://localhost:8000/analyze

# 3. Ask a question about the diagram
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"image_id":"606449c3-90db-41f2-8e5c-265c7d854ba2", "query":"What does FIC-101 do?"}' \
  http://localhost:8000/query

# 4. Export the results
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"image_id":"606449c3-90db-41f2-8e5c-265c7d854ba2", "format":"json"}' \
  -o results.json \
  http://localhost:8000/export
```

### Video Analysis

```bash
# 1. Upload a video
curl -X POST -F "file=@pid_video.mp4" http://localhost:8000/upload/video

# 2. Analyze the extracted frame
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"image_id":"7ec90ac3-b3ac-4b44-9ff3-0638eb870e1f"}' \
  http://localhost:8000/analyze
```

### Custom YOLO Model

```bash
# Load a custom model
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"model_path":"models/custom_pid_model.pt", "conf_threshold":0.6}' \
  http://localhost:8000/models/load

# Check model info
curl http://localhost:8000/models/info
```

## Data Models

### Node

```json
{
  "id": "string",
  "kind": "string",  // "equipment", "instrument", "junction"
  "type": "string",  // "pump", "valve_manual", etc.
  "bbox": {
    "x": 0,
    "y": 0,
    "w": 0,
    "h": 0
  },
  "confidence": 0.0,  // 0.0 to 1.0
  "tag": "string"
}
```

### Edge

```json
{
  "id": "string",
  "kind": "string",  // "process", "signal", "connection"
  "from_node": "string",  // Node ID
  "to_node": "string",    // Node ID
  "polyline": [
    [0, 0],  // [x, y] pairs
    [0, 0]
  ]
}
```

### Text

```json
{
  "id": "string",
  "content": "string",
  "bbox": {
    "x": 0,
    "y": 0,
    "w": 0,
    "h": 0
  }
}
```

### Issue

```json
{
  "id": "string",
  "severity": "string",  // "info", "warning", "error"
  "message": "string",
  "node_id": "string"  // Optional reference to a node
}
```

## Rate Limiting

> **Note**: The current implementation does not include rate limiting. In a production environment, appropriate rate limiting should be implemented to prevent abuse.

## Versioning

The API does not currently use explicit versioning. Future updates may introduce versioning through URL prefixes (e.g., `/v1/analyze`) or HTTP headers.

---

This API documentation provides a comprehensive reference for integrating with the P&ID Analyzer system. For further assistance or feature requests, please contact the development team.
```
