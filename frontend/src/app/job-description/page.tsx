"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { submitJobDescription } from "@/lib/api";

// Define interfaces for type safety
interface JobFormData {
  title: string;
  company: string;
  location: string;
  description: string;
}

interface JobResultData {
  id: string;
  title: string;
  company: string;
  summary: string;
  required_skills?: string[];
  required_experience?: string;
  responsibilities?: string[];
}

export default function JobDescriptionPage() {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [jobResult, setJobResult] = useState<JobResultData | null>(null);

  const form = useForm<JobFormData>({
    defaultValues: {
      title: "",
      company: "",
      location: "",
      description: "",
    },
  });

  async function onSubmit(data: JobFormData) {
    setIsSubmitting(true);
    try {
      // Validate required fields
      if (!data.title || !data.company || !data.description) {
        toast.error("Please fill in all required fields");
        setIsSubmitting(false);
        return;
      }

      const result = await submitJobDescription(data);
      setJobResult(result);
      form.reset(); // Clear the form
      toast.success("Job description submitted successfully!");
    } catch (error) {
      console.error(error);
      const errorMessage = error instanceof Error ? error.message : "Server error. Please try again.";
      toast.error(`Failed to submit job description: ${errorMessage}`);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="container py-10">
      <div className="flex flex-col items-center mb-8 text-center">
        <h1 className="text-3xl font-bold tracking-tight text-primary mb-2">Job Description</h1>
        <p className="text-muted-foreground max-w-2xl">
          Submit a job description to start matching with candidates.
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto">
        <Card>
          <CardHeader>
            <CardTitle>Enter Job Description</CardTitle>
            <CardDescription>
              Fill out the form below with details about the job you&apos;re hiring for.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                <FormField
                  control={form.control}
                  name="title"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Job Title</FormLabel>
                      <FormControl>
                        <Input placeholder="e.g. Senior Software Engineer" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="company"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Company Name</FormLabel>
                      <FormControl>
                        <Input placeholder="e.g. Acme Corporation" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="location"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Location</FormLabel>
                      <FormControl>
                        <Input placeholder="e.g. New York, NY (Remote)" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="description"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Job Description</FormLabel>
                      <FormControl>
                        <Textarea 
                          placeholder="Enter the full job description including responsibilities, requirements, and benefits..." 
                          className="min-h-32"
                          {...field} 
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <Button type="submit" className="w-full" disabled={isSubmitting}>
                  {isSubmitting ? "Submitting..." : "Submit Job Description"}
                </Button>
              </form>
            </Form>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>AI Processing Results</CardTitle>
            <CardDescription>
              AI-generated summary and analysis of your job description.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {jobResult ? (
              <div className="space-y-6">
                <div>
                  <h3 className="font-medium mb-2">Job Summary:</h3>
                  <p className="text-sm text-muted-foreground">
                    {jobResult.summary}
                  </p>
                </div>

                <div>
                  <h3 className="font-medium mb-2">Required Skills:</h3>
                  <div className="flex flex-wrap gap-2">
                    {jobResult.required_skills?.map((skill: string, index: number) => (
                      <span 
                        key={index}
                        className="px-2 py-1 rounded-full text-xs bg-primary/10 text-primary"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <h3 className="font-medium mb-2">Required Experience:</h3>
                  <p className="text-sm text-muted-foreground">
                    {jobResult.required_experience}
                  </p>
                </div>

                <div>
                  <h3 className="font-medium mb-2">Key Responsibilities:</h3>
                  <ul className="list-disc pl-5 text-sm text-muted-foreground space-y-1">
                    {jobResult.responsibilities?.map((responsibility: string, index: number) => (
                      <li key={index}>{responsibility}</li>
                    ))}
                  </ul>
                </div>
              </div>
            ) : (
              <div className="flex h-full min-h-40 items-center justify-center text-muted-foreground text-sm">
                <p>Submit a job description to see results here.</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
} 