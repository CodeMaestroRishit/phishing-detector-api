# Use lightweight Python 3.10 slim image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies (ffmpeg and libsndfile1 for audio)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Command to run the app
CMD sh -c "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"
