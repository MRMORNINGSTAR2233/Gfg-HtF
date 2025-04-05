import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from fastapi import FastAPI, File, Form, UploadFile, HTTPException, Depends, Query, Body
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from agents import (
    JobDescriptionAgent, 
    RecruitingAgent, 
    MatchingAgent, 
    SchedulingAgent,
    JobSummary,
    CandidateProfile,
    MatchResult
)
from database import Database
from utils import (
    setup_file_storage, 
    save_uploaded_file, 
    read_file, 
    parse_datetime, 
    format_datetime,
    log_event,
    serialize_model
)

# Setup directories
setup_file_storage()

# Initialize FastAPI app
app = FastAPI(
    title="Recruitment Automation API",
    description="API for multi-agent recruitment automation system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
db = Database()

# Initialize agents
jd_agent = JobDescriptionAgent()
recruiting_agent = RecruitingAgent()
matching_agent = MatchingAgent()
scheduling_agent = SchedulingAgent()

# ---- Request/Response Models ----

class JobDescriptionRequest(BaseModel):
    title: str
    description: str

class JobDescriptionResponse(BaseModel):
    id: int
    title: str
    summary: str
    required_skills: List[str]
    required_experience: str
    responsibilities: List[str]

class CandidateRequest(BaseModel):
    name: str
    email: str
    phone: str

class CandidateResponse(BaseModel):
    id: int
    name: str
    email: str
    education: List[Dict[str, str]]
    work_experience: List[Dict[str, str]]
    skills: List[str]
    certifications: List[str]

class MatchScoreResponse(BaseModel):
    id: int
    job_id: int
    job_title: str
    candidate_id: int
    candidate_name: str
    score: float
    skills_match: Dict[str, Any]
    experience_match: Dict[str, Any]
    education_match: Dict[str, Any]
    explanation: str

class InterviewRequest(BaseModel):
    job_id: int
    candidate_id: int
    slot_datetime: str
    duration_minutes: int = 60
    interview_link: Optional[str] = None

class InterviewResponse(BaseModel):
    id: int
    job_id: int
    job_title: str
    candidate_id: int
    candidate_name: str
    scheduled_time: str
    duration_minutes: int
    interview_link: str
    status: str
    email_template: Optional[str] = None

# ---- API Endpoints ----

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Recruitment Automation API"}

# Job Description Endpoints

@app.post("/jobs", response_model=JobDescriptionResponse)
async def create_job_description(job_data: JobDescriptionRequest):
    """
    Create a new job description and process it
    
    This endpoint:
    1. Creates a new job description record
    2. Processes the description with the JobDescriptionAgent
    3. Updates the record with the processed information
    4. Returns the processed job description
    """
    # Log the incoming request
    log_event("job_description_received", {"title": job_data.title})
    
    # Add job description to database
    job_id = db.add_job_description(job_data.title, job_data.description)
    
    # Process with agent
    job_summary = jd_agent.process_jd(job_data.title, job_data.description)
    
    # Update database with processed information
    db.update_job_summary(
        job_id, 
        job_summary.summary,
        json.dumps(job_summary.required_skills),
        job_summary.required_experience,
        json.dumps(job_summary.responsibilities)
    )
    
    # Get the updated job description
    job = db.get_job_description(job_id)
    
    # Convert database format to response model
    return JobDescriptionResponse(
        id=job["id"],
        title=job["title"],
        summary=job["summarized_description"],
        required_skills=json.loads(job["required_skills"] or "[]"),
        required_experience=job["required_experience"] or "",
        responsibilities=json.loads(job["responsibilities"] or "[]")
    )

@app.get("/jobs", response_model=List[JobDescriptionResponse])
async def get_all_jobs():
    """Get all job descriptions"""
    jobs = db.get_all_job_descriptions()
    
    # Convert database format to response models
    return [
        JobDescriptionResponse(
            id=job["id"],
            title=job["title"],
            summary=job["summarized_description"] or "",
            required_skills=json.loads(job["required_skills"] or "[]"),
            required_experience=job["required_experience"] or "",
            responsibilities=json.loads(job["responsibilities"] or "[]")
        )
        for job in jobs
    ]

@app.get("/jobs/{job_id}", response_model=JobDescriptionResponse)
async def get_job_description(job_id: int):
    """Get a specific job description by ID"""
    job = db.get_job_description(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail=f"Job description with ID {job_id} not found")
    
    # Convert database format to response model
    return JobDescriptionResponse(
        id=job["id"],
        title=job["title"],
        summary=job["summarized_description"] or "",
        required_skills=json.loads(job["required_skills"] or "[]"),
        required_experience=job["required_experience"] or "",
        responsibilities=json.loads(job["responsibilities"] or "[]")
    )

# Candidate Endpoints

@app.post("/candidates", response_model=CandidateResponse)
async def create_candidate(
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    cv_file: UploadFile = File(...)
):
    """
    Create a new candidate profile by uploading a CV
    
    This endpoint:
    1. Saves the uploaded CV file
    2. Creates a new candidate record
    3. Processes the CV with the RecruitingAgent
    4. Updates the record with the extracted information
    5. Returns the processed candidate profile
    """
    # Save uploaded CV
    cv_path = save_uploaded_file(await cv_file.read(), "uploads/cvs", cv_file.filename)
    
    # Add candidate to database
    candidate_id = db.add_candidate(name, email, phone, cv_path)
    
    # Process CV with agent
    candidate_profile = recruiting_agent.process_cv_file(cv_path)
    
    # Update database with extracted information
    db.update_candidate_profile(
        candidate_id,
        json.dumps(candidate_profile.education),
        json.dumps(candidate_profile.work_experience),
        json.dumps(candidate_profile.skills),
        json.dumps(candidate_profile.certifications)
    )
    
    # Get the updated candidate profile
    candidate = db.get_candidate(candidate_id)
    
    # Convert database format to response model
    return CandidateResponse(
        id=candidate["id"],
        name=candidate["name"],
        email=candidate["email"],
        education=json.loads(candidate["education"] or "[]"),
        work_experience=json.loads(candidate["work_experience"] or "[]"),
        skills=json.loads(candidate["skills"] or "[]"),
        certifications=json.loads(candidate["certifications"] or "[]")
    )

@app.get("/candidates", response_model=List[CandidateResponse])
async def get_all_candidates():
    """Get all candidate profiles"""
    candidates = db.get_all_candidates()
    
    # Convert database format to response models
    return [
        CandidateResponse(
            id=candidate["id"],
            name=candidate["name"],
            email=candidate["email"],
            education=json.loads(candidate["education"] or "[]"),
            work_experience=json.loads(candidate["work_experience"] or "[]"),
            skills=json.loads(candidate["skills"] or "[]"),
            certifications=json.loads(candidate["certifications"] or "[]")
        )
        for candidate in candidates
    ]

@app.get("/candidates/{candidate_id}", response_model=CandidateResponse)
async def get_candidate(candidate_id: int):
    """Get a specific candidate profile by ID"""
    candidate = db.get_candidate(candidate_id)
    
    if not candidate:
        raise HTTPException(status_code=404, detail=f"Candidate with ID {candidate_id} not found")
    
    # Convert database format to response model
    return CandidateResponse(
        id=candidate["id"],
        name=candidate["name"],
        email=candidate["email"],
        education=json.loads(candidate["education"] or "[]"),
        work_experience=json.loads(candidate["work_experience"] or "[]"),
        skills=json.loads(candidate["skills"] or "[]"),
        certifications=json.loads(candidate["certifications"] or "[]")
    )

# Match Score Endpoints

@app.post("/match", response_model=MatchScoreResponse)
async def calculate_match_score(job_id: int, candidate_id: int):
    """
    Calculate the match score between a job and a candidate
    
    This endpoint:
    1. Retrieves the job and candidate details
    2. Processes them with the MatchingAgent
    3. Stores the match score
    4. Returns the match result
    """
    # Get job and candidate
    job = db.get_job_description(job_id)
    candidate = db.get_candidate(candidate_id)
    
    if not job:
        raise HTTPException(status_code=404, detail=f"Job description with ID {job_id} not found")
    if not candidate:
        raise HTTPException(status_code=404, detail=f"Candidate with ID {candidate_id} not found")
    
    # Convert database format to agent models
    job_summary = JobSummary(
        title=job["title"],
        summary=job["summarized_description"] or "",
        required_skills=json.loads(job["required_skills"] or "[]"),
        required_experience=job["required_experience"] or "",
        responsibilities=json.loads(job["responsibilities"] or "[]")
    )
    
    candidate_profile = CandidateProfile(
        name=candidate["name"],
        education=json.loads(candidate["education"] or "[]"),
        work_experience=json.loads(candidate["work_experience"] or "[]"),
        skills=json.loads(candidate["skills"] or "[]"),
        certifications=json.loads(candidate["certifications"] or "[]")
    )
    
    # Calculate match score
    match_result = matching_agent.calculate_match(job_summary, candidate_profile)
    
    # Store match score in database
    match_id = db.add_match_score(
        job_id,
        candidate_id,
        match_result.score,
        json.dumps(match_result.skills_match),
        json.dumps(match_result.experience_match),
        json.dumps(match_result.education_match)
    )
    
    # Get the match from database with additional information
    matches = db.get_match_scores_by_job(job_id)
    match = next((m for m in matches if m["id"] == match_id), None)
    
    # Convert database format to response model
    return MatchScoreResponse(
        id=match["id"],
        job_id=match["job_id"],
        job_title=job["title"],
        candidate_id=match["candidate_id"],
        candidate_name=match["candidate_name"],
        score=match["score"],
        skills_match=json.loads(match["skills_match"] or "{}"),
        experience_match=json.loads(match["experience_match"] or "{}"),
        education_match=json.loads(match["education_match"] or "{}"),
        explanation=match_result.explanation
    )

@app.get("/match/job/{job_id}", response_model=List[MatchScoreResponse])
async def get_matches_by_job(job_id: int):
    """Get all matches for a specific job"""
    job = db.get_job_description(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail=f"Job description with ID {job_id} not found")
    
    matches = db.get_match_scores_by_job(job_id)
    
    # Convert database format to response models
    return [
        MatchScoreResponse(
            id=match["id"],
            job_id=match["job_id"],
            job_title=job["title"],
            candidate_id=match["candidate_id"],
            candidate_name=match["candidate_name"],
            score=match["score"],
            skills_match=json.loads(match["skills_match"] or "{}"),
            experience_match=json.loads(match["experience_match"] or "{}"),
            education_match=json.loads(match["education_match"] or "{}"),
            explanation=""  # Not stored in database
        )
        for match in matches
    ]

@app.get("/match/candidate/{candidate_id}", response_model=List[MatchScoreResponse])
async def get_matches_by_candidate(candidate_id: int):
    """Get all matches for a specific candidate"""
    candidate = db.get_candidate(candidate_id)
    
    if not candidate:
        raise HTTPException(status_code=404, detail=f"Candidate with ID {candidate_id} not found")
    
    matches = db.get_match_scores_by_candidate(candidate_id)
    
    # Convert database format to response models
    return [
        MatchScoreResponse(
            id=match["id"],
            job_id=match["job_id"],
            job_title=match["job_title"],
            candidate_id=match["candidate_id"],
            candidate_name=candidate["name"],
            score=match["score"],
            skills_match=json.loads(match["skills_match"] or "{}"),
            experience_match=json.loads(match["experience_match"] or "{}"),
            education_match=json.loads(match["education_match"] or "{}"),
            explanation=""  # Not stored in database
        )
        for match in matches
    ]

# Interview Endpoints

@app.post("/interviews", response_model=InterviewResponse)
async def schedule_interview(interview_data: InterviewRequest):
    """
    Schedule an interview between a job and a candidate
    
    This endpoint:
    1. Validates the job and candidate
    2. Schedules the interview
    3. Generates a personalized email template
    4. Returns the interview details
    """
    # Get job and candidate
    job = db.get_job_description(interview_data.job_id)
    candidate = db.get_candidate(interview_data.candidate_id)
    
    if not job:
        raise HTTPException(status_code=404, detail=f"Job description with ID {interview_data.job_id} not found")
    if not candidate:
        raise HTTPException(status_code=404, detail=f"Candidate with ID {interview_data.candidate_id} not found")
    
    # Get the match score if available
    matches = db.get_match_scores_by_job(interview_data.job_id)
    match = next((m for m in matches if m["candidate_id"] == interview_data.candidate_id), None)
    
    # Parse scheduled time
    scheduled_time = parse_datetime(interview_data.slot_datetime)
    
    # Create interview link if not provided
    interview_link = interview_data.interview_link
    if not interview_link:
        interview_link = f"https://meet.example.com/{job['id']}-{candidate['id']}-{scheduled_time.strftime('%Y%m%d%H%M')}"
    
    # Schedule interview
    interview_id = db.schedule_interview(
        interview_data.job_id,
        interview_data.candidate_id,
        scheduled_time,
        interview_data.duration_minutes,
        interview_link
    )
    
    # Generate personalized email template if we have match data
    email_template = None
    if match:
        # Convert database format to agent models
        job_summary = JobSummary(
            title=job["title"],
            summary=job["summarized_description"] or "",
            required_skills=json.loads(job["required_skills"] or "[]"),
            required_experience=job["required_experience"] or "",
            responsibilities=json.loads(job["responsibilities"] or "[]")
        )
        
        candidate_profile = CandidateProfile(
            name=candidate["name"],
            education=json.loads(candidate["education"] or "[]"),
            work_experience=json.loads(candidate["work_experience"] or "[]"),
            skills=json.loads(candidate["skills"] or "[]"),
            certifications=json.loads(candidate["certifications"] or "[]")
        )
        
        match_result = MatchResult(
            score=match["score"],
            skills_match=json.loads(match["skills_match"] or "{}"),
            experience_match=json.loads(match["experience_match"] or "{}"),
            education_match=json.loads(match["education_match"] or "{}"),
            explanation="Match found"
        )
        
        # Generate a single slot from the scheduled time
        slot = {
            "datetime": scheduled_time.isoformat(),
            "display": scheduled_time.strftime("%A, %B %d, %Y at %I:%M %p")
        }
        
        interview_schedule = scheduling_agent.create_interview_request(
            job_summary, 
            candidate_profile, 
            match_result, 
            [slot]
        )
        
        email_template = interview_schedule.email_template
    
    # Get all interviews for the job
    interviews = db.get_interviews_by_job(interview_data.job_id)
    interview = next((i for i in interviews if i["id"] == interview_id), None)
    
    # Convert database format to response model
    return InterviewResponse(
        id=interview["id"],
        job_id=interview["job_id"],
        job_title=interview["job_title"],
        candidate_id=interview["candidate_id"],
        candidate_name=interview["candidate_name"],
        scheduled_time=interview["scheduled_time"],
        duration_minutes=interview["duration_minutes"],
        interview_link=interview["interview_link"],
        status=interview["status"],
        email_template=email_template
    )

@app.get("/interviews/job/{job_id}", response_model=List[InterviewResponse])
async def get_interviews_by_job(job_id: int):
    """Get all interviews for a specific job"""
    job = db.get_job_description(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail=f"Job description with ID {job_id} not found")
    
    interviews = db.get_interviews_by_job(job_id)
    
    # Convert database format to response models
    return [
        InterviewResponse(
            id=interview["id"],
            job_id=interview["job_id"],
            job_title=interview["job_title"],
            candidate_id=interview["candidate_id"],
            candidate_name=interview["candidate_name"],
            scheduled_time=interview["scheduled_time"],
            duration_minutes=interview["duration_minutes"],
            interview_link=interview["interview_link"],
            status=interview["status"],
            email_template=None
        )
        for interview in interviews
    ]

@app.get("/interviews/candidate/{candidate_id}", response_model=List[InterviewResponse])
async def get_interviews_by_candidate(candidate_id: int):
    """Get all interviews for a specific candidate"""
    candidate = db.get_candidate(candidate_id)
    
    if not candidate:
        raise HTTPException(status_code=404, detail=f"Candidate with ID {candidate_id} not found")
    
    interviews = db.get_interviews_by_candidate(candidate_id)
    
    # Convert database format to response models
    return [
        InterviewResponse(
            id=interview["id"],
            job_id=interview["job_id"],
            job_title=interview["job_title"],
            candidate_id=interview["candidate_id"],
            candidate_name=candidate["name"],
            scheduled_time=interview["scheduled_time"],
            duration_minutes=interview["duration_minutes"],
            interview_link=interview["interview_link"],
            status=interview["status"],
            email_template=None
        )
        for interview in interviews
    ]

@app.patch("/interviews/{interview_id}", response_model=InterviewResponse)
async def update_interview_status(interview_id: int, status: str, notes: Optional[str] = None):
    """Update the status of an interview"""
    # Get interview data before update
    job_id = None
    candidate_id = None
    
    interviews_data = None
    for job in db.get_all_job_descriptions():
        interviews = db.get_interviews_by_job(job["id"])
        interview = next((i for i in interviews if i["id"] == interview_id), None)
        if interview:
            job_id = interview["job_id"]
            candidate_id = interview["candidate_id"]
            interviews_data = interviews
            break
    
    if not job_id or not candidate_id or not interviews_data:
        raise HTTPException(status_code=404, detail=f"Interview with ID {interview_id} not found")
    
    # Update status
    success = db.update_interview_status(interview_id, status, notes)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update interview status")
    
    # Get updated interview
    job = db.get_job_description(job_id)
    candidate = db.get_candidate(candidate_id)
    interviews = db.get_interviews_by_job(job_id)
    interview = next((i for i in interviews if i["id"] == interview_id), None)
    
    # Convert database format to response model
    return InterviewResponse(
        id=interview["id"],
        job_id=interview["job_id"],
        job_title=interview["job_title"],
        candidate_id=interview["candidate_id"],
        candidate_name=interview["candidate_name"],
        scheduled_time=interview["scheduled_time"],
        duration_minutes=interview["duration_minutes"],
        interview_link=interview["interview_link"],
        status=interview["status"],
        email_template=None
    )

# --- Utility endpoints ---

@app.get("/interview-slots", response_model=List[Dict[str, str]])
async def get_interview_slots(n_slots: int = Query(3, gt=0, lt=10)):
    """Generate possible interview time slots"""
    slots = scheduling_agent.generate_interview_slots(n_slots)
    return [{"datetime": slot["datetime"], "display": slot["display"]} for slot in slots]

@app.get("/match-stats/job/{job_id}")
async def get_job_match_statistics(job_id: int):
    """Get match statistics for a job"""
    job = db.get_job_description(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail=f"Job description with ID {job_id} not found")
    
    matches = db.get_match_scores_by_job(job_id)
    
    if not matches:
        return {
            "job_id": job_id,
            "job_title": job["title"],
            "total_candidates": 0,
            "average_score": 0,
            "top_candidates": []
        }
    
    # Calculate statistics
    average_score = sum(match["score"] for match in matches) / len(matches)
    
    # Get top 5 candidates
    top_candidates = sorted(matches, key=lambda x: x["score"], reverse=True)[:5]
    
    return {
        "job_id": job_id,
        "job_title": job["title"],
        "total_candidates": len(matches),
        "average_score": average_score,
        "top_candidates": [
            {
                "candidate_id": match["candidate_id"],
                "candidate_name": match["candidate_name"],
                "score": match["score"]
            }
            for match in top_candidates
        ]
    }

# Main entry point
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 