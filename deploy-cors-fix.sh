#!/bin/bash

echo "🚀 Deploying CORS fix to Railway..."

# Add all changes
git add backend/simple_server.py

# Commit the changes
git commit -m "Fix CORS headers for Railway backend - Allow localhost frontend access"

# Push to GitHub (Railway will auto-deploy)
git push origin main

echo "✅ CORS fix deployed! Railway will auto-deploy in ~2 minutes."
echo "🔍 Check your Railway dashboard for deployment status."
echo "🌐 Test your frontend connection after deployment completes."
