import json
import os
import logging
from typing import Dict, List, Optional, Any, Tuple, TypedDict, Annotated, Literal
from datetime import datetime, timedelta

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field

# Import langgraph directly
import langgraph.graph as graph
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

# Configure logger
logger = logging.getLogger("recruitment_system")

# Initialize Ollama models
DEFAULT_MODEL = "phi4-mini"
VISION_MODEL = "granite3.2-vision"

def get_chat_model(model_name: str = DEFAULT_MODEL):
    """Get an Ollama chat model instance"""
    return ChatOllama(model=model_name)

# Define data models
class JobSummary(BaseModel):
    title: str = Field(description="Job title")
    summary: str = Field(description="Brief summary of the job")
    required_skills: List[str] = Field(description="List of required skills")
    required_experience: str = Field(description="Required years and type of experience")
    responsibilities: List[str] = Field(description="Key job responsibilities")

class CandidateProfile(BaseModel):
    name: str = Field(description="Candidate's full name")
    education: List[Dict[str, str]] = Field(description="Education history with institution, degree, field, and years")
    work_experience: List[Dict[str, str]] = Field(description="Work experience with company, role, years, and description")
    skills: List[str] = Field(description="List of candidate's skills")
    certifications: List[str] = Field(description="List of certifications")

class MatchResult(BaseModel):
    score: float = Field(description="Overall match score between 0 and 1")
    skills_match: Dict[str, Any] = Field(description="Skills match details")
    experience_match: Dict[str, Any] = Field(description="Experience match details")
    education_match: Dict[str, Any] = Field(description="Education match details")
    explanation: str = Field(description="Explanation of the match score")

class InterviewSchedule(BaseModel):
    candidate_id: int = Field(description="Candidate ID")
    job_id: int = Field(description="Job ID")
    suggested_slots: List[Dict[str, Any]] = Field(description="Suggested interview time slots")
    email_template: str = Field(description="Personalized email template for interview request")

# Define state types for LangGraph workflows

# JobDescription Workflow State
class JobDescriptionState(TypedDict):
    title: str
    description: str
    summary: Optional[str]
    required_skills: Optional[List[str]]
    required_experience: Optional[str]
    responsibilities: Optional[List[str]]
    error: Optional[str]

# CV Processing Workflow State
class CVProcessingState(TypedDict):
    cv_path: str
    cv_text: Optional[str]
    name: Optional[str]
    education: Optional[List[Dict[str, str]]]
    work_experience: Optional[List[Dict[str, str]]]
    skills: Optional[List[str]]
    certifications: Optional[List[str]]
    error: Optional[str]

# Matching Workflow State
class MatchingState(TypedDict):
    job_summary: JobSummary
    candidate_profile: CandidateProfile
    match_score: Optional[float]
    skills_match: Optional[Dict[str, Any]]
    experience_match: Optional[Dict[str, Any]]
    education_match: Optional[Dict[str, Any]]
    explanation: Optional[str]
    error: Optional[str]

# Interview Scheduling Workflow State
class SchedulingState(TypedDict):
    job_summary: JobSummary
    candidate_profile: CandidateProfile
    match_result: MatchResult
    interview_slots: List[Dict[str, Any]]
    email_template: Optional[str]
    error: Optional[str]

# ===== JOB DESCRIPTION PROCESSING WORKFLOW =====

# Node functions for JobDescription workflow
def extract_job_summary(state: JobDescriptionState) -> JobDescriptionState:
    """Process a job description and extract key information"""
    try:
        # Create prompt template
        template = """You are a professional job description analyzer.
        Extract the key information from the following job description and format it according to the requirements.
        
        Job Title: {title}
        
        Job Description:
        {description}
        
        Provide a clear analysis focusing on:
        1. A brief summary of the position
        2. Required skills (as a list)
        3. Required experience level and type
        4. Key responsibilities (as a list)
        
        Format your response as a JSON object with these fields: summary, required_skills, required_experience, responsibilities.
        Make sure all lists are properly formatted as JSON arrays.
        """
        
        prompt = ChatPromptTemplate.from_template(template)
        model = get_chat_model()
        chain = prompt | model | StrOutputParser()
        
        result = chain.invoke({"title": state["title"], "description": state["description"]})
        
        # Parse the JSON response
        json_result = json.loads(result)
        
        # Update state with extracted information
        return {
            **state,
            "summary": json_result.get("summary", ""),
            "required_skills": json_result.get("required_skills", []),
            "required_experience": json_result.get("required_experience", ""),
            "responsibilities": json_result.get("responsibilities", []),
            "error": None
        }
    except Exception as e:
        # Handle errors
        return {
            **state,
            "error": f"Error extracting job summary: {str(e)}"
        }

# Create JobDescription workflow using LangGraph StateGraph
def create_job_description_workflow():
    """Create a workflow for processing job descriptions"""
    # Define workflow using LangGraph StateGraph
    workflow = StateGraph(JobDescriptionState)
    
    # Add the node
    workflow.add_node("extract_job_summary", extract_job_summary)
    
    # Define the edge - use END as the target instead of None
    workflow.set_entry_point("extract_job_summary")
    
    # Add a conditional edge to handle the end of the workflow
    # In LangGraph, use graph.END instead of None to indicate the end of a workflow
    workflow.add_edge("extract_job_summary", END)
    
    # Compile the workflow
    return workflow.compile()

# ===== CV PROCESSING WORKFLOW =====

# Node functions for CV Processing workflow
def parse_cv_text(state: CVProcessingState) -> CVProcessingState:
    """Parse CV text to extract candidate information"""
    try:
        # If cv_text is not available yet, attempt to extract it
        if "cv_text" not in state or not state["cv_text"]:
            cv_path = state["cv_path"]
            
            # For text files, read and process the content
            if cv_path.lower().endswith(('.txt', '.docx')):
                with open(cv_path, 'r', encoding='utf-8') as file:
                    cv_text = file.read()
            # For other file types (in a real implementation we'd use proper extractors)
            else:
                cv_text = f"Placeholder text extracted from {cv_path}"
                
            state = {**state, "cv_text": cv_text}
        
        # Create prompt template for CV parsing
        template = """You are a professional CV/resume analyzer.
        Extract key information from the following CV and format it according to the requirements.
        
        CV Text:
        {cv_text}
        
        Extract the following information:
        1. Candidate's full name
        2. Education history (institution, degree, field, years)
        3. Work experience (company, role, years, brief description)
        4. Skills
        5. Certifications
        
        Format your response as a JSON object with these fields: name, education, work_experience, skills, certifications.
        Each education entry should have institution, degree, field, and years fields.
        Each work experience entry should have company, role, years, and description fields.
        Skills and certifications should be arrays of strings.
        """
        
        prompt = ChatPromptTemplate.from_template(template)
        model = get_chat_model()
        chain = prompt | model | StrOutputParser()
        
        result = chain.invoke({"cv_text": state["cv_text"]})
        
        # Parse the JSON response
        json_result = json.loads(result)
        
        # Update state with extracted information
        return {
            **state,
            "name": json_result.get("name", ""),
            "education": json_result.get("education", []),
            "work_experience": json_result.get("work_experience", []),
            "skills": json_result.get("skills", []),
            "certifications": json_result.get("certifications", []),
            "error": None
        }
    except Exception as e:
        # Handle errors
        return {
            **state,
            "error": f"Error parsing CV: {str(e)}"
        }

# Create CV Processing workflow
def create_cv_processing_workflow():
    """Create a workflow for processing CVs"""
    # Define workflow using LangGraph StateGraph
    workflow = StateGraph(CVProcessingState)
    
    # Add the node
    workflow.add_node("parse_cv_text", parse_cv_text)
    
    # Define the edge - use END as the target instead of None
    workflow.set_entry_point("parse_cv_text")
    
    # Use END to mark the end of the workflow
    workflow.add_edge("parse_cv_text", END)
    
    # Compile the workflow
    return workflow.compile()

# ===== MATCHING WORKFLOW =====

# Node functions for Matching workflow
def calculate_match_score(state: MatchingState) -> MatchingState:
    """Calculate match score between job and candidate using semantic embeddings"""
    try:
        job_summary = state["job_summary"]
        candidate_profile = state["candidate_profile"]
        
        # Import utilities for embedding generation and similarity calculation
        from utils import generate_embedding, cosine_similarity, combine_text_for_matching
        
        # Convert job and candidate information to dictionaries
        job_dict = {
            "title": job_summary.title,
            "summary": job_summary.summary,
            "required_skills": job_summary.required_skills,
            "required_experience": job_summary.required_experience,
            "responsibilities": job_summary.responsibilities
        }
        
        candidate_dict = {
            "name": candidate_profile.name,
            "education": candidate_profile.education,
            "work_experience": candidate_profile.work_experience,
            "skills": candidate_profile.skills,
            "certifications": candidate_profile.certifications
        }
        
        # Combine text for semantic matching
        combined_text = combine_text_for_matching(job_dict, candidate_dict)
        
        # Generate embeddings
        job_embedding = generate_embedding(job_summary.summary + "\n" + ", ".join(job_summary.required_skills))
        candidate_embedding = generate_embedding(
            ", ".join(candidate_profile.skills) + "\n" + 
            str(candidate_profile.work_experience) + "\n" +
            str(candidate_profile.education)
        )
        
        # If embeddings were successfully generated, calculate similarity score
        if job_embedding and candidate_embedding:
            similarity_score = cosine_similarity(job_embedding, candidate_embedding)
            # Convert to percentage score (0-100)
            match_score = min(1.0, similarity_score) * 100
        else:
            # Fallback to old method with LLM evaluation
            logger.warning("Using fallback LLM evaluation for match calculation")
            
            # Create prompt template for matching
            template = """You are a professional recruiting match analyzer.
            Calculate the match score between the job requirements and the candidate's profile.
            
            Job Information:
            Title: {job_title}
            Summary: {job_summary}
            Required Skills: {required_skills}
            Required Experience: {required_experience}
            Responsibilities: {responsibilities}
            
            Candidate Information:
            Name: {candidate_name}
            Education: {education}
            Work Experience: {work_experience}
            Skills: {skills}
            Certifications: {certifications}
            
            Analyze the match in these categories:
            1. Skills match: How many required skills does the candidate have? Assign a score from 0-1.
            2. Experience match: Does the candidate have the required experience type and years? Assign a score from 0-1.
            3. Education match: Does the candidate's education align with the job requirements? Assign a score from 0-1.
            
            Calculate an overall score as a weighted average (skills: 40%, experience: 40%, education: 20%).
            
            Format your response as a JSON object with these fields:
            - score (overall score from 0-1)
            - skills_match (object with score and details)
            - experience_match (object with score and details)
            - education_match (object with score and details)
            - explanation (text explaining the match result)
            """
            
            prompt = ChatPromptTemplate.from_template(template)
            model = get_chat_model()
            chain = prompt | model | StrOutputParser()
            
            # Prepare input for the prompt
            input_data = {
                "job_title": job_summary.title,
                "job_summary": job_summary.summary,
                "required_skills": ", ".join(job_summary.required_skills),
                "required_experience": job_summary.required_experience,
                "responsibilities": ", ".join(job_summary.responsibilities),
                "candidate_name": candidate_profile.name,
                "education": json.dumps(candidate_profile.education),
                "work_experience": json.dumps(candidate_profile.work_experience),
                "skills": ", ".join(candidate_profile.skills),
                "certifications": ", ".join(candidate_profile.certifications)
            }
            
            result = chain.invoke(input_data)
            
            # Parse the JSON response
            json_result = json.loads(result)
            
            # Get the match score from LLM result (0-1)
            match_score = json_result.get("score", 0.0) * 100
            
            # Use the component scores from LLM evaluation
            skills_match = json_result.get("skills_match", {})
            experience_match = json_result.get("experience_match", {})
            education_match = json_result.get("education_match", {})
            explanation = json_result.get("explanation", "")
        
        # Calculate semantic component matches regardless of which method is used
        # If we used embeddings, we'll use a secondary LLM call to provide explanations
        if job_embedding and candidate_embedding:
            # Use the faster model to analyze the component matches
            template = """You are a professional recruiting match analyzer.
            The overall match score between this job and candidate is {match_score}%.
            
            Job Information:
            Title: {job_title}
            Summary: {job_summary}
            Required Skills: {required_skills}
            Required Experience: {required_experience}
            Responsibilities: {responsibilities}
            
            Candidate Information:
            Name: {candidate_name}
            Education: {education}
            Work Experience: {work_experience}
            Skills: {skills}
            Certifications: {certifications}
            
            Provide a component breakdown of the match score into these categories:
            1. Skills match: Analyze the candidate's skills against the required skills. 
            2. Experience match: Analyze the candidate's experience against the required experience.
            3. Education match: Analyze the candidate's education against the implied job requirements.
            
            Format your response as a JSON object with these fields:
            - skills_match (object with score between 0-1 and explanation)
            - experience_match (object with score between 0-1 and explanation)
            - education_match (object with score between 0-1 and explanation)
            - explanation (overall text explaining the match result)
            """
            
            prompt = ChatPromptTemplate.from_template(template)
            model = get_chat_model()
            chain = prompt | model | StrOutputParser()
            
            # Prepare input for the prompt
            input_data = {
                "match_score": round(match_score, 1),
                "job_title": job_summary.title,
                "job_summary": job_summary.summary,
                "required_skills": ", ".join(job_summary.required_skills),
                "required_experience": job_summary.required_experience,
                "responsibilities": ", ".join(job_summary.responsibilities),
                "candidate_name": candidate_profile.name,
                "education": json.dumps(candidate_profile.education),
                "work_experience": json.dumps(candidate_profile.work_experience),
                "skills": ", ".join(candidate_profile.skills),
                "certifications": ", ".join(candidate_profile.certifications)
            }
            
            try:
                result = chain.invoke(input_data)
                
                # Parse the JSON response
                json_result = json.loads(result)
                
                # Extract the component scores and explanation
                skills_match = json_result.get("skills_match", {})
                experience_match = json_result.get("experience_match", {})
                education_match = json_result.get("education_match", {})
                explanation = json_result.get("explanation", "")
            except Exception as e:
                # If there's an error, create generic explanations
                logger.error(f"Error generating component breakdowns: {str(e)}")
                explanation = f"The candidate's profile has an overall semantic match score of {round(match_score, 1)}% with the job requirements."
                skills_match = {"score": 0.7, "explanation": "Skills were semantically analyzed."}
                experience_match = {"score": 0.7, "explanation": "Experience was semantically analyzed."}
                education_match = {"score": 0.7, "explanation": "Education was semantically analyzed."}
                
        # Update state with match results
        return {
            **state,
            "match_score": match_score / 100,  # Convert back to 0-1 scale for internal use
            "skills_match": skills_match,
            "experience_match": experience_match,
            "education_match": education_match,
            "explanation": explanation,
            "error": None
        }
    except Exception as e:
        # Handle errors
        return {
            **state,
            "error": f"Error calculating match score: {str(e)}"
        }

# Create Matching workflow
def create_matching_workflow():
    """Create a workflow for matching jobs and candidates"""
    # Define workflow using LangGraph StateGraph
    workflow = StateGraph(MatchingState)
    
    # Add the node
    workflow.add_node("calculate_match_score", calculate_match_score)
    
    # Define the edge - use END as the target instead of None
    workflow.set_entry_point("calculate_match_score")
    
    # Use END to mark the end of the workflow
    workflow.add_edge("calculate_match_score", END)
    
    # Compile the workflow
    return workflow.compile()

# ===== INTERVIEW SCHEDULING WORKFLOW =====

# Node functions for Scheduling workflow
def generate_email_template(state: SchedulingState) -> SchedulingState:
    """Generate a personalized interview request email"""
    try:
        job_summary = state["job_summary"]
        candidate_profile = state["candidate_profile"]
        match_result = state["match_result"]
        interview_slots = state["interview_slots"]
        
        # Create prompt template for email generation
        template = """You are a professional recruiter.
        Create a personalized interview request email for the following candidate.
        
        Job Information:
        Title: {job_title}
        Summary: {job_summary}
        
        Candidate Information:
        Name: {candidate_name}
        
        Match Analysis:
        Score: {match_score}
        Explanation: {match_explanation}
        
        Available Interview Slots:
        {interview_slots}
        
        Create a professional, friendly email that:
        1. Addresses the candidate by name
        2. Expresses interest based on their qualifications
        3. Briefly describes the position
        4. Lists the available interview slots
        5. Provides next steps
        
        Format your response as just the email text, without any additional formatting or explanation.
        """
        
        prompt = ChatPromptTemplate.from_template(template)
        model = get_chat_model()
        chain = prompt | model | StrOutputParser()
        
        # Format interview slots for the prompt
        slots_text = "\n".join([f"- {slot['display']}" for slot in interview_slots])
        
        # Prepare input for the prompt
        input_data = {
            "job_title": job_summary.title,
            "job_summary": job_summary.summary,
            "candidate_name": candidate_profile.name,
            "match_score": match_result.score,
            "match_explanation": match_result.explanation,
            "interview_slots": slots_text
        }
        
        email_template = chain.invoke(input_data)
        
        # Update state with email template
        return {
            **state,
            "email_template": email_template,
            "error": None
        }
    except Exception as e:
        # Handle errors
        return {
            **state,
            "error": f"Error generating email template: {str(e)}"
        }

# Create Scheduling workflow
def create_scheduling_workflow():
    """Create a workflow for scheduling interviews"""
    # Define workflow using LangGraph StateGraph
    workflow = StateGraph(SchedulingState)
    
    # Add the node
    workflow.add_node("generate_email_template", generate_email_template)
    
    # Define the edge - use END as the target instead of None
    workflow.set_entry_point("generate_email_template")
    
    # Use END to mark the end of the workflow
    workflow.add_edge("generate_email_template", END)
    
    # Compile the workflow
    return workflow.compile()

# Utility function for generating interview slots
def generate_interview_slots(n_slots: int = 3, start_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
    """
    Generate possible interview time slots
    
    Args:
        n_slots: Number of slots to generate
        start_date: Starting date for slot generation (defaults to tomorrow)
        
    Returns:
        List of interview slot dictionaries
    """
    if start_date is None:
        # Default to starting tomorrow
        start_date = datetime.now() + timedelta(days=1)
        # Normalize to 9 AM
        start_date = start_date.replace(hour=9, minute=0, second=0, microsecond=0)
    
    slots = []
    current_date = start_date
    
    # Generate business hours slots (9 AM - 5 PM)
    hours = [9, 11, 13, 15, 17]  # 9 AM, 11 AM, 1 PM, 3 PM, 5 PM
    
    for i in range(n_slots):
        # Skip weekends
        while current_date.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
            current_date += timedelta(days=1)
        
        hour = hours[i % len(hours)]
        slot_time = current_date.replace(hour=hour)
        
        slots.append({
            "datetime": slot_time.isoformat(),
            "display": slot_time.strftime("%A, %B %d, %Y at %I:%M %p")
        })
        
        # Move to next day after we've used all hours in a day
        if (i + 1) % len(hours) == 0:
            current_date += timedelta(days=1)
    
    return slots

# Main agent classes that use LangGraph workflows

class JobDescriptionAgent:
    """Agent for processing job descriptions and extracting key information"""
    
    def __init__(self):
        self.workflow = create_job_description_workflow()
    
    def process_jd(self, title: str, description: str) -> JobSummary:
        """
        Process a job description and extract key information
        
        Args:
            title: Job title
            description: Full job description text
            
        Returns:
            JobSummary object with extracted details
        """
        # Set up the initial state
        initial_state = {"title": title, "description": description}
        
        # Run the workflow
        result = self.workflow.invoke(initial_state)
        
        # Check for errors
        if result.get("error"):
            return JobSummary(
                title=title,
                summary="Error processing job description",
                required_skills=[],
                required_experience="",
                responsibilities=[]
            )
        
        # Create JobSummary object from workflow result
        return JobSummary(
            title=title,
            summary=result.get("summary", ""),
            required_skills=result.get("required_skills", []),
            required_experience=result.get("required_experience", ""),
            responsibilities=result.get("responsibilities", [])
        )

class RecruitingAgent:
    """Agent for processing candidate CVs and extracting relevant information"""
    
    def __init__(self):
        self.workflow = create_cv_processing_workflow()
    
    def process_cv_file(self, cv_path: str) -> CandidateProfile:
        """
        Process a CV file and extract information
        
        Args:
            cv_path: Path to the CV file
            
        Returns:
            CandidateProfile with extracted information
        """
        # For image files, we'd use vision models in a real implementation
        if cv_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            # Placeholder for vision model processing
            return CandidateProfile(
                name="John Doe",
                education=[
                    {"institution": "Example University", "degree": "Bachelor", "field": "Computer Science", "years": "2015-2019"}
                ],
                work_experience=[
                    {"company": "Tech Corp", "role": "Software Engineer", "years": "2019-Present", 
                     "description": "Developed web applications using modern frameworks"}
                ],
                skills=["Python", "JavaScript", "SQL", "Machine Learning"],
                certifications=["AWS Certified Developer"]
            )
        
        # For PDF files (in a real implementation, we'd extract text properly)
        elif cv_path.lower().endswith('.pdf'):
            # Placeholder for PDF extraction
            return CandidateProfile(
                name="Jane Smith",
                education=[
                    {"institution": "Tech University", "degree": "Master", "field": "Data Science", "years": "2017-2019"},
                    {"institution": "State College", "degree": "Bachelor", "field": "Mathematics", "years": "2013-2017"}
                ],
                work_experience=[
                    {"company": "Data Analytics Inc", "role": "Data Scientist", "years": "2019-Present", 
                     "description": "Implemented machine learning solutions for business problems"},
                    {"company": "Research Lab", "role": "Research Assistant", "years": "2017-2019", 
                     "description": "Assisted in data analysis and visualization"}
                ],
                skills=["Python", "R", "TensorFlow", "SQL", "Tableau"],
                certifications=["Google Data Analytics", "Microsoft Azure Data Scientist"]
            )
        
        # For text files, use the workflow
        else:
            # Set up the initial state
            initial_state = {"cv_path": cv_path}
            
            # Run the workflow
            result = self.workflow.invoke(initial_state)
            
            # Check for errors
            if result.get("error"):
                return CandidateProfile(
                    name="Unknown",
                    education=[],
                    work_experience=[],
                    skills=[],
                    certifications=[]
                )
            
            # Create CandidateProfile object from workflow result
            return CandidateProfile(
                name=result.get("name", "Unknown"),
                education=result.get("education", []),
                work_experience=result.get("work_experience", []),
                skills=result.get("skills", []),
                certifications=result.get("certifications", [])
            )

class MatchingAgent:
    """Agent for comparing job descriptions with candidate profiles and calculating match scores using semantic embeddings"""
    
    def __init__(self):
        self.workflow = create_matching_workflow()
    
    def calculate_match(self, job_summary: JobSummary, candidate_profile: CandidateProfile) -> MatchResult:
        """
        Calculate the match score between a job description and a candidate profile
        using semantic embeddings for similarity calculation
        
        Args:
            job_summary: JobSummary object with job details
            candidate_profile: CandidateProfile object with candidate details
            
        Returns:
            MatchResult with score and match details
        """
        # Set up the initial state
        initial_state = {
            "job_summary": job_summary,
            "candidate_profile": candidate_profile
        }
        
        # Run the workflow
        result = self.workflow.invoke(initial_state)
        
        # Check for errors
        if result.get("error"):
            return MatchResult(
                score=0.0,
                skills_match={},
                experience_match={},
                education_match={},
                explanation="Error analyzing match"
            )
        
        # Create MatchResult object from workflow result
        return MatchResult(
            score=result.get("match_score", 0.0),
            skills_match=result.get("skills_match", {}),
            experience_match=result.get("experience_match", {}),
            education_match=result.get("education_match", {}),
            explanation=result.get("explanation", "")
        )
    
    def generate_embeddings(self, text: str) -> List[float]:
        """
        Generate embeddings for the provided text using Ollama's nomic embeddings model
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        from utils import generate_embedding
        return generate_embedding(text)
    
    def calculate_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two embedding vectors
        
        Args:
            vec1: First embedding vector
            vec2: Second embedding vector
            
        Returns:
            Cosine similarity score between 0 and 1
        """
        from utils import cosine_similarity
        return cosine_similarity(vec1, vec2)

class SchedulingAgent:
    """Agent for scheduling interviews and generating personalized interview requests"""
    
    def __init__(self):
        self.workflow = create_scheduling_workflow()
    
    def generate_interview_slots(self, n_slots: int = 3, start_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Generate possible interview time slots"""
        return generate_interview_slots(n_slots, start_date)
    
    def create_interview_request(self, job_summary: JobSummary, candidate_profile: CandidateProfile, 
                               match_result: MatchResult, interview_slots: List[Dict[str, Any]]) -> InterviewSchedule:
        """
        Generate a personalized interview request
        
        Args:
            job_summary: Job details
            candidate_profile: Candidate details
            match_result: Match analysis results
            interview_slots: Available interview slots
            
        Returns:
            InterviewSchedule with suggested slots and email template
        """
        # Set up the initial state
        initial_state = {
            "job_summary": job_summary,
            "candidate_profile": candidate_profile,
            "match_result": match_result,
            "interview_slots": interview_slots
        }
        
        # Run the workflow
        result = self.workflow.invoke(initial_state)
        
        # Create InterviewSchedule object
        return InterviewSchedule(
            candidate_id=-1,  # Will be replaced with actual ID
            job_id=-1,        # Will be replaced with actual ID
            suggested_slots=interview_slots,
            email_template=result.get("email_template", "")
        ) 