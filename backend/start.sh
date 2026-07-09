#!/bin/sh

# Run database migrations before starting servers to ensure up-to-date schema
echo "Running database migrations..."
python manage.py migrate --noinput

# Start gRPC server in background
echo "Starting gRPC server on port 50051..."
python manage.py run_grpc_server &

# Start Gunicorn in foreground
echo "Starting Gunicorn HTTP server on port 8000..."
exec gunicorn config.wsgi:application \
     --bind 0.0.0.0:8000 \
     --workers 3 \
     --timeout 60 \
     --access-logfile - \
     --error-logfile -
