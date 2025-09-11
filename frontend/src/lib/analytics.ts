'use client';

import { track } from '@vercel/analytics';

// Simple analytics wrapper using Vercel Analytics
export const analytics = {
  // Track custom events using Vercel Analytics
  trackEvent: (event: string, category: string, label?: string, value?: number) => {
    // Vercel Analytics automatically tracks page views and user interactions
    // Custom events can be tracked with the track function
    track(event, { category, label, value: value?.toString() });
  },

  // Track errors
  trackError: (error: string, details?: string) => {
    track('error', { error, details });
    console.error('Analytics Error:', error, details);
  },

  // Track performance metrics
  trackPerformance: (metric: string, value: number, unit: string = 'ms') => {
    track('performance', { metric, value: value.toString(), unit });
  },

  // Track user interactions
  trackInteraction: (action: string, element: string) => {
    track('interaction', { action, element });
  },

  // Track API calls
  trackAPICall: (endpoint: string, duration: number, status: number) => {
    track('api_call', { 
      endpoint, 
      duration: duration.toString(), 
      status: status.toString() 
    });
  },

  // Track slow loading
  slowLoading: (duration: number, type: string) => {
    track('slow_loading', { duration: duration.toString(), type });
  },

  // Track paper upload
  paperUpload: (size: number, type: string) => {
    track('paper_upload', { size: size.toString(), type });
  },

  // Track summary generation
  summaryGenerated: (processingTime: number, noveltyScore?: number) => {
    track('summary_generated', { 
      processingTime: processingTime.toString(),
      noveltyScore: noveltyScore?.toString() || 'unknown'
    });
  },

  // Track summary failures
  summaryFailed: (errorType: string) => {
    track('summary_failed', { errorType });
  }
};

// Export a simple useAnalytics hook
export const useAnalytics = () => {
  return analytics;
};
