import Link from "next/link";
import { Button } from "@/components/ui/button";

export function Navbar() {
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center">
        <Link href="/" className="flex items-center gap-2 font-bold text-2xl text-primary">
          RecruitAI
        </Link>
        <nav className="ml-auto flex gap-4 sm:gap-6">
          <Link href="/" className="text-sm font-medium hover:text-primary">
            Home
          </Link>
          <Link href="/job-description" className="text-sm font-medium hover:text-primary">
            Job Description
          </Link>
          <Link href="/candidate-upload" className="text-sm font-medium hover:text-primary">
            Upload CV
          </Link>
          <Link href="/dashboard" className="text-sm font-medium hover:text-primary">
            Dashboard
          </Link>
        </nav>
        <div className="ml-4">
          <Button variant="outline" className="hidden sm:inline-flex">
            Contact
          </Button>
        </div>
      </div>
    </header>
  );
} 