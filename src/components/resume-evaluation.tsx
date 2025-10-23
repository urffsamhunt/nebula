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
// Local Job type (define here to avoid incorrect absolute import path)
// Adjust fields to match your backend Job shape if needed.
type Job = {
  id: string | number;
  jobRole: string;
  companyName: string;
};
import { fetchEventSource } from "@microsoft/fetch-event-source";
import { Skeleton } from "./ui/skeleton";

type ResumeCardsProps = {
  jobs: Job[];
  onNavigate: (sectionName: string) => void;
};

export function ResumeCards({ jobs, onNavigate }: ResumeCardsProps) {
  const [selectedJobId, setSelectedJobId] = useState<string>("");
  // overall fallback states (kept for compatibility)
  const [relevanceScore, setRelevanceScore] = useState<number>(0);
  const [missingDetails, setMissingDetails] = useState<string>("");
  const [verdict, setVerdict] = useState<string>("");
  const [suggestions, setSuggestions] = useState<string>("");

  // New state: store uploaded files and per-file results
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [selectedResumeIndex, setSelectedResumeIndex] = useState<number>(-1);
  const [perResults, setPerResults] = useState<
    Array<{
      name: string;
      status: string; // pending | processing | success | error
      result?: any;
      error?: string;
    }>
  >([]);

  // Saved evaluations pulled from the backend
  const [savedEvals, setSavedEvals] = useState<any[]>([]);
  // spinner / disabled state for the Evaluate button
  const [isEvaluating, setIsEvaluating] = useState<boolean>(false);

  async function handleEvaluate() {
    const fileInput = document.getElementById("file") as HTMLInputElement;
    if (!fileInput || !fileInput.files || fileInput.files.length === 0) {
      alert("Please upload at least one resume file.");
      return;
    }

    if (!selectedJobId) {
      alert("Please select a job description.");
      return;
    }

    try {
      // mark as evaluating which disables the button and shows a spinner
      setIsEvaluating(true);
      // 1. Fetch the job description text from backend
      const jdRes = await fetch(`http://localhost:8000/api/v1/get-job-description/${selectedJobId}`);
      if (!jdRes.ok) throw new Error("Failed to fetch job description.");
      const jdPayload = await jdRes.json();
      const jobDescriptionText = jdPayload?.job_description?.description ?? "";

      // 2. Build form data matching backend expectations
      const filesArray = Array.from(fileInput.files);
      setUploadedFiles(filesArray);
      setSelectedResumeIndex(filesArray.length > 0 ? 0 : -1);

      const initialResults = filesArray.map((f) => ({ name: f.name, status: "pending" }));
      setPerResults(initialResults);

      // immediately mark as processing so UI shows skeletons/spinner
      setPerResults((prev) => prev.map((p) => ({ ...p, status: "processing" })));

      const formData = new FormData();
      filesArray.forEach((file) => {
        // backend expects field name 'resumes' for the list of UploadFile
        formData.append("resumes", file);
      });
      console.log(formData);
      formData.append("job_description", jobDescriptionText);

      // 3. Simple POST (non-streaming). The backend returns a JSON batch_results array.
      const resp = await fetch("http://localhost:8000/api/v1/analyze-batch", {
        method: "POST",
        body: formData as any,
      });

      if (!resp.ok) {
        const text = await resp.text();
        throw new Error(`Analysis request failed: ${resp.status} ${text}`);
      }

      const payload = await resp.json();
      // Expect payload.batch_results to be an array of per-file results
      if (Array.isArray(payload.batch_results)) {
        const updated = [...initialResults];
        payload.batch_results.forEach((item: any) => {
          const idx = updated.findIndex((r) => r.name === item.filename || r.name === item.name);
          const entry = {
            name: item.filename ?? item.name ?? `file-${Math.random().toString(36).slice(2, 7)}`,
            status: item.status ?? (item.result ? "success" : "error"),
            result: item.result,
            error: item.error ?? item.detail,
          };
          if (idx >= 0) updated[idx] = { ...updated[idx], ...entry };
          else updated.push(entry);
        });
        setPerResults(updated);
      } else {
        // unexpected shape — place entire payload into first entry
        setPerResults((prev) => {
          const copy = [...prev];
          copy[0] = { ...copy[0], status: payload.status ?? "error", result: payload };
          return copy;
        });
      }
    } catch (error) {
      console.error("Error evaluating resume:", error);
      alert("An error occurred while evaluating the resume. See console for details.");
    } finally {
      // clear evaluating state regardless of outcome
      setIsEvaluating(false);
    }
  }

  // Fetch saved evaluations from the backend and store them in state
  async function refreshEvaluations() {
    try {
      const res = await fetch("http://localhost:8000/api/v1/evaluations");
      if (!res.ok) throw new Error(`Failed to fetch evaluations: ${res.status}`);
      const payload = await res.json();
      // payload.data is expected to be an array of saved evaluations
      setSavedEvals(Array.isArray(payload.data) ? payload.data : []);
    } catch (err) {
      console.error("Failed to refresh evaluations:", err);
      alert("Failed to refresh evaluations. See console for details.");
    }
  }

  // helper to derive the selected resume's result
  const selectedResult = selectedResumeIndex >= 0 && perResults[selectedResumeIndex]
    ? perResults[selectedResumeIndex]
    : null;

  return (
    <div className="grid grid-cols-1 gap-4 px-4 lg:px-6 @xl/main:grid-cols-2">
      <Card className="@container/card">
        <CardHeader>
          <CardTitle className="text-2xl font-semibold">Resume Evaluation</CardTitle>
        </CardHeader>
        <CardContent>
          <form>
            <div className="flex flex-col gap-6">
              <div className="grid w-full max-w-sm items-center gap-3">
                <Label htmlFor="file">Upload resume(s)</Label>
                <Input
                  id="file"
                  type="file"
                  required
                  multiple
                  onChange={(e) => {
                    const files = e.target.files ? Array.from(e.target.files) : [];
                    setUploadedFiles(files);
                    setPerResults(files.map((f) => ({ name: f.name, status: "pending" })));
                    setSelectedResumeIndex(files.length > 0 ? 0 : -1);
                  }}
                />
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

              <div className="flex gap-2">
                <Button type="button" onClick={handleEvaluate} disabled={isEvaluating}>
                  {isEvaluating ? (
                    <>
                      <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"></path>
                      </svg>
                      Evaluating...
                    </>
                  ) : (
                    'Evaluate'
                  )}
                </Button>
                <Button type="button" variant="ghost" onClick={refreshEvaluations}>Refresh Evaluations</Button>
                <div className="text-sm text-muted-foreground self-center">Saved: {savedEvals.length}</div>
              </div>

              {/* Scrollable list of uploaded resumes */}
              <div className="mt-4">
                <Label>Uploaded Resumes</Label>
                <div className="mt-2 max-h-48 overflow-y-auto border rounded p-2">
                  {uploadedFiles.length === 0 ? (
                    <div className="text-sm text-muted-foreground">No files selected</div>
                  ) : (
                    uploadedFiles.map((file, idx) => {
                      const r = perResults[idx];
                      return (
                        <div
                          key={file.name + idx}
                          className={`flex items-center justify-between p-2 rounded cursor-pointer hover:bg-slate-50 ${selectedResumeIndex === idx ? 'bg-slate-100' : ''}`}
                          onClick={() => setSelectedResumeIndex(idx)}
                        >
                          <div className="flex flex-col">
                            <span className="font-medium">{file.name}</span>
                            <span className="text-xs text-muted-foreground">{r?.status ?? 'pending'}</span>
                          </div>
                          <div className="text-xs text-muted-foreground flex items-center gap-2">
                            {r?.status === 'pending' || r?.status === 'processing' ? (
                              // show a compact skeleton for ongoing evaluations
                              <Skeleton className="w-16 h-4" />
                            ) : (
                              <>{r?.result ? `${Math.round((r.result.relevance_score ?? 0) * 100)/100}` : ''}</>
                            )}
                          </div>
                        </div>
                      );
                    })
                  )}
                </div>
              </div>

              {/* Optional: show a small list of saved evaluations fetched from DB */}
              <div className="mt-4">
                <Label>Saved Evaluations (latest)</Label>
                <div className="mt-2 max-h-36 overflow-y-auto border rounded p-2 text-sm">
                  {savedEvals.length === 0 ? (
                    <div className="text-muted-foreground">No saved evaluations</div>
                  ) : (
                    savedEvals.map((s, i) => (
                      <div key={s.id ?? i} className="py-1 border-b last:border-b-0">
                        <div className="font-medium">{s.filename ?? '–'}</div>
                        <div className="text-xs text-muted-foreground">{s.verdict ?? s.result?.verdict ?? ''} — {s.relevance_score ?? s.result?.relevance_score ?? ''}</div>
                      </div>
                    ))
                  )}
                </div>
              </div>

            </div>
          </form>
        </CardContent>
      </Card>

      <Card className="@container/card">
        <CardHeader>
          <CardTitle className="text-2xl font-semibold">Evaluation Report</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col gap-6">
            {selectedResult ? (
              <>
                <div className="grid gap-3">
                  <Label>File</Label>
                  <span>{selectedResult.name}</span>
                </div>

                {selectedResult.status === 'pending' || selectedResult.status === 'processing' ? (
                  // show skeleton placeholders while processing
                  <>
                    <div className="grid gap-3">
                      <Label>Relevance Score:</Label>
                      <div className="w-full"><Skeleton className="w-full h-6" /></div>
                    </div>
                    <div className="grid gap-3">
                      <Label>Missing Details:</Label>
                      <div className="space-y-2">
                        <Skeleton className="w-full h-4" />
                        <Skeleton className="w-3/4 h-4" />
                      </div>
                    </div>
                    <div className="grid gap-3">
                      <Label>Verdict:</Label>
                      <div><Skeleton className="w-24 h-4" /></div>
                    </div>
                    <div className="grid gap-3">
                      <Label>Suggestions for improvement:</Label>
                      <div className="space-y-2">
                        <Skeleton className="w-full h-4" />
                        <Skeleton className="w-5/6 h-4" />
                        <Skeleton className="w-2/3 h-4" />
                      </div>
                    </div>
                  </>
                ) : (
                  <>
                    <div className="grid gap-3">
                      <Label>Relevance Score:</Label>
                      <Slider value={[selectedResult.result?.relevance_score ?? 0]} max={100} step={1} />
                    </div>
                    <div className="grid gap-3">
                      <Label>Missing Details:</Label>
                      <span id="missing">{(selectedResult.result?.missing_keywords ?? []).join(", ")}</span>
                    </div>
                    <div className="grid gap-3">
                      <Label>Verdict:</Label>
                      <span id="verdict">{selectedResult.result?.verdict ?? selectedResult.status}</span>
                    </div>
                    <div className="grid gap-3">
                      <Label>Suggestions for improvement:</Label>
                      <span id="suggestions">{selectedResult.result?.suggestions ?? ''}</span>
                    </div>
                  </>
                )}
              </>
            ) : (
              <div className="text-sm text-muted-foreground">Select a resume from the left to view its evaluation.</div>
            )}

            <Button>Generate</Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}