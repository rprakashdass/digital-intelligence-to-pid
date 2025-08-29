# P&ID to Digital MVP

This project is a minimal, working P&ID-to-digital converter built in one day as part of a hackathon. It uses a simple HTML/CSS/JS frontend and a Python FastAPI backend to perform OCR, symbol detection, and graph construction from a P&ID image.

## Features (MVP)

- **Image Upload**: Upload a P&ID as a PNG or JPG.
- **OCR**: Extracts text using `pytesseract`.
- **Symbol Detection**: Simple template matching for a small set of symbols (pump, valves, instrument bubble).
- **Line Extraction**: Detects straight lines using OpenCV.
- **Graph Construction**: Builds a basic process graph of nodes and edges.
- **ISA Tag Parsing**: Parses instrument tags like `FIC-101`.
- **Issue Detection**: Flags potential problems like missing labels or dangling lines.
- **DEXPI-lite Export**: Exports the graph to a simplified JSON format.
- **Simple UI**: View the original image, toggle overlays, and review extracted data.

## Project Structure

- `backend/`: FastAPI application.
  - `main.py`: API endpoints (`/ingest`, `/analyze`, `/export`).
  - `models.py`: Pydantic data models.
  - `services/`: Core logic for OCR, symbol/line detection, etc.
- `frontend/`: Vanilla HTML, CSS, and JavaScript frontend.
  - `index.html`: The main UI.
  - `app.js`: Frontend logic for interacting with the backend.
- `data/`:
  - `templates/`: PNG images for symbol template matching.
  - `samples/`: Sample P&ID images for testing.
- `README.md`: This file.
- `Makefile`: Helper commands for setup and execution.

## Setup and Running

### Prerequisites

- Python 3.8+ and `pip`
- A virtual environment tool (`venv`)
- Tesseract OCR engine installed and in your system's PATH.
  - **Windows**: Download from the official Tesseract repository.
  - **macOS**: `brew install tesseract`
  - **Linux**: `sudo apt-get install tesseract-ocr`

### Installation

1.  **Clone the repository and create a virtual environment:**
    ```bash
    git clone <repo-url>
    cd <repo-name>
    python -m venv .venv
    ```

2.  **Activate the virtual environment:**
    -   **Windows (cmd.exe):**
        ```
        .venv\Scripts\activate.bat
        ```
    -   **PowerShell:**
        ```
        .venv\Scripts\Activate.ps1
        ```
    -   **macOS/Linux:**
        ```
        source .venv/bin/activate
        ```

3.  **Install Python dependencies:**
    ```bash
    pip install -r backend/requirements.txt
    ```

### Running the Application

1.  **Start the backend server:**
    ```bash
    uvicorn backend.main:app --reload --port 8000
    ```
    The server will be running at `http://localhost:8000`.

2.  **Open the frontend:**
    Open the `frontend/index.html` file directly in your web browser.

    > **Note:** The application is configured with CORS to allow `file://` origins for local development, so you don't need a separate frontend server.

## How to Use

1.  Open `frontend/index.html` in your browser.
2.  Click "Choose File" and select a P&ID image from the `data/samples` folder or your own.
3.  The image will be displayed in the viewer.
4.  Click the "Analyze" button.
5.  After a few moments, the tables on the right will populate with extracted objects, lines, and any identified issues.
6.  Use the "Toggle Overlays" checkboxes to view the detected symbols and lines on the image.
7.  Click "Export DEXPI-lite JSON" or "Export CSVs" to download the results.

## Limitations and Next Steps

This is a hackathon MVP and has several limitations:

-   **Limited Symbol Library**: Only a few symbols are recognized.
-   **Straight Lines Only**: Does not detect curved pipes.
-   **Basic Text Association**: Associates text based on simple proximity, which can be inaccurate.
-   **No CAD Import**: Only works with raster images.
-   **Single-Page Only**: Does not process multi-page documents.

### Future Improvements

-   **ML-based Symbol Detection**: Replace template matching with a more robust machine learning model (e.g., YOLO).
-   **Improved Line Merging**: Implement more sophisticated algorithms to connect broken line segments.
-   **DEXPI/ISO 15926 Mapping**: Create a proper mapping from detected symbols to standard industry classes.
-   **Support for Curved Pipes**: Use contour detection or other CV techniques.
-   **Interactive Correction**: Allow users to correct misidentifications in the UI.
