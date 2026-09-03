# Dockerfile for Kirki eCommerce Automation Suite
FROM python:3.9-slim-bullseye

# Install system dependencies & Chromium
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    git \
    curl \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    && rm -rf /var/lib/apt/lists/*

ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose Web Studio port
EXPOSE 5001

# Launch Web Studio GUI by default
CMD ["python3", "gui_web.py"]
