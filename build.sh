#!/bin/bash
# Ensure pip and Python are available
if ! command -v pip &> /dev/null
then
    echo "pip could not be found"
    exit 1
fi

if ! command -v python3 &> /dev/null
then
    echo "python3 could not be found"
    exit 1
fi

# Install dependencies
pip install -r requirements.txt

# Collect static files
python3 manage.py collectstatic --noinput

# Create Vercel-compatible output directory
mkdir -p .vercel/output/static
cp -r staticfiles/. .vercel/output/static/

# Run migrations
python3 manage.py makemigrations
python3 manage.py migrate
