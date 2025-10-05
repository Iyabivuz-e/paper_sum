'use client'

import React from 'react'
import { Coffee, Heart, Linkedin } from 'lucide-react'
import Link from 'next/link'

export function Footer() {
  return (
    <footer className="border-t bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 mt-20">
      <div className="container mx-auto px-4 py-10">
        <div className="flex flex-col md:flex-row md:justify-between md:items-start gap-10">
          {/* About Section */}
          <div className="flex-1 space-y-4">
            <h3 className="text-lg font-semibold text-foreground">AI Paper Explainer</h3>
            <p className="text-sm text-muted-foreground leading-relaxed max-w-xs">
              Making complex research papers accessible to everyone through AI-powered explanations, 
              fun analogies, and clear insights.
            </p>
            <div className="flex items-center gap-1 text-sm text-muted-foreground">
              <span>Made with</span>
              <Heart className="w-4 h-4 text-red-500" />
              <span>for the research community</span>
            </div>
          </div>

          {/* Support & Contact */}
          <div className="flex flex-col items-start gap-4">
            <h3 className="text-lg font-semibold text-foreground">Support the Project</h3>
            <a
              href="https://buymeacoffee.com/Iyabivuze"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-4 py-2 bg-yellow-500 hover:bg-yellow-600 text-yellow-900 font-medium rounded-full transition-colors text-sm"
            >
              <Coffee className="w-4 h-4" />
              Buy me a coffee
            </a>
            <a
              href="https://www.linkedin.com/in/iyabivuze"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-4 py-2 border border-blue-600 text-blue-700 hover:bg-blue-50 rounded-full transition-colors text-sm"
            >
              <Linkedin className="w-4 h-4" />
              LinkedIn
            </a>
          </div>
        </div>

        {/* Bottom Section */}
        <div className="border-t mt-10 pt-6 flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="text-sm text-muted-foreground">
            © 2025 AI Paper Explainer. Open source and free to use.
          </div>
          <div className="text-xs text-muted-foreground text-center md:text-right">
            <p>Powered by AI • Built for researchers • Made with <span className="inline-block align-middle"><Heart className="w-3 h-3 text-red-500 inline" /></span></p>
          </div>
        </div>
      </div>
    </footer>
  )
}
