'use client';

import React, { useState } from 'react';
import { formatText, formatChatText } from '../utils/textFormatter';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Copy, Share2, ExternalLink, Calendar, User, Tag } from 'lucide-react';

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

interface ResultCardsProps {
  results: Results;
}

export default function ResultCards({ results }: ResultCardsProps) {
  const [copiedCard, setCopiedCard] = useState<string | null>(null);

  const copyToClipboard = async (text: string, cardType: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedCard(cardType);
      setTimeout(() => setCopiedCard(null), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  const shareContent = async (text: string, title: string) => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: title,
          text: text,
          url: window.location.href,
        });
      } catch (err) {
        console.error('Failed to share: ', err);
      }
    } else {
      // Fallback to copying to clipboard
      copyToClipboard(text, 'share');
    }
  };

  // Parse serious summary into sections
  const parseSeriousSummary = (text: string) => {
    const sections = {
      contribution: '',
      approach: '',
      results: '',
      limitations: ''
    };

    // Try to extract sections based on common patterns
    const contributionMatch = text.match(/(?:1\.|Main contribution|Contribution|Innovation)[\s\S]*?(?=(?:2\.|Technical|Approach|Methodology)|$)/i);
    const approachMatch = text.match(/(?:2\.|Technical|Approach|Methodology)[\s\S]*?(?=(?:3\.|Results|Key results|Performance)|$)/i);
    const resultsMatch = text.match(/(?:3\.|Results|Key results|Performance)[\s\S]*?(?=(?:4\.|Limitations|Drawbacks)|$)/i);
    const limitationsMatch = text.match(/(?:4\.|Limitations|Drawbacks)[\s\S]*?$/i);

    // Helper function to clean section content
    const cleanSection = (content: string) => {
      return content
        .replace(/^(?:1\.|Main contribution|Contribution|Innovation)[\s:]*\n?/i, '')
        .replace(/^(?:2\.|Technical|Approach|Methodology)[\s:]*\n?/i, '')
        .replace(/^(?:3\.|Results|Key results|Performance)[\s:]*\n?/i, '')
        .replace(/^(?:4\.|Limitations|Drawbacks)[\s:]*\n?/i, '')
        .replace(/^\*+\s*/, '') // Remove leading stars
        .replace(/\s*\*+$/, '') // Remove trailing stars
        .replace(/^\*\*([^*]+)\*\*\s*\n?/g, '') // Remove bold headers completely
        .replace(/^([^*\n]+)\*\*\s*\n?/g, '') // Remove lines ending with **
        .replace(/^(Technical approach|Main contribution|Key results|Limitations)[\s*]*\n?/gi, '') // Remove duplicate titles
        .replace(/\n\s*\n/g, '\n') // Clean up multiple newlines
        .trim();
    };

    sections.contribution = contributionMatch ? cleanSection(contributionMatch[0]) : '';
    sections.approach = approachMatch ? cleanSection(approachMatch[0]) : '';
    sections.results = resultsMatch ? cleanSection(resultsMatch[0]) : '';
    sections.limitations = limitationsMatch ? cleanSection(limitationsMatch[0]) : '';

    // Fallback: if parsing fails, split by sentences
    if (!sections.contribution && !sections.approach) {
      const sentences = text.split(/[.!?]+/).filter((s: string) => s.trim().length > 10);
      sections.contribution = sentences.slice(0, 2).join('. ') + '.';
      sections.approach = sentences.slice(2, 4).join('. ') + '.';
      sections.results = sentences.slice(4, 6).join('. ') + '.';
      sections.limitations = sentences.slice(6, 8).join('. ') + '.';
    }

    return sections;
  };

  const seriousSections = parseSeriousSummary(results.seriousSummary);

  return (
    <div className="space-y-8">
      {/* Paper Metadata Card */}
      {results.metadata && (
        <Card className="border-2 border-slate-300/20 bg-gradient-to-br from-background to-slate-50/50 dark:to-slate-950/20">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <div className="w-3 h-3 bg-slate-500 rounded-full"></div>
              <span className="text-lg text-foreground">
                {results.metadata.title}
              </span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">

            {/* Authors & Date */}
            <div className="grid md:grid-cols-2 gap-4">
              <div className="flex items-start gap-2">
                <User size={16} className="text-blue-600 dark:text-blue-400 mt-1 flex-shrink-0" />
                <div>
                  <div className="text-sm font-semibold text-foreground mb-1">Authors</div>
                  <div className="text-sm text-muted-foreground">
                    {results.metadata.authors.join(', ')}
                  </div>
                </div>
              </div>
              
              <div className="flex items-start gap-2">
                <Calendar size={16} className="text-green-600 dark:text-green-400 mt-1 flex-shrink-0" />
                <div>
                  <div className="text-sm font-semibold text-foreground mb-1">Published</div>
                  <div className="text-sm text-muted-foreground">
                    {new Date(results.metadata.published_date).toLocaleDateString()}
                  </div>
                </div>
              </div>
            </div>

            {/* Categories & ArXiv Link */}
            <div className="grid md:grid-cols-2 gap-4">
              <div className="flex items-start gap-2">
                <Tag size={16} className="text-purple-600 dark:text-purple-400 mt-1 flex-shrink-0" />
                <div>
                  <div className="text-sm font-semibold text-foreground mb-1">Categories</div>
                  <div className="flex flex-wrap gap-1">
                    {results.metadata.categories.map((category, index) => (
                      <span 
                        key={index}
                        className="px-2 py-1 bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200 text-xs rounded-full font-medium"
                      >
                        {category}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              <div className="flex items-start gap-2">
                <ExternalLink size={16} className="text-orange-600 dark:text-orange-400 mt-1 flex-shrink-0" />
                <div>
                  <div className="text-sm font-semibold text-foreground mb-1">Source</div>
                  <a 
                    href={results.metadata.arxiv_id}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 hover:underline flex items-center gap-1 font-medium"
                  >
                    View on ArXiv <ExternalLink size={12} />
                  </a>
                </div>
              </div>
            </div>

            {/* Abstract Summary */}
            <div>
              <div className="text-sm font-semibold text-foreground mb-2">Summary</div>
              <div className="text-sm text-muted-foreground leading-relaxed">
                {results.metadata.abstract.split('.').slice(0, 2).join('.') + '.'}
              </div>
            </div>

            {/* Copy button */}
            <div className="flex gap-2 pt-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => copyToClipboard(`${results.metadata?.title}\nBy: ${results.metadata?.authors.join(', ')}\n${results.metadata?.arxiv_id}`, 'metadata')}
                className="flex items-center gap-2"
              >
                <Copy size={16} />
                {copiedCard === 'metadata' ? 'Copied!' : 'Copy Citation'}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Technical Analysis Card */}
      <Card className="border-2 border-blue-300/20 bg-gradient-to-br from-background to-blue-50/50 dark:to-blue-950/20">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
            Technical Analysis
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 gap-4">
            {/* Main Contribution */}
            <div className="p-4 bg-gradient-to-br from-green-50 to-green-100 dark:from-green-950 dark:to-green-900 rounded-lg border border-green-200 dark:border-green-800">
              <h4 className="font-semibold text-green-800 dark:text-green-200 mb-2 flex items-center gap-2">
                <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                Main Contribution
              </h4>
              <div className="text-sm text-green-700 dark:text-green-300 prose prose-sm max-w-none dark:prose-invert">
                {formatText(seriousSections.contribution || 'Not available')}
              </div>
            </div>

            {/* Technical Approach */}
            <div className="p-4 bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-950 dark:to-blue-900 rounded-lg border border-blue-200 dark:border-blue-800">
              <h4 className="font-semibold text-blue-800 dark:text-blue-200 mb-2 flex items-center gap-2">
                <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
                Technical Approach
              </h4>
              <div className="text-sm text-blue-700 dark:text-blue-300 prose prose-sm max-w-none dark:prose-invert">
                {formatText(seriousSections.approach || 'Not available')}
              </div>
            </div>

            {/* Key Results */}
            <div className="p-4 bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-950 dark:to-purple-900 rounded-lg border border-purple-200 dark:border-purple-800">
              <h4 className="font-semibold text-purple-800 dark:text-purple-200 mb-2 flex items-center gap-2">
                <span className="w-2 h-2 bg-purple-500 rounded-full"></span>
                Key Results
              </h4>
              <div className="text-sm text-purple-700 dark:text-purple-300 prose prose-sm max-w-none dark:prose-invert">
                {formatText(seriousSections.results || 'Not available')}
              </div>
            </div>

            {/* Limitations */}
            <div className="p-4 bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-950 dark:to-orange-900 rounded-lg border border-orange-200 dark:border-orange-800">
              <h4 className="font-semibold text-orange-800 dark:text-orange-200 mb-2 flex items-center gap-2">
                <span className="w-2 h-2 bg-orange-500 rounded-full"></span>
                Limitations
              </h4>
              <div className="text-sm text-orange-700 dark:text-orange-300 prose prose-sm max-w-none dark:prose-invert">
                {formatText(seriousSections.limitations || 'Not available')}
              </div>
            </div>
          </div>

          {/* Novelty Score */}
          <div className="flex items-center gap-3 p-3 bg-secondary/50 rounded-lg mt-4">
            <div className="text-sm font-medium">Novelty Score:</div>
            <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <div 
                className="bg-gradient-to-r from-yellow-400 to-green-500 h-2 rounded-full transition-all duration-1000"
                style={{ width: `${(results.noveltyScore || 0) * 100}%` }}
              ></div>
            </div>
            <div className="text-sm font-bold">{((results.noveltyScore || 0) * 100).toFixed(0)}%</div>
          </div>

          <div className="flex gap-2 mt-4">
            <Button
              variant="outline"
              size="sm"
              onClick={() => copyToClipboard(results.seriousSummary, 'technical')}
              className="flex items-center gap-2"
            >
              <Copy size={16} />
              {copiedCard === 'technical' ? 'Copied!' : 'Copy'}
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => shareContent(results.seriousSummary, 'Technical Analysis')}
              className="flex items-center gap-2"
            >
              <Share2 size={16} />
              Share
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Two Main Cards */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Card 1: Fun Take */}
        <Card className="border-2 border-primary/20 bg-gradient-to-br from-background to-primary/5">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
              Fun Take & Analogies
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="max-h-96 overflow-y-auto prose prose-sm max-w-none dark:prose-invert">
              {formatText(results.funAnalogy)}
            </div>

            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => copyToClipboard(results.funAnalogy, 'fun-take')}
                className="flex items-center gap-2"
              >
                <Copy size={16} />
                {copiedCard === 'fun-take' ? 'Copied!' : 'Copy'}
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => shareContent(results.funAnalogy, 'Fun Take')}
                className="flex items-center gap-2"
              >
                <Share2 size={16} />
                Share
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Card 2: Friend's Take (Conversation Style) */}
        <Card className="border-2 border-green-300/20 bg-gradient-to-br from-background to-green-50/50 dark:to-green-950/20">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              Friend's Take - Coffee Chat
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="max-h-96 overflow-y-auto">
              {formatChatText(results.friendsTake)}
            </div>

            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => copyToClipboard(results.friendsTake, 'friends-take')}
                className="flex items-center gap-2"
              >
                <Copy size={16} />
                {copiedCard === 'friends-take' ? 'Copied!' : 'Copy'}
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => shareContent(results.friendsTake, "Friend's Take")}
                className="flex items-center gap-2"
              >
                <Share2 size={16} />
                Share
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
