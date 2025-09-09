"use client"

import React, { useState } from "react"
import { Send, Loader2 } from "lucide-react"
import { cn } from "@/lib/utils"

interface InputFormProps {
  onSubmit: (data: { arxivId?: string; pdfUrl?: string; pdfFile?: File }) => void
  isLoading: boolean
}

export function InputForm({ onSubmit, isLoading }: InputFormProps) {
  const [input, setInput] = useState("")

  // Function to parse different input formats
  const parseInput = (inputText: string) => {
    const trimmed = inputText.trim();
    
    // Check if it's an ArXiv URL (https://arxiv.org/abs/XXXX.XXXXX)
    const arxivUrlMatch = trimmed.match(/(?:https?:\/\/)?(?:www\.)?arxiv\.org\/abs\/(\d{4}\.\d{4,5})/);
    if (arxivUrlMatch) {
      return { arxivId: arxivUrlMatch[1] };
    }
    
    // Check if it's an ArXiv PDF URL (https://arxiv.org/pdf/XXXX.XXXXX.pdf)
    const arxivPdfMatch = trimmed.match(/(?:https?:\/\/)?(?:www\.)?arxiv\.org\/pdf\/(\d{4}\.\d{4,5})(?:\.pdf)?/);
    if (arxivPdfMatch) {
      return { arxivId: arxivPdfMatch[1] };
    }
    
    // Check if it's a PDF URL (ends with .pdf)
    if (trimmed.match(/^https?:\/\/.+\.pdf$/i)) {
      return { pdfUrl: trimmed };
    }
    
    // Check if it's just an ArXiv ID (XXXX.XXXXX format)
    if (trimmed.match(/^\d{4}\.\d{4,5}$/)) {
      return { arxivId: trimmed };
    }
    
    // If none of the above, treat as potential ArXiv ID or return error
    return { arxivId: trimmed };
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (input.trim()) {
      const parsedInput = parseInput(input.trim());
      onSubmit(parsedInput);
      setInput("")
    }
  }

  return (
    <div className="w-full max-w-2xl mx-auto space-y-6">
      <div className="text-center space-y-2">
        <h2 className="text-2xl font-semibold">Transform Research Papers</h2>
        <p className="text-muted-foreground">
          Enter an ArXiv ID, ArXiv URL, PDF URL, or upload a PDF to get serious analysis, fun analogies, and witty takes
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="space-y-2">
          <div className="relative">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Enter ArXiv ID (2509.04198), ArXiv URL (https://arxiv.org/abs/2509.04198), or PDF URL..."
              className={cn(
                "w-full h-12 px-4 pr-12 rounded-lg border border-input bg-background",
                "text-sm placeholder:text-muted-foreground",
                "focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent",
                "disabled:cursor-not-allowed disabled:opacity-50"
              )}
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              className={cn(
                "absolute right-2 top-1/2 -translate-y-1/2",
                "h-8 w-8 rounded-md bg-primary text-primary-foreground",
                "hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed",
                "flex items-center justify-center transition-colors"
              )}
            >
              {isLoading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </button>
          </div>
          <p className="text-xs text-muted-foreground text-center">
            📖 All papers are sourced from the arXiv library
          </p>
        </div>

        {/* <div className="relative">
          <div className="flex items-center justify-center">
            <div className="flex-1 border-t border-border"></div>
            <span className="px-3 text-sm text-muted-foreground">or</span>
            <div className="flex-1 border-t border-border"></div>
          </div>
        </div> */}

        {/* <div
          className={cn(
            "relative rounded-lg border-2 border-dashed p-6 text-center transition-colors",
            "border-muted bg-muted/20 cursor-not-allowed opacity-60"
          )}
        >
          <div className="space-y-2">
            <div className="h-8 w-8 mx-auto bg-muted-foreground/20 rounded-lg flex items-center justify-center">
              <span className="text-xs">📄</span>
            </div>
            <div className="space-y-1">
              <p className="text-sm font-medium text-muted-foreground">PDF Upload - Coming Soon</p>
              <p className="text-xs text-muted-foreground">
                We're working on file upload support. For now, please use ArXiv IDs or PDF URLs.
              </p>
            </div>
          </div>
        </div> */}
      </form>
    </div>
  )
}
