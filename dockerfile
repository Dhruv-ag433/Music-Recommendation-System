FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libsndfile1 \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (better caching)
COPY requirements.txt .

# Install Python deps
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Copy supervisor config
COPY supervisor.conf /etc/supervisor/conf.d/supervisor.conf

# Expose ports
EXPOSE 8000 8501

# Run supervisor
CMD ["/usr/bin/supervisord"]
