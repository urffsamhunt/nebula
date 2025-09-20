"use client";

import { useState } from "react";
import { Label } from "./ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "./ui/input";
import { Button } from "./ui/button";
import { Slider } from "@/components/ui/slider";
import { type Job } from "@/app/page";

type ResumeCardsProps = {
  jobs: Job[];
  onNavigate: (sectionName: string) => void;
};

export function ResumeCards({ jobs, onNavigate }: ResumeCardsProps) {
  const [selectedJobId, setSelectedJobId] = useState<string>("");

  return (
    <div className="grid grid-cols-1 gap-4 px-4 lg:px-6 @xl/main:grid-cols-2">
      <Card className="@container/card">
        <CardHeader>
          <CardTitle className="text-2xl font-semibold">Resume Evaluation Form</CardTitle>
        </CardHeader>
        <CardContent>
          <form>
            <div className="flex flex-col gap-6">
              <div className="grid w-full max-w-sm items-center gap-3">
                <Label htmlFor="file">Upload resume</Label>
                <Input id="file" type="file" required multiple />
              </div>
              <div className="grid gap-3">
                <Label htmlFor="job-select">Choose a job description:</Label>
                <div className="flex items-center gap-2">
                  <Select value={selectedJobId} onValueChange={setSelectedJobId}>
                    <SelectTrigger id="job-select" className="w-full">
                      <SelectValue placeholder="Select a job..." />
                    </SelectTrigger>
                    <SelectContent>
                      {jobs.length > 0 ? (
                        jobs.map((job) => (
                          <SelectItem key={job.id} value={String(job.id)}>
                            {job.jobRole} - {job.companyName}
                          </SelectItem>
                        ))
                      ) : (
                        <SelectItem value="none" disabled>
                          No jobs added yet
                        </SelectItem>
                      )}
                    </SelectContent>
                  </Select>
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => onNavigate("Job Description")}
                  >
                    Add New
                  </Button>
                </div>
              </div>
              <Button>Evaluate</Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <Card className="@container/card">
        <CardHeader>
          <CardTitle className="text-2xl font-semibold">Report</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col gap-6">
            <div className="grid gap-3">
              <Label>Relevance Score:</Label>
              <Slider defaultValue={[33]} max={100} step={1} />
            </div>
            <div className="grid gap-3">
              <Label>Missing Details:</Label>
              <span id="missing"></span>
            </div>
            <div className="grid gap-3">
              <Label>Verdict:</Label>
              <span id="verdict"></span>
            </div>
            <div className="grid gap-3">
              <Label>Suggestions for improvement:</Label>
              <span id="suggestions"></span>
            </div>
            <Button>Generate</Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}