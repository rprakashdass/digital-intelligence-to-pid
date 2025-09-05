from fastapi import FastAPI, File, UploadFile, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
import os
import uuid
import io
import zipfile
from pydantic import BaseModel
from typing import List, Optional

# Import your models and services
from backend.models import Graph
# Assume other services will be created
# from backend.services import ocr, symbols, lines, tagging, graph, validate, export, pdf

app = FastAPI()

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Enable CORS for all routes with additional headers for debugging
@app.middleware("http")
async def add_cors_headers(request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

TEMP_DIR = "temp_images"
MODELS_DIR = "models"  # Directory for YOLO models
VIDEO_DIR = "temp_videos"  # Directory for video uploads
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)

class IngestResponse(BaseModel):
    image_id: str
    filename: str
    content_type: str

class AnalyzeRequest(BaseModel):
    image_id: str
    options: Optional[dict] = None

class ExportRequest(BaseModel):
    image_id: str
    format: str # "json" or "csv"

class ModelLoadRequest(BaseModel):
    model_path: str
    conf_threshold: Optional[float] = 0.5

class RAGQueryRequest(BaseModel):
    image_id: str
    query: str

class VideoUploadResponse(BaseModel):
    video_id: str
    filename: str
    content_type: str
    frame_extracted: bool
    frame_path: Optional[str] = None

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/models/info")
async def get_model_info():
    """Get information about the currently loaded YOLO model."""
    try:
        from backend.services import yolo_symbols
        return yolo_symbols.get_yolo_model_info()
    except ImportError:
        return {"status": "yolo_service_not_available"}

@app.post("/models/load")
async def load_yolo_model(request: ModelLoadRequest):
    """Load a custom YOLO model for symbol detection."""
    try:
        from backend.services import yolo_symbols
        
        # Check if model file exists
        model_path = request.model_path
        if not os.path.isabs(model_path):
            model_path = os.path.join(MODELS_DIR, model_path)
        
        if not os.path.exists(model_path):
            raise HTTPException(status_code=404, detail=f"Model file not found: {model_path}")
        
        # Load the model
        success = yolo_symbols.yolo_detector.load_model(model_path)
        if success:
            yolo_symbols.yolo_detector.conf_threshold = request.conf_threshold
            return {"status": "success", "message": f"Model loaded from {model_path}"}
        else:
            raise HTTPException(status_code=500, detail="Failed to load model")
            
    except ImportError:
        raise HTTPException(status_code=500, detail="YOLO service not available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading model: {str(e)}")

@app.post("/ingest", response_model=IngestResponse)
async def ingest_image(file: UploadFile = File(...)):
    """
    Handles image upload, saves it temporarily, and returns an ID.
    """
    if not file.content_type.startswith('image/'):
        # A simple check for PDFs, which we might handle differently
        if file.content_type != 'application/pdf':
            raise HTTPException(status_code=415, detail="Unsupported file type. Please upload an image or a single-page PDF.")

    image_id = str(uuid.uuid4())
    file_extension = os.path.splitext(file.filename)[1]
    temp_file_path = os.path.join(TEMP_DIR, f"{image_id}{file_extension}")

    try:
        with open(temp_file_path, "wb") as buffer:
            buffer.write(await file.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save file: {e}")

    return IngestResponse(
        image_id=image_id,
        filename=file.filename,
        content_type=file.content_type
    )

@app.post("/upload", response_model=IngestResponse)
async def upload_image(file: UploadFile = File(...)):
    """
    Alias for /ingest to match frontend expectations.
    """
    return await ingest_image(file)

@app.post("/analyze", response_model=Graph)
async def analyze_image(request: AnalyzeRequest):
    """
    Triggers the full analysis pipeline on a previously ingested image.
    """
    print("Starting analysis pipeline...")
    try:
        # Test imports first to catch any issues
        from backend.models import Graph, Node, Edge, Text, BoundingBox, Issue
        print("Successfully imported models")
    except Exception as e:
        print(f"Error importing models: {e}")
        raise HTTPException(status_code=500, detail=f"Error importing models: {str(e)}")
    image_id = request.image_id
    # Find the image file
    temp_file_path = None
    for ext in ['.png', '.jpg', '.jpeg', '.pdf']:
        path = os.path.join(TEMP_DIR, f"{image_id}{ext}")
        if os.path.exists(path):
            temp_file_path = path
            break
    
    if not temp_file_path:
        raise HTTPException(status_code=404, detail=f"Image with ID {image_id} not found.")

    # Handle PDF rasterization if necessary
    if temp_file_path.endswith('.pdf'):
        try:
            from backend.services import pdf
            png_path = os.path.join(TEMP_DIR, f"{image_id}.png")
            pdf.rasterize_pdf_to_image(temp_file_path, png_path)
            temp_file_path = png_path
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to process PDF: {e}")

    # --- Run Analysis Pipeline ---
    from backend.services import ocr, lines, tagging, graph, validate
    
    # Use YOLO for symbol detection if available, otherwise fallback to template matching
    try:
        from backend.services import yolo_symbols
        detection_result = yolo_symbols.detect_symbols_yolo(temp_file_path)
    except ImportError:
        from backend.services import symbols
        detection_result = symbols.detect_symbols(temp_file_path)
    
    detected_symbols = detection_result["nodes"]
    symbol_issues = detection_result["issues"]

    # 1. OCR
    texts = ocr.ocr_image(temp_file_path)

    # 2. Line and Junction Extraction
    line_edges, junction_nodes = lines.extract_lines_and_junctions(temp_file_path)

    # 3. Assemble the graph
    initial_graph = graph.assemble_graph(detected_symbols, line_edges, junction_nodes, texts)

    # 4. Parse tags
    for node in initial_graph.nodes:
        if node.tag:
            parsed_tag = tagging.parse_isa_tag(node.tag)
            if parsed_tag.isParsed:
                node.attributes['parsed_tag'] = parsed_tag.model_dump()

    # 5. Validate the graph
    validation_issues = validate.validate_graph(initial_graph)
    
    # Combine symbol issues with validation issues
    all_issues = symbol_issues + validation_issues
    initial_graph.issues = all_issues

    return initial_graph

@app.post("/export")
async def export_data(request: ExportRequest):
    """
    Exports the analysis results in the specified format (JSON or CSV).
    """
    image_id = request.image_id
    # Find the image file
    temp_file_path = None
    for ext in ['.png', '.jpg', '.jpeg', '.pdf']:
        path = os.path.join(TEMP_DIR, f"{image_id}{ext}")
        if os.path.exists(path):
            temp_file_path = path
            break

    if not temp_file_path:
        raise HTTPException(status_code=404, detail=f"Image with ID {image_id} not found.")

    # Re-run the analysis to get the latest graph (could be cached in a real system)
    from backend.services import ocr, lines, tagging, graph, validate, export

    # Handle PDF rasterization if necessary
    if temp_file_path.endswith('.pdf'):
        try:
            from backend.services import pdf
            png_path = os.path.join(TEMP_DIR, f"{image_id}.png")
            pdf.rasterize_pdf_to_image(temp_file_path, png_path)
            temp_file_path = png_path
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to process PDF: {e}")

    texts = ocr.ocr_image(temp_file_path)
    
    # Use YOLO for symbol detection if available
    try:
        from backend.services import yolo_symbols
        detection_result = yolo_symbols.detect_symbols_yolo(temp_file_path)
    except ImportError:
        from backend.services import symbols
        detection_result = symbols.detect_symbols(temp_file_path)
    
    detected_symbols = detection_result["nodes"]
    symbol_issues = detection_result["issues"]
    
    line_edges, junction_nodes = lines.extract_lines_and_junctions(temp_file_path)
    final_graph = graph.assemble_graph(detected_symbols, line_edges, junction_nodes, texts)

    for node in final_graph.nodes:
        if node.tag:
            parsed_tag = tagging.parse_isa_tag(node.tag)
            if parsed_tag.isParsed:
                node.attributes['parsed_tag'] = parsed_tag.model_dump()

    validation_issues = validate.validate_graph(final_graph)
    final_graph.issues = symbol_issues + validation_issues

    # --- Export Logic ---
    if request.format == "json":
        json_str = export.to_dexpi_lite_json(final_graph)
        return Response(
            content=json_str,
            media_type='application/json',
            headers={'Content-Disposition': f'attachment; filename="{image_id}_dexpi_lite.json"'}
        )
    elif request.format == "csv":
        csv_files = export.to_csv(final_graph)

        # Create a zip file in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            zip_file.writestr("nodes.csv", csv_files["nodes"])
            zip_file.writestr("edges.csv", csv_files["edges"])

        zip_buffer.seek(0)
        return StreamingResponse(
            zip_buffer,
            media_type='application/zip',
            headers={'Content-Disposition': f'attachment; filename="{image_id}_csv_export.zip"'}
        )
    else:
        raise HTTPException(status_code=400, detail="Unsupported format. Use 'json' or 'csv'.")

@app.post("/run/{type}")
async def run_analysis(type: str):
    """
    API endpoint for various analysis operations (validate, ocr, graph, export)
    to match frontend expectations.
    """
    print(f"Starting analysis: {type}")
    
    # Get the most recent image ID (or eventually store it in a session)
    image_files = os.listdir(TEMP_DIR)
    if not image_files:
        raise HTTPException(status_code=404, detail="No images uploaded yet")
    
    # Get most recent file
    image_paths = [os.path.join(TEMP_DIR, f) for f in image_files if os.path.isfile(os.path.join(TEMP_DIR, f))]
    if not image_paths:
        raise HTTPException(status_code=404, detail="No valid image files found")
        
    try:
        most_recent = max(image_paths, key=os.path.getctime)
        print(f"Using most recent file: {most_recent}")
        image_id = os.path.splitext(os.path.basename(most_recent))[0]
    except Exception as e:
        print(f"Error finding most recent file: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing image files: {str(e)}")
    
    # Handle different analysis types
    try:
        if type == "export":
            print("Handling export request")
            request = ExportRequest(image_id=image_id, format="json")
            return await export_data(request)
        elif type in ["validate", "ocr", "graph"]:
            print(f"Handling {type} analysis request")
            request = AnalyzeRequest(image_id=image_id, options={"type": type})
            result = await analyze_image(request)
            
            print(f"Analysis complete, processing results for {type}")
            # Return only the relevant part of the analysis based on type
            if type == "validate":
                return {"issues": result.issues}
            elif type == "ocr":
                return {"texts": [text.model_dump() for text in result.texts]}
            elif type == "graph":
                print(f"Returning graph with {len(result.nodes)} nodes, {len(result.edges)} edges, {len(result.texts)} texts")
                return result
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported analysis type: {type}")
    except Exception as e:
        print(f"Error in run_analysis for {type}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing {type} request: {str(e)}")

@app.post("/upload/video", response_model=VideoUploadResponse)
async def upload_video(file: UploadFile = File(...)):
    """
    Handles video upload, extracts best frame, and returns frame for analysis.
    """
    # Check if it's a supported video format
    from backend.services import video
    if not video.video_processor.is_supported_format(file.filename):
        raise HTTPException(status_code=415, detail="Unsupported video format. Supported: MP4, AVI, MOV, MKV, WebM, GIF")

    video_id = str(uuid.uuid4())
    file_extension = os.path.splitext(file.filename)[1]
    temp_file_path = os.path.join(VIDEO_DIR, f"{video_id}{file_extension}")

    try:
        # Save video file
        with open(temp_file_path, "wb") as buffer:
            buffer.write(await file.read())
        
        # Process video to extract best frame
        result = video.process_video_for_analysis(temp_file_path)
        
        if result['success']:
            # Move frame to temp_images directory for analysis
            frame_filename = f"{video_id}_frame.png"
            frame_path = os.path.join(TEMP_DIR, frame_filename)
            
            import shutil
            shutil.move(result['frame_path'], frame_path)
            
            return VideoUploadResponse(
                video_id=video_id,
                filename=file.filename,
                content_type=file.content_type,
                frame_extracted=True,
                frame_path=frame_path
            )
        else:
            raise HTTPException(status_code=500, detail=f"Failed to extract frame: {result['error']}")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not process video: {e}")

@app.post("/query")
async def rag_query(request: RAGQueryRequest):
    """
    Process a natural language query about a P&ID diagram using RAG.
    """
    try:
        print(f"Processing RAG query: {request.query} for image_id: {request.image_id}")
        
        # Find the image file
        image_id = request.image_id
        temp_file_path = None
        for ext in ['.png', '.jpg', '.jpeg', '.pdf']:
            path = os.path.join(TEMP_DIR, f"{image_id}{ext}")
            if os.path.exists(path):
                temp_file_path = path
                break
        
        if not temp_file_path:
            print(f"Error: Image with ID {image_id} not found.")
            raise HTTPException(status_code=404, detail=f"Image with ID {image_id} not found.")

        print(f"Found image at: {temp_file_path}")
        
        # Create a simple default graph if analysis fails
        from backend.models import Graph, Node, Edge, Text, BoundingBox, Issue
        default_graph = Graph(nodes=[], edges=[], texts=[], issues=[])
        
        # Try to run analysis to get the graph
        try:
            from backend.services import ocr, lines, tagging, graph, validate
            
            # Use YOLO for symbol detection if available
            try:
                from backend.services import yolo_symbols
                print("Checking YOLO dependencies...")
                # Explicitly check for torch to avoid cryptic errors
                try:
                    import torch
                    print(f"PyTorch version: {torch.__version__}")
                    detection_result = yolo_symbols.detect_symbols_yolo(temp_file_path)
                    print(f"YOLO detection completed successfully")
                except ImportError:
                    print("PyTorch not installed. Using template matching instead.")
                    raise ImportError("PyTorch not installed")
            except (ImportError, Exception) as e:
                print(f"YOLO error: {e}, falling back to template matching")
                from backend.services import symbols
                print("Using template matching for symbol detection")
                detection_result = symbols.detect_symbols(temp_file_path)
            
            print(f"Symbol detection completed: {len(detection_result['nodes'])} symbols detected")
            detected_symbols = detection_result["nodes"]
            symbol_issues = detection_result["issues"]
            
            print("Running OCR on image...")
            texts = ocr.ocr_image(temp_file_path)
            print(f"OCR completed: {len(texts)} text elements detected")
            
            print("Extracting lines and junctions...")
            line_edges, junction_nodes = lines.extract_lines_and_junctions(temp_file_path)
            print(f"Line extraction completed: {len(line_edges)} lines, {len(junction_nodes)} junctions detected")
            
            print("Assembling graph...")
            analysis_graph = graph.assemble_graph(detected_symbols, line_edges, junction_nodes, texts)
            print(f"Graph assembled: {len(analysis_graph.nodes)} nodes, {len(analysis_graph.edges)} edges")

            print("Processing tags...")
            for node in analysis_graph.nodes:
                if node.tag:
                    try:
                        parsed_tag = tagging.parse_isa_tag(node.tag)
                        if parsed_tag.isParsed:
                            node.attributes['parsed_tag'] = parsed_tag.model_dump()
                    except Exception as e:
                        print(f"Error parsing tag {node.tag}: {e}")

            print("Validating graph...")
            validation_issues = validate.validate_graph(analysis_graph)
            analysis_graph.issues = symbol_issues + validation_issues
            print(f"Validation completed: {len(analysis_graph.issues)} issues identified")
        except Exception as e:
            import traceback
            print(f"Error in analysis pipeline: {e}")
            print(traceback.format_exc())
            print("Using default empty graph for RAG query")
            analysis_graph = default_graph

        # Process RAG query with fallback handling
        try:
            from backend.services import rag
            print(f"Processing query: '{request.query}'")
            rag_response = rag.answer_pid_query(request.query, analysis_graph)
            print("RAG query processed successfully")
        except Exception as e:
            import traceback
            print(f"Error in RAG service: {e}")
            print(traceback.format_exc())
            
            # Create a simple fallback response
            rag_response = {
                'answer': f"I'm sorry, I couldn't analyze the diagram properly. The diagram contains {len(analysis_graph.nodes)} symbols, {len(analysis_graph.texts)} text elements, and {len(analysis_graph.edges)} connections.",
                'query': request.query,
                'confidence': 0.1,
                'knowledge_sources': []
            }
        
        return {
            "query": request.query,
            "answer": rag_response.get('answer', "Sorry, I couldn't analyze this diagram."),
            "confidence": rag_response.get('confidence', 0.1),
            "knowledge_sources": rag_response.get('knowledge_sources', []),
            "analysis_summary": {
                "symbols_detected": len(analysis_graph.nodes),
                "text_elements": len(analysis_graph.texts),
                "issues_found": len(analysis_graph.issues)
            }
        }
            
    except Exception as e:
        import traceback
        print(f"Error processing query: {e}")
        print(traceback.format_exc())
        
        # Return a useful error response
        return JSONResponse(
            status_code=500,
            content={
                "query": getattr(request, "query", "Unknown query"),
                "error": f"Error processing query: {str(e)}",
                "answer": "I'm sorry, I encountered an error while processing your request.",
                "confidence": 0.0,
                "knowledge_sources": [],
                "analysis_summary": {
                    "symbols_detected": 0,
                    "text_elements": 0,
                    "issues_found": 1
                }
            }
        )

@app.get("/knowledge-base/info")
async def get_knowledge_base_info():
    """Get information about the loaded knowledge base."""
    try:
        from backend.services import rag
        
        kb_info = {
            "instrument_tags": len(rag.rag_service.knowledge_base.get('instrument_tags', {})),
            "equipment": len(rag.rag_service.knowledge_base.get('equipment', {})),
            "process_logic": len(rag.rag_service.knowledge_base.get('process_logic', {})),
            "safety_systems": len(rag.rag_service.knowledge_base.get('safety_systems', {})),
            "common_issues": len(rag.rag_service.knowledge_base.get('common_issues', {})),
            "embedding_model_loaded": rag.rag_service.embedding_model is not None
        }
        
        return kb_info
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting knowledge base info: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
