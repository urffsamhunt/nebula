import { IconTrendingDown, IconTrendingUp } from "@tabler/icons-react"
import { Label } from "./ui/label"
import { Badge } from "@/components/ui/badge"
import {
  Card,
  CardAction,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Input } from "./ui/input"
import { Button } from "./ui/button"
import { Slider } from "@/components/ui/slider"

export function ResumeCards() {
  return (
    <div className="*:data-[slot=card]:from-primary/2 *:data-[slot=card]:to-card dark:*:data-[slot=card]:bg-card grid grid-cols-1 gap-4 px-4 *:data-[slot=card]:bg-gradient-to-t *:data-[slot=card]:shadow-xs lg:px-6 @xl/main:grid-cols-2 @5xl/main:grid-cols-2">
      <Card className="@container/card">
        <CardHeader>
          <CardTitle className="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl">
            Resume Evaluation Form
          </CardTitle>
          <CardDescription></CardDescription>
          {/* <CardAction>
            <Badge variant="outline">
              <IconTrendingUp />
              +12.5%
            </Badge>
          </CardAction> */}
        </CardHeader>
        <CardContent>
            <form>
            <div className="flex flex-col gap-6">
                <div className="grid w-full max-w-sm items-center gap-3">
                    <Label htmlFor="file">Upload resume</Label>
                    <Input id="file" type="file" accept=".pdf,.odt,.doc,.docx,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document" required />
                </div>
                <div className="grid gap-3">
                    <Label htmlFor="password">Choose a job drescription :</Label>
                    <Select>
                        <SelectTrigger className="w-[180px]">
                            <SelectValue placeholder="Job description" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="light">+</SelectItem>
                            {/* <SelectItem value="dark">Dark</SelectItem>
                            <SelectItem value="system">System</SelectItem> */}
                        </SelectContent>
                    </Select>
                </div>
                <Button>Evaluate</Button>
            </div>
            </form>
        </CardContent>
        {/* <CardFooter className="flex-col items-start gap-1.5 text-sm">
          <div className="line-clamp-1 flex gap-2 font-medium">
            Trending up this month <IconTrendingUp className="size-4" />
          </div>
          <div className="text-muted-foreground">
            Visitors for the last 6 months
          </div>
        </CardFooter> */}
      </Card>


      <Card className="@container/card">
        <CardHeader>
          <CardTitle className="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl">
            Report
          </CardTitle>
          <CardDescription></CardDescription>
          {/* <CardAction>
            <Badge variant="outline">
              <IconTrendingUp />
              +12.5%
            </Badge>
          </CardAction> */}
        </CardHeader>
        <CardContent>
            <div className="flex flex-col gap-6">
                <div className="grid gap-3">
                    <Label htmlFor="file">Relevance Score :</Label>
                    <Slider defaultValue={[33]} max={100} step={1} />                
                </div>
                <div className="grid gap-3">
                    <Label htmlFor="file">Missing Details :</Label>
                    <span id="missing"></span>
                </div>
                <div className="grid gap-3">
                    <Label htmlFor="file">Verdict :</Label>
                    <span id="verdict"></span>
                </div>
                <div className="grid gap-3">
                    <Label htmlFor="file">Suggestions for improvement :</Label>
                    <span id="suggestions"></span>
                </div>
                <Button>Generate</Button>
            </div>    
        </CardContent>
        {/* <CardFooter className="flex-col items-start gap-1.5 text-sm">
          <div className="line-clamp-1 flex gap-2 font-medium">
            Trending up this month <IconTrendingUp className="size-4" />
          </div>
          <div className="text-muted-foreground">
            Visitors for the last 6 months
          </div>
        </CardFooter> */}
      </Card>
    </div>
  )
}
