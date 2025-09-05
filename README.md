# P&ID Analyzer

<div align="center">

```
    ____  ____     __________    ___                __                     
   / __ \/ __ \   /  _/ __ \ \  / / | _____  ___ _/ /_ __________
  / /_/ / /_/ /   / // / / /\ \/ /| |/ / _ \/ _ `/ / // / __/ -_)
 / ____/ ____/  _/ // /_/ /  \  / |   /  __/ /_/ / \_,_/_/  \__/ 
/_/   /_/      /___/_____/    \/ /___/\___/\__,_/_/___/      
                                                                
 AI-Powered P&ID Analysis & Intelligence Platform
```

**Transform static diagrams into intelligent, interactive assets**

[Quick Start](#-quick-start) • 
[Features](#-key-features) • 
[Documentation](#-documentation) • 
[Architecture](#-architecture) • 
[Contributing](#-contributing)

</div>

This AI-driven platform transforms Piping and Instrumentation Diagrams (P&IDs) into structured, machine-readable datasets. Built with modern deep learning and computer vision techniques, it provides robust symbol detection, OCR, and process flow mapping compliant with ISA-5.1 and ISO standards.

## 🚀 Key Features

- **AI-Powered Symbol Detection**: YOLO-based deep learning for robust ISA-5.1 symbol recognition
- **Advanced OCR**: Tesseract-based text extraction with natural language processing
- **Process Flow Mapping**: Intelligent line detection and junction identification
- **ISA Tag Parsing**: Automated parsing of instrument tags (e.g., FIC-101, PSV-201)
- **🤖 Smart Q&A (RAG)**: Natural language queries about P&ID diagrams with intelligent responses
- **📹 Video Support**: Upload and analyze P&ID videos with automatic frame extraction
- **🧠 Knowledge Base**: 50+ ISA-5.1 instrument tags and process equipment definitions
- **Industry Standards Compliance**: DEXPI-lite export format with ISO 15926 mapping support
- **Quality Validation**: Comprehensive issue detection and reporting
- **Modern Web Interface**: React-based UI with real-time visualization overlays
- **Flexible Export**: JSON, CSV, and DEXPI-lite formats for downstream integration

## 🏗️ Architecture

```
                             P&ID Analyzer Architecture
                          ============================

┌───────────────────────────────────────────────────────────────────┐
│                         Client Applications                        │
│                                                                   │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌──────────┐
│  │ React Web UI│   │Mobile Client│   │ CLI Tool    │   │3rd Party │
│  │             │   │(Future)     │   │(Future)     │   │Integration│
│  └─────────────┘   └─────────────┘   └─────────────┘   └──────────┘
└───────────────────────────────────────────────────────────────────┘
                                  ▲
                                  │
                                  ▼
┌───────────────────────────────────────────────────────────────────┐
│                           API Layer (FastAPI)                      │
│                                                                   │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌──────────┐
│  │ Upload API  │   │ Analysis API│   │ Query API   │   │Export API│
│  │             │   │             │   │             │   │          │
│  └─────────────┘   └─────────────┘   └─────────────┘   └──────────┘
└───────────────────────────────────────────────────────────────────┘
                                  ▲
                                  │
                                  ▼
┌───────────────────────────────────────────────────────────────────┐
│                       Core Analysis Pipeline                       │
│                                                                   │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌──────────┐
│  │ Symbol      │   │ Text        │   │ Line        │   │Graph     │
│  │ Detection   │   │ Extraction  │   │ Detection   │   │Builder   │
│  │ ┌─────────┐ │   │ ┌─────────┐ │   │ ┌─────────┐ │   │┌────────┐│
│  │ │  YOLO   │ │   │ │ OCR     │ │   │ │OpenCV   │ │   ││Tagging ││
│  │ │         │ │   │ │         │ │   │ │         │ │   ││        ││
│  │ └─────────┘ │   │ └─────────┘ │   │ └─────────┘ │   │└────────┘│
│  └─────────────┘   └─────────────┘   └─────────────┘   └──────────┘
└───────────────────────────────────────────────────────────────────┘
```

### Backend (FastAPI + AI)
- **Symbol Detection**: YOLO deep learning models with template matching fallback
- **Computer Vision**: OpenCV for line detection, contour analysis, and image processing
- **OCR Pipeline**: Tesseract with text association and validation
- **Graph Construction**: Intelligent process flow mapping with junction detection
- **RAG System**: Retrieval-Augmented Generation with knowledge base and LLM integration
- **Video Processing**: Frame extraction and quality assessment for video uploads
- **Export Engine**: Multi-format export with industry-standard compliance

### Frontend (React + Tailwind)
- **Interactive Viewer**: Toggle-able overlays for symbols, lines, and text
- **Results Dashboard**: Tabbed interface for comprehensive analysis review
- **Smart Q&A Panel**: Natural language query interface with intelligent responses
- **Video Upload**: Support for video file uploads with frame extraction
- **Export Controls**: One-click export to various formats
- **Responsive Design**: Modern UI optimized for engineering workflows

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ and pip
- Tesseract OCR engine
- Node.js and npm (for frontend)
- GPU recommended for YOLO inference (CUDA compatible)

### Installation

1. **Clone and setup environment:**
```bash
git clone <repo-url>
cd <repo-name>
```

2. **Run the startup script:**
```bash
# Windows
start_dev.bat

# Linux/Mac
./start_dev.sh
```

3. **Alternative manual setup:**
```bash
# Install backend dependencies
pip install torch torchvision ultralytics fastapi uvicorn sentence-transformers openai

# Setup YOLO model
python backend/initialize_yolo.py

# Start backend server
python -m uvicorn backend.main:app --reload --port 8000

# In another terminal, start frontend
cd frontend
npm install
npm run dev
```

4. **Access the application:**
- Backend API: http://localhost:8000
- Frontend UI: http://localhost:5173

## 🤖 YOLO Integration

### Why YOLO?
- **Better Accuracy**: Deep learning vs. template matching
- **Robustness**: Handles drawing style variations, rotations, scales
- **Extensibility**: Easy to add new symbols through training
- **Performance**: GPU acceleration for real-time processing

### Model Management
```bash
# Load custom trained model
curl -X POST "http://localhost:8000/models/load" \
     -H "Content-Type: application/json" \
     -d '{"model_path": "models/pid_symbols.pt", "conf_threshold": 0.6}'

# Check model status
curl "http://localhost:8000/models/info"
```

### Training Your Own Model
1. **Prepare dataset** in YOLO format
2. **Train model** using ultralytics
3. **Deploy** via API endpoint
4. **Monitor** performance and retrain as needed

See [YOLO_INTEGRATION.md](YOLO_INTEGRATION.md) for detailed training instructions.

## 🤖 Smart Q&A (RAG) System

### Natural Language Queries
Ask questions about your P&ID diagrams in plain English:

```bash
# Example queries
"What does FIC-101 do?"
"Explain the function of the pump in this diagram"
"What safety systems are present?"
"Are there any issues with this P&ID?"
```

### Video Support
Upload video files (MP4, AVI, MOV, MKV, WebM, GIF) for analysis:

```bash
# Upload video and extract best frame
curl -X POST "http://localhost:8000/upload/video" \
     -F "file=@pid_video.mp4"

# Ask questions about the extracted frame
curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{"image_id": "video_id", "query": "What does FIC-101 do?"}'
```

### Knowledge Base
The system includes a comprehensive knowledge base with:
- **50+ ISA-5.1 instrument tags** (FIC, PIC, TIC, LIC, etc.)
- **Process equipment definitions** (pumps, valves, tanks, heat exchangers)
- **Control logic explanations** (flow control, pressure control, level control)
- **Safety systems** (pressure relief, emergency shutdown)
- **Common issues** (missing tags, broken lines, unknown symbols)

### Demo Test
Run the RAG test suite to see it in action:

```bash
cd backend
python test_rag.py
```

See [RAG_DOCUMENTATION.md](RAG_DOCUMENTATION.md) for comprehensive RAG system documentation.

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/upload` | POST | Upload P&ID image |
| `/upload/video` | POST | Upload P&ID video |
| `/analyze` | POST | Run complete analysis |
| `/run/{type}` | POST | Run specific analysis (validate/ocr/graph) |
| `/export` | POST | Export results (JSON/CSV) |
| `/query` | POST | RAG query processing |
| `/models/load` | POST | Load custom YOLO model |
| `/models/info` | GET | Get model information |
| `/knowledge-base/info` | GET | Get knowledge base statistics |

## 🔍 Analysis Pipeline

1. **Image/Video Preprocessing**: PDF rasterization, format conversion, frame extraction
2. **Symbol Detection**: YOLO inference with confidence scoring
3. **Line Extraction**: Hough transform with junction identification
4. **OCR Processing**: Text extraction and symbol association
5. **Graph Assembly**: Process flow construction and validation
6. **Issue Detection**: Quality checks and problem flagging
7. **RAG Processing**: Knowledge base retrieval and query answering
8. **Export Generation**: Structured output in multiple formats

## 📈 Export Formats

### DEXPI-lite JSON
Industry-standard format with equipment, instruments, connections, and metadata.

### CSV Export
Separate files for nodes, edges, and issues with comprehensive attributes.

### ISO 15926 Ready
Optional mapping to ISO 15926 classes for enterprise integration.

## 🎯 Use Cases

- **Engineering Documentation**: Convert legacy P&IDs to digital format
- **Process Analysis**: Extract process flow for simulation and analysis
- **Asset Management**: Create equipment inventories from diagrams
- **Compliance**: Validate diagrams against industry standards
- **Training**: Generate structured data for operator training systems

## 🔧 Configuration

### YOLO Model Settings
Edit `models/config.yaml`:
```yaml
model_path: "your_model.pt"
confidence_threshold: 0.5
symbol_classes: [pump, valve_manual, instrument_bubble, ...]
```

### Analysis Parameters
- Confidence thresholds for symbol detection
- OCR preprocessing options
- Line detection sensitivity
- Validation rule sets

## 🚧 Current Limitations

- **Curved Pipes**: Limited to straight line detection
- **Multi-page**: Single page processing only
- **Symbol Rotation**: Basic rotation handling
- **Text Association**: Proximity-based linking

## 🚀 Roadmap

- [ ] **Curved Pipe Detection**: Spline fitting and contour analysis
- [ ] **Multi-page Support**: Batch processing for large documents
- [ ] **Real-time Processing**: Stream processing for live diagrams
- [ ] **Advanced OCR**: Layout-aware text extraction
- [ ] **3D Support**: Z-axis information extraction
- [ ] **Cloud Deployment**: Scalable cloud infrastructure

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Implement improvements
4. Add tests and documentation
5. Submit pull request

## 📚 Documentation

### User Guides
- [Quick Start Guide](docs/guides/quickstart.md)
- [User Guide](docs/guides/user_guide.md)
- [Developer Guide](docs/guides/developer_guide.md)

### API Reference
- [API Overview](docs/api/api_reference.md)
- [Query API](docs/api/query_api.md)
- [Analysis API](docs/api/analysis_api.md)

### Technical Documentation
- [System Architecture](docs/architecture/system_overview.md)
- [AI/ML Architecture](docs/architecture/ai_ml_architecture.md)
- [RAG Documentation](RAG_DOCUMENTATION.md)
- [YOLO Integration](YOLO_INTEGRATION.md)
- [Troubleshooting](TROUBLESHOOTING.md)

## 📄 License

This project is developed for educational and research purposes. Please ensure compliance with relevant licenses when using third-party models or datasets.

---

**Built with ❤️ for the Industrial AI community**
