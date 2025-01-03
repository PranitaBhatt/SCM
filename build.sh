#!/bin/bash
# Install dependencies
pip install -r requirements.txt

# Collect static files
python3 manage.py collectstatic --noinput

# Create Vercel-compatible output directory
mkdir -p .vercel/output/static
cp -r staticfiles/ .vercel/output/static/

# Run migrations
python3 manage.py makemigrations
python3.manage.py migrate
