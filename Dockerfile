FROM python:3.11-slim

# Install system dependencies and Chromium/Chromium-driver
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy test files
COPY . .

# Environment variable to indicate headless execution inside Docker
ENV HEADLESS=true
ENV IS_DOCKER=true

# Command to execute tests and output Cucumber JSON report
CMD ["behave", "-f", "json", "-o", "evidence/report.json"]
