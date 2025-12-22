"""
FastAPI wrapper for AI Video Generator
Allows remote video processing via HTTP API
Perfect for running on RunPod and accessing from local machine
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import shutil
from pathlib import Path
import uuid
from datetime import datetime

# Import your video processor
from models.processor import VideoProcessor
from models.config_loader import ModelConfig

app = FastAPI(title="AI Video Generator API", version="1.0")

# Enable CORS for web access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directories
UPLOAD_DIR = Path("api_uploads")
OUTPUT_DIR = Path("api_outputs")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Initialize processor
processor = VideoProcessor()
config = ModelConfig()

# Job tracking
jobs = {}

@app.get("/")
def read_root():
    """API health check"""
    return {
        "status": "online",
        "service": "AI Video Generator",
        "version": "1.0",
        "endpoints": {
            "process": "/process",
            "status": "/status/{job_id}",
            "download": "/download/{job_id}",
            "models": "/models"
        }
    }

@app.get("/models")
def list_models():
    """Get available model configurations"""
    models = config.list_models()
    return {
        "available_models": models,
        "default": "default_model"
    }

@app.post("/process")
async def process_video(
    video: UploadFile = File(...),
    model_name: str = Form("default_model")
):
    """
    Process a video with AI model replacement
    
    Args:
        video: Video file to process
        model_name: Model configuration to use (default: default_model)
    
    Returns:
        job_id: Use this to check status and download result
    """
    # Validate model exists
    if model_name not in config.list_models():
        raise HTTPException(status_code=400, detail=f"Model '{model_name}' not found")
    
    # Generate unique job ID
    job_id = str(uuid.uuid4())
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save uploaded video
    input_path = UPLOAD_DIR / f"{job_id}_{timestamp}_{video.filename}"
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(video.file, buffer)
    
    output_path = OUTPUT_DIR / f"{job_id}_processed.mp4"
    
    # Store job info
    jobs[job_id] = {
        "status": "processing",
        "input": str(input_path),
        "output": str(output_path),
        "model": model_name,
        "created_at": timestamp,
        "progress": 0
    }
    
    try:
        # Process video (synchronous for now)
        result_path = processor.replace_model(
            str(input_path),
            str(output_path),
            model_name=model_name
        )
        
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["progress"] = 100
        
        # Clean up input file
        os.remove(input_path)
        
        return {
            "job_id": job_id,
            "status": "completed",
            "message": "Video processed successfully",
            "download_url": f"/download/{job_id}"
        }
        
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.get("/status/{job_id}")
def get_status(job_id: str):
    """Check processing status of a job"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return jobs[job_id]

@app.get("/download/{job_id}")
def download_result(job_id: str):
    """Download processed video"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    
    if job["status"] != "completed":
        raise HTTPException(
            status_code=400, 
            detail=f"Video not ready. Status: {job['status']}"
        )
    
    output_path = job["output"]
    if not os.path.exists(output_path):
        raise HTTPException(status_code=404, detail="Output file not found")
    
    return FileResponse(
        output_path,
        media_type="video/mp4",
        filename=f"processed_{job_id}.mp4"
    )

@app.delete("/cleanup/{job_id}")
def cleanup_job(job_id: str):
    """Delete job files and data"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    
    # Remove output file if exists
    if os.path.exists(job["output"]):
        os.remove(job["output"])
    
    # Remove input file if exists
    if os.path.exists(job["input"]):
        os.remove(job["input"])
    
    # Remove job record
    del jobs[job_id]
    
    return {"status": "deleted", "job_id": job_id}

if __name__ == "__main__":
    print("🚀 Starting AI Video Generator API...")
    print("📡 API will be available at:")
    print("   - Local: http://localhost:8000")
    print("   - RunPod: Use the HTTP Service proxy URL")
    print("\n📚 API Docs: http://localhost:8000/docs")
    
    uvicorn.run(
        app, 
        host="0.0.0.0",  # Allow external access
        port=8000,
        log_level="info"
    )
