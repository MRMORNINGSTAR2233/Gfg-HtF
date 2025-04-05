"use client";

import { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { uploadCandidateCV, getJobDescriptions } from "@/lib/api";
import { Loader2 } from "lucide-react";

// Define interfaces for type safety
interface CandidateFormData {
  name: string;
  email: string;
  phone: string;
  jobDescriptionId: string;
  resume: string;
}

interface JobDescription {
  id: number;
  title: string;
  company: string;
}

interface MatchResultData {
  success: boolean;
  candidateId: number;
  matchScore: number;
  strengths: string[];
  gaps: string[];
  interview: {
    status: string;
    date: string;
    time: string;
  };
}

export default function CandidateUploadPage() {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isProcessingFile, setIsProcessingFile] = useState(false);
  const [matchResult, setMatchResult] = useState<MatchResultData | null>(null);
  const [jobDescriptions, setJobDescriptions] = useState<JobDescription[]>([]);
  const [isLoadingJobs, setIsLoadingJobs] = useState(true);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [fileText, setFileText] = useState<string>("");

  const form = useForm<CandidateFormData>({
    defaultValues: {
      name: "",
      email: "",
      phone: "",
      jobDescriptionId: "",
      resume: "",
    },
  });

  // Fetch job descriptions on component mount
  useEffect(() => {
    async function loadJobDescriptions() {
      try {
        const jobs = await getJobDescriptions();
        setJobDescriptions(jobs || []);
      } catch (error) {
        console.error("Error loading job descriptions:", error);
        toast.error("Failed to load job descriptions. Please refresh the page.");
      } finally {
        setIsLoadingJobs(false);
      }
    }

    loadJobDescriptions();
  }, []);

  // Handle file selection
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null;
    if (file) {
      setSelectedFile(file);
      
      // Read the file content if it's a text file
      if (file.type === "text/plain" || file.name.endsWith('.txt')) {
        setIsProcessingFile(true);
        const reader = new FileReader();
        reader.onload = (event) => {
          const text = event.target?.result as string;
          setFileText(text);
          form.setValue("resume", text);
          setIsProcessingFile(false);
        };
        reader.onerror = () => {
          toast.error("Failed to read file. Please try again.");
          setIsProcessingFile(false);
        };
        reader.readAsText(file);
      } else {
        toast.info("Non-text files will be processed by the server.");
      }
    }
  };

  // Trigger the file input click
  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  // Handle direct submission without mock data fallback
  const handleSubmission = async (data: CandidateFormData) => {
    try {
      return await uploadCandidateCV({
        name: data.name,
        email: data.email,
        phone: data.phone,
        jobDescriptionId: data.jobDescriptionId,
        resume: data.resume || fileText,
        file: selectedFile
      });
    } catch (error) {
      console.error("CV submission error:", error);
      // Rethrow the error to be handled by the onSubmit function
      throw error;
    }
  };

  async function onSubmit(data: CandidateFormData) {
    setIsSubmitting(true);
    try {
      // Validate required fields
      if (!data.name || !data.email || !data.jobDescriptionId) {
        toast.error("Please fill in all required fields");
        setIsSubmitting(false);
        return;
      }

      // Ensure phone is present (required by backend)
      if (!data.phone) {
        data.phone = "555-0000"; // Provide default if empty
        form.setValue("phone", data.phone);
      }

      // Ensure either resume text or file is provided
      if (!data.resume && !fileText && !selectedFile) {
        toast.error("Please provide a resume text or upload a file");
        setIsSubmitting(false);
        return;
      }

      // If there's a file but no resume text, let the user know
      if (selectedFile && !data.resume && !fileText) {
        toast.info("Reading file content...");
        return;
      }

      // Submit data to API
      const result = await handleSubmission(data);
      
      setMatchResult(result);
      toast.success("CV analyzed successfully!");
      
      // Reset form after successful submission
      form.reset();
      setSelectedFile(null);
      setFileText("");
    } catch (error) {
      console.error(error);
      const errorMessage = error instanceof Error ? error.message : "Server error occurred. Please try again.";
      toast.error(`Failed to analyze CV: ${errorMessage}`);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="container py-10">
      <div className="flex flex-col items-center mb-8 text-center">
        <h1 className="text-3xl font-bold tracking-tight text-primary mb-2">Upload Your CV</h1>
        <p className="text-muted-foreground max-w-2xl">
          Submit your CV to get matched with relevant job opportunities.
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto">
        <Card>
          <CardHeader>
            <CardTitle>Candidate Information</CardTitle>
            <CardDescription>
              Fill out the form below with your details and resume.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                <FormField
                  control={form.control}
                  name="name"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Full Name</FormLabel>
                      <FormControl>
                        <Input placeholder="e.g. John Smith" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="email"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Email Address</FormLabel>
                      <FormControl>
                        <Input type="email" placeholder="e.g. john.smith@example.com" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="phone"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Phone Number</FormLabel>
                      <FormControl>
                        <Input placeholder="e.g. 555-123-4567" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="jobDescriptionId"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Select Job Description</FormLabel>
                      <Select onValueChange={field.onChange} defaultValue={field.value}>
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder={isLoadingJobs ? "Loading job descriptions..." : "Select a job description"} />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          {jobDescriptions.length > 0 ? (
                            jobDescriptions.map((job) => (
                              <SelectItem key={job.id} value={job.id.toString()}>
                                {job.title} at {job.company || "Company"}
                              </SelectItem>
                            ))
                          ) : (
                            <SelectItem value="no-jobs" disabled>
                              {isLoadingJobs ? "Loading..." : "No job descriptions available"}
                            </SelectItem>
                          )}
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="resume"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Resume/CV Text</FormLabel>
                      <FormControl>
                        <Textarea 
                          placeholder="Paste your resume or CV text here..." 
                          className="min-h-32"
                          {...field} 
                          value={field.value || fileText}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <div className="flex items-center justify-between">
                  <p className="text-sm text-muted-foreground">
                    Or upload a file {selectedFile && !isProcessingFile && `(Selected: ${selectedFile.name})`}
                    {isProcessingFile && (
                      <span className="flex items-center ml-1">
                        <Loader2 className="h-3 w-3 animate-spin mr-1" />
                        Processing file...
                      </span>
                    )}
                  </p>
                  <input 
                    type="file" 
                    ref={fileInputRef} 
                    className="hidden" 
                    onChange={handleFileChange} 
                    accept=".txt,.pdf,.doc,.docx"
                    aria-label="Upload resume file"
                    disabled={isProcessingFile || isSubmitting}
                  />
                  <Button 
                    type="button" 
                    variant={selectedFile ? "default" : "outline"} 
                    onClick={handleUploadClick}
                    className={selectedFile ? "bg-green-600 hover:bg-green-700" : ""}
                    disabled={isProcessingFile || isSubmitting}
                  >
                    {isProcessingFile ? (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin mr-2" />
                        Processing...
                      </>
                    ) : selectedFile ? "Change File" : "Upload File"}
                  </Button>
                </div>

                <Button 
                  type="submit" 
                  className="w-full" 
                  disabled={isSubmitting || isProcessingFile || jobDescriptions.length === 0}
                >
                  {isSubmitting ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin mr-2" />
                      Analyzing...
                    </>
                  ) : "Submit Application"}
                </Button>
              </form>
            </Form>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Match Results</CardTitle>
            <CardDescription>
              AI-generated match score and analysis.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {matchResult ? (
              <div className="space-y-6">
                <div className="flex justify-center">
                  <div className="relative h-32 w-32 rounded-full flex items-center justify-center">
                    <div className="absolute inset-1 rounded-full bg-gradient-to-r from-blue-200 to-green-200 flex items-center justify-center">
                      <div className="absolute inset-2 rounded-full bg-white flex flex-col items-center justify-center">
                        <span className="text-3xl font-bold text-primary">{Math.round(matchResult.matchScore)}%</span>
                        <span className="text-xs text-muted-foreground">Match Score</span>
                      </div>
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className="font-medium text-sm mb-2">Strengths:</h3>
                  <ul className="list-disc pl-5 text-sm text-muted-foreground space-y-1">
                    {matchResult.strengths.map((strength: string, index: number) => (
                      <li key={index}>{strength}</li>
                    ))}
                  </ul>
                </div>

                <div>
                  <h3 className="font-medium text-sm mb-2">Areas for Improvement:</h3>
                  <ul className="list-disc pl-5 text-sm text-muted-foreground space-y-1">
                    {matchResult.gaps.map((gap: string, index: number) => (
                      <li key={index}>{gap}</li>
                    ))}
                  </ul>
                </div>

                <div className="bg-muted p-4 rounded-lg">
                  <h3 className="font-medium text-sm mb-2">Interview Details:</h3>
                  <p className="text-sm text-muted-foreground">
                    Status: <span className="font-medium text-green-600">{matchResult.interview.status}</span>
                  </p>
                  <p className="text-sm text-muted-foreground">
                    Date: {matchResult.interview.date} at {matchResult.interview.time}
                  </p>
                </div>
              </div>
            ) : (
              <div className="flex h-full min-h-40 items-center justify-center text-muted-foreground text-sm">
                <p>Submit your CV to see match results here.</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
} 