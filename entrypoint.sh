#!/bin/sh

# Wait for the database to be ready
echo "Waiting for MySQL to start..."
# Try for 60 seconds (30 attempts, 2 seconds between each)
max_tries=30
count=0
while [ $count -lt $max_tries ]
do
    if nc -z $DATABASE_HOST $DATABASE_PORT; then
        echo "MySQL started successfully!"
        break
    fi
    echo "MySQL not available yet - retrying in 2 seconds (attempt $((count+1))/$max_tries)..."
    count=$((count+1))
    sleep 2
done

if [ $count -eq $max_tries ]; then
    echo "Error: MySQL did not start within the allotted time!"
    echo "Current environment variables:"
    echo "DATABASE_HOST: $DATABASE_HOST"
    echo "DATABASE_PORT: $DATABASE_PORT"
    exit 1
fi

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start server
echo "Starting server..."
exec "$@"
