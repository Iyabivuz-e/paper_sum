'use client';

import { useState, useEffect } from 'react';
import { X, Shield, BarChart, Zap } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';

interface CookieConsentProps {
  onAccept: () => void;
  onDecline: () => void;
}

export function CookieConsent({ onAccept, onDecline }: CookieConsentProps) {
  const [isVisible, setIsVisible] = useState(false);
  const [showDetails, setShowDetails] = useState(false);

  useEffect(() => {
    // Check if user has already made a choice
    const consent = localStorage.getItem('cookie-consent');
    if (!consent) {
      setIsVisible(true);
    }
  }, []);

  const handleAccept = () => {
    localStorage.setItem('cookie-consent', 'accepted');
    localStorage.setItem('analytics-enabled', 'true');
    setIsVisible(false);
    onAccept();
  };

  const handleDecline = () => {
    localStorage.setItem('cookie-consent', 'declined');
    localStorage.setItem('analytics-enabled', 'false');
    setIsVisible(false);
    onDecline();
  };

  const handleCustomize = () => {
    setShowDetails(!showDetails);
  };

  if (!isVisible) return null;

  return (
    <div className="fixed bottom-4 left-4 right-4 z-50 md:max-w-md md:left-auto">
      <Card className="bg-background border-2 shadow-lg">
        <CardContent className="p-4">
          <div className="flex items-start gap-3">
            <Shield className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
            <div className="flex-1">
              <h3 className="font-semibold text-sm mb-2">
                🍪 We value your privacy
              </h3>
              <p className="text-xs text-muted-foreground mb-3">
                We use cookies to improve your experience and understand how our app is used. 
                This helps us make it better for everyone!
              </p>

              {showDetails && (
                <div className="mb-3 space-y-2 text-xs">
                  <div className="flex items-center gap-2">
                    <BarChart className="w-4 h-4 text-green-600" />
                    <span className="text-green-700 dark:text-green-300">
                      <strong>Analytics:</strong> Track usage patterns and improve features
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Zap className="w-4 h-4 text-blue-600" />
                    <span className="text-blue-700 dark:text-blue-300">
                      <strong>Performance:</strong> Monitor speed and fix issues
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Shield className="w-4 h-4 text-purple-600" />
                    <span className="text-purple-700 dark:text-purple-300">
                      <strong>Privacy:</strong> No personal data collection
                    </span>
                  </div>
                </div>
              )}

              <div className="flex flex-wrap gap-2">
                <Button
                  size="sm"
                  onClick={handleAccept}
                  className="text-xs h-7"
                >
                  Accept All
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleDecline}
                  className="text-xs h-7"
                >
                  Decline
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleCustomize}
                  className="text-xs h-7"
                >
                  {showDetails ? 'Less Info' : 'Learn More'}
                </Button>
              </div>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleDecline}
              className="p-1 h-auto text-muted-foreground hover:text-foreground"
            >
              <X className="w-4 h-4" />
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

// Hook to manage consent state
export function useCookieConsent() {
  const [hasConsent, setHasConsent] = useState<boolean | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const consent = localStorage.getItem('cookie-consent');
    const analyticsEnabled = localStorage.getItem('analytics-enabled') === 'true';
    
    setHasConsent(consent === 'accepted' && analyticsEnabled);
    setIsLoading(false);
  }, []);

  const grantConsent = () => {
    localStorage.setItem('cookie-consent', 'accepted');
    localStorage.setItem('analytics-enabled', 'true');
    setHasConsent(true);
  };

  const revokeConsent = () => {
    localStorage.setItem('cookie-consent', 'declined');
    localStorage.setItem('analytics-enabled', 'false');
    setHasConsent(false);
  };

  const resetConsent = () => {
    localStorage.removeItem('cookie-consent');
    localStorage.removeItem('analytics-enabled');
    setHasConsent(null);
  };

  return {
    hasConsent,
    isLoading,
    grantConsent,
    revokeConsent,
    resetConsent,
  };
}

// Privacy-compliant analytics wrapper
export function PrivacyAnalytics({ children }: { children: React.ReactNode }) {
  const { hasConsent, grantConsent, revokeConsent } = useCookieConsent();

  return (
    <>
      {children}
      <CookieConsent
        onAccept={grantConsent}
        onDecline={revokeConsent}
      />
    </>
  );
}
