#!/bin/sh

# Collect static files
echo "Collect static files"
python manage.py collectstatic --noinput


# Apply database migrations
echo "Apply database migrations"
python manage.py migrate

# Localization
echo "Localization with gettext"
python manage.py compilemessages

# Start server
echo "Starting server"
uwsgi --http :8000 --module pleio_account.wsgi --static-map /static=/app/static --static-map /media=/app/media
