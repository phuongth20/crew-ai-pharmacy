from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import asyncio
import os
import json
from datetime import datetime

from .crew import PharmacyTechnicianCrew
from .tools import Database

app = FastAPI(
    title="Pharmacy Technician LinkedIn Agent API",
    description="API for automating LinkedIn searches for Pharmacy Technicians",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

background_jobs = {}

class SearchRequest(BaseModel):
    criteria: str
    job_description: Optional[str] = None

class CandidateResponse(BaseModel):
    id: int
    name: str
    position: str
    location: str
    profile_link: str
    experience: Optional[str] = None
    certifications: Optional[str] = None
    skills: Optional[str] = None
    workplace: Optional[str] = None
    score: Optional[float] = None

class OutreachRequest(BaseModel):
    candidate_id: int
    message_template: str
    strategy: Optional[str] = "Standard outreach"

class ReportRequest(BaseModel):
    search_criteria: Optional[str] = None
    top_candidates_count: Optional[int] = 10

class JobStatus(BaseModel):
    job_id: str
    status: str
    start_time: str
    end_time: Optional[str] = None
    result: Optional[Dict[str, Any]] = None

async def run_linkedin_search(job_id: str, criteria: str):
    try:
        background_jobs[job_id]["status"] = "running"
        
        # Initialize and run CrewAI crew
        crew = PharmacyTechnicianCrew()
        results = crew.crew().kickoff(inputs={"criteria": criteria}) 
        
        # Update job with results
        background_jobs[job_id]["status"] = "completed"
        background_jobs[job_id]["end_time"] = datetime.now().isoformat()
        background_jobs[job_id]["result"] = {"message": "Search completed successfully", "details": results}
        
    except Exception as e:
        background_jobs[job_id]["status"] = "failed"
        background_jobs[job_id]["end_time"] = datetime.now().isoformat()
        background_jobs[job_id]["result"] = {"error": str(e)}

@app.post("/api/search", response_model=Dict[str, str])
async def search_linkedin(search_request: SearchRequest, background_tasks: BackgroundTasks):
    job_id = f"search_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    background_jobs[job_id] = {
        "status": "queued",
        "start_time": datetime.now().isoformat(),
        "end_time": None,
        "result": None
    }
    
    # Start background task
    background_tasks.add_task(run_linkedin_search, job_id, search_request.criteria)
    
    return {"job_id": job_id, "message": "Search job started"}


@app.get("/api/candidates", response_model=List[CandidateResponse])
async def get_candidates(
    limit: int = Query(100, description="Maximum number of candidates to return"),
    offset: int = Query(0, description="Number of candidates to skip")
):
    """Get all candidates from the database"""
    try:
        db = Database()
        candidates = db.get_candidates(limit, offset)
        db.close()
        return candidates
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/candidates/top", response_model=List[CandidateResponse])
async def get_top_candidates(
    limit: int = Query(10, description="Number of top candidates to return")
):
    """Get top scored candidates from the database"""
    try:
        db = Database()
        candidates = db.get_top_candidates(limit)
        db.close()
        return candidates
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/candidates/{candidate_id}", response_model=CandidateResponse)
async def get_candidate(candidate_id: int):
    """Get a specific candidate by ID"""
    try:
        db = Database()
        candidate = db.get_candidate_by_id(candidate_id)
        db.close()
        
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
            
        return candidate
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


    """Generate a comprehensive report on candidates"""
    job_id = f"report_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    background_jobs[job_id] = {
        "status": "queued",
        "start_time": datetime.now().isoformat(),
        "end_time": None,
        "result": None
    }
    
    # This would normally trigger the report agent via CrewAI
    # For now, we'll just return a job ID
    
    return {"job_id": job_id, "message": "Report generation started"}