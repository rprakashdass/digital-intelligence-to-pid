# Troubleshooting Guide

## WebSocket Connection Issues

### Problem: WebSocket connection to 'ws://localhost:5173' failed

This is a common Vite development server issue related to Hot Module Replacement (HMR).

### Solutions:

#### 1. **Restart Development Servers**
```bash
# Stop all running servers (Ctrl+C)
# Then restart in the correct order:

# Terminal 1: Backend
cd backend
uvicorn main:app --reload --port 8000

# Terminal 2: Frontend (wait 3 seconds after backend starts)
cd frontend
npm run dev
```

#### 2. **Use the Development Scripts**
```bash
# Windows
start_dev.bat

# Linux/Mac
chmod +x start_dev.sh
./start_dev.sh
```

#### 3. **Clear Browser Cache**
- Hard refresh: `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac)
- Clear browser cache and cookies for localhost
- Try incognito/private browsing mode

#### 4. **Check Port Availability**
```bash
# Check if ports are in use
netstat -an | findstr :5173  # Windows
lsof -i :5173                # Mac/Linux

# Kill processes if needed
taskkill /PID <PID> /F       # Windows
kill -9 <PID>                # Mac/Linux
```

#### 5. **Update Vite Configuration**
The `vite.config.js` has been updated with proper HMR settings:
```javascript
server: {
  port: 5173,
  host: true,
  hmr: {
    port: 5173,
    host: 'localhost'
  },
  cors: true
}
```

#### 6. **Alternative Ports**
If port 5173 is problematic, try different ports:
```bash
# Frontend on different port
npm run dev -- --port 3000

# Update vite.config.js accordingly
```

## Backend Connection Issues

### Problem: Cannot connect to backend API

#### 1. **Check Backend Status**
```bash
curl http://localhost:8000/health
# Should return: {"status": "ok"}
```

#### 2. **Verify CORS Settings**
The backend has CORS enabled for all origins:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 3. **Check API Endpoints**
```bash
# Test upload endpoint
curl -X POST http://localhost:8000/upload \
     -F "file=@test_image.png"

# Test RAG endpoint
curl -X POST http://localhost:8000/query \
     -H "Content-Type: application/json" \
     -d '{"image_id": "test", "query": "test"}'
```

## RAG System Issues

### Problem: RAG queries not working

#### 1. **Check Dependencies**
```bash
cd backend
pip install sentence-transformers openai
```

#### 2. **Test Knowledge Base**
```bash
cd backend
python test_rag.py
```

#### 3. **Check Knowledge Base File**
```bash
# Verify knowledge base exists
ls -la backend/data/knowledge_base.json

# Check file content
head -20 backend/data/knowledge_base.json
```

#### 4. **Environment Variables**
```bash
# Optional: Set OpenAI API key for enhanced responses
export OPENAI_API_KEY="your-api-key-here"

# Optional: Set custom Tesseract path
export TESSERACT_PATH="/path/to/tesseract"
```

## Video Processing Issues

### Problem: Video upload fails

#### 1. **Check Supported Formats**
Supported formats: MP4, AVI, MOV, MKV, WebM, GIF

#### 2. **Verify OpenCV Installation**
```bash
python -c "import cv2; print(cv2.__version__)"
```

#### 3. **Check File Size**
Large video files may cause timeouts. Try smaller files first.

#### 4. **Test Video Processing**
```python
from backend.services.video import VideoProcessor
processor = VideoProcessor()
result = processor.process_video_for_analysis("test_video.mp4")
print(result)
```

## YOLO Model Issues

### Problem: YOLO model not loading

#### 1. **Check Model File**
```bash
ls -la backend/models/
```

#### 2. **Install Dependencies**
```bash
pip install torch torchvision ultralytics
```

#### 3. **Test Model Loading**
```bash
cd backend
python -c "from services.yolo_symbols import YOLOSymbolDetector; print('YOLO service loaded')"
```

#### 4. **Load Model via API**
```bash
curl -X POST http://localhost:8000/models/load \
     -H "Content-Type: application/json" \
     -d '{"model_path": "models/your_model.pt", "conf_threshold": 0.5}'
```

## OCR Issues

### Problem: Text detection not working

#### 1. **Check Tesseract Installation**
```bash
tesseract --version
```

#### 2. **Test OCR Service**
```python
from backend.services.ocr import ocr_image
result = ocr_image("test_image.png")
print(result)
```

#### 3. **Update Tesseract Path**
Edit `backend/services/ocr.py` and update the path:
```python
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

## General Development Issues

### Problem: Frontend not updating

#### 1. **Check File Watching**
```bash
# Increase file watcher limit (Linux/Mac)
echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

#### 2. **Restart with Clean Cache**
```bash
cd frontend
rm -rf node_modules/.vite
npm run dev
```

### Problem: Build Errors

#### 1. **Clear All Caches**
```bash
# Frontend
cd frontend
rm -rf node_modules dist .vite
npm install
npm run build

# Backend
cd backend
rm -rf __pycache__ .pytest_cache
pip install -r requirements.txt
```

#### 2. **Check Node Version**
```bash
node --version  # Should be 16+ for React 19
npm --version
```

## Performance Issues

### Problem: Slow analysis

#### 1. **Use GPU for YOLO**
```bash
# Check CUDA availability
python -c "import torch; print(torch.cuda.is_available())"
```

#### 2. **Optimize Image Size**
- Resize large images before upload
- Use appropriate image formats (PNG for diagrams)

#### 3. **Reduce Analysis Scope**
- Use specific analysis types (validate, ocr, graph) instead of full analysis
- Lower confidence thresholds for faster processing

## Getting Help

### 1. **Check Logs**
```bash
# Backend logs
tail -f backend/logs/app.log

# Frontend logs (browser console)
F12 -> Console tab
```

### 2. **Enable Debug Mode**
```python
# Backend
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 3. **Test Individual Components**
```bash
# Test backend health
curl http://localhost:8000/health

# Test knowledge base
curl http://localhost:8000/knowledge-base/info

# Test model info
curl http://localhost:8000/models/info
```

### 4. **Common Error Messages**

| Error | Solution |
|-------|----------|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| `Connection refused` | Check if backend is running on port 8000 |
| `WebSocket failed` | Restart frontend server, clear browser cache |
| `Tesseract not found` | Install Tesseract OCR and set correct path |
| `CUDA out of memory` | Use CPU mode or smaller batch sizes |

## Still Having Issues?

1. **Check the main README.md** for setup instructions
2. **Run the test suite**: `python backend/test_rag.py`
3. **Verify all dependencies** are installed correctly
4. **Check system requirements** (Python 3.8+, Node 16+)
5. **Try the development scripts** (`start_dev.bat` or `start_dev.sh`)

The WebSocket errors you're seeing are typically resolved by restarting the development servers in the correct order and clearing browser cache.
