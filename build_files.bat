:: Install dependencies
pip install -r requirements.txt

:: Collect static files
python manage.py collectstatic --noinput

:: Create Vercel-compatible output directory
mkdir .vercel\output\static
xcopy /s staticfiles .vercel\output\static

python manage.py makemigrations
python manage.py migrate
