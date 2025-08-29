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
from .models import Graph
# Assume other services will be created
# from .services import ocr, symbols, lines, tagging, graph, validate, export, pdf

app = FastAPI()

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

TEMP_DIR = "temp_images"
os.makedirs(TEMP_DIR, exist_ok=True)

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

@app.get("/health")
async def health_check():
    return {"status": "ok"}

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
            from .services import pdf
            png_path = os.path.join(TEMP_DIR, f"{image_id}.png")
            pdf.rasterize_pdf_to_image(temp_file_path, png_path)
            temp_file_path = png_path
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to process PDF: {e}")

    # --- Run Analysis Pipeline ---
    from .services import ocr, symbols, lines, tagging, graph, validate

    # 1. OCR
    texts = ocr.ocr_image(temp_file_path)

    # 2. Symbol Detection
    detection_result = symbols.detect_symbols(temp_file_path)
    detected_symbols = detection_result["nodes"]
    symbol_issues = detection_result["issues"]

    # 3. Line and Junction Extraction
    line_edges, junction_nodes = lines.extract_lines_and_junctions(temp_file_path)

    # 4. Assemble the graph
    initial_graph = graph.assemble_graph(detected_symbols, line_edges, junction_nodes, texts)

    # 5. Parse tags
    for node in initial_graph.nodes:
        if node.tag:
            parsed_tag = tagging.parse_isa_tag(node.tag)
            if parsed_tag.isParsed:
                node.attributes['parsed_tag'] = parsed_tag.model_dump()

    # 6. Validate the graph
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
    
@app.post("/run/{type}")
async def run_analysis(type: str):
    """
    API endpoint for various analysis operations (validate, ocr, graph, export)
    to match frontend expectations.
    """
    # Get the most recent image ID (or eventually store it in a session)
    image_files = os.listdir(TEMP_DIR)
    if not image_files:
        raise HTTPException(status_code=404, detail="No images uploaded yet")
    
    # Get most recent file
    image_paths = [os.path.join(TEMP_DIR, f) for f in image_files]
    most_recent = max(image_paths, key=os.path.getctime)
    image_id = os.path.splitext(os.path.basename(most_recent))[0]
    
    # Handle different analysis types
    if type == "export":
        request = ExportRequest(image_id=image_id, format="json")
        return await export_data(request)
    elif type in ["validate", "ocr", "graph"]:
        request = AnalyzeRequest(image_id=image_id, options={"type": type})
        result = await analyze_image(request)
        
        # Return only the relevant part of the analysis based on type
        if type == "validate":
            return {"issues": result.issues}
        elif type == "ocr":
            return {"texts": [text.model_dump() for text in result.texts]}
        elif type == "graph":
            return result
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported analysis type: {type}")
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

    # Re-run the analysis to get the graph data
    # (In a real app, you might cache this result)
    from .services import ocr, symbols, lines, tagging, graph, validate, export
    if temp_file_path.endswith('.pdf'):
        try:
            from .services import pdf
            png_path = os.path.join(TEMP_DIR, f"{image_id}.png")
            pdf.rasterize_pdf_to_image(temp_file_path, png_path)
            temp_file_path = png_path
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to process PDF: {e}")

    texts = ocr.ocr_image(temp_file_path)
    detected_symbols = symbols.detect_symbols(temp_file_path)
    line_edges, junction_nodes = lines.extract_lines_and_junctions(temp_file_path)
    final_graph = graph.assemble_graph(detected_symbols, line_edges, junction_nodes, texts)
    for node in final_graph.nodes:
        if node.tag:
            parsed_tag = tagging.parse_isa_tag(node.tag)
            if parsed_tag.isParsed:
                node.attributes['parsed_tag'] = parsed_tag.model_dump()
    final_graph.issues = validate.validate_graph(final_graph)

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
