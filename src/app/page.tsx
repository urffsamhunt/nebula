"use client";
import { useState } from "react";
import { AppSidebar } from "@/components/app-sidebar";
import { SiteHeader } from "@/components/site-header";
import { ResumeCards } from "@/components/resume-evaluation";
import { JobCards } from "@/components/job-description";
import {
  SidebarInset,
  SidebarProvider,
} from "@/components/ui/sidebar";

export default function Home() {
  const [activeSection, setActiveSection] = useState("Resume Evaluation");

  const renderContent = () => {
    switch (activeSection) {
      case "Resume Evaluation":
        return <ResumeCards />;
      case "Job Description":
        return <JobCards />;
      default:
        return <ResumeCards />;
    }
  };

  return (
    <SidebarProvider
      style={
        {
          "--sidebar-width": "calc(var(--spacing) * 72)",
          "--header-height": "calc(var(--spacing) * 12)",
        } as React.CSSProperties
      }
    >
      <AppSidebar
        variant="inset"
        activeSection={activeSection}
        onSectionChange={setActiveSection}
      />
      
      <SidebarInset>
        {/* Pass the activeSection state as the 'title' prop */}
        <SiteHeader title={activeSection} />

        <main className="flex-1 p-4 md:p-6">
          {renderContent()}
        </main>
      </SidebarInset>
    </SidebarProvider>
  );
}