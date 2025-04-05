import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import Link from "next/link";

export default function Home() {
  return (
    <div className="flex flex-col min-h-[calc(100vh-80px)]">
      {/* Hero Section */}
      <section className="w-full py-12 md:py-24 lg:py-32 bg-gradient-to-b from-blue-50 to-white">
        <div className="container px-4 md:px-6">
          <div className="grid gap-6 lg:grid-cols-2 lg:gap-12 items-center">
            <div className="flex flex-col justify-center space-y-4">
              <div className="space-y-2">
                <h1 className="text-3xl font-bold tracking-tighter sm:text-5xl xl:text-6xl/none text-primary">
                  Smart Recruitment for the Modern Workplace
                </h1>
                <p className="max-w-[600px] text-muted-foreground md:text-xl">
                  Our AI-powered platform streamlines your recruitment process by matching the best candidates 
                  to your job descriptions with unprecedented accuracy.
                </p>
              </div>
              <div className="flex flex-col gap-2 min-[400px]:flex-row">
                <Link href="/job-description">
                  <Button size="lg" className="bg-primary hover:bg-primary/90">Submit Job Description</Button>
                </Link>
                <Link href="/candidate-upload">
                  <Button size="lg" variant="outline" className="border-primary text-primary hover:bg-primary/10">
                    Upload CV
                  </Button>
                </Link>
              </div>
            </div>
            <div className="flex justify-center">
              <div className="relative h-[350px] w-[350px] rounded-full bg-gradient-to-r from-blue-200 to-blue-400 flex items-center justify-center">
                <div className="absolute inset-4 rounded-full bg-white flex items-center justify-center">
                  <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-primary">
                    <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"></path>
                    <circle cx="9" cy="7" r="4"></circle>
                    <path d="M22 21v-2a4 4 0 0 0-3-3.87"></path>
                    <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
                  </svg>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="w-full py-12 md:py-24 lg:py-32">
        <div className="container px-4 md:px-6">
          <div className="flex flex-col items-center justify-center space-y-4 text-center">
            <div className="space-y-2">
              <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl text-primary">
                Key Features
              </h2>
              <p className="max-w-[900px] text-muted-foreground md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed">
                Our platform combines cutting-edge AI with intuitive design to transform your recruitment process.
              </p>
            </div>
          </div>
          <div className="mx-auto grid max-w-5xl grid-cols-1 gap-6 py-12 md:grid-cols-3">
            <Card>
              <CardHeader>
                <CardTitle>Smart JD Processing</CardTitle>
                <CardDescription>
                  Analyze and extract key requirements from job descriptions.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Our AI parses job descriptions and identifies key skills, experience, and qualifications needed.
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>CV Matching</CardTitle>
                <CardDescription>
                  Match candidates to jobs with precision.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Advanced algorithms compare CVs against job requirements to find the perfect match.
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>Real-time Analytics</CardTitle>
                <CardDescription>
                  Monitor recruitment progress in real-time.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Track candidate statuses, match scores, and recruitment pipeline metrics in one place.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>
    </div>
  );
}
