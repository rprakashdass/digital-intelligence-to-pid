```markdown
# Components & Data Flow

## Component Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        P&ID Analyzer System                         │
│                                                                     │
│  ┌───────────┐     ┌───────────┐      ┌───────────┐    ┌──────────┐ │
│  │ Frontend  │◄────┤ HTTP API  │◄─────┤ Analysis  │◄───┤  Models  │ │
│  │   (UI)    │────►│ (FastAPI) │─────►│ Pipeline  │───►│  (YOLO)  │ │
│  └───────────┘     └───────────┘      └───────────┘    └──────────┘ │
│        │                 │                 │                │       │
│        ▼                 ▼                 ▼                ▼       │
│  ┌───────────┐     ┌───────────┐      ┌───────────┐    ┌──────────┐ │
│  │   User    │     │  Storage  │      │  Export   │    │Knowledge │ │
│  │Interaction│     │ (Images)  │      │ Formats   │    │  Base    │ │
│  └───────────┘     └───────────┘      └───────────┘    └──────────┘ │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Component Descriptions

### 1. Frontend (UI)
- **Purpose**: User interface for interacting with the P&ID analysis system
- **Key Features**:
  - Image/Video Upload
  - Analysis Visualization
  - Result Display
  - Smart Q&A Interface
- **Technologies**: React, TailwindCSS, HTML5 Canvas

### 2. HTTP API (FastAPI)
- **Purpose**: Backend service exposing REST endpoints
- **Key Endpoints**:
  - `/upload`: Image and video ingestion
  - `/analyze`: Process P&ID images
  - `/export`: Generate structured outputs
  - `/query`: Handle natural language queries
- **Technologies**: FastAPI, Uvicorn, Pydantic

### 3. Analysis Pipeline
- **Purpose**: Process P&ID images to extract structured data
- **Key Modules**:
  - Symbol Detection
  - OCR Processing
  - Line Detection
  - Graph Assembly
- **Technologies**: OpenCV, Tesseract, PyTorch

### 4. Models (YOLO)
- **Purpose**: AI models for symbol detection
- **Key Features**:
  - YOLO deep learning model
  - Fallback template matching
  - Confidence scoring
- **Technologies**: YOLOv5, PyTorch, OpenCV

### 5. Knowledge Base
- **Purpose**: Domain knowledge for RAG system
- **Key Contents**:
  - Instrument tags (ISA-5.1)
  - Equipment information
  - Process logic
  - Safety systems
- **Technologies**: JSON, SentenceTransformers

### 6. Storage (Images)
- **Purpose**: Temporary storage for uploaded images/videos
- **Key Features**:
  - Image persistence
  - Video frame extraction
  - PDF rasterization
- **Technologies**: File system, OpenCV

### 7. Export Formats
- **Purpose**: Convert internal graph to standard formats
- **Key Formats**:
  - DEXPI-lite JSON
  - CSV tables
  - Structured reports
- **Technologies**: JSON, CSV

### 8. User Interaction
- **Purpose**: Handle user interactions and display results
- **Key Features**:
  - Interactive visualization
  - Query interface
  - Result navigation
- **Technologies**: JavaScript events, DOM manipulation

## Data Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Upload  │────►│  Analyze │────►│ Assemble │────►│  Export  │
│  Image   │     │ Elements │     │  Graph   │     │  Results │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
                       │                │
                       ▼                ▼
                  ┌──────────┐    ┌──────────┐
                  │  Query   │◄───┤ Knowledge │
                  │ Response │    │   Base   │
                  └──────────┘    └──────────┘
```

### Key Data Flow Steps:

1. **Image Upload**:
   - User uploads P&ID image or video
   - System stores file and assigns unique ID
   - PDF files are converted to PNG

2. **Element Analysis**:
   - Symbol detection with YOLO or template matching
   - OCR extracts text elements
   - Line detection identifies connections
   - Each element gets unique ID and metadata

3. **Graph Assembly**:
   - Associate text with nearby symbols (tagging)
   - Connect lines to symbols (connectivity)
   - Parse ISA tags for structured information
   - Flag quality issues in the diagram

4. **Query Processing**:
   - User submits natural language query
   - System extracts context from graph
   - Knowledge base entries are retrieved
   - Response is generated combining both sources

5. **Result Export**:
   - Internal graph is converted to DEXPI-lite format
   - Nodes and edges are formatted for CSV export
   - Issues are collected into a validation report
   - Results are served to user for download

## Interaction Patterns

### 1. Image Analysis Flow
```
User → Upload Image → Process Diagram → View Results → Export Data
```

### 2. RAG Query Flow
```
User → View Diagram → Ask Question → System Processes → View Answer
```

### 3. Video Analysis Flow
```
User → Upload Video → Extract Frame → Process Frame → View Results
```

### 4. Export Flow
```
User → Process Diagram → Select Format → System Generates → Download
```

## Component Integration

### 1. Symbol Detection + OCR
- Symbol detection identifies equipment and instruments
- OCR identifies text elements
- Integration associates text with symbols

### 2. Line Detection + Graph Assembly
- Line detection identifies connections
- Graph assembly links lines to symbols
- Creates structured process flow graph

### 3. Graph Assembly + RAG
- Graph provides context for queries
- Knowledge base provides domain expertise
- Integration enables intelligent responses

### 4. Analysis Pipeline + Export
- Analysis pipeline creates internal graph model
- Export converts to standard formats
- Provides interoperability with other systems

## Extension Points

### 1. Custom Symbol Detection
```
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│  YOLO Model   │◄────┤ Model Registry │◄────┤ Custom Model  │
│  Integration  │     │                │     │   Training    │
└───────────────┘     └───────────────┘     └───────────────┘
```

### 2. Knowledge Base Extension
```
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│  Knowledge    │◄────┤  Knowledge    │◄────┤   Custom      │
│   Retrieval   │     │   Import      │     │   Knowledge   │
└───────────────┘     └───────────────┘     └───────────────┘
```

### 3. Pipeline Customization
```
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│   Analysis    │◄────┤   Plugin      │◄────┤    Custom     │
│   Pipeline    │     │  Registry     │     │   Processors  │
└───────────────┘     └───────────────┘     └───────────────┘
```

---

This document provides a comprehensive view of the P&ID Analyzer system components and their interactions, showing how data flows through the system and how components integrate to create a cohesive application.
```
