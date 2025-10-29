FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 10000

# Run the app
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "10000"]
