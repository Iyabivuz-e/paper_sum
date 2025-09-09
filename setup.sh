#!/bin/bash

# 🚀 AI Paper Explainer - Quick Setup Script
# This script helps you set up the analytics database quickly

echo "🎯 AI Paper Explainer - Analytics Setup"
echo "======================================"
echo

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ] && [ ! -f "backend/pyproject.toml" ]; then
    echo "❌ Error: Run this script from the project root directory"
    exit 1
fi

# Navigate to backend if needed
if [ -f "backend/pyproject.toml" ]; then
    cd backend
fi

echo "📁 Current directory: $(pwd)"
echo

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "📋 Creating .env file from template..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ Created .env file"
        echo "⚠️  Please edit .env with your actual NeonDB connection string"
        echo
    else
        echo "❌ Error: .env.example not found"
        exit 1
    fi
else
    echo "✅ .env file already exists"
fi

# Check if Prisma is installed
echo "🔍 Checking Prisma installation..."
if ! command -v prisma &> /dev/null; then
    echo "📦 Installing Prisma CLI..."
    npm install -g prisma
fi

# Check database connection
echo "🔌 Testing database connection..."
echo "📝 Please ensure your DATABASE_URL is set in .env"
echo "   Format: postgresql://user:pass@host:port/db?sslmode=require"
echo

read -p "Press Enter when your DATABASE_URL is configured in .env..."

# Generate Prisma client
echo "⚙️  Generating Prisma client..."
prisma generate

# Push database schema
echo "🗄️  Creating database tables..."
if prisma db push; then
    echo "✅ Database tables created successfully!"
    echo
else
    echo "❌ Failed to create database tables"
    echo "💡 Check your DATABASE_URL in .env"
    echo "💡 Ensure your NeonDB database is accessible"
    exit 1
fi

# Start Prisma Studio (optional)
echo "🎯 Setup complete! Here's what you can do next:"
echo
echo "1. 🔍 View your database:"
echo "   prisma studio"
echo "   (Opens at http://localhost:5555)"
echo
echo "2. 🚀 Start the backend server:"
echo "   uvicorn api:app --host 0.0.0.0 --port 8001 --reload"
echo
echo "3. 🎨 Start the frontend (in a new terminal):"
echo "   cd frontend && npm run dev"
echo
echo "4. 📊 Access admin dashboard:"
echo "   http://localhost:3000/admin"
echo "   Password: admin123 (change this!)"
echo
echo "5. ✨ Test the feedback system:"
echo "   Analyze a paper and provide feedback"
echo

read -p "Would you like to open Prisma Studio now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔍 Opening Prisma Studio..."
    prisma studio &
    echo "📊 Prisma Studio is running at http://localhost:5555"
fi

echo
echo "🎉 Setup completed successfully!"
echo "📖 See DEPLOYMENT_CHECKLIST.md for detailed instructions"
echo "📊 See ANALYTICS_SETUP.md for feature documentation"
