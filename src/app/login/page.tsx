import { GalleryVerticalEnd } from "lucide-react"
import LoginForms from "@/components/ui/login-form"
import { Suspense } from "react"

export default function LoginPage() {
  return (
    <div className="grid min-h-svh lg:grid-cols-2">
      <div className="flex flex-col gap-4 p-6 md:p-10">
        <div className="flex justify-center gap-2 md:justify-start">
          <a href="#" className="flex items-center gap-2 font-medium">
            <div className="bg-primary text-primary-foreground flex size-6 items-center justify-center rounded-md">
              <GalleryVerticalEnd className="size-4" />
            </div>
            Nebula
          </a>
        </div>
        <div className="flex flex-1 items-center justify-center">
          <div className="w-full max-w-xs">
            <Suspense fallback={<div>Loading...</div>}>
              <LoginForms />
            </Suspense>
          </div>
        </div>
      </div>
      
      <div className="bg-muted relative hidden lg:flex lg:items-center lg:justify-center">
        <div className="relative z-10 w-full max-w-md p-10">
          <h1 className="text-4xl font-bold">Nebula</h1>
          <p className="mt-3 text-lg text-muted-foreground">
            An intelligent application that leverages Generative AI to analyze and
            score resumes against job descriptions in real-time.
          </p>
          <ul className="mt-6 list-disc space-y-2 pl-5 text-muted-foreground">
            <li>
              <strong>Concurrent Batch Processing:</strong> Analyze multiple
              resumes at once.
            </li>
            <li>
              <strong>Real-Time Progress:</strong> See live status updates from
              extraction to scoring.
            </li>
            <li>
              <strong>Multi-Layered AI Analysis:</strong> Combines keyword matching,
              semantic similarity, and an LLM-powered final verdict.
            </li>
            <li>
              <strong>Persistent Job Descriptions:</strong> Save, manage, and
              reuse job descriptions.
            </li>
          </ul>
        </div>
        {/* This div creates a subtle dark overlay, similar to the original image's dark:brightness-[0.2] */}
        <div className="absolute inset-0 bg-black/20 dark:bg-black/50" />
      </div>
      {/* --- END OF REPLACEMENT --- */}
      
    </div>
  )
}