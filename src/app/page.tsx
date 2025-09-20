"use client";
import { useState } from "react";
import { AppSidebar } from "@/components/app-sidebar";
import { SiteHeader } from "@/components/site-header";
import { ResumeCards } from "@/components/resume-evaluation";
import { JobCards } from "@/components/job-description";
import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar";

export type Job = {
  id: number;
  companyName: string;
  jobRole: string;
  description: string;
};

export default function Home() {
  const [activeSection, setActiveSection] = useState("Resume Evaluation");
  
  const [jobs, setJobs] = useState<Job[]>([]);

  const handleAddJob = (newJobData: Omit<Job, 'id'>) => {
    const newJob: Job = { id: Date.now(), ...newJobData };
    setJobs([...jobs, newJob]);
  };

  const handleUpdateJob = (updatedJob: Job) => {
    setJobs(jobs.map((job) => (job.id === updatedJob.id ? updatedJob : job)));
  };

  const renderContent = () => {
    switch (activeSection) {
      case "Resume Evaluation":
        return <ResumeCards jobs={jobs} onNavigate={setActiveSection} />;
      case "Job Description":
        return (
          <JobCards
            jobs={jobs}
            onAddJob={handleAddJob}
            onUpdateJob={handleUpdateJob}
          />
        );
      default:
        return <ResumeCards jobs={jobs} onNavigate={setActiveSection} />;
    }
  };

  return (
    <SidebarProvider
      style={{
        "--sidebar-width": "calc(var(--spacing) * 72)",
        "--header-height": "calc(var(--spacing) * 12)",
      } as React.CSSProperties}
    >
      <AppSidebar
        variant="inset"
        activeSection={activeSection}
        onSectionChange={setActiveSection}
      />
      <SidebarInset>
        <SiteHeader title={activeSection} />
        <main className="flex-1 p-4 md:p-6">{renderContent()}</main>
      </SidebarInset>
    </SidebarProvider>
  );
}