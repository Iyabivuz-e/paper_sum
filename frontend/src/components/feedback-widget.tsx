"use client"

import React, { useState } from "react"
import { ThumbsUp, ThumbsDown, MessageSquare, Send, Coffee, Heart } from "lucide-react"
import { Button } from "../components/ui/button"

interface FeedbackWidgetProps {
  paperTitle?: string
  arxivId?: string
  onFeedbackSubmit?: (feedback: {
    rating: 'positive' | 'negative'
    comment?: string
    paperInfo: {
      title?: string
      arxivId?: string
    }
  }) => void
}

export function FeedbackWidget({ paperTitle, arxivId, onFeedbackSubmit }: FeedbackWidgetProps) {
  const [rating, setRating] = useState<'positive' | 'negative' | null>(null)
  const [showComment, setShowComment] = useState(false)
  const [comment, setComment] = useState("")
  const [isSubmitted, setIsSubmitted] = useState(false)

  const handleRating = (newRating: 'positive' | 'negative') => {
    setRating(newRating)
    if (newRating === 'positive') {
      // For positive feedback, submit immediately
      handleSubmit(newRating, "")
    } else {
      // For negative feedback, ask for comment
      setShowComment(true)
    }
  }

  const handleSubmit = (finalRating: 'positive' | 'negative', finalComment: string) => {
    const feedback = {
      rating: finalRating,
      comment: finalComment,
      paperInfo: {
        title: paperTitle,
        arxivId: arxivId
      }
    }
    
    onFeedbackSubmit?.(feedback)
    setIsSubmitted(true)
    
    // Hide after 3 seconds
    setTimeout(() => setIsSubmitted(false), 3000)
  }

  const handleCommentSubmit = () => {
    if (rating) {
      handleSubmit(rating, comment)
    }
  }

  if (isSubmitted) {
    return (
      <div className="bg-card border rounded-lg p-6 text-center space-y-4">
        <div className="text-green-600 dark:text-green-400 text-2xl">✨</div>
        <div className="space-y-2">
          <h3 className="text-lg font-semibold text-foreground">
            Thank you for your feedback!
          </h3>
          <p className="text-sm text-muted-foreground">
            Your input helps us improve our AI explanations
          </p>
        </div>
        
        {/* Coffee Button for Positive Feedback */}
        {rating === 'positive' && (
          <div className="pt-4 border-t space-y-3">
            <p className="text-sm text-muted-foreground">
              Enjoyed the explanation? Consider supporting the project! ☕
            </p>
            <a
              href="https://buymeacoffee.com/yourname"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-4 py-2 bg-yellow-500 hover:bg-yellow-600 text-yellow-900 font-medium rounded-full transition-colors"
            >
              <Coffee className="h-4 w-4" />
              Buy me a coffee
            </a>
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="bg-card border rounded-lg p-6 space-y-4">
      <div className="text-center space-y-2">
        <h3 className="text-lg font-semibold text-foreground flex items-center justify-center gap-2">
          <Heart className="h-5 w-5 text-red-500" />
          How was this explanation?
        </h3>
        <p className="text-sm text-muted-foreground">
          Your feedback helps us make better AI explanations
        </p>
      </div>

      {!rating && (
        <div className="flex justify-center gap-4">
          <Button
            onClick={() => handleRating('positive')}
            variant="outline"
            size="lg"
            className="flex items-center gap-2 hover:bg-green-100 dark:hover:bg-green-900/20 hover:border-green-300 dark:hover:border-green-700 transition-colors"
          >
            <ThumbsUp className="h-5 w-5" />
            Yes, helpful!
          </Button>
          <Button
            onClick={() => handleRating('negative')}
            variant="outline"
            size="lg"
            className="flex items-center gap-2 hover:bg-red-100 dark:hover:bg-red-900/20 hover:border-red-300 dark:hover:border-red-700 transition-colors"
          >
            <ThumbsDown className="h-5 w-5" />
            Could be better
          </Button>
        </div>
      )}

      {showComment && rating === 'negative' && (
        <div className="space-y-3 mt-4">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <MessageSquare className="h-4 w-4" />
            Help us improve - what could be better?
          </div>
          <div className="space-y-2">
            <textarea
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              placeholder="Optional: Tell us how we can improve..."
              className="w-full p-3 border border-input rounded-md bg-background text-sm resize-none h-20 focus:outline-none focus:ring-2 focus:ring-ring transition-colors"
            />
            <div className="flex gap-2 justify-end">
              <Button
                onClick={() => handleCommentSubmit()}
                size="sm"
                className="flex items-center gap-2"
              >
                <Send className="h-4 w-4" />
                Submit Feedback
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
