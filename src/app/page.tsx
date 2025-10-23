import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Target, PencilLine, FileCheck } from "lucide-react"; // Icons for features

export default function LandingPage() {
  return (
    <div className="flex flex-col min-h-screen bg-white text-gray-900">
      
      <header className="container mx-auto max-w-5xl px-4 sm:px-6 lg:px-8 py-4">
        <nav className="flex justify-between items-center">
          <h1 className="text-2xl font-bold">Nebula</h1>
          <Link href="/login">
            <Button variant="outline">Login</Button>
          </Link>
        </nav>
      </header>

      
      <main className="flex-1">
        <section className="container mx-auto max-w-5xl px-4 sm:px-6 lg:px-8 text-center py-20 sm:py-32">
          <h2 className="text-4xl sm:text-5xl md:text-6xl font-bold">
            Stop Guessing. Start Impressing.
          </h2>
          <p className="mt-4 text-lg sm:text-xl text-gray-600 max-w-2xl mx-auto">
            Nebula is your personal AI resume coach. We analyze your resume
            against any job description to give you the exact keywords and
            feedback you need to get past recruiters.
          </p>
          <div className="mt-8">
            <Link href="/signup">
              <Button size="lg">Get Started Free</Button>
            </Link>
          </div>
        </section>

        <section className="bg-gray-50 py-20 sm:py-24">
          <div className="container mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
            <h3 className="text-3xl font-bold text-center">
              Why You'll Love Nebula
            </h3>
            <p className="text-center text-gray-600 mt-2">
              Everything you need to build a winning resume.
            </p>

            <div className="grid md:grid-cols-3 gap-8 mt-12">
              <Card>
                <CardHeader>
                  <Target className="h-8 w-8 text-rose-600 mb-2" />
                  <CardTitle>AI Keyword Matching</CardTitle>
                  <CardDescription>
                    Instantly find the most important keywords from a job
                    description and see how well your resume matches.
                  </CardDescription>
                </CardHeader>
              </Card>

              <Card>
                <CardHeader>
                  <PencilLine className="h-8 w-8 text-rose-600 mb-2" />
                  <CardTitle>Action Verb Suggestions</CardTitle>
                  <CardDescription>
                    Upgrade weak language with powerful action verbs that
                    showcase your true impact and achievements.
                  </CardDescription>
                </CardHeader>
              </Card>

              <Card>
                <CardHeader>
                  <FileCheck className="h-8 w-8 text-rose-600 mb-2" />
                  <CardTitle>ATS-Friendly Check</CardTitle>
                  <CardDescription>
                    Ensure your resume's format is easily parsable by Applicant
                    Tracking Systems (ATS) so a human actually sees it.
                  </CardDescription>
                </CardHeader>
              </Card>
            </div>
          </div>
        </section>

        <section className="py-20 sm:py-24">
          <div className="container mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
            <h3 className="text-3xl font-bold text-center">
              Get Hired in 3 Easy Steps
            </h3>
            <div className="grid md:grid-cols-3 gap-8 text-center mt-12">
              <div>
                <span className="text-4xl font-bold text-rose-600">1.</span>
                <h4 className="text-xl font-semibold mt-2">Upload</h4>
                <p className="text-gray-600 mt-1">
                  Add your current resume and the job description you're
                  targeting.
                </p>
              </div>
              <div>
                <span className="text-4xl font-bold text-rose-600">2.</span>
                <h4 className="text-xl font-semibold mt-2">Analyze</h4>
                <p className="text-gray-600 mt-1">
                  Nebula's AI analyzes both documents in seconds and provides a
                  detailed report.
                </p>
              </div>
              <div>
                <span className="text-4xl font-bold text-rose-600">3.</span>
                <h4 className="text-xl font-semibold mt-2">Optimize</h4>
                <p className="text-gray-600 mt-1">
                  Make the recommended changes, export your new resume, and apply
                  with confidence.
                </p>
              </div>
            </div>
          </div>
        </section>
      </main>

      <footer className="border-t bg-gray-50">
        <div className="container mx-auto max-w-5xl px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-sm text-gray-500">
            © {new Date().getFullYear()} Nebula. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
}