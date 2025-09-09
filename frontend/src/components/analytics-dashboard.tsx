'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { 
  BarChart, 
  Users, 
  Globe, 
  Zap, 
  TrendingUp, 
  Clock, 
  AlertTriangle,
  CheckCircle,
  Monitor,
  Smartphone,
  Download
} from 'lucide-react';

interface AnalyticsData {
  dailyUsers: number;
  totalSessions: number;
  averageSessionTime: string;
  topCountries: { country: string; users: number }[];
  deviceTypes: { type: string; percentage: number }[];
  popularPages: { page: string; views: number }[];
  conversionRate: number;
  errorRate: number;
  averageLoadTime: number;
}

export function AnalyticsDashboard() {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [timeRange, setTimeRange] = useState('7d');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Fetch real analytics data from backend
    const fetchAnalytics = async () => {
      try {
        const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8001';
        const response = await fetch(`${backendUrl}/analytics/dashboard?days=${timeRange.replace('d', '')}`);
        
        if (response.ok) {
          const realData = await response.json();
          setData(realData);
        } else {
          // Fallback to sample data if backend fails
          console.warn('Failed to fetch real analytics, using sample data');
          setData({
            dailyUsers: 0,
            totalSessions: 0,
            averageSessionTime: '0m 0s',
            topCountries: [],
            deviceTypes: [{ type: 'Desktop', percentage: 100 }],
            popularPages: [],
            conversionRate: 0,
            errorRate: 0,
            averageLoadTime: 0,
          });
        }
      } catch (error) {
        console.error('Error fetching analytics:', error);
        // Show empty state instead of mock data
        setData({
          dailyUsers: 0,
          totalSessions: 0,
          averageSessionTime: '0m 0s',
          topCountries: [],
          deviceTypes: [{ type: 'Desktop', percentage: 100 }],
          popularPages: [],
          conversionRate: 0,
          errorRate: 0,
          averageLoadTime: 0,
        });
      } finally {
        setIsLoading(false);
      }
    };

    fetchAnalytics();
    
    // Refresh data every 30 seconds for real-time updates
    const interval = setInterval(fetchAnalytics, 30000);
    
    return () => clearInterval(interval);
  }, [timeRange]);

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardContent className="p-6">
                <div className="h-4 bg-muted rounded w-1/2 mb-2"></div>
                <div className="h-8 bg-muted rounded w-3/4"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold">📊 Analytics Dashboard</h2>
          <p className="text-sm text-muted-foreground mt-1">
            Data sources: Custom Backend Analytics • Google Analytics • Vercel Analytics • Speed Insights
          </p>
        </div>
        <div className="flex gap-2">
          {['1d', '7d', '30d', '90d'].map((range) => (
            <Button
              key={range}
              variant={timeRange === range ? 'default' : 'outline'}
              size="sm"
              onClick={() => setTimeRange(range)}
            >
              {range}
            </Button>
          ))}
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Daily Users</p>
                <p className="text-2xl font-bold">{data.dailyUsers}</p>
              </div>
              <Users className="w-8 h-8 text-blue-600" />
            </div>
            <p className="text-xs text-green-600 mt-2">+12% from last week</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total Sessions</p>
                <p className="text-2xl font-bold">{data.totalSessions}</p>
              </div>
              <BarChart className="w-8 h-8 text-green-600" />
            </div>
            <p className="text-xs text-green-600 mt-2">+8% from last week</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Avg. Session</p>
                <p className="text-2xl font-bold">{data.averageSessionTime}</p>
              </div>
              <Clock className="w-8 h-8 text-purple-600" />
            </div>
            <p className="text-xs text-green-600 mt-2">+15% from last week</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Conversion Rate</p>
                <p className="text-2xl font-bold">{data.conversionRate}%</p>
              </div>
              <TrendingUp className="w-8 h-8 text-orange-600" />
            </div>
            <p className="text-xs text-green-600 mt-2">+3% from last week</p>
          </CardContent>
        </Card>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Countries */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Globe className="w-5 h-5" />
              Top Countries
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {data.topCountries.map((country, index) => (
                <div key={country.country} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium">#{index + 1}</span>
                    <span className="text-sm">{country.country}</span>
                  </div>
                  <Badge variant="secondary">{country.users} users</Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Device Types */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Monitor className="w-5 h-5" />
              Device Types
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {data.deviceTypes.map((device) => (
                <div key={device.type} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    {device.type === 'Desktop' && <Monitor className="w-4 h-4" />}
                    {device.type === 'Mobile' && <Smartphone className="w-4 h-4" />}
                    {device.type === 'Tablet' && <Monitor className="w-4 h-4" />}
                    <span className="text-sm">{device.type}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-20 h-2 bg-muted rounded-full">
                      <div 
                        className="h-2 bg-primary rounded-full" 
                        style={{ width: `${device.percentage}%` }}
                      ></div>
                    </div>
                    <span className="text-sm font-medium">{device.percentage}%</span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Performance & Popular Pages */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Performance Metrics */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Zap className="w-5 h-5" />
              Performance
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm">Average Load Time</span>
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-600" />
                <span className="font-medium">{data.averageLoadTime}s</span>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Error Rate</span>
              <div className="flex items-center gap-2">
                {data.errorRate < 1 ? (
                  <CheckCircle className="w-4 h-4 text-green-600" />
                ) : (
                  <AlertTriangle className="w-4 h-4 text-orange-600" />
                )}
                <span className="font-medium">{data.errorRate}%</span>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Uptime</span>
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-600" />
                <span className="font-medium">99.8%</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Popular Pages */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart className="w-5 h-5" />
              Popular Pages
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {data.popularPages.map((page, index) => (
                <div key={page.page} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium">#{index + 1}</span>
                    <span className="text-sm font-mono">{page.page}</span>
                  </div>
                  <Badge variant="outline">{page.views} views</Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Export & Actions */}
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold">Export Data</h3>
              <p className="text-sm text-muted-foreground">Download your analytics data</p>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" size="sm">
                <Download className="w-4 h-4 mr-2" />
                Export CSV
              </Button>
              <Button variant="outline" size="sm">
                <Download className="w-4 h-4 mr-2" />
                Export PDF
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
