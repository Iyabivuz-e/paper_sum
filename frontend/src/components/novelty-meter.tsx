import { cn } from "@/lib/utils"

interface NoveltyMeterProps {
  score: number
  className?: string
}

export function NoveltyMeter({ score, className }: NoveltyMeterProps) {
  const getScoreLabel = (score: number) => {
    if (score < 0.3) return { text: "Another fine-tune 😅", color: "text-orange-600" }
    if (score < 0.7) return { text: "Pretty cool 🚴→🏍️", color: "text-blue-600" }
    return { text: "Breakthrough 🚀🔥", color: "text-green-600" }
  }

  const getScoreColor = (score: number) => {
    if (score < 0.3) return "bg-orange-500"
    if (score < 0.7) return "bg-blue-500"
    return "bg-green-500"
  }

  const label = getScoreLabel(score)
  const percentage = Math.round(score * 100)

  return (
    <div className={cn("space-y-3", className)}>
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium">Novelty Score</span>
        <span className={cn("text-sm font-semibold", label.color)}>
          {label.text}
        </span>
      </div>
      
      <div className="space-y-2">
        <div className="w-full bg-secondary rounded-full h-2 relative overflow-hidden">
          <div
            className={cn(
              "h-full rounded-full transition-all duration-700 ease-out",
              getScoreColor(score)
            )}
            style={{ width: `${percentage}%` }}
          />
        </div>
        
        <div className="flex justify-between text-xs text-muted-foreground">
          <span>0.0</span>
          <span className="font-medium">{score.toFixed(1)}</span>
          <span>1.0</span>
        </div>
      </div>
    </div>
  )
}
