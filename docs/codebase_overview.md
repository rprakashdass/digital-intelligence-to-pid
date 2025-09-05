# P&ID Diagram Analyzer Codebase Overview

## Project Summary
This project is a P&ID (Piping and Instrumentation Diagram) to digital converter application built during a hackathon. It's designed specifically for oil & gas and chemical process P&ID diagrams using ISA-5.1 core symbols. The system analyzes uploaded P&ID diagrams, detects symbols, lines, and text, then constructs a graph representation of the process flow.

## Tech Stack
- **Backend**: Python with FastAPI
- **Frontend**: React with Tailwind CSS
- **Computer Vision**: OpenCV for image processing, symbol detection, and line extraction
- **OCR**: Tesseract for text recognition
- **Data Models**: Pydantic for type-safe data structures

## System Architecture

### 1. Backend Architecture (FastAPI)
The backend provides a REST API with these key endpoints:
- `/upload` and `/ingest`: Accepts image uploads and assigns an ID
- `/run/{type}`: Performs different analyses based on the type parameter
  - `validate`: Checks for issues in the P&ID
  - `ocr`: Extracts text elements
  - `graph`: Performs complete analysis and builds the process graph
- `/export`: Exports results in JSON or CSV format

The analysis pipeline consists of:
1. **Symbol Detection**: Template matching for 5 core ISA-5.1 symbols
2. **Line Detection**: HoughLinesP transform for straight line segments
3. **Junction Identification**: Creates nodes at line endpoints and intersections
4. **OCR**: Text extraction and association with symbols
5. **Graph Construction**: Connecting symbols via lines and junctions
6. **Tag Parsing**: Parsing ISA tags like FIC-101
7. **Validation**: Finding issues like unknown symbols, missing tags, etc.

### 2. Frontend Structure (React)
The React frontend provides:
- **Control Panel**: For uploading images and initiating different analyses
- **Viewer**: Displays the original image with optional overlays for symbols, lines, and text
- **Results Panel**: Shows tabbed analysis results (summary, symbols, connections, texts, issues)

Key UI features:
- Toggle-able visualization controls for symbols, lines, and text elements
- Color-coded overlays (green for equipment, yellow for instruments, blue for lines)
- Detailed results tables with detection confidence
- Issue highlighting and summaries

### 3. Data Models
- `Node`: Represents equipment, instruments, and junctions with attributes:
  - `id`: Unique identifier
  - `kind`: Type categorization (equipment, instrument, junction)
  - `type`: Specific type (pump, valve_manual, etc.)
  - `bbox`: Bounding box coordinates
  - `tag`: Associated tag if present
  - `attributes`: Additional metadata
  - `confidence`: Detection confidence score

- `Edge`: Represents connections (lines) with attributes:
  - `id`: Unique identifier
  - `kind`: Type of connection (process, signal)
  - `polyline`: Series of points defining the line
  - `direction`: Flow direction
  - `endpoints`: Connected node IDs
  - `attributes`: Additional metadata

- `Graph`: Container for the complete analysis:
  - `nodes`: Equipment, instruments, and junctions
  - `edges`: Connecting lines
  - `texts`: OCR-extracted text elements
  - `issues`: Detected problems

## Key Implementation Details

### 1. Symbol Detection (symbols.py)
- Uses OpenCV template matching against 5 core templates
- Templates are loaded from `data/templates/`
- Non-maximum suppression to avoid duplicate detections
- Flags unknown symbols and low-confidence detections as issues

### 2. Line Detection (lines.py)
- Uses Canny edge detection followed by Hough transform
- Creates line edges from detected segments
- Creates junction nodes at line endpoints
- Junction nodes use "jct_" prefix in their IDs

### 3. OCR and Text Processing (ocr.py)
- Uses Tesseract for text extraction
- Creates Text objects with content and position
- Text objects can be associated with nearby symbols

### 4. Graph Assembly (graph.py)
- Connects symbols via junctions and lines
- Associates text with nearby symbols (for tagging)
- Creates a structured graph representation

### 5. ISA Tag Parsing (tagging.py)
- Parses instrument tags like "FIC-101"
- Extracts loop letters, numbers, and modifiers
- Associates parsed information with the appropriate nodes

### 6. Validation (validate.py)
- Checks for dangling connections
- Identifies unknown symbols
- Finds missing or improperly formatted tags
- Returns issues array with severity levels and messages

## Current Limitations
1. Only supports 5 symbol types (pump, manual valve, control valve, instrument bubble, tank)
2. Only detects straight lines, not curved pipes
3. Basic text association based on proximity
4. Template matching can be brittle compared to ML-based approaches
5. No support for multi-page documents

## Recent Improvements
1. Streamlined UI workflow with clearer analysis buttons
2. Enhanced visualization controls for overlay toggling
3. Added detailed results panels with tabbed interfaces
4. Fixed API route mismatches between frontend and backend
5. Improved error handling for symbol detection and OCR
6. Added unknown symbol detection

## Execution Flow
1. User uploads a P&ID image
2. Backend saves it with a unique ID
3. User initiates analysis (complete, validation, or OCR)
4. Backend processes the image through the analysis pipeline
5. Results are returned to the frontend
6. Frontend displays results and optional overlays on the image
7. User can export results in structured formats

This codebase provides a foundation for automated P&ID digitization with room for extending symbol coverage and improving detection accuracy.
