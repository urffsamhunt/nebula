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

export function JobCards() {
  return (
    <div className="*:data-[slot=card]:from-primary/2 *:data-[slot=card]:to-card dark:*:data-[slot=card]:bg-card grid grid-cols-1 gap-4 px-4 *:data-[slot=card]:bg-gradient-to-t *:data-[slot=card]:shadow-xs lg:px-6 @xl/main:grid-cols-2 @5xl/main:grid-cols-1">

    <Card className="@container/card">
        <CardHeader>
          <CardTitle className="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl">Job Description</CardTitle>
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
                    <div className="grid gap-2">
                        <Label htmlFor="comp-name">Company Name :</Label>
                        <Input id="comp-name" type="text"></Input>
                    </div>
                    <div className="grid gap-2">
                        <Label htmlFor="job-role">Job Role :</Label>
                        <Input id="job-role" type="text"></Input>
                    </div>
                    <div className="grid gap-2">
                        <Label htmlFor="desc">Description :</Label>
                        <Input id="desc" type="textarea"></Input>
                    </div>
                    <Button>Add</Button>
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


    </div>
  )
}
