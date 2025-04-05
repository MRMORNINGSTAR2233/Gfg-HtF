import os
import json
import uuid
import logging
import numpy as np
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('recruitment_system.log')
    ]
)

logger = logging.getLogger("recruitment_system")

# Ollama API settings
OLLAMA_API_BASE = os.environ.get("OLLAMA_API_BASE", "http://localhost:11434")
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "nomic-embed-text")

def setup_file_storage():
    """Create necessary directories for file storage"""
    directories = [
        "uploads/cvs",
        "uploads/job_descriptions",
        "logs"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Created directory: {directory}")

def generate_unique_filename(original_filename: str) -> str:
    """Generate a unique filename to avoid collisions"""
    ext = os.path.splitext(original_filename)[1]
    return f"{uuid.uuid4().hex}{ext}"

def save_uploaded_file(file_content: bytes, directory: str, original_filename: str) -> str:
    """
    Save an uploaded file to the specified directory
    
    Args:
        file_content: File content as bytes
        directory: Target directory
        original_filename: Original filename
        
    Returns:
        Path to the saved file
    """
    filename = generate_unique_filename(original_filename)
    file_path = os.path.join(directory, filename)
    
    os.makedirs(directory, exist_ok=True)
    
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    logger.info(f"Saved file to {file_path}")
    return file_path

def read_file(file_path: str) -> str:
    """Read the contents of a file"""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def format_datetime(dt: datetime) -> str:
    """Format a datetime object for display"""
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def parse_datetime(dt_str: str) -> datetime:
    """Parse a datetime string to a datetime object"""
    return datetime.fromisoformat(dt_str)

def calculate_date_overlap(start1: datetime, end1: datetime, start2: datetime, end2: datetime) -> int:
    """Calculate the overlap in minutes between two time periods"""
    overlap_start = max(start1, start2)
    overlap_end = min(end1, end2)
    
    if overlap_start < overlap_end:
        # Calculate the overlap in minutes
        return (overlap_end - overlap_start).seconds // 60
    
    return 0  # No overlap

def parse_boolean(value: Any) -> bool:
    """Parse various boolean representations to a Python boolean"""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ("yes", "true", "t", "1", "y")
    return bool(value)

def serialize_model(model: Any) -> Dict[str, Any]:
    """
    Serialize a Pydantic model to a dictionary
    
    This handles datetime conversion for JSON serialization
    """
    if hasattr(model, "dict"):
        data = model.dict()
        # Handle datetime objects
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
            elif isinstance(value, list) and value and isinstance(value[0], dict):
                # Handle lists of objects
                for i, item in enumerate(value):
                    for k, v in item.items():
                        if isinstance(v, datetime):
                            value[i][k] = v.isoformat()
    else:
        # If not a Pydantic model, try to convert to dict
        data = dict(model)
    
    return data

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from a PDF file
    
    In a real implementation, this would use a PDF extraction library.
    For simplicity, we're returning a placeholder.
    """
    # This is a stub - in a real application, you would use PyPDF2, pdfplumber, or similar
    return f"Placeholder text extracted from {pdf_path}"

def validate_email(email: str) -> bool:
    """Validate an email address format"""
    # Simple validation using split - in a real app, use a regex or validation library
    parts = email.split('@')
    if len(parts) != 2:
        return False
    
    if not parts[0] or not parts[1]:
        return False
    
    domain_parts = parts[1].split('.')
    if len(domain_parts) < 2:
        return False
    
    return all(part for part in domain_parts)

def log_event(event_type: str, details: Dict[str, Any]):
    """Log an event with details"""
    logger.info(f"Event: {event_type} - {json.dumps(details)}")
    
def generate_embedding(text: str, model: str = EMBEDDING_MODEL) -> Union[List[float], None]:
    """
    Generate text embedding using Ollama API
    
    Args:
        text: Text to embed
        model: Embedding model to use (default: nomic-embed-text)
        
    Returns:
        List of floats representing the embedding, or None if there was an error
    """
    try:
        # For very long texts, we truncate to avoid exceeding token limits
        # This is a simplistic approach - in a production system, you might want
        # to implement more sophisticated chunking and averaging
        if len(text) > 8192:
            text = text[:8192]
            logger.warning("Text truncated to 8192 characters for embedding generation")
        
        # Call Ollama API to generate embeddings
        response = requests.post(
            f"{OLLAMA_API_BASE}/api/embeddings",
            json={"model": model, "prompt": text}
        )
        
        if response.status_code != 200:
            logger.error(f"Failed to generate embedding: {response.text}")
            return None
        
        embedding = response.json().get("embedding")
        return embedding
    
    except Exception as e:
        logger.error(f"Error generating embedding: {str(e)}")
        
        # Fallback to use mock embeddings for demo or testing
        # In a real application, you would handle this error differently
        logger.warning("Using fallback random embedding (this is only for demonstration)")
        import numpy as np
        return list(np.random.normal(0, 1, 768))  # Mock 768-dim embedding

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors
    
    Args:
        vec1: First vector
        vec2: Second vector
        
    Returns:
        Cosine similarity score between 0 and 1
    """
    try:
        # Convert to numpy arrays for efficient computation
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        
        # Calculate cosine similarity
        dot_product = np.dot(v1, v2)
        norm_v1 = np.linalg.norm(v1)
        norm_v2 = np.linalg.norm(v2)
        
        # Handle zero division
        if norm_v1 == 0 or norm_v2 == 0:
            return 0.0
            
        similarity = dot_product / (norm_v1 * norm_v2)
        
        # Ensure result is between 0 and 1
        return max(0.0, min(1.0, similarity))
    
    except Exception as e:
        logger.error(f"Error calculating cosine similarity: {str(e)}")
        return 0.0

def combine_text_for_matching(job_summary_dict: Dict[str, Any], candidate_profile_dict: Dict[str, Any]) -> str:
    """
    Combine job and candidate information for semantic matching
    
    This function creates a structured text representation of all relevant information
    for semantic matching between a job and a candidate.
    
    Args:
        job_summary_dict: Job summary dictionary 
        candidate_profile_dict: Candidate profile dictionary
        
    Returns:
        Formatted text combining key information
    """
    # Format job information
    job_text = f"""
    JOB: {job_summary_dict.get('title', '')}
    SUMMARY: {job_summary_dict.get('summary', '')}
    REQUIRED SKILLS: {', '.join(job_summary_dict.get('required_skills', []))}
    REQUIRED EXPERIENCE: {job_summary_dict.get('required_experience', '')}
    RESPONSIBILITIES: {', '.join(job_summary_dict.get('responsibilities', []))}
    """
    
    # Format candidate information
    education_text = ""
    for edu in candidate_profile_dict.get('education', []):
        education_text += f"{edu.get('degree', '')} in {edu.get('field', '')} from {edu.get('institution', '')}, "
    
    work_exp_text = ""
    for exp in candidate_profile_dict.get('work_experience', []):
        work_exp_text += f"{exp.get('role', '')} at {exp.get('company', '')} for {exp.get('years', '')}, "
    
    candidate_text = f"""
    CANDIDATE: {candidate_profile_dict.get('name', '')}
    EDUCATION: {education_text}
    WORK EXPERIENCE: {work_exp_text}
    SKILLS: {', '.join(candidate_profile_dict.get('skills', []))}
    CERTIFICATIONS: {', '.join(candidate_profile_dict.get('certifications', []))}
    """
    
    return job_text + candidate_text 