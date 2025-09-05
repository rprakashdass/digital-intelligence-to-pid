```markdown
# Analysis API Guide

## Overview

The Analysis API provides endpoints for processing P&ID diagrams through the system's computer vision pipeline. These endpoints handle image/video uploads and trigger various analysis stages that extract symbols, text, lines, and build a graph representation of the diagram.

## Analysis Pipeline

The P&ID Analyzer processes diagrams through a multi-stage pipeline:

1. **Upload**: Image or video is uploaded and stored temporarily
2. **Symbol Detection**: Identifies equipment, instruments, and valves
   - Primary: YOLO-based deep learning model
   - Fallback: Template matching for environments without PyTorch
3. **Text Extraction**: OCR identifies and extracts text elements
4. **Line Detection**: Identifies process lines, signal lines, and junctions
5. **Graph Construction**: Builds a connected graph of components
6. **Tag Parsing**: Interprets ISA-style tags (e.g., FIC-101, PT-202)
7. **Validation**: Checks for common issues and inconsistencies
8. **Export**: Provides results in structured formats (JSON, CSV)

## Endpoints

### Upload Image

```http
POST /upload
Content-Type: multipart/form-data
```

Upload a P&ID image for analysis.

#### Request

A multipart form with:
- `file`: The image file to upload (PNG, JPG, PDF)

#### Response

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

Upload a video file containing P&ID footage. The system will extract the best frame for analysis.

#### Request

A multipart form with:
- `file`: The video file to upload (MP4, AVI, MOV, etc.)

#### Response

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

#### Request

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

The `options` parameter is optional and defaults to running all analysis steps.

#### Response

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

#### Path Parameters

- `type`: Analysis type
  - `validate`: Run validation on the diagram
  - `ocr`: Extract text only
  - `graph`: Build the full graph

#### Response

Same format as `/analyze` endpoint, but with only the relevant sections populated.

### Export Results

```http
POST /export
Content-Type: application/json
```

Export analysis results in the specified format.

#### Request

```json
{
  "image_id": "606449c3-90db-41f2-8e5c-265c7d854ba2",
  "format": "json"  // or "csv"
}
```

#### Response

- For JSON: A JSON file with the analysis results in DEXPI-lite format
- For CSV: A ZIP file containing multiple CSV files for nodes, edges, and issues

## YOLO Model Management

The system uses a YOLO (You Only Look Once) deep learning model for symbol detection. The following endpoints allow managing this model:

### Get Model Info

```http
GET /models/info
```

Get information about the currently loaded YOLO model for symbol detection.

#### Response

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

#### Request

```json
{
  "model_path": "models/custom_pid_model.pt",
  "conf_threshold": 0.6
}
```

#### Response

```json
{
  "status": "success",
  "message": "Model loaded from models/custom_pid_model.pt"
}
```

## Data Models

### Node

A node represents a symbol or junction in the P&ID diagram.

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
  "tag": "string",
  "attributes": {
    // Optional additional attributes
    "parsed_tag": {
      "prefix": "string",
      "suffix": "string",
      "number": "string"
    }
  }
}
```

#### Node Kinds

- `equipment`: Physical equipment like pumps, tanks, heat exchangers
- `instrument`: Instruments like gauges, controllers, transmitters
- `junction`: Connection points where lines meet

#### Common Node Types

| Type | Description |
|------|-------------|
| `pump` | Centrifugal pump |
| `valve_manual` | Hand-operated valve |
| `valve_control` | Automated control valve |
| `instrument_bubble` | Instrument circle/bubble |
| `tank` | Storage tank or vessel |

### Edge

An edge represents a connection between nodes in the P&ID diagram.

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

#### Edge Kinds

- `process`: Process flow lines (e.g., fluid flow)
- `signal`: Signal or control lines
- `connection`: Other types of connections

### Text

A text element represents a piece of text detected in the diagram.

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

An issue represents a potential problem or inconsistency in the diagram.

```json
{
  "id": "string",
  "severity": "string",  // "info", "warning", "error"
  "message": "string",
  "node_id": "string"  // Optional reference to a node
}
```

#### Issue Severities

- `info`: Informational note, not necessarily a problem
- `warning`: Potential issue that might need attention
- `error`: Serious problem that should be fixed

## Error Handling

The API returns appropriate HTTP status codes and error messages:

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

## Fallback Mechanisms

The system includes several fallback mechanisms to ensure robustness:

1. **Symbol Detection**: Falls back to template matching if YOLO is unavailable
2. **PDF Handling**: Automatically rasterizes PDF files to PNG for processing
3. **Video Processing**: Extracts the best frame from videos for analysis
4. **Error Recovery**: Continues with partial results if some analysis steps fail

## Example Code

### Python

```python
import requests
import json

BASE_URL = "http://localhost:8000"

# Upload an image
def upload_image(file_path):
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{BASE_URL}/upload", files=files)
    
    return response.json()

# Analyze an image
def analyze_image(image_id):
    response = requests.post(
        f"{BASE_URL}/analyze",
        json={"image_id": image_id}
    )
    
    return response.json()

# Export analysis results
def export_results(image_id, format="json"):
    response = requests.post(
        f"{BASE_URL}/export",
        json={"image_id": image_id, "format": format}
    )
    
    if format == "json":
        return response.json()
    else:  # CSV
        with open(f"{image_id}_export.zip", 'wb') as f:
            f.write(response.content)
        return f"{image_id}_export.zip"

# Example usage
result = upload_image("path/to/pid.png")
image_id = result['image_id']

analysis = analyze_image(image_id)
print(f"Detected {len(analysis['nodes'])} symbols, {len(analysis['edges'])} connections")

export_file = export_results(image_id, "csv")
print(f"Exported results to {export_file}")
```

### JavaScript

```javascript
async function uploadImage(file) {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch('http://localhost:8000/upload', {
    method: 'POST',
    body: formData
  });
  
  return response.json();
}

async function analyzeImage(imageId) {
  const response = await fetch('http://localhost:8000/analyze', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ image_id: imageId })
  });
  
  return response.json();
}

async function exportResults(imageId, format = 'json') {
  const response = await fetch('http://localhost:8000/export', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ image_id: imageId, format })
  });
  
  if (format === 'json') {
    return response.json();
  } else {
    // Handle CSV zip file
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${imageId}_export.zip`;
    a.click();
    return `Downloaded ${imageId}_export.zip`;
  }
}

// Example usage
uploadImage(fileInput.files[0])
  .then(result => {
    const imageId = result.image_id;
    return analyzeImage(imageId).then(analysis => {
      console.log(`Detected ${analysis.nodes.length} symbols, ${analysis.edges.length} connections`);
      return exportResults(imageId, 'json');
    });
  })
  .then(exportedData => {
    console.log('Exported data:', exportedData);
  });
```

## Performance Considerations

1. **Image Size**: Large images (>2000px) may take longer to process
2. **Complexity**: Diagrams with many symbols and connections require more processing time
3. **PDF Processing**: PDF conversion adds overhead to the processing time
4. **YOLO Model**: First-time model loading may take a few seconds
5. **Resource Constraints**: CPU-only environments will be slower than GPU-accelerated ones

## Limitations

The current analysis pipeline has some limitations:

1. **Symbol Recognition**: Limited to trained symbol types (pump, valve, etc.)
2. **OCR Quality**: Text recognition depends on image clarity and font
3. **Line Types**: May not distinguish all line types (e.g., pneumatic vs. hydraulic)
4. **Complex Symbols**: Custom or complex symbols may not be detected accurately
5. **Multi-page Diagrams**: Currently processes single-page diagrams only

## Further Reading

- [API Reference](./api_reference.md)
- [YOLO Integration](../YOLO_INTEGRATION.md)
- [System Architecture](../architecture/system_overview.md)
```
