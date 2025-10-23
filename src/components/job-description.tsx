"use client";

import { useState } from "react";
import { Label } from "./ui/label";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "./ui/input";
import { Button } from "./ui/button";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter,
  DialogClose,
} from "@/components/ui/dialog";
import { type Job } from "@/app/dashboard/dashboard-client"
type JobCardsProps = {
  jobs: Job[];
  onAddJob: (newJobData: Omit<Job, "id">) => void;
  onUpdateJob: (updatedJob: Job) => void;
};

export function JobCards({ jobs, onAddJob, onUpdateJob }: JobCardsProps) {

  const [companyName, setCompanyName] = useState("");
  const [jobRole, setJobRole] = useState("");
  const [description, setDescription] = useState("");
  const [editingJob, setEditingJob] = useState<Job | null>(null);

  const handleAddJobClick = () => {
    if (!companyName.trim() || !jobRole.trim() || !description.trim()) {
      alert("Please fill out all fields.");
      return;
    }
    onAddJob({ companyName, jobRole, description });
    setCompanyName("");
    setJobRole("");
    setDescription("");
  };

  const handleUpdateJobClick = () => {
    if (!editingJob) return;
    onUpdateJob(editingJob);
    setEditingJob(null);
  };

  return (
    <div className="grid grid-cols-1 gap-4 px-4 lg:px-6 @container/main">
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl font-semibold">Add Job Description</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col gap-6">
            <div className="grid gap-2">
              <Label htmlFor="comp-name">Company Name:</Label>
              <Input id="comp-name" type="text" value={companyName} onChange={(e) => setCompanyName(e.target.value)} />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="job-role">Job Role:</Label>
              <Input id="job-role" type="text" value={jobRole} onChange={(e) => setJobRole(e.target.value)} />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="desc">Description:</Label>
              <Textarea id="desc" value={description} onChange={(e) => setDescription(e.target.value)} />
            </div>
            <Input type="file" />
            <Button onClick={handleAddJobClick} type="button">Add</Button>
          </div>
        </CardContent>
      </Card>

      {jobs.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Entered Jobs</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-wrap gap-2">
            {jobs.map((job) => (
              <Dialog key={job.id} onOpenChange={(isOpen) => !isOpen && setEditingJob(null)}>
                <DialogTrigger asChild>
                  <Badge
                    variant="secondary"
                    className="cursor-pointer hover:bg-primary hover:text-primary-foreground"
                    onClick={() => setEditingJob({ ...job })}
                  >
                    {job.jobRole} - {job.companyName}
                  </Badge>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Edit Job Description</DialogTitle>
                  </DialogHeader>
                  {editingJob && (
                    <div className="grid gap-4 py-4">
                      <div className="grid grid-cols-4 items-center gap-4">
                        <Label htmlFor="edit-comp-name" className="text-right">Company</Label>
                        <Input id="edit-comp-name" value={editingJob.companyName} onChange={(e) => setEditingJob({ ...editingJob, companyName: e.target.value })} className="col-span-3" />
                      </div>
                      <div className="grid grid-cols-4 items-center gap-4">
                        <Label htmlFor="edit-job-role" className="text-right">Job Role</Label>
                        <Input id="edit-job-role" value={editingJob.jobRole} onChange={(e) => setEditingJob({ ...editingJob, jobRole: e.target.value })} className="col-span-3" />
                      </div>
                      <div className="grid grid-cols-4 items-center gap-4">
                        <Label htmlFor="edit-desc" className="text-right">Description</Label>
                        <Textarea id="edit-desc" value={editingJob.description} onChange={(e) => setEditingJob({ ...editingJob, description: e.target.value })} className="col-span-3" />
                      </div>
                    </div>
                  )}
                  <DialogFooter>
                    <DialogClose asChild>
                      <Button type="button" variant="secondary">Cancel</Button>
                    </DialogClose>
                    <DialogTrigger asChild>
                    <Button type="button" onClick={handleUpdateJobClick}>Save Changes</Button>
                    </DialogTrigger>
                  </DialogFooter>
                </DialogContent>
              </Dialog>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  );
}