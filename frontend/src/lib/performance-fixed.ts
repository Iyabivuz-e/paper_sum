'use client';

import { useEffect, useCallback } from 'react';
import { analytics } from './analytics';

interface ExtendedPerformanceEntry extends PerformanceEntry {
  hadRecentInput?: boolean;
  value?: number;
  processingStart?: number;
  duration: number;
  initiatorType?: string;
}

class PerformanceMonitor {
  private observers: PerformanceObserver[] = [];
  private navigationStart = 0;

  constructor() {
    if (typeof window !== 'undefined') {
      this.navigationStart = performance.timeOrigin || performance.timing?.navigationStart || Date.now();
      this.init();
    }
  }

  private init() {
    this.observeWebVitals();
    this.observeResources();
    this.observeNavigation();
  }

  private observeWebVitals() {
    // First Contentful Paint (FCP)
    if ('PerformanceObserver' in window) {
      const fcpObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const lastEntry = entries[entries.length - 1] as ExtendedPerformanceEntry;
        const fcp = lastEntry.startTime;
        
        analytics.trackEvent('core_web_vital', 'performance', 'FCP', Math.round(fcp));
        
        if (fcp > 1800) {
          analytics.slowLoading(fcp, 'FCP');
        }
      });
      
      fcpObserver.observe({ entryTypes: ['paint'] });
      this.observers.push(fcpObserver);
    }

    // Largest Contentful Paint (LCP)
    if ('PerformanceObserver' in window) {
      const lcpObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const lastEntry = entries[entries.length - 1] as ExtendedPerformanceEntry;
        const lcp = lastEntry.startTime;
        
        analytics.trackEvent('core_web_vital', 'performance', 'LCP', Math.round(lcp));
        
        if (lcp > 2500) {
          analytics.slowLoading(lcp, 'LCP');
        }
      });
      
      lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });
      this.observers.push(lcpObserver);
    }

    // First Input Delay (FID)
    if ('PerformanceObserver' in window) {
      const fidObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach((entry) => {
          const fidEntry = entry as ExtendedPerformanceEntry;
          if (fidEntry.processingStart) {
            const fid = fidEntry.processingStart - fidEntry.startTime;
            analytics.trackEvent('core_web_vital', 'performance', 'FID', Math.round(fid));
            
            if (fid > 100) {
              analytics.slowLoading(fid, 'FID');
            }
          }
        });
      });
      
      fidObserver.observe({ entryTypes: ['first-input'] });
      this.observers.push(fidObserver);
    }

    // Cumulative Layout Shift (CLS)
    if ('PerformanceObserver' in window) {
      let clsValue = 0;
      const clsObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach((entry) => {
          const clsEntry = entry as ExtendedPerformanceEntry;
          if (!clsEntry.hadRecentInput && clsEntry.value) {
            clsValue += clsEntry.value;
          }
        });
        
        analytics.trackEvent('core_web_vital', 'performance', 'CLS', Math.round(clsValue * 1000));
        
        if (clsValue > 0.1) {
          analytics.slowLoading(clsValue * 1000, 'CLS');
        }
      });
      
      clsObserver.observe({ entryTypes: ['layout-shift'] });
      this.observers.push(clsObserver);
    }
  }

  private observeResources() {
    if ('PerformanceObserver' in window) {
      const resourceObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach((entry) => {
          const resourceEntry = entry as ExtendedPerformanceEntry;
          // Track slow resources
          if (resourceEntry.duration > 1000) {
            analytics.trackEvent('slow_resource', 'performance', resourceEntry.name, Math.round(resourceEntry.duration));
          }
          
          // Track resource types
          if (resourceEntry.initiatorType) {
            analytics.trackEvent('resource_type', 'performance', resourceEntry.initiatorType);
          }
        });
      });
      
      resourceObserver.observe({ entryTypes: ['resource'] });
      this.observers.push(resourceObserver);
    }
  }

  private observeNavigation() {
    if ('PerformanceObserver' in window) {
      const navObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach((entry) => {
          const navEntry = entry as ExtendedPerformanceEntry;
          analytics.trackEvent('navigation_timing', 'performance', 'total_load_time', Math.round(navEntry.duration));
        });
      });
      
      navObserver.observe({ entryTypes: ['navigation'] });
      this.observers.push(navObserver);
    }
  }

  // Track API call performance
  trackAPICall = (url: string, startTime: number, endTime: number, status: number) => {
    const duration = endTime - startTime;
    analytics.trackEvent('api_call', 'performance', url, duration);
    
    if (duration > 5000) {
      analytics.slowLoading(duration, 'API');
    }
    
    if (status >= 400) {
      analytics.trackEvent('api_error', 'error', url, status);
    }
  };

  // Track user interactions
  trackInteraction = (action: string, element: string) => {
    const timestamp = performance.now();
    analytics.trackEvent('user_interaction', 'engagement', `${action}_${element}`, timestamp);
  };

  // Track component render times
  trackRender = (componentName: string, renderTime: number) => {
    analytics.trackEvent('component_render', 'performance', componentName, renderTime);
    
    if (renderTime > 16) { // 60fps threshold
      analytics.slowLoading(renderTime, 'Render');
    }
  };

  // Memory usage tracking
  trackMemoryUsage = () => {
    if ('memory' in performance) {
      const memory = (performance as unknown as { memory: { usedJSHeapSize: number; totalJSHeapSize: number; jsHeapSizeLimit: number } }).memory;
      const usedMB = Math.round(memory.usedJSHeapSize / 1024 / 1024);
      const totalMB = Math.round(memory.totalJSHeapSize / 1024 / 1024);
      
      analytics.trackEvent('memory_usage', 'performance', 'used_mb', usedMB);
      analytics.trackEvent('memory_usage', 'performance', 'total_mb', totalMB);
      
      // Alert if memory usage is high
      if (usedMB > 100) {
        analytics.trackEvent('high_memory_usage', 'performance', 'warning', usedMB);
      }
    }
  };

  // Page visibility tracking
  trackPageVisibility = () => {
    document.addEventListener('visibilitychange', () => {
      const isVisible = !document.hidden;
      analytics.trackEvent('page_visibility', 'engagement', isVisible ? 'visible' : 'hidden');
    });
  };

  // Error boundary integration
  static logError(error: Error, errorInfo?: Record<string, unknown>) {
    analytics.trackEvent('error', 'error', error.message);
    console.error('Performance Monitor Error:', error, errorInfo);
  }

  // Cleanup
  destroy() {
    this.observers.forEach(observer => observer.disconnect());
    this.observers = [];
  }
}

// Singleton instance
let performanceMonitorInstance: PerformanceMonitor | null = null;

// React hook for performance monitoring
export const usePerformanceMonitor = () => {
  useEffect(() => {
    if (typeof window !== 'undefined' && !performanceMonitorInstance) {
      performanceMonitorInstance = new PerformanceMonitor();
      performanceMonitorInstance.trackPageVisibility();
      
      // Track memory usage periodically
      const memoryInterval = setInterval(() => {
        performanceMonitorInstance?.trackMemoryUsage();
      }, 30000); // Every 30 seconds
      
      return () => {
        clearInterval(memoryInterval);
        performanceMonitorInstance?.destroy();
        performanceMonitorInstance = null;
      };
    }
  }, []);

  const trackAPICall = useCallback((url: string, startTime: number, endTime: number, status: number) => {
    performanceMonitorInstance?.trackAPICall(url, startTime, endTime, status);
  }, []);

  const trackInteraction = useCallback((action: string, element: string) => {
    performanceMonitorInstance?.trackInteraction(action, element);
  }, []);

  const trackRender = useCallback((componentName: string, renderTime: number) => {
    performanceMonitorInstance?.trackRender(componentName, renderTime);
  }, []);

  return {
    trackAPICall,
    trackInteraction,
    trackRender,
  };
};

export { PerformanceMonitor };
