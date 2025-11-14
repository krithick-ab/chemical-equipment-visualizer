# Use the official Python image as the base image
FROM python:3.10-slim-buster

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE backend.backend.settings

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required for Python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    python3-dev \
    nginx \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install poetry

# Copy the entire project into the container
COPY . /app/

# Expose the port that Gunicorn will listen on
EXPOSE 8000

# Command to run the application using Gunicorn
CMD ["gunicorn", "backend.backend.wsgi:application", "--bind", "0.0.0.0:8000"]