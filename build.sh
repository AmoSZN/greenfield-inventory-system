#!/bin/bash
echo "🚀 Building Greenfield Inventory System for Render"
echo "=================================================="

# Install Python dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Create data directory if it doesn't exist
echo "📁 Setting up data directory..."
mkdir -p Data

# Set up logging directory
echo "📝 Setting up logging..."
mkdir -p logs

echo "✅ Build complete - ready for deployment!"
