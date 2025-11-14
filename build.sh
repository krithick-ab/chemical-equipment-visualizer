#!/usr/bin/env bash
# Exit on error
set -o errexit

# Apply database migrations
python backend/manage.py migrate

# Collect static files
python backend/manage.py collectstatic --noinput