'use client';

import { useState, useEffect, useMemo } from 'react';
import { InputForm } from '../components/input-form';
import { NoveltyMeter } from '../components/novelty-meter';
import ResultCards from '../components/ResultCards';
import { FeedbackWidget } from '../components/feedback-widget';
import { Navbar } from '../components/modern-navbar';
import { PrivacyAnalytics } from '../components/cookie-consent';
import { useAnalytics } from '../lib/analytics';
import { usePerformanceMonitor } from '../lib/performance-fixed';
import { Footer } from '../components/footer';

interface PaperMetadata {
  title: string;
  authors: string[];
  abstract: string;
  published_date: string;
  arxiv_id: string;
  categories: string[];
}

interface Results {
  seriousSummary: string;
  funAnalogy: string;
  friendsTake: string;
  noveltyScore: number;
  metadata?: PaperMetadata;
}

export default function Home() {
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<Results | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isRateLimit, setIsRateLimit] = useState(false);
  const [retryAfter, setRetryAfter] = useState<number | null>(null);
  const [timeLeft, setTimeLeft] = useState<number | null>(null);
  const [loadingStep, setLoadingStep] = useState('');
  const [funFact, setFunFact] = useState('');
  const [factVisible, setFactVisible] = useState(true);

  // Analytics and performance monitoring
  const analytics = useAnalytics();
  const { trackAPICall } = usePerformanceMonitor();

  // Fun facts about AI and research (memoized to prevent unnecessary re-renders)
  const funFacts = useMemo(() => [
    "🤖 Did you know? The average research paper takes 2-3 months to write, but AI can summarize it in minutes!",
    "📚 Fun fact: arXiv receives over 150,000 papers annually - that's about 400 papers every day!",
    "🧠 Amazing: The human brain processes visual information 60,000x faster than text - that's why we make analogies!",
    "⚡ Cool fact: Modern AI models can read a 50-page paper in seconds, but understanding takes sophisticated reasoning!",
    "🔬 Research shows: Papers with clear abstracts get 50% more citations than complex ones!",
    "🎯 Interesting: The most cited paper in history has over 300,000 citations - it's about protein measurement!",
    "💡 AI insight: Large language models read billions of papers during training - like having a research library in their brain!",
    "📊 Did you know? 90% of all data was created in the last 2 years - AI helps us make sense of this explosion!",
    "🌟 Fun fact: The term 'peer review' was first used in 1967, but the practice dates back to 1731!",
    "🚀 Amazing: AI can now identify research trends before humans notice them in the data!"
  ], []);

  // Loading steps that match backend processing
  const loadingSteps = [
    { step: 'ingestion', message: '📥 Fetching your paper...' },
    { step: 'parsing', message: '📖 Reading and parsing content...' },
    { step: 'rag_processing', message: '🧠 Building knowledge context...' },
    { step: 'summarizer_context', message: '📝 Preparing summary context...' },
    { step: 'novelty_analysis', message: '⭐ Analyzing novelty and impact...' },
    { step: 'humanizing', message: '👥 Making it human-friendly...' },
    { step: 'output_generation', message: '✨ Generating your explanation...' }
  ];

  // Rotate fun facts every 8 seconds during loading with fade animation
  useEffect(() => {
    if (isLoading) {
      // Set initial fact
      setFunFact(funFacts[Math.floor(Math.random() * funFacts.length)]);
      setFactVisible(true);
      
      const factInterval = setInterval(() => {
        // Fade out
        setFactVisible(false);
        
        // After fade out, change fact and fade in
        setTimeout(() => {
          setFunFact(funFacts[Math.floor(Math.random() * funFacts.length)]);
          setFactVisible(true);
        }, 300); // 300ms for fade out transition
      }, 8000);
      
      return () => clearInterval(factInterval);
    }
  }, [isLoading, funFacts]);

  // Countdown timer effect
  useEffect(() => {
    if (retryAfter && timeLeft && timeLeft > 0) {
      const timer = setInterval(() => {
        setTimeLeft(prev => {
          if (prev && prev <= 1) {
            setIsRateLimit(false);
            setRetryAfter(null);
            setError(null);
            return null;
          }
          return prev ? prev - 1 : null;
        });
      }, 1000);

      return () => clearInterval(timer);
    }
  }, [retryAfter, timeLeft]);

  const formatTime = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const handleFeedbackSubmit = async (feedback: {
    rating: 'positive' | 'negative'
    comment?: string
    paperInfo: { title?: string; arxivId?: string }
  }) => {
    try {
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8001';
      
      // Send to backend API
      await fetch(`${backendUrl}/api/feedback`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          rating: feedback.rating,
          comment: feedback.comment,
          paper_info: feedback.paperInfo,
          timestamp: new Date().toISOString()
        }),
      });
      
      // Optional: Send to analytics service like Google Analytics, Mixpanel, etc.
      if (typeof window !== 'undefined' && (window as unknown as { gtag?: (...args: unknown[]) => void }).gtag) {
        (window as unknown as { gtag: (...args: unknown[]) => void }).gtag('event', 'feedback_submitted', {
          feedback_rating: feedback.rating,
          paper_title: feedback.paperInfo.title,
          arxiv_id: feedback.paperInfo.arxivId
        });
      }
    } catch (error) {
      console.error('Failed to submit feedback:', error);
      // Still show success to user even if backend fails
    }
  };

  const handleSubmit = async (data: { arxivId?: string; pdfUrl?: string; pdfFile?: File }) => {
    const startTime = performance.now();
    
    setIsLoading(true);
    setError(null);
    setResults(null);
    setIsRateLimit(false);
    setRetryAfter(null);
    setTimeLeft(null);

    // Track paper upload analytics
    if (data.pdfFile) {
      analytics.paperUpload(data.pdfFile.size, data.pdfFile.type);
    } else if (data.arxivId) {
      analytics.paperUpload(0, 'arxiv_id');
    } else if (data.pdfUrl) {
      analytics.paperUpload(0, 'pdf_url');
    }

    try {
      // Call the actual backend API
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8001';
      
      // Check if backend is available (for production deployment)
      const isProduction = process.env.NODE_ENV === 'production';
      const isLocalhost = backendUrl.includes('localhost');
      
      if (isProduction && isLocalhost) {
        throw new Error('Backend service is not properly configured for production. Please set NEXT_PUBLIC_BACKEND_URL environment variable.');
      }
      
      let submitResponse;
      
      if (data.pdfFile) {
        // Handle PDF file upload
        const formData = new FormData();
        formData.append('pdf_file', data.pdfFile);
        
        submitResponse = await fetch(`${backendUrl}/api/summarize`, {
          method: 'POST',
          body: formData,
        });
      } else {
        // Handle ArXiv ID or PDF URL
        submitResponse = await fetch(`${backendUrl}/api/summarize`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            arxiv_id: data.arxivId,
            pdf_url: data.pdfUrl,
          }),
        });
      }

      if (!submitResponse.ok) {
        const errorData = await submitResponse.json().catch(() => ({}));
        
        // Check for rate limit error
        if (submitResponse.status === 429) {
          const retryAfterHeader = submitResponse.headers.get('Retry-After');
          const retrySeconds = retryAfterHeader ? parseInt(retryAfterHeader) : 300; // Default 5 minutes
          
          setIsRateLimit(true);
          setRetryAfter(retrySeconds);
          setTimeLeft(retrySeconds);
          setError(`Rate limit exceeded. Please wait ${formatTime(retrySeconds)} before trying again.`);
          setIsLoading(false);
          return;
        }
        
        throw new Error(errorData.detail || `Failed to submit paper: ${submitResponse.statusText}`);
      }

      const submitData = await submitResponse.json();
      const jobId = submitData.job_id;

      // Step 2: Poll for results and track progress
      let attempts = 0;
      const maxAttempts = 120; // 10 minutes max (5 second intervals)
      
      while (attempts < maxAttempts) {
        await new Promise(resolve => setTimeout(resolve, 3000)); // Wait 3 seconds for faster updates
        
        const statusResponse = await fetch(`${backendUrl}/api/jobs/${jobId}`);
        
        if (!statusResponse.ok) {
          // Check for rate limit during polling
          if (statusResponse.status === 429) {
            const retryAfterHeader = statusResponse.headers.get('Retry-After');
            const retrySeconds = retryAfterHeader ? parseInt(retryAfterHeader) : 300;
            
            setIsRateLimit(true);
            setRetryAfter(retrySeconds);
            setTimeLeft(retrySeconds);
            setError(`Rate limit exceeded. Please wait ${formatTime(retrySeconds)} before trying again.`);
            setIsLoading(false);
            return;
          }
          
          throw new Error(`Failed to get job status: ${statusResponse.statusText}`);
        }

        const statusData = await statusResponse.json();
        
        // Update loading step based on current status
        if (statusData.current_step) {
          const stepInfo = loadingSteps.find(s => s.step === statusData.current_step);
          if (stepInfo) {
            setLoadingStep(stepInfo.message);
          }
        }
        
        if (statusData.status === 'completed') {
          const processingTime = performance.now() - startTime;
          
          // Extract the results from the backend response
          const results: Results = {
            seriousSummary: statusData.analysis_result?.serious_summary || 'Processing completed',
            funAnalogy: statusData.analysis_result?.human_fun_summary || 'Fun summary not available',
            friendsTake: statusData.analysis_result?.final_digest || "Here's what we think about this paper! 😄",
            noveltyScore: statusData.analysis_result?.novelty_score || 0.5,
            metadata: statusData.paper_metadata || undefined,
          };
          
          // Track successful completion
          const endTime = performance.now();
          analytics.summaryGenerated(processingTime, results.noveltyScore);
          trackAPICall('/api/summarize', startTime, endTime, 200);
          
          setResults(results);
          setIsLoading(false);
          setLoadingStep('');
          return;
        } else if (statusData.status === 'failed') {
          throw new Error(statusData.error_message || 'Processing failed');
        }
        
        attempts++;
      }
      
      throw new Error('Processing timeout - please try again');
    } catch (err) {
      console.error('Error processing paper:', err);
      const errorMessage = err instanceof Error ? err.message : 'Failed to process the paper. Please try again.';
      
      // Track error analytics
      const endTime = performance.now();
      analytics.summaryFailed(err instanceof Error ? err.name : 'unknown_error');
      trackAPICall('/api/summarize', startTime, endTime, 500);
      
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <PrivacyAnalytics>
      <div className="min-h-screen bg-gradient-to-br from-background via-background to-secondary/20">
        <Navbar />
        
        <main className="container mx-auto px-4 py-8 space-y-8">
        {/* Hero Section */}
        <div className="text-center space-y-4 py-8">
          <h1 className="text-4xl md:text-6xl font-bold bg-gradient-to-r from-primary via-blue-600 to-purple-600 bg-clip-text text-transparent">
            AI Paper Explainer
          </h1>
          <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto">
            Transform research papers into digestible insights with serious analysis, fun analogies, and witty takes
          </p>
        </div>

        {/* Input Form */}
        <div className="max-w-2xl mx-auto">
          <InputForm onSubmit={handleSubmit} isLoading={isLoading} />
        </div>

        {/* Error Display */}
        {error && (
          <div className={`max-w-2xl mx-auto p-6 rounded-lg border ${
            isRateLimit 
              ? 'bg-amber-50 dark:bg-amber-950/20 border-amber-200 dark:border-amber-800' 
              : 'bg-destructive/10 border-destructive/20'
          }`}>
            {isRateLimit ? (
              <div className="text-center space-y-3">
                <div className="flex items-center justify-center gap-2">
                  <div className="w-5 h-5 text-amber-600 dark:text-amber-400">⏱️</div>
                  <h3 className="text-lg font-semibold text-amber-800 dark:text-amber-200">
                    Rate Limit Reached
                  </h3>
                </div>
                <p className="text-amber-700 dark:text-amber-300">
                  You&apos;ve reached the usage limit. Our AI needs a moment to recharge! ⚡
                </p>
                {timeLeft && (
                  <div className="space-y-2">
                    <div className="text-2xl font-mono font-bold text-amber-800 dark:text-amber-200">
                      {formatTime(timeLeft)}
                    </div>
                    <p className="text-sm text-amber-600 dark:text-amber-400">
                      Time remaining until you can try again
                    </p>
                  </div>
                )}
                <div className="pt-2 text-sm text-amber-600 dark:text-amber-400">
                  💡 Tip: While you wait, maybe grab a coffee or stretch? Your paper will be ready soon!
                </div>
              </div>
            ) : (
              <p className="text-destructive text-center">{error}</p>
            )}
          </div>
        )}

        {/* Enhanced Loading State with Animations */}
        {isLoading && (
          <div className="max-w-4xl mx-auto">
            <div className="bg-gradient-to-br from-blue-50 to-purple-50 dark:from-blue-950/20 dark:to-purple-950/20 border border-blue-200 dark:border-blue-800 rounded-xl p-8 shadow-lg">
              <div className="text-center space-y-6">
                {/* Animated Processing Icon */}
                <div className="relative">
                  <div className="inline-block animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600"></div>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="w-8 h-8 bg-blue-600 rounded-full animate-pulse"></div>
                  </div>
                </div>
                
                {/* Current Step */}
                <div className="space-y-3">
                  <h3 className="text-xl font-semibold text-foreground">
                    🧠 AI Brain at Work
                  </h3>
                  <div className="min-h-[60px] flex items-center justify-center">
                    <p className="text-lg text-muted-foreground animate-pulse transition-all duration-500">
                      {loadingStep || '📥 Initializing AI analysis...'}
                    </p>
                  </div>
                </div>

                {/* Progress Dots */}
                <div className="flex justify-center space-x-2">
                  {[0, 1, 2, 3].map((dot) => (
                    <div
                      key={dot}
                      className="w-3 h-3 bg-blue-600 rounded-full animate-bounce"
                      style={{ animationDelay: `${dot * 0.1}s` }}
                    ></div>
                  ))}
                </div>

                {/* Fun Facts Section */}
                <div className="border-t pt-6 mt-6">
                  <div className="bg-green-50 dark:bg-green-950/30 border border-green-200 dark:border-green-800 rounded-lg p-4">
                    <div className="flex items-start gap-3">
                      <div className="text-2xl">💡</div>
                      <div className="text-left">
                        <h4 className="font-medium text-green-800 dark:text-green-200 mb-2">
                          While You Wait...
                        </h4>
                        <div className="min-h-[3rem] flex items-center">
                          <p 
                            className={`text-sm text-green-700 dark:text-green-300 transition-all duration-300 transform ${
                              factVisible 
                                ? 'opacity-100 translate-y-0' 
                                : 'opacity-0 -translate-y-2'
                            }`}
                          >
                            {funFact || "AI is processing your paper with the knowledge of millions of research papers!"}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Estimated Time */}
                <div className="text-xs text-muted-foreground">
                  ⏱️ Typical processing time: 30-60 seconds
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Results with Slide-in Animation */}
        {results && !isLoading && (
          <div className="max-w-6xl mx-auto space-y-8 animate-slide-up">
            {/* Novelty Score with fade-in */}
            <div className="max-w-2xl mx-auto transform transition-all duration-700 hover:scale-105">
              <div className="animate-fade-in-delayed">
                <NoveltyMeter score={results.noveltyScore} />
              </div>
            </div>
            
            {/* Result Cards with staggered animation */}
            <div className="animate-slide-up-delayed">
              <ResultCards results={results} />
            </div>
            
            {/* Feedback Widget */}
            <div className="max-w-2xl mx-auto">
              <FeedbackWidget
                paperTitle={results.metadata?.title}
                arxivId={results.metadata?.arxiv_id}
                onFeedbackSubmit={handleFeedbackSubmit}
              />
            </div>
          </div>
        )}

        {/* Empty State */}
        {!results && !isLoading && !error && (
          <div className="text-center py-16 space-y-4">
            <div className="text-6xl mb-4">📚</div>
            <h2 className="text-2xl font-semibold text-muted-foreground">
              Ready to explain your paper!
            </h2>
            <p className="text-muted-foreground max-w-md mx-auto">
              Paste an arXiv ID, or share a paper URL to get started
            </p>
          </div>
        )}
      </main>

      <Footer />
      </div>
    </PrivacyAnalytics>
  );
}
