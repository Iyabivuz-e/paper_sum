"use client"

import React, { useState, useEffect, useCallback } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { BarChart3, TrendingUp, Users, MessageCircle, RefreshCw } from "lucide-react"

interface FeedbackAnalytics {
  total_feedback: number
  positive_feedback: number
  negative_feedback: number
  satisfaction_rate: number
  recent_comments: Array<{
    rating: string
    comment: string
    paper_title: string
    created_at: string
  }>
  period_days: number
}

interface UsageAnalytics {
  total_analyses: number
  successful_analyses: number
  failed_analyses: number
  success_rate: number
  avg_processing_time_ms: number
  avg_novelty_score: number
  period_days: number
}

export function AdminDashboard() {
  const [feedbackData, setFeedbackData] = useState<FeedbackAnalytics | null>(null)
  const [usageData, setUsageData] = useState<UsageAnalytics | null>(null)
  const [loading, setLoading] = useState(false)
  const [days, setDays] = useState(30)

  const fetchAnalytics = useCallback(async () => {
    setLoading(true)
    try {
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8001'
      
      const [feedbackResponse, usageResponse] = await Promise.all([
        fetch(`${backendUrl}/api/analytics/feedback?days=${days}`),
        fetch(`${backendUrl}/api/analytics/usage?days=${days}`)
      ])

      if (feedbackResponse.ok) {
        const feedback = await feedbackResponse.json()
        setFeedbackData(feedback)
      }

      if (usageResponse.ok) {
        const usage = await usageResponse.json()
        setUsageData(usage)
      }
    } catch (error) {
      console.error('Failed to fetch analytics:', error)
    } finally {
      setLoading(false)
    }
  }, [days])

  useEffect(() => {
    fetchAnalytics()
  }, [days, fetchAnalytics])

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Analytics Dashboard</h1>
          <p className="text-muted-foreground">AI Paper Explainer Performance Metrics</p>
        </div>
        
        <div className="flex items-center gap-4">
          <select
            value={days}
            onChange={(e) => setDays(Number(e.target.value))}
            className="px-3 py-2 border border-input rounded-md bg-background"
          >
            <option value={7}>Last 7 days</option>
            <option value={30}>Last 30 days</option>
            <option value={90}>Last 90 days</option>
          </select>
          
          <Button onClick={fetchAnalytics} disabled={loading} variant="outline" size="sm">
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Usage Analytics */}
      {usageData && (
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Total Analyses</CardTitle>
              <BarChart3 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{usageData.total_analyses}</div>
              <p className="text-xs text-muted-foreground">
                {usageData.successful_analyses} successful, {usageData.failed_analyses} failed
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{usageData.success_rate}%</div>
              <p className="text-xs text-muted-foreground">
                Processing reliability
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Avg Processing Time</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {Math.round(usageData.avg_processing_time_ms / 1000)}s
              </div>
              <p className="text-xs text-muted-foreground">
                Time to complete analysis
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Avg Novelty Score</CardTitle>
              <BarChart3 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{usageData.avg_novelty_score}</div>
              <p className="text-xs text-muted-foreground">
                Research innovation level
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Feedback Analytics */}
      {feedbackData && (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Total Feedback</CardTitle>
              <MessageCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{feedbackData.total_feedback}</div>
              <p className="text-xs text-muted-foreground">
                User responses received
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Satisfaction Rate</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                {feedbackData.satisfaction_rate}%
              </div>
              <p className="text-xs text-muted-foreground">
                {feedbackData.positive_feedback} positive, {feedbackData.negative_feedback} negative
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Feedback Rate</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {usageData ? Math.round((feedbackData.total_feedback / usageData.total_analyses) * 100) : 0}%
              </div>
              <p className="text-xs text-muted-foreground">
                Users providing feedback
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Recent Comments */}
      {feedbackData && feedbackData.recent_comments.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Recent Feedback Comments</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {feedbackData.recent_comments.map((comment, index) => (
              <div key={index} className="border-l-4 border-muted pl-4 space-y-1">
                <div className="flex items-center gap-2">
                  <span className={`text-sm font-medium ${
                    comment.rating === 'positive' ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {comment.rating === 'positive' ? '👍' : '👎'} {comment.rating}
                  </span>
                  <span className="text-xs text-muted-foreground">
                    {new Date(comment.created_at).toLocaleDateString()}
                  </span>
                </div>
                <p className="text-sm">{comment.comment}</p>
                <p className="text-xs text-muted-foreground">
                  Paper: {comment.paper_title || 'Unknown'}
                </p>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {(!feedbackData || !usageData) && !loading && (
        <Card>
          <CardContent className="text-center py-8">
            <p className="text-muted-foreground">
              No analytics data available. Make sure the database is connected and you have processed some papers.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
