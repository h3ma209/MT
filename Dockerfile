# Use python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies if needed (e.g. for building some python packages)
# but for most wheels slim is fine.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# The model will be downloaded by the application on startup if not present
# COPY nllb-1.3b-int8 ./nllb-1.3b-int8

# Copy the rest of the application code (changes more often)
COPY translator.py server.py ./

# Expose the port
EXPOSE 8000

# Run the server
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
