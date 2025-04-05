# RecruitAI - AI-Powered Recruitment System

A modern recruitment application leveraging AI for semantic matching between job descriptions and candidate profiles.

## Features

- **Job Description Analysis**: Submit and process job descriptions with AI
- **CV Parsing and Analysis**: Extract key information from candidate CVs
- **Semantic Matching**: Match candidates to jobs using embedding-based similarity
- **Interview Scheduling**: Schedule interviews and generate personalized interview requests
- **Real-time Dashboard**: Track candidates, match scores, and recruitment metrics

## System Architecture

This application consists of two main components:

1. **Backend**: FastAPI application with LangChain and Ollama integration for AI-powered processing
2. **Frontend**: Next.js application with TailwindCSS and ShadCN UI for a modern user experience

## Prerequisites

- Python 3.9+ (for the backend)
- Node.js 18+ (for the frontend)
- Ollama with nomic-embed-text model (for semantic embeddings)

## Quick Start

### 1. Set up the Backend

```bash
# Clone the repository
git clone <repository-url>
cd RecruitAI

# Create and activate a virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate

# Install dependencies
cd backend
pip install -r requirements.txt

# Set up Ollama for embeddings (if not already installed)
curl -fsSL https://ollama.com/install.sh | sh
ollama pull nomic-embed-text

# Start the backend server
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 2. Set up the Frontend

In a new terminal:

```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# Create environment file
cp .env.local.example .env.local

# Start the development server
npm run dev
```

### 3. Access the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API documentation: http://localhost:8000/docs

## Usage Flow

1. **Submit Job Descriptions**:
   - Go to the "Job Description" page
   - Fill out the form with job details
   - Submit to get an AI-processed summary

2. **Upload Candidate CVs**:
   - Go to the "Upload CV" page
   - Select a job description
   - Enter candidate details and CV text
   - Submit to get a semantic match score

3. **View the Dashboard**:
   - Monitor recruitment metrics
   - Track candidate matches and statuses
   - Filter candidates by match score and status

## Development

### Backend Structure

- `main.py`: FastAPI application and endpoints
- `agents.py`: AI agent definitions for processing job descriptions and CVs
- `database.py`: Database models and operations
- `utils.py`: Utility functions including embedding generation

### Frontend Structure

- `src/app/*`: Next.js pages and routes
- `src/components/*`: Reusable UI components
- `src/lib/api.ts`: API service for backend integration

## Troubleshooting

- **Backend connection issues**: Ensure the backend is running and the `NEXT_PUBLIC_API_URL` in the frontend's `.env.local` file is correct.
- **Embedding errors**: Make sure Ollama is running and the nomic-embed-text model is installed.
- **Database errors**: Check the database file permissions and that SQLite is working correctly.

## License

This project is licensed under the MIT License - see the LICENSE file for details.