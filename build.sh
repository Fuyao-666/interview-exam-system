#!/usr/bin/env bash
set -o errexit

# Install Python dependencies
pip install -r backend/requirements.txt

# Install Node.js and build frontend
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs || true

cd frontend
npm install
npm run build
cd ..
