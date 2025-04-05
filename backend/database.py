import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Any

class Database:
    def __init__(self, db_path: str = "recruitment.db"):
        self.db_path = db_path
        self.initialize_db()
        
    def get_connection(self):
        """Create and return a database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def initialize_db(self):
        """Initialize the database with required tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create JobDescriptions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS job_descriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            original_description TEXT NOT NULL,
            summarized_description TEXT,
            required_skills TEXT,
            required_experience TEXT,
            responsibilities TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create Candidates table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            phone TEXT,
            education TEXT,
            work_experience TEXT,
            skills TEXT,
            certifications TEXT,
            cv_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create MatchScores table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS match_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER NOT NULL,
            candidate_id INTEGER NOT NULL,
            score REAL NOT NULL,
            skills_match TEXT,
            experience_match TEXT,
            education_match TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (job_id) REFERENCES job_descriptions (id),
            FOREIGN KEY (candidate_id) REFERENCES candidates (id)
        )
        ''')
        
        # Create Interviews table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS interviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER NOT NULL,
            candidate_id INTEGER NOT NULL,
            scheduled_time TIMESTAMP,
            duration_minutes INTEGER DEFAULT 60,
            interview_link TEXT,
            status TEXT DEFAULT 'scheduled',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (job_id) REFERENCES job_descriptions (id),
            FOREIGN KEY (candidate_id) REFERENCES candidates (id)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    # Job Description methods
    def add_job_description(self, title: str, description: str) -> int:
        """Add a job description to the database and return its ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO job_descriptions (title, original_description) VALUES (?, ?)",
            (title, description)
        )
        job_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return job_id
    
    def update_job_summary(self, job_id: int, summary: str, skills: str, experience: str, responsibilities: str) -> bool:
        """Update job description with summarized information"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """UPDATE job_descriptions 
               SET summarized_description = ?, required_skills = ?, 
                   required_experience = ?, responsibilities = ?
               WHERE id = ?""",
            (summary, skills, experience, responsibilities, job_id)
        )
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
    
    def get_job_description(self, job_id: int) -> Optional[Dict]:
        """Retrieve a job description by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM job_descriptions WHERE id = ?", (job_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def get_all_job_descriptions(self) -> List[Dict]:
        """Retrieve all job descriptions"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM job_descriptions ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    # Candidate methods
    def add_candidate(self, name: str, email: str, phone: str, cv_path: str) -> int:
        """Add a candidate to the database and return their ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO candidates (name, email, phone, cv_path) VALUES (?, ?, ?, ?)",
            (name, email, phone, cv_path)
        )
        candidate_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return candidate_id
    
    def update_candidate_profile(self, candidate_id: int, education: str, work_experience: str, 
                                skills: str, certifications: str) -> bool:
        """Update candidate with extracted information"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """UPDATE candidates 
               SET education = ?, work_experience = ?, skills = ?, certifications = ?
               WHERE id = ?""",
            (education, work_experience, skills, certifications, candidate_id)
        )
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
    
    def get_candidate(self, candidate_id: int) -> Optional[Dict]:
        """Retrieve a candidate by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM candidates WHERE id = ?", (candidate_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def get_all_candidates(self) -> List[Dict]:
        """Retrieve all candidates"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM candidates ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    # Match Score methods
    def add_match_score(self, job_id: int, candidate_id: int, score: float, 
                        skills_match: str, experience_match: str, education_match: str) -> int:
        """Add a match score between a job and a candidate"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """INSERT INTO match_scores 
               (job_id, candidate_id, score, skills_match, experience_match, education_match) 
               VALUES (?, ?, ?, ?, ?, ?)""",
            (job_id, candidate_id, score, skills_match, experience_match, education_match)
        )
        match_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return match_id
    
    def get_match_scores_by_job(self, job_id: int) -> List[Dict]:
        """Get all candidate matches for a specific job"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT ms.*, c.name AS candidate_name, c.email AS candidate_email
            FROM match_scores ms
            JOIN candidates c ON ms.candidate_id = c.id
            WHERE ms.job_id = ?
            ORDER BY ms.score DESC
        """, (job_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_match_scores_by_candidate(self, candidate_id: int) -> List[Dict]:
        """Get all job matches for a specific candidate"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT ms.*, jd.title AS job_title
            FROM match_scores ms
            JOIN job_descriptions jd ON ms.job_id = jd.id
            WHERE ms.candidate_id = ?
            ORDER BY ms.score DESC
        """, (candidate_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    # Interview methods
    def schedule_interview(self, job_id: int, candidate_id: int, 
                          scheduled_time: datetime, duration_minutes: int, 
                          interview_link: str) -> int:
        """Schedule an interview between a job and a candidate"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """INSERT INTO interviews 
               (job_id, candidate_id, scheduled_time, duration_minutes, interview_link) 
               VALUES (?, ?, ?, ?, ?)""",
            (job_id, candidate_id, scheduled_time.isoformat(), duration_minutes, interview_link)
        )
        
        interview_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return interview_id
    
    def update_interview_status(self, interview_id: int, status: str, notes: Optional[str] = None) -> bool:
        """Update the status of an interview"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if notes:
            cursor.execute(
                "UPDATE interviews SET status = ?, notes = ? WHERE id = ?",
                (status, notes, interview_id)
            )
        else:
            cursor.execute(
                "UPDATE interviews SET status = ? WHERE id = ?",
                (status, interview_id)
            )
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
    
    def get_interviews_by_job(self, job_id: int) -> List[Dict]:
        """Get all interviews for a specific job"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT i.*, c.name AS candidate_name, c.email AS candidate_email,
                   jd.title AS job_title
            FROM interviews i
            JOIN candidates c ON i.candidate_id = c.id
            JOIN job_descriptions jd ON i.job_id = jd.id
            WHERE i.job_id = ?
            ORDER BY i.scheduled_time
        """, (job_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_interviews_by_candidate(self, candidate_id: int) -> List[Dict]:
        """Get all interviews for a specific candidate"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT i.*, jd.title AS job_title
            FROM interviews i
            JOIN job_descriptions jd ON i.job_id = jd.id
            WHERE i.candidate_id = ?
            ORDER BY i.scheduled_time
        """, (candidate_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows] 