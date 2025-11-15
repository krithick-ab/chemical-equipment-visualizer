# Use the official Python image as the base image
FROM python:3.10-slim-buster

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/app/backend:$PYTHONPATH
ENV DJANGO_SETTINGS_MODULE=backend.settings

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required for Python packages
RUN DEBIAN_FRONTEND=noninteractive apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    python3-dev \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install Python dependencies
# Stage 1: Build the frontend
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm install
COPY frontend/ .
RUN npm run build

# Stage 2: Build the backend
FROM python:3.10-slim-buster
ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install poetry

# Copy the entire project into the container
COPY . /app/

# Expose the port that Gunicorn will listen on
EXPOSE 8000

# Command to run the application using Gunicorn
CMD ["gunicorn", "backend.backend.wsgi:application", "--bind", "0.0.0.0:8000"]