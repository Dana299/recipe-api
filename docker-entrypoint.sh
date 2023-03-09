#!/bin/bash

sleep 10

# Apply database migrations
echo "Apply database migrations"
python manage.py migrate

# Creating superuser
echo "Creating superuser"
if [ "$DJANGO_SUPERUSER_USERNAME" ]
then
    python manage.py createsuperuser \
        --noinput \
        --user_name $DJANGO_SUPERUSER_USERNAME \
        --email $DJANGO_SUPERUSER_EMAIL
fi

# Load ingredients from json
echo "Loading dump data"
python manage.py loaddata ingredients_dump.json

# Start server
echo "Starting server"
python manage.py runserver 0.0.0.0:8000
