# AI Paper Explainer Frontend

A modern, responsive Next.js application that transforms research papers into accessible insights with serious analysis, fun analogies, and witty takes.

## Features

- **🌓 Dark/Light Mode**: Seamless theme switching with system preference detection
- **📱 Responsive Design**: Beautiful on both mobile and desktop
- **🎯 Smart Input**: Support for arXiv IDs, PDF URLs, and file uploads
- **📊 Novelty Meter**: Visual scoring of paper innovation level
- **🎭 Three Analysis Modes**:
  - **Serious Summary**: Academic, thorough analysis
  - **Fun Analogy**: Colorful explanations with relatable metaphors
  - **Friend's Take**: Short, witty, comic-style commentary
- **⚡ Real-time Processing**: Live updates during paper analysis
- **📋 Copy/Share**: Easy content sharing capabilities

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: TailwindCSS with custom design system
- **Icons**: Lucide React
- **Theme**: next-themes for dark/light mode
- **UI**: Custom components with accessibility focus

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser.

### Building for Production

```bash
npm run build
npm start
```

## Project Structure

```
src/
├── app/                    # Next.js app router
│   ├── layout.tsx         # Root layout with theme provider
│   ├── page.tsx           # Main application page
│   └── globals.css        # Global styles and CSS variables
├── components/            # React components
│   ├── navbar.tsx         # Navigation with logo and theme toggle
│   ├── input-form.tsx     # Paper input form with drag/drop
│   ├── result-cards.tsx   # Tabbed results display
│   ├── novelty-meter.tsx  # Progress bar for novelty scoring
│   ├── footer.tsx         # Footer component
│   ├── theme-provider.tsx # Theme context provider
│   └── theme-toggle.tsx   # Dark/light mode switch
└── lib/
    └── utils.ts           # Utility functions
```

## Component Overview

### InputForm
- Supports arXiv IDs and PDF URLs
- Drag-and-drop file upload
- Loading states and validation

### ResultCards
- Tabbed interface for three analysis types
- Copy-to-clipboard functionality
- Responsive design with color coding

### NoveltyMeter
- Visual progress bar (0.0 - 1.0 scale)
- Dynamic color coding:
  - 🟠 0-0.3: "Another fine-tune 😅"
  - 🔵 0.3-0.7: "Pretty cool 🚴→🏍️"
  - 🟢 0.7-1.0: "Breakthrough 🚀🔥"

## Customization

### Theme Colors
Modify CSS variables in `globals.css` to customize the color scheme:

```css
:root {
  --primary: 222.2 47.4% 11.2%;
  --secondary: 210 40% 96%;
  /* ... */
}
```

### Backend Integration
Update the API endpoint in `src/app/page.tsx`:

```typescript
// Replace the mock API call with your backend
const response = await fetch('/api/summarize', {
  method: 'POST',
  body: JSON.stringify(data),
});
```

## API Interface

Expected backend API response format:

```json
{
  "serious_summary": "Technical analysis...",
  "fun_analogy": "Fun explanation with analogies...",
  "friends_take": "Witty commentary...",
  "novelty_score": 0.85
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) for details.

## Built with ❤️ by Dieudonne

---

**Note**: This frontend is designed to work with the AI Paper Summarizer backend API. Make sure your backend is running and accessible before testing the full functionality.
