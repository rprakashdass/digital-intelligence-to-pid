```markdown
# User Guide

## Overview

This comprehensive guide explains how to use all features of the P&ID Analyzer system effectively. From uploading diagrams to querying with natural language, this guide covers the complete workflow for analyzing Piping and Instrumentation Diagrams.

## Getting Started

### Accessing the Application

The P&ID Analyzer can be accessed through:

1. **Web Browser**: Navigate to the application URL (typically `http://localhost:3000` for local deployments)
2. **Local Installation**: Follow the [Quickstart Guide](./quickstart.md) for installation instructions

### User Interface Overview

The interface is divided into several key areas:

![UI Overview](../media/images/ui_overview.png)

1. **Upload Panel**: For submitting diagrams
2. **Main Viewer**: Displays the diagram with analysis overlays
3. **Results Panel**: Shows structured analysis results
4. **Query Interface**: For asking questions about the diagram

## Uploading Diagrams

### Supported File Types

The system accepts the following file formats:

- **Images**: PNG, JPG/JPEG
- **Documents**: PDF (single page)
- **Videos**: MP4, AVI, MOV (will extract the best frame)

### Upload Methods

#### Method 1: Drag and Drop

1. Drag a file from your computer
2. Drop it onto the upload area
3. The file will upload automatically

#### Method 2: File Browser

1. Click the "Choose File" button
2. Navigate to and select your diagram
3. Click "Open" to upload

#### Method 3: Paste Image

1. Copy an image to your clipboard
2. Click into the upload area
3. Press Ctrl+V (Cmd+V on Mac)

### Upload Status

After uploading, you'll see:
- A thumbnail of your uploaded image
- The file name and size
- A progress indicator during processing

## Analyzing Diagrams

### Running Analysis

Analysis starts automatically after upload, but you can also:

1. Click "Analyze" to start or restart analysis
2. Choose specific analysis types from the dropdown menu:
   - Full Analysis (default)
   - Symbol Detection Only
   - Text Recognition Only
   - Line Detection Only

### Analysis Progress

During analysis, you'll see:
1. A progress indicator showing the current stage
2. Status messages for each step
3. Estimated time remaining for large diagrams

### Viewing Results

After analysis completes, the results appear in multiple views:

#### Visual Overlay View

The diagram with analysis overlays showing:
- Colored bounding boxes around detected symbols
- Tags and labels for identified components
- Highlighted process and signal lines
- Connection points and junctions

Controls for this view:
- Zoom: Mouse wheel or pinch gesture
- Pan: Click and drag or touch and drag
- Toggle overlays: Use the eye icons in the sidebar

#### Structured Results View

Tabbed interface with:
- **Symbols**: List of all detected equipment and instruments
- **Connections**: Process and signal lines
- **Text**: OCR results with position information
- **Issues**: Warnings and errors detected during validation

Each tab includes:
- Sortable and filterable tables
- Count summaries
- Confidence scores

#### Graph View

Interactive graph representation showing:
- Nodes for symbols and equipment
- Edges for connections
- Tooltips with detailed information
- Ability to highlight paths and relationships

Controls:
- Zoom and pan the graph
- Click nodes to see details
- Toggle visibility of node types
- Adjust layout algorithm

## Querying the Diagram

The natural language query system lets you ask questions about the diagram.

### How to Ask Questions

1. Type your question in the query field
2. Click "Ask" or press Enter
3. View the response below your question

### Example Queries

You can ask questions like:
- "What does FIC-101 mean?"
- "How many pumps are in this diagram?"
- "What is connected to Tank T-201?"
- "Trace the flow from the inlet to the separator."
- "Explain the control loop for temperature control."

### Understanding Responses

Each response includes:
- A natural language answer
- Confidence score indicating reliability
- Sources of information used
- Highlighted relevant parts of the diagram (when applicable)

### Query History

Your queries are saved in the session, allowing you to:
- Scroll through previous questions
- Revisit earlier answers
- Continue related lines of questioning

## Exporting Results

### Export Formats

Analysis results can be exported in several formats:

1. **JSON**: Complete analysis results in DEXPI-lite format
2. **CSV**: Tabular data in multiple CSV files
3. **PDF Report**: Visual diagram with annotations and findings
4. **Image**: The diagram with analysis overlays

### How to Export

1. Click the "Export" button in the top right
2. Select your desired format
3. Choose additional options (if applicable)
4. Click "Download"

### Batch Processing

For multiple diagrams:
1. Upload all files using the batch upload option
2. Run analysis on each or use "Analyze All"
3. Use "Export All" to generate a ZIP with all results

## Advanced Features

### Video Analysis

To analyze P&ID diagrams from videos:
1. Upload a video file in supported format
2. The system automatically extracts the best frame
3. Proceed with analysis as normal

### Custom Templates

For specialized symbols:
1. Go to Settings > Templates
2. Upload your custom symbol templates
3. Provide names and descriptions
4. Use them in future analyses

### Validation Rules

Control the validation process:
1. Go to Settings > Validation
2. Enable/disable specific rule categories
3. Adjust severity levels
4. Create custom validation rules

### User Preferences

Customize your experience:
1. Go to Settings > Preferences
2. Adjust overlay colors and transparency
3. Set default analysis options
4. Configure display preferences

## Troubleshooting

### Common Issues

#### Poor Symbol Detection

**Symptoms**: 
- Missing symbols
- Incorrect classifications
- Low confidence scores

**Solutions**:
1. Ensure image quality is good (600+ DPI recommended)
2. Check image orientation is correct
3. Increase contrast if diagram is faded
4. Try preprocessing the image externally
5. Add custom templates for unusual symbols

#### Text Recognition Problems

**Symptoms**:
- Missing text
- Incorrect text recognition
- Unassociated text elements

**Solutions**:
1. Ensure text is clear and legible
2. Check for standard engineering fonts
3. Adjust OCR settings in preferences
4. Manually associate text where needed

#### Connection Issues

**Symptoms**:
- Missing or incorrect connections
- Disconnected symbols
- Improper flow direction

**Solutions**:
1. Ensure line quality is clear
2. Check for line interruptions in the diagram
3. Adjust line detection settings
4. Manually correct connections if needed

### Error Messages

| Error Message | Likely Cause | Solution |
|---------------|--------------|----------|
| "Failed to process image" | Corrupted image file | Try a different file format or reexport the image |
| "YOLO model not found" | Missing AI model files | Reinstall or update the application |
| "OCR engine error" | Tesseract installation issue | Check Tesseract installation |
| "Memory limit exceeded" | Image too large | Resize the image or increase memory allocation |

### Getting Support

If you encounter persistent issues:
1. Check the [Troubleshooting Guide](../TROUBLESHOOTING.md)
2. Look for solutions in the [FAQ](../faq.md)
3. Contact support with:
   - Description of the issue
   - Steps to reproduce
   - Screenshot or example diagram
   - Log files (if available)

## Best Practices

### Image Preparation

For optimal results:
1. Use high-resolution scans (min. 300 DPI, recommended 600+ DPI)
2. Ensure good contrast between lines, symbols, and background
3. Crop to include only the relevant diagram area
4. Remove any handwritten annotations when possible
5. Ensure text is horizontal where possible

### Workflow Efficiency

To work more efficiently:
1. Process similar diagrams in batches
2. Create templates for recurring symbols
3. Save common queries for reuse
4. Use keyboard shortcuts for common actions
5. Export results in formats matching your downstream tools

### Interpretation Guidelines

When reviewing results:
1. Check confidence scores for reliability
2. Verify critical connections manually
3. Pay attention to validation warnings
4. Use natural language queries to confirm understanding
5. Compare results with engineering specifications

## Keyboard Shortcuts

| Function | Shortcut (Windows/Linux) | Shortcut (Mac) |
|----------|--------------------------|----------------|
| Upload | Ctrl+O | Cmd+O |
| Analyze | Ctrl+R | Cmd+R |
| Export | Ctrl+E | Cmd+E |
| Zoom In | Ctrl++ | Cmd++ |
| Zoom Out | Ctrl+- | Cmd+- |
| Reset View | Ctrl+0 | Cmd+0 |
| Toggle Overlays | Ctrl+H | Cmd+H |
| Submit Query | Ctrl+Enter | Cmd+Return |
| Clear Query | Esc | Esc |
| Switch Tabs | Ctrl+1,2,3,4 | Cmd+1,2,3,4 |
| Help | F1 | F1 |

## Glossary

| Term | Definition |
|------|------------|
| P&ID | Piping and Instrumentation Diagram - a detailed diagram in the process industry showing the piping and process equipment together with the instrumentation and control devices |
| Symbol | A graphical representation of equipment or instruments in a P&ID |
| Tag | An identifier for equipment or instruments following standards like ISA-5.1 |
| Node | A component in the diagram's graph representation (symbol or junction) |
| Edge | A connection between nodes in the graph (process line or signal) |
| OCR | Optical Character Recognition - technology to recognize text in images |
| YOLO | You Only Look Once - an object detection algorithm used for symbol detection |
| RAG | Retrieval-Augmented Generation - system for answering natural language queries using a knowledge base |
| DEXPI | Data Exchange in the Process Industry - a standard for P&ID data exchange |

## Additional Resources

- [API Reference](../api/api_reference.md)
- [Technical Documentation](../architecture/system_overview.md)
- [Video Tutorials](https://example.com/tutorials)
- [Sample Diagrams](https://example.com/samples)

---

This user guide provides comprehensive instructions for all features of the P&ID Analyzer. For additional assistance, please contact support or refer to the other documentation resources.
```
