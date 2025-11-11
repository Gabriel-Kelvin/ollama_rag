#!/bin/bash
# Apply Supabase auth fix to backend/auth.py and docker-compose.yml

cd ~/ollama_rag || exit 1

# Backup files
cp backend/auth.py backend/auth.py.bak
cp docker-compose.yml docker-compose.yml.bak

# Fix backend/auth.py - add SUPABASE_ANON_KEY
if ! grep -q "SUPABASE_ANON_KEY = os.getenv" backend/auth.py; then
    sed -i '/^SUPABASE_SERVICE_ROLE = os.getenv/a SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")' backend/auth.py
fi

# Fix backend/auth.py - update apikey header
sed -i 's/"apikey": SUPABASE_SERVICE_ROLE if SUPABASE_SERVICE_ROLE else token,/"apikey": SUPABASE_ANON_KEY if SUPABASE_ANON_KEY else SUPABASE_SERVICE_ROLE,/' backend/auth.py

# Fix docker-compose.yml - add SUPABASE_ANON_KEY to backend environment
if ! grep -q "SUPABASE_ANON_KEY=\${VITE_SUPABASE_ANON_KEY}" docker-compose.yml; then
    sed -i '/SUPABASE_JWT_SECRET=\${SUPABASE_JWT_SECRET}/a\      - SUPABASE_ANON_KEY=${VITE_SUPABASE_ANON_KEY}' docker-compose.yml
fi

echo "✅ Auth fix applied! Rebuilding backend..."
sudo docker-compose up -d --build backend

