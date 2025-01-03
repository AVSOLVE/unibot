FROM python:3.12-slim

# Install system dependencies and clean up after
RUN apt-get update && apt-get install -y \
    xvfb \
    git \
    build-essential \
    redis-server \
    libpq-dev \
    curl \
    unzip \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libxcomposite1 \
    libxrandr2 \
    libxdamage1 \
    libxkbcommon0 \
    libgtk-3-0 \
    libpango-1.0-0 \
    libgbm1 \
    libasound2 \
    libpangocairo-1.0-0 \
    libxshmfence1 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Set up working directory
WORKDIR /app

# Install Poetry and Python dependencies
COPY pyproject.toml poetry.lock /app/
RUN pip install poetry && poetry install --no-dev --no-root

# Install playwright and Chromium
RUN poetry run playwright install chromium --with-deps

# Install Daphne for Channels
RUN pip install daphne

# Copy the rest of the app's code into the container
COPY . /app/

# Expose the necessary ports
EXPOSE 8000 6379

# Add entrypoint script and make it executable
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set entrypoint to start both Django, Daphne, and Celery
CMD ["/entrypoint.sh"]
