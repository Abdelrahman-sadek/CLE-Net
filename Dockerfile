# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Install CLE-Net
RUN pip install -e .

# Expose ports (if running a node)
EXPOSE 26656 26657 1317

# Set environment variables
ENV PYTHONPATH=/app
ENV CLE_NET_HOME=/data

# Create data directory
RUN mkdir -p /data

# Default command
CMD ["python", "-m", "core.cosmos.app.app"]
