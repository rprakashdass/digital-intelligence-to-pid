```markdown
# Query API Guide

## Overview

The Query API enables natural language interactions with P&ID diagrams through a Retrieval-Augmented Generation (RAG) system. This API allows users to ask questions about diagram components, connections, instrument functions, and process flows in natural language.

## RAG Architecture

The P&ID Analyzer uses a Retrieval-Augmented Generation (RAG) system with the following components:

1. **Knowledge Base**: Contains structured information about:
   - Instrument tags (FIC, PT, etc.)
   - Equipment types (pumps, valves, tanks)
   - Process logic relationships
   - Safety systems
   - Common P&ID conventions

2. **Embedding Model**: Converts queries and knowledge items into vector representations for semantic matching

3. **Context Generation**: Creates a rich context from:
   - The analyzed diagram (detected symbols, text, connections)
   - Relevant knowledge base entries
   - Diagram metadata

4. **Response Generation**: Produces natural language answers based on the query and context

## Endpoint

```http
POST /query
Content-Type: application/json
```

Submit a natural language query about a previously analyzed P&ID diagram.

### Request

```json
{
  "image_id": "606449c3-90db-41f2-8e5c-265c7d854ba2",
  "query": "What does FIC-101 do?"
}
```

#### Parameters

| Parameter | Type   | Description                                                    |
|-----------|--------|----------------------------------------------------------------|
| image_id  | string | The ID of a previously uploaded and analyzed P&ID image        |
| query     | string | Natural language question about the diagram or its components  |

### Response

```json
{
  "query": "What does FIC-101 do?",
  "answer": "FIC-101 is a Flow Indicating Controller that measures and controls the flow rate of the process fluid. In this diagram, it is connected to the control valve CV-101 which regulates the flow to the tank T-101.",
  "confidence": 0.85,
  "knowledge_sources": [
    {
      "type": "instrument_tag",
      "key": "FIC",
      "similarity": 0.92
    }
  ],
  "analysis_summary": {
    "symbols_detected": 15,
    "text_elements": 28,
    "issues_found": 2
  }
}
```

#### Response Fields

| Field             | Type    | Description                                               |
|-------------------|---------|-----------------------------------------------------------|
| query             | string  | The original query that was processed                      |
| answer            | string  | Natural language response to the query                    |
| confidence        | float   | Confidence score for the answer (0.0-1.0)                |
| knowledge_sources | array   | List of knowledge base entries used to generate the answer |
| analysis_summary  | object  | Summary statistics of the diagram analysis                |

## Knowledge Base Info

Get information about the loaded knowledge base:

```http
GET /knowledge-base/info
```

### Response

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

## Example Queries

The Query API can handle a wide range of questions about P&ID diagrams, including:

### Component Identification

* "What does PT-101 stand for?"
* "What type of valve is V-201?"
* "How many pumps are in this diagram?"

### Process Flow

* "What is connected to the outlet of Pump P-101?"
* "Describe the flow path from Tank T-101 to Heat Exchanger HX-201"
* "What controls the flow to the separator?"

### Function & Purpose

* "What is the purpose of the control loop with FIC-301?"
* "Why is there a pressure relief valve on this vessel?"
* "How does the level control system for Tank T-101 work?"

### Standards & Compliance

* "Are there any missing tags in this diagram?"
* "Does this diagram follow ISA standards for instrument tagging?"
* "What safety systems are shown for the reactor?"

## Advanced Features

### Diagram Context

The system automatically analyzes the diagram to create context for the RAG system:

* **Symbol Detection**: Identifies equipment, instruments, and valves
* **Text Association**: Links text elements with the closest symbols for tagging
* **Connection Analysis**: Maps process flows and signal paths
* **Tag Parsing**: Interprets ISA-style tags (e.g., FIC-101, PT-202)

### Answer Sources

The `knowledge_sources` field shows which parts of the knowledge base contributed to the answer:

```json
"knowledge_sources": [
  {
    "type": "instrument_tag",
    "key": "FIC",
    "similarity": 0.92,
    "description": "Flow Indicating Controller"
  },
  {
    "type": "process_logic",
    "key": "flow_control_loop",
    "similarity": 0.85
  }
]
```

### Confidence Scores

The `confidence` score (0.0-1.0) indicates the system's certainty about the answer:
* **High (0.8-1.0)**: System found direct matches in the knowledge base and diagram
* **Medium (0.5-0.8)**: System made reasonable inferences but with some uncertainty
* **Low (0.0-0.5)**: System had limited relevant information to answer the query

## Error Handling

The API handles several error conditions:

* **Invalid image_id**: Returns a 404 error if the image ID doesn't exist
* **Analysis failures**: Still attempts to answer the query with available information
* **Knowledge base limitations**: Indicates when it doesn't have enough information
* **Processing errors**: Returns a 500 error with a useful error message

### Error Response Example

```json
{
  "query": "What does FIC-101 do?",
  "error": "Error processing query: Knowledge base not initialized",
  "answer": "I'm sorry, I encountered an error while processing your request.",
  "confidence": 0.0,
  "knowledge_sources": [],
  "analysis_summary": {
    "symbols_detected": 0,
    "text_elements": 0,
    "issues_found": 1
  }
}
```

## Best Practices

1. **Always analyze the image first** using the `/analyze` endpoint before using `/query`
2. **Be specific** in your queries for more accurate answers
3. **Reference specific tags** (e.g., "What is FIC-101?") rather than vague descriptions
4. **Check confidence scores** to gauge the reliability of answers
5. **Consider the context** of the full diagram when interpreting answers

## Limitations

The current RAG system has some limitations:

1. **Knowledge base scope**: Limited to common P&ID symbols and conventions
2. **Complex reasoning**: May struggle with multi-step logical inferences
3. **Diagram quality**: Poor image quality affects analysis accuracy
4. **Missing context**: Cannot access information not visible in the diagram
5. **Domain specificity**: Better at general P&ID concepts than industry-specific details

## Example Code

### Python

```python
import requests
import json

BASE_URL = "http://localhost:8000"

# Upload and analyze an image
def upload_and_analyze(file_path):
    # Upload the image
    with open(file_path, 'rb') as f:
        files = {'file': f}
        upload_response = requests.post(f"{BASE_URL}/upload", files=files)
    
    image_id = upload_response.json()['image_id']
    
    # Analyze the image
    analyze_response = requests.post(
        f"{BASE_URL}/analyze",
        json={"image_id": image_id}
    )
    
    return image_id

# Query the diagram
def query_diagram(image_id, question):
    response = requests.post(
        f"{BASE_URL}/query",
        json={
            "image_id": image_id,
            "query": question
        }
    )
    
    return response.json()

# Example usage
image_id = upload_and_analyze("path/to/pid.png")
answer = query_diagram(image_id, "What does FIC-101 do?")
print(f"Query: {answer['query']}")
print(f"Answer: {answer['answer']}")
print(f"Confidence: {answer['confidence']}")
```

### JavaScript

```javascript
async function uploadAndAnalyze(file) {
  // Upload the image
  const formData = new FormData();
  formData.append('file', file);
  
  const uploadResponse = await fetch('http://localhost:8000/upload', {
    method: 'POST',
    body: formData
  });
  
  const { image_id } = await uploadResponse.json();
  
  // Analyze the image
  await fetch('http://localhost:8000/analyze', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ image_id })
  });
  
  return image_id;
}

async function queryDiagram(imageId, question) {
  const response = await fetch('http://localhost:8000/query', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      image_id: imageId,
      query: question
    })
  });
  
  return response.json();
}

// Example usage
uploadAndAnalyze(fileInput.files[0])
  .then(imageId => {
    return queryDiagram(imageId, 'What does FIC-101 do?');
  })
  .then(answer => {
    console.log(`Query: ${answer.query}`);
    console.log(`Answer: ${answer.answer}`);
    console.log(`Confidence: ${answer.confidence}`);
  });
```

## Further Reading

- [RAG Documentation](../RAG_DOCUMENTATION.md)
- [API Reference](./api_reference.md)
- [System Architecture](../architecture/system_overview.md)
```
