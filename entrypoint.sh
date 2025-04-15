#!/bin/sh

# Wait for database to be ready
echo "Waiting for MySQL to be available..."
python -c "
import sys
import time
import pymysql

retries = 30
while retries > 0:
    try:
        pymysql.connect(
            host='$DB_HOST',
            user='$DB_USER',
            passwd='$DB_PASSWORD',
            db='$DB_NAME',
            port=int('$DB_PORT')
        )
        break
    except pymysql.OperationalError:
        retries -= 1
        print('Waiting for MySQL to be available... (%s retries left)' % retries)
        time.sleep(1)

if retries == 0:
    print('Could not connect to MySQL database')
    sys.exit(1)

print('MySQL database is available')
"

# Apply database migrations
echo "Apply database migrations"
python manage.py migrate

# Collect static files
echo "Collect static files"
python manage.py collectstatic --noinput

# Start Gunicorn server
echo "Starting Gunicorn server"
exec gunicorn eparliament.wsgi:application --bind 0.0.0.0:8000