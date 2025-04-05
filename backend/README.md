# Multi-Agent Recruitment Automation System

A sophisticated recruitment automation backend built with FastAPI, SQLite, Langchain, and Ollama. This system uses AI agents for processing job descriptions, analyzing candidate CVs, matching candidates to jobs, and automating interview scheduling.

## Features

- **AI-Powered Job Description Analysis**: Extract key skills, responsibilities, and experience requirements
- **CV Parsing & Candidate Profiling**: Extract candidate education, work experience, skills, and certifications
- **Intelligent Candidate-Job Matching**: Calculate match scores with detailed breakdowns
- **Automated Interview Scheduling**: Generate time slots and personalized interview invitation emails
- **Persistent Data Storage**: Store all information in a SQLite3 database
- **RESTful API**: Comprehensive API for frontend integration

## System Architecture

### Components

1. **Agents**:
   - `JobDescriptionAgent`: Analyzes and summarizes job descriptions
   - `RecruitingAgent`: Parses candidate CVs and extracts key information
   - `MatchingAgent`: Computes match scores between candidates and jobs
   - `SchedulingAgent`: Handles interview scheduling and email generation

2. **Database**:
   - SQLite3 database with tables for job descriptions, candidates, match scores, and interviews

3. **API Endpoints**:
   - Job description management
   - Candidate profile management
   - Match score calculation and retrieval
   - Interview scheduling and management

## Setup & Installation

### Prerequisites

- Python 3.8+
- [Ollama](https://ollama.ai/) installed and running with `llama3` and `llava` models
  - Run: `ollama pull llama3`
  - Run: `ollama pull llava`

### Installation Steps

1. Clone the repository

2. Navigate to the backend directory:
   ```
   cd backend
   ```

3. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install required packages:
   ```
   pip install -r requirements.txt
   ```

5. Run the application:
   ```
   python main.py
   ```

6. Access the API documentation:
   ```
   http://localhost:8000/docs
   ```

## API Usage Examples

### 1. Create a Job Description

```bash
curl -X 'POST' \
  'http://localhost:8000/jobs' \
  -H 'Content-Type: application/json' \
  -d '{
  "title": "Senior Software Engineer",
  "description": "We are looking for a Senior Software Engineer with 5+ years of experience in Python, FastAPI, and cloud technologies. The candidate will be responsible for designing and implementing scalable backend services..."
}'
```

### 2. Upload a Candidate CV

```bash
curl -X 'POST' \
  'http://localhost:8000/candidates' \
  -H 'Content-Type: multipart/form-data' \
  -F 'name=John Doe' \
  -F 'email=john@example.com' \
  -F 'phone=+1234567890' \
  -F 'cv_file=@/path/to/cv.pdf'
```

### 3. Calculate Match Score

```bash
curl -X 'POST' \
  'http://localhost:8000/match?job_id=1&candidate_id=1'
```

### 4. Schedule an Interview

```bash
curl -X 'POST' \
  'http://localhost:8000/interviews' \
  -H 'Content-Type: application/json' \
  -d '{
  "job_id": 1,
  "candidate_id": 1,
  "slot_datetime": "2023-12-01T14:00:00",
  "duration_minutes": 60
}'
```

## Folder Structure

```
backend/
├── main.py              # FastAPI application
├── agents.py            # AI agents implementation
├── database.py          # Database models and utilities
├── utils.py             # Helper functions
├── requirements.txt     # Dependencies
└── README.md            # This file
```

## Testing

The API endpoints can be tested using the Swagger UI at `http://localhost:8000/docs` or using tools like `curl` or Postman.

## Extending the System

The modular design of this system makes it easy to extend:

1. **Add New Agents**: Create new specialized agents in `agents.py` for additional functionality
2. **Enhance Database Schema**: Modify `database.py` to add new tables or fields
3. **Add API Endpoints**: Extend `main.py` with new routes and functionality

## Security Considerations

For production deployments:

1. Replace the `allow_origins=["*"]` in CORS middleware with specific origins
2. Implement proper authentication and authorization
3. Use environment variables for sensitive configuration values
4. Consider implementing rate limiting for API endpoints

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Embedding-Based Matching with Ollama

The system now uses semantic embeddings through Ollama for more accurate candidate-job matching. This approach provides better semantic understanding than simple keyword matching.

### Setup Ollama with Nomic Embeddings

1. Install Ollama:
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ```

2. Pull the Nomic embedding model:
   ```bash
   ollama pull nomic-embed-text
   ```

3. Configure environment variables (optional - defaults are provided):
   ```bash
   export OLLAMA_API_BASE=http://localhost:11434  # Default Ollama API endpoint
   export EMBEDDING_MODEL=nomic-embed-text        # Default embedding model
   ```

### How Embedding-Based Matching Works

1. The system converts both job descriptions and candidate profiles to text representations
2. Ollama's nomic-embed-text model generates embeddings for both texts
3. Cosine similarity is calculated between these embeddings to determine the match score
4. An LLM is used to generate component breakdowns and explanations based on the similarity score

This approach provides several advantages:
- Better semantic understanding of qualifications and requirements
- More nuanced matching beyond simple keyword overlap
- Ability to recognize related skills and experiences even with different terminology

If Ollama is not available, the system will fall back to the previous LLM-based matching approach. 