import Head from 'next/head';
import { Metadata } from 'next';

interface SEOProps {
  title?: string;
  description?: string;
  keywords?: string;
  image?: string;
  url?: string;
  type?: 'website' | 'article';
}

// Default SEO configuration
const defaultSEO = {
  title: 'AI Paper Summarizer - Instantly Understand Research Papers',
  description: 'Transform complex research papers into clear, engaging summaries with AI. Get technical analysis, fun analogies, and novelty scores in seconds.',
  keywords: 'AI paper summarizer, research analysis, academic papers, artificial intelligence, machine learning, scientific literature',
  image: '/og-image.png',
  url: 'https://your-app.vercel.app',
};

// Generate metadata for Next.js 13+ app directory
export function generateSEOMetadata({
  title,
  description,
  keywords,
  image,
  url,
  type = 'website'
}: SEOProps = {}): Metadata {
  const seoTitle = title ? `${title} | AI Paper Summarizer` : defaultSEO.title;
  const seoDescription = description || defaultSEO.description;
  const seoImage = image || defaultSEO.image;
  const seoUrl = url || defaultSEO.url;

  return {
    title: seoTitle,
    description: seoDescription,
    keywords: keywords || defaultSEO.keywords,
    
    // Open Graph
    openGraph: {
      title: seoTitle,
      description: seoDescription,
      url: seoUrl,
      siteName: 'AI Paper Summarizer',
      images: [
        {
          url: seoImage,
          width: 1200,
          height: 630,
          alt: 'AI Paper Summarizer - Understand Research Instantly',
        },
      ],
      locale: 'en_US',
      type: type,
    },

    // Twitter Card
    twitter: {
      card: 'summary_large_image',
      title: seoTitle,
      description: seoDescription,
      images: [seoImage],
      creator: '@your_twitter_handle',
    },

    // Additional meta tags
    robots: {
      index: true,
      follow: true,
      googleBot: {
        index: true,
        follow: true,
        'max-video-preview': -1,
        'max-image-preview': 'large',
        'max-snippet': -1,
      },
    },

    // Verification tags
    verification: {
      google: 'your-google-verification-code',
      other: {
        'bing': 'your-bing-verification-code',
      },
    },
  };
}

// Legacy Head component for pages directory
export function SEOHead({
  title,
  description,
  keywords,
  image,
  url,
  type = 'website'
}: SEOProps) {
  const seoTitle = title ? `${title} | AI Paper Summarizer` : defaultSEO.title;
  const seoDescription = description || defaultSEO.description;
  const seoImage = image || defaultSEO.image;
  const seoUrl = url || defaultSEO.url;

  return (
    <Head>
      {/* Basic meta tags */}
      <title>{seoTitle}</title>
      <meta name="description" content={seoDescription} />
      <meta name="keywords" content={keywords || defaultSEO.keywords} />
      <meta name="author" content="AI Paper Summarizer" />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      
      {/* Open Graph */}
      <meta property="og:title" content={seoTitle} />
      <meta property="og:description" content={seoDescription} />
      <meta property="og:image" content={seoImage} />
      <meta property="og:url" content={seoUrl} />
      <meta property="og:type" content={type} />
      <meta property="og:site_name" content="AI Paper Summarizer" />
      
      {/* Twitter Card */}
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content={seoTitle} />
      <meta name="twitter:description" content={seoDescription} />
      <meta name="twitter:image" content={seoImage} />
      <meta name="twitter:creator" content="@your_twitter_handle" />
      
      {/* Additional SEO */}
      <link rel="canonical" href={seoUrl} />
      <meta name="robots" content="index, follow" />
      
      {/* Favicon */}
      <link rel="icon" href="/favicon.ico" />
      <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
      
      {/* Preload critical resources */}
      <link rel="preload" href="/fonts/inter.woff2" as="font" type="font/woff2" crossOrigin="" />
    </Head>
  );
}

// JSON-LD Schema markup
export function generateSchemaMarkup(type: 'WebApplication' | 'Article' = 'WebApplication') {
  const baseSchema = {
    '@context': 'https://schema.org',
    '@type': type,
    name: 'AI Paper Summarizer',
    description: defaultSEO.description,
    url: defaultSEO.url,
    applicationCategory: 'EducationalApplication',
    operatingSystem: 'Web Browser',
    offers: {
      '@type': 'Offer',
      price: '0',
      priceCurrency: 'USD',
    },
    creator: {
      '@type': 'Organization',
      name: 'AI Paper Summarizer',
      url: defaultSEO.url,
    },
    featureList: [
      'AI-powered paper analysis',
      'Technical summary generation',
      'Fun analogies and explanations',
      'Novelty score calculation',
      'Multiple output formats'
    ],
  };

  return JSON.stringify(baseSchema);
}

// React component for Schema markup
export function SchemaMarkup({ type = 'WebApplication' }: { type?: 'WebApplication' | 'Article' }) {
  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{
        __html: generateSchemaMarkup(type),
      }}
    />
  );
}
