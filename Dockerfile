# Base Python image
FROM python:3.13-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    python3-dev \
    bash \
    nginx \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

## Install uv
RUN pip install --no-cache-dir uv
COPY pyproject.toml .
COPY .python-version .
COPY uv.lock .

# Copy application code
COPY ./BackEnd/ ./BackEnd/
RUN uv sync

# -------------------- Frontend Setup --------------------
COPY ./FrontEnd/ ./FrontEnd/

# -------------------- NGINX Setup --------------------
# NGINX configuration
COPY /nginx.conf /etc/nginx/nginx.conf

# Copy and prepare startup script
COPY ./start_server.sh ./start_server.sh
RUN sed -i 's/\r$//' ./start_server.sh && chmod +x ./start_server.sh

# Expose NGINX port
EXPOSE 8080

# Start server
CMD ["./start_server.sh"]