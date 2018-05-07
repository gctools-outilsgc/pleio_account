#!/bin/sh

# Collect static files
echo "Collect static files"
python manage.py collectstatic --noinput

# Wait for database to be ready
echo "Waiting for database..."
until nc -w 1 $DB_HOST 5432 >/dev/null 2>&1
do
    printf '.'
    sleep 1
done
echo

# Localization
echo "Localization with gettext"
django-admin compilemessages

# Apply database migrations
echo "Apply database migrations"
python manage.py migrate

# Start Redis Server
echo "Starting Redis Cache Server"
redis-server --daemonize yes

# Start server
echo "Starting web server"
uwsgi --http :8000 --module pleio_account.wsgi --workers 5 --static-map /static=/app/static --static-map /media=/app/media


