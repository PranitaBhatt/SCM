#!/bin/bash

# Ensure Python is installed
if ! command -v python3 &> /dev/null
then
    echo "python3 could not be found, installing..."
    apt-get update
    apt-get install -y python3
fi

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Ensure pip is installed within the virtual environment
if ! command -v pip &> /dev/null
then
    echo "pip could not be found, installing..."
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python3 get-pip.py
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

# Deactivate the virtual environment
deactivate
