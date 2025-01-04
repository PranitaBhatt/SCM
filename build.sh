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

# Navigate to the directory containing manage.py
cd scm_survey  # Change to the directory where manage.py is located

# Ensure manage.py exists
if [ ! -f "manage.py" ]; then
    echo "manage.py not found."
    exit 1
fi

# Collect static files
python3 manage.py collectstatic --noinput

# Ensure the static files directory exists and is not empty
if [ ! -d "../staticfiles" ]; then
    echo "staticfiles directory does not exist."
    exit 1
fi

if [ -z "$(ls -A ../staticfiles)" ]; then
    echo "staticfiles directory is empty."
    exit 1
fi

# Copy JSON files to the output directory
mkdir -p ../.vercel/output/data
cp survey/questions.json ../.vercel/output/data/
cp survey/suggestions.json ../.vercel/output/data/

# Create Vercel-compatible output directory
mkdir -p ../.vercel/output/static
cp -r ../staticfiles/. ../.vercel/output/static/

# Deactivate the virtual environment
deactivate
