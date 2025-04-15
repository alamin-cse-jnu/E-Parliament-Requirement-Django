FROM python:3.13.1-slim

# Install dependencies for WeasyPrint (GTK3)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    python3-pip \
    python3-cffi \
    python3-brotli \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libpangocairo-1.0-0 \
    libcairo2 \
    libcairo2-dev \
    libgdk-pixbuf2.0-0 \
    shared-mime-info \
    mime-support \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create and set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Make entrypoint executable
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Use entrypoint script
ENTRYPOINT ["./entrypoint.sh"]