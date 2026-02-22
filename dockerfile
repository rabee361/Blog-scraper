# Use a slim Python image
FROM python:3.12-slim

# Install system dependencies for Playwright and uv
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uv/bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY requirements.txt .

# Install dependencies using uv
RUN /uv/bin/uv pip install --system --no-cache -r requirements.txt

# Install Playwright browsers (Chromium only for slimness)
RUN playwright install chromium

# Copy the rest of the application
COPY . .

# Expose the API port
EXPOSE 4040

# Run the FastAPI server
CMD ["python", "api.py"]
