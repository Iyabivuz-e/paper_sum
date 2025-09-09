'use client';

import { useState, useEffect } from 'react';
import { Navbar } from '@/components/modern-navbar';
import { InputForm } from '@/components/input-form';
import ResultCards from '@/components/ResultCards';
import { NoveltyMeter } from '@/components/novelty-meter';
import { FeedbackWidget } from '@/components/feedback-widget';
import { Footer } from '@/components/footer';

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
      if (typeof window !== 'undefined' && (window as any).gtag) {
        (window as any).gtag('event', 'feedback_submitted', {
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
    setIsLoading(true);
    setError(null);
    setResults(null);
    setIsRateLimit(false);
    setRetryAfter(null);
    setTimeLeft(null);

    try {
      // Call the actual backend API
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8001';
      
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
        submitResponse = await fetch(`${backendUrl}/api/summarize-json`, {
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

      // Step 2: Poll for results
      let attempts = 0;
      const maxAttempts = 60; // 5 minutes max (5 second intervals)
      
      while (attempts < maxAttempts) {
        await new Promise(resolve => setTimeout(resolve, 5000)); // Wait 5 seconds
        
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
        
        if (statusData.status === 'completed') {
          // Extract the results from the backend response
          const results: Results = {
            seriousSummary: statusData.analysis_result?.serious_summary || 'Processing completed',
            funAnalogy: statusData.analysis_result?.human_fun_summary || 'Fun summary not available',
            friendsTake: statusData.analysis_result?.final_digest || "Here's what we think about this paper! 😄",
            noveltyScore: statusData.analysis_result?.novelty_score || 0.5,
            metadata: statusData.paper_metadata || undefined,
          };
          
          setResults(results);
          setIsLoading(false);
          return;
        } else if (statusData.status === 'failed') {
          throw new Error(statusData.error_message || 'Processing failed');
        }
        
        attempts++;
      }
      
      throw new Error('Processing timeout - please try again');
    } catch (err) {
      console.error('Error processing paper:', err);
      setError(err instanceof Error ? err.message : 'Failed to process the paper. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
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
                  You've reached the usage limit. Our AI needs a moment to recharge! ⚡
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

        {/* Loading State */}
        {isLoading && (
          <div className="max-w-4xl mx-auto">
            <div className="text-center space-y-4 py-8">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
              <p className="text-muted-foreground">Processing your paper... This may take a few moments.</p>
            </div>
          </div>
        )}

        {/* Results */}
        {results && !isLoading && (
          <div className="max-w-6xl mx-auto space-y-8">
            {/* Novelty Score */}
            <div className="max-w-2xl mx-auto">
              <NoveltyMeter score={results.noveltyScore} />
            </div>
            
            {/* Result Cards */}
            <ResultCards results={results} />
            
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
              Upload a PDF, paste an arXiv ID, or share a paper URL to get started
            </p>
          </div>
        )}
      </main>

      <Footer />
    </div>
  );
}
