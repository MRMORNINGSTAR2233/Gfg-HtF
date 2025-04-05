const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Type definitions for API responses
interface JobResponse {
  id: number;
  title: string;
  company: string;
  summary?: string;
  required_skills?: string[];
  required_experience?: string;
  responsibilities?: string[];
}

interface CandidateResponse {
  id: number;
  name: string;
  email: string;
  phone: string;
  education?: Array<Record<string, string>>;
  work_experience?: Array<Record<string, string>>;
  skills?: string[];
  certifications?: string[];
}

interface MatchResponse {
  id: number;
  job_id: number;
  job_title: string;
  candidate_id: number;
  candidate_name: string;
  score: number;
  skills_match?: Record<string, unknown>;
  experience_match?: Record<string, unknown>;
  education_match?: Record<string, unknown>;
  explanation?: string;
}

interface ErrorDetail {
  loc: string[];
  msg: string;
  type: string;
  input: unknown;
}

export interface JobSubmission {
  title: string;
  company: string;
  description: string;
}

export interface JobResult {
  id: string;
  title: string;
  company: string;
  summary: string;
  required_skills: string[];
  required_experience: string;
  responsibilities: string[];
  [key: string]: unknown;
}

/**
 * Submit a job description to the backend
 */
export async function submitJobDescription(jobData: JobSubmission): Promise<JobResult> {
  try {
    console.log("Submitting job data:", jobData);
    
    const jobFormData = new FormData();
    jobFormData.append('title', jobData.title);
    jobFormData.append('company', jobData.company);
    jobFormData.append('description', jobData.description);
    
    const response = await fetch(`${API_URL}/jobs`, {
      method: 'POST',
      body: jobFormData,
    });
    
    if (!response.ok) {
      const errorDetail = await response.json().catch(() => null);
      throw new Error(
        errorDetail?.detail || `Error submitting job description: ${response.status} ${response.statusText}`
      );
    }
    
    const data = await response.json();
    console.log("Job submission successful:", data);
    return data;
  } catch (error) {
    console.error("Job submission failed:", error);
    throw error;
  }
}

/**
 * Upload a candidate CV and match with job description
 */
export async function uploadCandidateCV(data: {
  name: string;
  email: string;
  jobDescriptionId: string;
  resume?: string;
  file?: File;
  phone?: string;
}) {
  try {
    console.log("Starting CV upload with data:", {
      name: data.name,
      email: data.email,
      phone: data.phone,
      jobId: data.jobDescriptionId,
      hasFile: !!data.file,
      hasResume: !!data.resume
    });

    // Create FormData for proper backend submission
    const formData = new FormData();
    formData.append('name', data.name);
    formData.append('email', data.email);
    formData.append('phone', data.phone || '555-0000'); // Required by backend
    
    // We need to create a file from the resume text if none was uploaded
    let cvFile: File;
    if (data.file) {
      cvFile = data.file;
    } else if (data.resume) {
      // Create a file from the resume text
      console.log("Creating file from resume text");
      const textFileBlob = new Blob([data.resume], { type: 'text/plain' });
      cvFile = new File([textFileBlob], 'resume.txt', { type: 'text/plain' });
    } else {
      throw new Error('No resume content provided. Please upload a file or enter resume text.');
    }
    
    // The backend expects a form field named 'cv_file'
    formData.append('cv_file', cvFile);
    
    // Log the form data for debugging
    for (const pair of formData.entries()) {
      if (pair[1] instanceof File) {
        console.log(`${pair[0]}: File (${(pair[1] as File).name}, ${(pair[1] as File).type}, ${(pair[1] as File).size} bytes)`);
      } else {
        console.log(`${pair[0]}: ${pair[1]}`);
      }
    }
    
    // 1. Submit candidate data to create the candidate
    console.log(`Submitting to ${API_URL}/candidates`);
    const candidateResponse = await fetch(`${API_URL}/candidates`, {
      method: 'POST',
      body: formData, // FormData will set the correct multipart/form-data content type
    });
    
    if (!candidateResponse.ok) {
      const errorText = await candidateResponse.text();
      console.error("Candidate creation failed:", errorText);
      let errorMessage = "Failed to create candidate profile";
      
      try {
        // Try to parse the error as JSON for a better error message
        const errorJson = JSON.parse(errorText);
        if (errorJson.detail) {
          if (Array.isArray(errorJson.detail)) {
            errorMessage = errorJson.detail.map((err: ErrorDetail) => 
              `${err.loc.join('.')}: ${err.msg}`
            ).join(', ');
          } else {
            errorMessage = errorJson.detail;
          }
        }
      } catch {
        // If error isn't valid JSON, use the raw text
        errorMessage = errorText;
      }
      
      throw new Error(errorMessage);
    }
    
    const candidateData = await candidateResponse.json();
    console.log("Candidate created successfully:", candidateData);
    
    // 2. Calculate match score with the job
    try {
      console.log(`Calculating match for job ${data.jobDescriptionId} and candidate ${candidateData.id}`);
      const matchResponse = await fetch(`${API_URL}/match`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          job_id: parseInt(data.jobDescriptionId),
          candidate_id: candidateData.id,
        }),
      });
      
      if (!matchResponse.ok) {
        const errorText = await matchResponse.text();
        console.error("Match calculation failed:", errorText);
        throw new Error(`Failed to calculate match score: ${matchResponse.statusText}`);
      }
      
      const matchData = await matchResponse.json();
      console.log("Match calculated successfully:", matchData);
      
      // 3. Format the result for the UI
      return {
        success: true,
        candidateId: candidateData.id,
        matchScore: matchData.score * 100 || 0, // Convert from 0-1 to percentage
        strengths: matchData.skills_match?.strong_points || [],
        gaps: matchData.skills_match?.gaps || [],
        interview: {
          status: "Pending",
          date: new Date(Date.now() + 5 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
          time: "10:00 AM",
        }
      };
    } catch (matchError) {
      console.error("Match calculation error:", matchError);
      // Return basic candidate data without match information
      return {
        success: true,
        candidateId: candidateData.id,
        matchScore: 0,
        strengths: [],
        gaps: [],
        interview: {
          status: "Pending",
          date: new Date(Date.now() + 5 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], 
          time: "10:00 AM",
        }
      };
    }
  } catch (error) {
    console.error('Error in uploadCandidateCV:', error);
    throw error; // Rethrow to let the component handle the error
  }
}

/**
 * Get available job descriptions
 */
export async function getJobDescriptions(): Promise<JobResponse[]> {
  try {
    const response = await fetch(`${API_URL}/jobs`);
    
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to fetch job descriptions: ${errorText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching job descriptions:', error);
    throw error;
  }
}

/**
 * Get job description by ID
 */
export async function getJobDescriptionById(id: string): Promise<JobResponse> {
  try {
    const response = await fetch(`${API_URL}/jobs/${id}`);
    
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to fetch job description: ${errorText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching job description:', error);
    throw error;
  }
}

/**
 * Get all candidates
 */
export async function getCandidates(): Promise<CandidateResponse[]> {
  try {
    const response = await fetch(`${API_URL}/candidates`);
    
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to fetch candidates: ${errorText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching candidates:', error);
    throw error;
  }
}

/**
 * Get candidate by ID
 */
export async function getCandidateById(id: string): Promise<CandidateResponse> {
  try {
    const response = await fetch(`${API_URL}/candidates/${id}`);
    
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to fetch candidate: ${errorText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching candidate:', error);
    throw error;
  }
}

/**
 * Get match by job ID and candidate ID
 */
export async function getMatchByJobAndCandidate(jobId: string, candidateId: string): Promise<MatchResponse> {
  try {
    const response = await fetch(`${API_URL}/match/${jobId}/${candidateId}`);
    
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to fetch match: ${errorText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching match:', error);
    throw error;
  }
}

/**
 * Get all matches
 */
export async function getMatches(): Promise<MatchResponse[]> {
  try {
    const response = await fetch(`${API_URL}/matches`);
    
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to fetch matches: ${errorText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching matches:', error);
    throw error;
  }
}

/**
 * Get dashboard stats
 */
export async function getDashboardStats() {
  try {
    const response = await fetch(`${API_URL}/dashboard/stats`);
    
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to fetch dashboard stats: ${errorText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching dashboard stats:', error);
    throw error;
  }
} 