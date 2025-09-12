'use client'

import React from 'react'
import { Brain, Github, Coffee } from 'lucide-react'
import { ThemeToggle } from "./theme-toggle"

export function Navbar() {
  return (
    <nav className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          {/* Logo and Brand */}
          <div className="flex items-center space-x-2">
            <div className="flex items-center justify-center w-8 h-8 bg-blue-600 rounded-lg">
              <Brain className="w-5 h-5 text-white" />
            </div>
            <div className="hidden sm:block">
              <h1 className="text-xl font-bold text-foreground">AI Paper Explainer</h1>
              <p className="text-xs text-muted-foreground -mt-1">Research made simple</p>
            </div>
            <div className="sm:hidden">
              <h1 className="text-lg font-bold text-foreground">Paper AI</h1>
            </div>
          </div>

          {/* Navigation Links */}
          <div className="hidden md:flex items-center space-x-6">

            <a 
              href="https://github.com/your-repo" 
              target="_blank" 
              rel="noopener noreferrer"
              className="flex items-center space-x-1 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
            >
              <Github className="w-4 h-4" />
              <span>GitHub</span>
            </a>

            <a 
              href="https://buymeacoffee.com/Iyabivuze" 
              target="_blank" 
              rel="noopener noreferrer"
              className="flex items-center space-x-1 px-3 py-1.5 bg-yellow-500 hover:bg-yellow-600 text-yellow-900 text-sm font-medium rounded-full transition-colors"
            >
              <Coffee className="w-4 h-4" />
              <span className="hidden lg:inline">Buy me a coffee</span>
              <span className="lg:hidden">Coffee</span>
            </a>

            <ThemeToggle />
          </div>

          {/* Mobile Menu */}
          <div className="md:hidden flex items-center space-x-2">
            <a 
              href="https://buymeacoffee.com/Iyabivuze" 
              target="_blank" 
              rel="noopener noreferrer"
              className="flex items-center space-x-1 p-2 bg-yellow-500 hover:bg-yellow-600 text-yellow-900 rounded-full transition-colors"
            >
              <Coffee className="w-4 h-4" />
            </a>
            <ThemeToggle />
          </div>
        </div>
      </div>
    </nav>
  )
}
