"use client";
import { useState, useEffect } from "react";
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
  const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "https://letapreemas-nebula-resume-api.hf.space";

  const [activeSection, setActiveSection] = useState("Resume Evaluation");
  
  const [jobs, setJobs] = useState<Job[]>([]);

  const handleAddJob = async (newJobData: Omit<Job, 'id'>) => {
    try {
      const body = new URLSearchParams()
      body.append('company_name', newJobData.companyName)
      body.append('job_role', newJobData.jobRole)
      body.append('description', newJobData.description)

      const res = await fetch(`${API_BASE}/api/v1/save-job-description`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: body.toString(),
      })

      if (!res.ok) {
        const text = await res.text()
        throw new Error(text || 'Failed to save job')
      }

      const data = await res.json()
      const saved = data.saved
      const createdId = saved?.id ?? data.id ?? Date.now()
      const newJob: Job = {
        id: createdId,
        companyName: saved?.company_name ?? newJobData.companyName,
        jobRole: saved?.job_role ?? newJobData.jobRole,
        description: saved?.description ?? newJobData.description,
      }

      setJobs((prev) => [...prev, newJob])
      return newJob
    } catch (err) {
      console.error('handleAddJob error', err)
      alert('Unable to save job description')
      throw err
    }
  };

  const handleUpdateJob = async (updatedJob: Job) => {
    // Optimistically update UI and attempt to persist; roll back on failure.
    const previous = [...jobs]
    setJobs((prev) => prev.map((j) => (j.id === updatedJob.id ? updatedJob : j)))

    try {
      const body = new URLSearchParams()
      body.append('company_name', updatedJob.companyName)
      body.append('job_role', updatedJob.jobRole)
      body.append('description', updatedJob.description)

      const res = await fetch(`${API_BASE}/api/v1/job-descriptions/${updatedJob.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: body.toString(),
      })

      if (!res.ok) {
        const text = await res.text()
        throw new Error(text || 'Failed to update job')
      }

      const data = await res.json()
      const saved = data.saved
      if (saved) {
        const mapped: Job = {
          id: saved.id,
          companyName: saved.company_name,
          jobRole: saved.job_role,
          description: saved.description,
        }
        setJobs((prev) => prev.map((j) => (j.id === mapped.id ? mapped : j)))
      }

      return updatedJob
    } catch (err) {
      console.error('handleUpdateJob error', err)
      alert('Unable to update job description, reverting changes')
      setJobs(previous) // rollback
      throw err
    }
  };

  // Load persisted jobs from backend on component mount
  useEffect(() => {
    const loadJobs = async () => {
      try {
        const res = await fetch(`https://${API_BASE}/api/v1/all-job-descriptions`);
        if (!res.ok) {
          console.error('Failed to fetch job descriptions', await res.text());
          return;
        }
        const payload = await res.json();
        const rows = payload.data ?? payload.job_descriptions ?? [];
        const mapped: Job[] = rows.map((r: any) => ({
          id: r.id,
          companyName: r.company_name,
          jobRole: r.job_role,
          description: r.description,
        }));
        setJobs(mapped);
      } catch (err) {
        console.error('Error loading job descriptions', err);
      }
    };

    void loadJobs();
  }, []);

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