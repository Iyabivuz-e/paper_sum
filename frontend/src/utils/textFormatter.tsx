import React from 'react';

export function formatText(text: string): React.ReactNode {
  if (!text) return null;

  // Split text into lines for processing
  const lines = text.split('\n');
  const elements: React.ReactNode[] = [];
  
  let listItems: string[] = [];
  let inList = false;
  
  lines.forEach((line, index) => {
    const trimmedLine = line.trim();
    
    // Handle lists (- or * or numbered)
    if (/^[-*]\s/.test(trimmedLine) || /^\d+\.\s/.test(trimmedLine)) {
      if (!inList) {
        inList = true;
        listItems = [];
      }
      listItems.push(trimmedLine.replace(/^[-*]\s/, '').replace(/^\d+\.\s/, ''));
    } else {
      // If we were in a list, close it
      if (inList) {
        elements.push(
          <ul key={`list-${index}`} className="list-disc list-inside mb-4 space-y-1">
            {listItems.map((item, i) => (
              <li key={i}>{formatInlineText(item)}</li>
            ))}
          </ul>
        );
        inList = false;
        listItems = [];
      }
      
      // Handle headers
      if (/^#{1,6}\s/.test(trimmedLine)) {
        const level = trimmedLine.match(/^#{1,6}/)?.[0].length || 1;
        const text = trimmedLine.replace(/^#{1,6}\s/, '');
        const headingClass = `font-bold mb-2 ${
          level === 1 ? 'text-2xl' : 
          level === 2 ? 'text-xl' : 
          level === 3 ? 'text-lg' : 'text-base'
        }`;
        
        if (level === 1) {
          elements.push(<h1 key={index} className={headingClass}>{formatInlineText(text)}</h1>);
        } else if (level === 2) {
          elements.push(<h2 key={index} className={headingClass}>{formatInlineText(text)}</h2>);
        } else if (level === 3) {
          elements.push(<h3 key={index} className={headingClass}>{formatInlineText(text)}</h3>);
        } else {
          elements.push(<h4 key={index} className={headingClass}>{formatInlineText(text)}</h4>);
        }
      } else if (trimmedLine) {
        // Regular paragraph
        elements.push(
          <p key={index} className="mb-3">
            {formatInlineText(trimmedLine)}
          </p>
        );
      } else {
        // Empty line
        elements.push(<br key={index} />);
      }
    }
  });
  
  // Close any remaining list
  if (inList) {
    elements.push(
      <ul key="final-list" className="list-disc list-inside mb-4 space-y-1">
        {listItems.map((item, i) => (
          <li key={i}>{formatInlineText(item)}</li>
        ))}
      </ul>
    );
  }
  
  return <div className="prose prose-sm max-w-none">{elements}</div>;
}

function formatInlineText(text: string): React.ReactNode {
  if (!text) return null;

  // First, handle LaTeX math expressions - support multiline with [\s\S]
  const parts: React.ReactNode[] = [];
  let lastIndex = 0;
  
  // Match both inline math \(...\) and display math \[...\] (including multiline)
  // [\s\S] matches any character including newlines
  const mathRegex = /\\\(([\s\S]+?)\\\)|\\\[([\s\S]+?)\\\]/g;
  let match;
  let matchCount = 0;
  
  while ((match = mathRegex.exec(text)) !== null) {
    // Add text before the math
    if (match.index > lastIndex) {
      const textBefore = text.substring(lastIndex, match.index);
      parts.push(<React.Fragment key={`text-${matchCount}`}>{formatNonMathText(textBefore)}</React.Fragment>);
    }
    
    // Add the math expression
    const mathContent = match[1] || match[2];
    const isDisplayMode = !!match[2];
    
    try {
      // Use dynamic import to avoid SSR issues
      if (typeof window !== 'undefined') {
        const katex = require('katex');
        const html = katex.renderToString(mathContent, {
          displayMode: isDisplayMode,
          throwOnError: false,
          output: 'html',
        });
        parts.push(
          <span 
            key={`math-${matchCount}`}
            className={isDisplayMode ? 'block my-2' : 'inline-block mx-1'}
            dangerouslySetInnerHTML={{ __html: html }} 
          />
        );
      } else {
        // Fallback for SSR
        parts.push(
          <code key={`math-${matchCount}`} className="bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded text-sm font-mono">
            {mathContent}
          </code>
        );
      }
    } catch (err) {
      // If rendering fails, show as code
      parts.push(
        <code key={`math-error-${matchCount}`} className="bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded text-sm font-mono">
          {mathContent}
        </code>
      );
    }
    
    lastIndex = match.index + match[0].length;
    matchCount++;
  }
  
  // Add remaining text
  if (lastIndex < text.length) {
    parts.push(<React.Fragment key={`text-final-${matchCount}`}>{formatNonMathText(text.substring(lastIndex))}</React.Fragment>);
  }
  
  return parts.length > 0 ? <>{parts}</> : formatNonMathText(text);
}

function formatNonMathText(text: string): React.ReactNode {
  if (!text) return null;

  let processedText = text;
  
  // Handle bold text (**text** or __text__) - process these first
  processedText = processedText.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  processedText = processedText.replace(/__(.*?)__/g, '<strong>$1</strong>');
  
  // Handle italic text (*text* or _text_) - but avoid conflicts with bold
  // Use negative lookbehind/lookahead to avoid matching * that are part of **
  processedText = processedText.replace(/(?<!\*)\*([^*]+?)\*(?!\*)/g, '<em>$1</em>');
  processedText = processedText.replace(/(?<!_)_([^_]+?)_(?!_)/g, '<em>$1</em>');
  
  // Handle inline code (`code`)
  processedText = processedText.replace(/`([^`]+)`/g, '<code class="bg-gray-100 dark:bg-gray-800 px-1 py-0.5 rounded text-sm font-mono">$1</code>');
  
  // Handle links [text](url)
  processedText = processedText.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" class="text-blue-600 dark:text-blue-400 hover:underline" target="_blank" rel="noopener noreferrer">$1</a>');
  
  // Return as JSX with proper HTML rendering
  return <span dangerouslySetInnerHTML={{ __html: processedText }} />;
}

export function formatChatText(text: string): React.ReactNode {
  if (!text) return null;

  // Clean up the text first
  let cleanText = text.replace(/^\d+\.\s*/, ''); // Remove leading numbers like "1. "
  cleanText = cleanText.replace(/^FRIEND'S TAKE[^\n]*\n?/i, ''); // Remove section headers
  cleanText = cleanText.replace(/^COFFEE CHAT[^\n]*\n?/i, '');
  
  // Stop at Twitter thread or other content sections
  const stopPatterns = [
    /\*\*2\.\s*TWITTER THREAD/i,
    /TWITTER THREAD/i,
    /\*\*3\.\s*BLOG POST/i,
    /BLOG POST/i,
    /\*\*LINKEDIN/i,
    /LINKEDIN POST/i
  ];
  
  for (const pattern of stopPatterns) {
    const match = cleanText.search(pattern);
    if (match !== -1) {
      cleanText = cleanText.substring(0, match).trim();
      break;
    }
  }
  
  // Split by conversation turns (look for Professor: and Friend: patterns)
  const turns = cleanText.split(/(?=\*\*(?:Professor|Friend):\*\*|(?:Professor|Friend):)/).filter(Boolean);
  
  if (turns.length === 0) {
    // Fallback: if no conversation format detected, format as regular text
    return <div className="prose prose-sm max-w-none dark:prose-invert">{formatText(text)}</div>;
  }
  
  return (
    <div className="space-y-4">
      {turns.map((turn, index) => {
        // Clean up the turn text
        const turnText = turn.trim();
        if (!turnText) return null;
        
        // Detect speaker
        const isProfessor = /^\*\*Professor:\*\*|^Professor:/i.test(turnText);
        const isFriend = /^\*\*Friend:\*\*|^Friend:/i.test(turnText);
        
        if (!isProfessor && !isFriend) {
          // Regular text, might be intro or conclusion
          return (
            <div key={index} className="text-sm text-gray-600 dark:text-gray-400 italic border-l-2 border-gray-300 pl-3">
              {formatInlineText(turnText)}
            </div>
          );
        }
        
        // Extract speaker and message
        const speaker = isProfessor ? 'Professor' : 'Friend';
        let message = turnText
          .replace(/^\*\*(Professor|Friend):\*\*\s*/i, '')
          .replace(/^(Professor|Friend):\s*/i, '')
          .replace(/^[""]/, '')
          .replace(/[""]$/, '')
          .trim();
        
        // Additional cleanup for any remaining markdown artifacts
        message = message.replace(/^\*+\s*/, '').replace(/\s*\*+$/, '');
        
        return (
          <div key={index} className={`flex gap-3 ${isFriend ? 'justify-end' : 'justify-start'} mb-4`}>
            <div className={`flex gap-3 max-w-[80%] ${isFriend ? 'flex-row-reverse' : 'flex-row'}`}>
              <div className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0 ${
                isProfessor 
                  ? 'bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200' 
                  : 'bg-green-200 dark:bg-green-900 text-green-900 dark:text-green-200'
              }`}>
                {speaker[0]}
              </div>
              <div className={`p-4 rounded-lg min-w-0 flex-1 ${
                isProfessor
                  ? 'bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-800'
                  : 'bg-green-100 dark:bg-green-950 border border-green-300 dark:border-green-800'
              }`}>
                <div className="font-semibold text-sm mb-2 text-gray-900 dark:text-gray-100">{speaker}</div>
                <div className={`text-sm leading-relaxed ${
                  isProfessor 
                    ? 'text-gray-700 dark:text-gray-300'
                    : 'text-gray-900 dark:text-gray-200'
                }`}>{formatInlineText(message)}</div>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
