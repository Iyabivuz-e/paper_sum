'use client'

import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { AdminDashboard } from '@/components/admin-dashboard'
import { AnalyticsDashboard } from '@/components/analytics-dashboard'
import { Lock, Shield, Activity, Users, FileText, TrendingUp, BarChart3 } from 'lucide-react'

export default function AdminPage() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [activeTab, setActiveTab] = useState('overview')

  // Simple password authentication (replace with proper auth in production)
  const handleAuth = () => {
    if (password === 'admin123') { // Change this to a secure password
      setIsAuthenticated(true)
      setError('')
    } else {
      setError('Invalid password')
    }
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <div className="mx-auto w-12 h-12 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center mb-4">
              <Shield className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
            <CardTitle className="text-2xl">Admin Access</CardTitle>
            <CardDescription>
              Enter password to access analytics dashboard
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <label htmlFor="password" className="text-sm font-medium">
                Password
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleAuth()}
                className="w-full px-3 py-2 border border-input rounded-md bg-background"
                placeholder="Enter admin password"
              />
            </div>
            {error && (
              <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
            )}
            <Button onClick={handleAuth} className="w-full">
              <Lock className="w-4 h-4 mr-2" />
              Access Dashboard
            </Button>
            <div className="text-xs text-muted-foreground text-center">
              Default password: admin123 (change in production)
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  const tabs = [
    { id: 'overview', label: 'Overview', icon: TrendingUp },
    { id: 'feedback', label: 'Feedback', icon: Users },
    { id: 'analytics', label: 'User Analytics', icon: BarChart3 },
    { id: 'performance', label: 'Performance', icon: Activity },
    { id: 'papers', label: 'Papers', icon: FileText },
  ]

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <Activity className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold">AI Paper Explainer</h1>
                <p className="text-sm text-muted-foreground">Analytics Dashboard</p>
              </div>
            </div>
            <div className="px-3 py-1 bg-green-50 dark:bg-green-900 text-green-700 dark:text-green-300 rounded-full text-sm border border-green-200 dark:border-green-800">
              <Shield className="w-3 h-3 mr-1 inline" />
              Admin Access
            </div>
          </div>
        </div>
      </div>

      {/* Dashboard Content */}
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h2 className="text-3xl font-bold tracking-tight">Dashboard Overview</h2>
          <p className="text-muted-foreground mt-2">
            Monitor user feedback, system performance, and usage analytics
          </p>
        </div>

        {/* Custom Tab Navigation */}
        <div className="mb-6">
          <div className="flex space-x-1 bg-muted p-1 rounded-lg w-fit">
            {tabs.map((tab) => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`
                    flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors
                    ${activeTab === tab.id 
                      ? 'bg-background text-foreground shadow-sm' 
                      : 'text-muted-foreground hover:text-foreground'
                    }
                  `}
                >
                  <Icon className="w-4 h-4" />
                  {tab.label}
                </button>
              )
            })}
          </div>
        </div>

        {/* Tab Content */}
        <div className="space-y-6">
          {activeTab === 'overview' && (
            <div>
              <AdminDashboard />
            </div>
          )}

          {activeTab === 'feedback' && (
            <Card>
              <CardHeader>
                <CardTitle>User Feedback Analysis</CardTitle>
                <CardDescription>
                  Detailed breakdown of user satisfaction and comments
                </CardDescription>
              </CardHeader>
              <CardContent>
                <AdminDashboard />
              </CardContent>
            </Card>
          )}

          {activeTab === 'analytics' && (
            <div>
              <AnalyticsDashboard />
            </div>
          )}

          {activeTab === 'performance' && (
            <Card>
              <CardHeader>
                <CardTitle>System Performance</CardTitle>
                <CardDescription>
                  Processing times, success rates, and technical metrics
                </CardDescription>
              </CardHeader>
              <CardContent>
                <AdminDashboard />
              </CardContent>
            </Card>
          )}

          {activeTab === 'papers' && (
            <Card>
              <CardHeader>
                <CardTitle>Paper Analytics</CardTitle>
                <CardDescription>
                  Most analyzed papers, popularity trends, and topic insights
                </CardDescription>
              </CardHeader>
              <CardContent>
                <AdminDashboard />
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}
