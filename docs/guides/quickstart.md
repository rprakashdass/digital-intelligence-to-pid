```markdown
# Quick Start Guide

## Overview

This guide will help you quickly set up and start using the P&ID Analyzer system. Follow these steps to get up and running in minutes.

## Installation

### Prerequisites

Before installing, ensure you have:

- **Python**: Version 3.9+ (3.10 recommended)
- **Node.js**: Version 16+ (for the frontend)
- **Git**: For cloning the repository
- **Disk Space**: At least 2GB free space

### Option 1: Quick Setup (Recommended)

For Windows:

1. Clone the repository:
   ```
   git clone https://github.com/your-org/pid-analyzer.git
   cd pid-analyzer
   ```

2. Run the setup script:
   ```
   start_dev.bat
   ```

For macOS/Linux:

1. Clone the repository:
   ```
   git clone https://github.com/your-org/pid-analyzer.git
   cd pid-analyzer
   ```

2. Run the setup script:
   ```
   chmod +x start_dev.sh
   ./start_dev.sh
   ```

The script will:
- Create a Python virtual environment
- Install required Python packages
- Install frontend dependencies
- Launch both backend and frontend servers

### Option 2: Manual Setup

#### Backend Setup

1. Create a Python virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install backend dependencies:
   ```
   cd backend
   pip install -r requirements.txt
   cd ..
   ```

3. Start the backend server:
   ```
   python -m backend.main
   ```

#### Frontend Setup

1. Install frontend dependencies:
   ```
   cd frontend
   npm install  # or pnpm install
   ```

2. Start the frontend development server:
   ```
   npm run dev  # or pnpm run dev
   ```

## Accessing the Application

After installation:

1. The backend API server will be running at: [http://localhost:8000](http://localhost:8000)
2. The frontend web interface will be available at: [http://localhost:3000](http://localhost:3000)

Open [http://localhost:3000](http://localhost:3000) in your browser to access the P&ID Analyzer interface.

## Basic Usage

### Step 1: Upload a Diagram

1. Open the web interface at [http://localhost:3000](http://localhost:3000)
2. Drag and drop a P&ID diagram (PNG, JPG, or PDF) onto the upload area
   - or -
   Click "Choose File" and select a diagram from your computer

Sample diagrams are available in the `data/samples/` directory if you need test files.

### Step 2: Analyze the Diagram

Analysis starts automatically after upload, but you can also:

1. Click the "Analyze" button to start or restart analysis
2. Wait for the analysis to complete (usually 5-30 seconds depending on complexity)

### Step 3: Explore the Results

After analysis completes:

1. **Visual Results**: The diagram appears with colored overlays showing:
   - Blue: Equipment symbols (pumps, valves, tanks)
   - Green: Instrument symbols
   - Yellow: Text elements
   - Red: Connections and lines

2. **Detailed Results**: Explore the tabs in the results panel:
   - **Symbols**: List of detected equipment and instruments
   - **Connections**: Process and signal lines
   - **Text**: OCR-extracted text elements
   - **Issues**: Warnings and validation problems

### Step 4: Ask Questions

Use the natural language query interface to ask about the diagram:

1. Type a question in the query box (e.g., "What does FIC-101 do?")
2. Click "Ask" or press Enter
3. View the AI-generated response below your question

### Step 5: Export Results

To save or share the analysis:

1. Click the "Export" button
2. Choose a format:
   - **JSON**: Complete analysis data
   - **CSV**: Tabular data for spreadsheets
3. Save the file to your computer

## Video Tutorial

For a visual walkthrough of these steps, watch our [Quick Start Video Tutorial](https://example.com/quickstart-video).

## Common Issues

### YOLO Model Installation

If you see a message about missing YOLO models:

1. The system will automatically fall back to template matching
2. For better results, install PyTorch and YOLO:
   ```
   python backend/setup_yolo.py
   ```

### OCR Quality

If text recognition isn't accurate:

1. Ensure your diagram has clear, readable text
2. Try uploading a higher resolution image
3. Check if text is oriented horizontally (works best)

### Connection Issues

If browser can't connect to the server:

1. Verify both backend and frontend servers are running
2. Check terminal windows for error messages
3. Ensure ports 8000 and 3000 are not blocked by firewall

## Next Steps

- Read the [User Guide](./user_guide.md) for detailed usage instructions
- Explore the [Developer Guide](./developer_guide.md) to extend the system
- Check the [API Reference](../api/api_reference.md) for integration options

## Getting Help

If you encounter issues:

- Check the [Troubleshooting Guide](../TROUBLESHOOTING.md)
- Review [YOLO Integration](../YOLO_INTEGRATION.md) for AI model setup
- Contact support with specific error messages and screenshots

---

Congratulations! You've completed the quick start guide for P&ID Analyzer. You can now analyze engineering diagrams, extract structured data, and query them using natural language.
```
