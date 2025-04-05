"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { useRouter } from "next/navigation";
import { getCandidates, getJobDescriptions, getDashboardStats } from "@/lib/api";
import { toast } from "sonner";

// Define interfaces for type safety
interface Job {
  id: number;
  title: string;
  company: string;
  location?: string;
  status?: string;
  candidateCount?: number;
}

interface Candidate {
  id: number;
  name: string;
  email: string;
  jobTitle?: string;
  status?: string;
  matchScore?: number;
}

interface DashboardStats {
  totalJobs: number;
  totalCandidates: number;
  averageMatchScore: number;
  scheduledInterviews: number;
  jobsLastWeek?: number;
  candidatesLastWeek?: number;
  interviewsLastWeek?: number;
}

export default function DashboardPage() {
  const router = useRouter();
  const [jobs, setJobs] = useState<Job[]>([]);
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [stats, setStats] = useState<DashboardStats>({
    totalJobs: 0,
    totalCandidates: 0,
    averageMatchScore: 0,
    scheduledInterviews: 0,
  });
  const [loading, setLoading] = useState(true);

  // Function to fetch all data
  const fetchData = async () => {
    try {
      // Fetch jobs, candidates, and stats in parallel
      const [jobsData, candidatesData, statsData] = await Promise.all([
        getJobDescriptions(),
        getCandidates(),
        getDashboardStats().catch(() => null) // If stats API fails, return null
      ]);
      
      setJobs(jobsData || []);
      setCandidates(candidatesData || []);
      
      if (statsData) {
        setStats(statsData);
      }
    } catch (error) {
      console.error("Error fetching dashboard data:", error);
      toast.error("Failed to load some dashboard data. Please refresh.");
    } finally {
      setLoading(false);
    }
  };

  // Initial data fetch
  useEffect(() => {
    fetchData();
    
    // Set up polling every 10 seconds for real-time updates
    const interval = setInterval(fetchData, 10000);
    
    // Clean up the interval on component unmount
    return () => clearInterval(interval);
  }, []);

  // Navigate to job description page
  const navigateToJobForm = () => {
    router.push("/job-description");
  };

  // Navigate to candidate upload page
  const navigateToUploadCV = () => {
    router.push("/candidate-upload");
  };

  return (
    <div className="container py-10">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-primary">Dashboard</h1>
          <p className="text-muted-foreground">Monitor your recruitment analytics and candidate matches.</p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline" onClick={navigateToJobForm}>
            Post New Job
          </Button>
          <Button onClick={navigateToUploadCV}>
            Upload CV
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Active Jobs</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{jobs.length}</div>
            <p className="text-xs text-muted-foreground">
              {stats.jobsLastWeek ? `+${stats.jobsLastWeek} from last week` : ""}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Candidates</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{candidates.length}</div>
            <p className="text-xs text-muted-foreground">
              {stats.candidatesLastWeek ? `+${stats.candidatesLastWeek} from last week` : ""}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Average Match Score</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.averageMatchScore ? `${Math.round(stats.averageMatchScore)}%` : "N/A"}</div>
            <Progress value={stats.averageMatchScore || 0} className="h-1 mt-2" />
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Scheduled Interviews</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.scheduledInterviews || 0}</div>
            <p className="text-xs text-muted-foreground">
              {stats.interviewsLastWeek ? `+${stats.interviewsLastWeek} from last week` : ""}
            </p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="candidates" className="w-full">
        <TabsList className="grid w-full md:w-[400px] grid-cols-2">
          <TabsTrigger value="candidates">Candidates</TabsTrigger>
          <TabsTrigger value="jobs">Jobs</TabsTrigger>
        </TabsList>
        <TabsContent value="candidates" className="mt-6">
          <div className="rounded-lg border">
            <div className="bg-muted p-4 grid grid-cols-6 font-medium">
              <div className="col-span-2">Name</div>
              <div className="col-span-1">Job Position</div>
              <div className="col-span-1">Status</div>
              <div className="col-span-1">Match Score</div>
              <div className="col-span-1 text-right">Actions</div>
            </div>
            <div className="divide-y">
              {loading ? (
                <div className="p-4 text-center text-muted-foreground">Loading candidates...</div>
              ) : candidates.length === 0 ? (
                <div className="p-4 text-center text-muted-foreground">No candidates found. Upload some CVs to get started.</div>
              ) : (
                candidates.map((candidate) => (
                  <div key={candidate.id} className="p-4 grid grid-cols-6 items-center">
                    <div className="col-span-2">
                      <div className="font-medium">{candidate.name}</div>
                      <div className="text-sm text-muted-foreground">{candidate.email}</div>
                    </div>
                    <div className="col-span-1">
                      {candidate.jobTitle || "Not specified"}
                    </div>
                    <div className="col-span-1">
                      <Badge variant={candidate.status === "Interviewed" ? "success" : candidate.status === "Matched" ? "default" : "secondary"}>
                        {candidate.status || "New"}
                      </Badge>
                    </div>
                    <div className="col-span-1">
                      <div className="flex items-center gap-2">
                        <Progress value={candidate.matchScore || 0} className="h-2" />
                        <span className="text-sm font-medium">{Math.round(candidate.matchScore || 0)}%</span>
                      </div>
                    </div>
                    <div className="col-span-1 text-right">
                      <Button variant="outline" size="sm" onClick={() => router.push(`/candidates/${candidate.id}`)}>
                        View
                      </Button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </TabsContent>
        <TabsContent value="jobs" className="mt-6">
          <div className="rounded-lg border">
            <div className="bg-muted p-4 grid grid-cols-6 font-medium">
              <div className="col-span-2">Title</div>
              <div className="col-span-1">Company</div>
              <div className="col-span-1">Candidates</div>
              <div className="col-span-1">Status</div>
              <div className="col-span-1 text-right">Actions</div>
            </div>
            <div className="divide-y">
              {loading ? (
                <div className="p-4 text-center text-muted-foreground">Loading jobs...</div>
              ) : jobs.length === 0 ? (
                <div className="p-4 text-center text-muted-foreground">No jobs found. Add a job description to get started.</div>
              ) : (
                jobs.map((job) => (
                  <div key={job.id} className="p-4 grid grid-cols-6 items-center">
                    <div className="col-span-2">
                      <div className="font-medium">{job.title}</div>
                      <div className="text-sm text-muted-foreground">{job.location || "Remote"}</div>
                    </div>
                    <div className="col-span-1">
                      {job.company || "Not specified"}
                    </div>
                    <div className="col-span-1">
                      {job.candidateCount || 0} applicants
                    </div>
                    <div className="col-span-1">
                      <Badge variant={job.status === "Closed" ? "destructive" : job.status === "Interviewing" ? "success" : "default"}>
                        {job.status || "Open"}
                      </Badge>
                    </div>
                    <div className="col-span-1 text-right">
                      <Button variant="outline" size="sm" onClick={() => router.push(`/jobs/${job.id}`)}>
                        View
                      </Button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
} 