# Use Python 3.11 slim base image
FROM python:3.11-slim

# Build arguments with defaults
ARG BACKEND_PORT=8000
ARG BACKEND_HOST=0.0.0.0

# Set environment variables from build args
ENV BACKEND_PORT=${BACKEND_PORT}
ENV BACKEND_HOST=${BACKEND_HOST}

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose configurable port
EXPOSE ${BACKEND_PORT}

# Command to run the application
# Note: Environment variables are read from .env by the application
CMD ["python", "main.py"]
