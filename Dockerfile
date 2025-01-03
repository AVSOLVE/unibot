FROM python:3.12-slim

# Install system dependencies including xvfb and playwright
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
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create and set the working directory
RUN mkdir /app
WORKDIR /app
COPY . /app

# Install Poetry and project dependencies
RUN pip install poetry django celery djangorestframework playwright redis && \
  poetry config virtualenvs.in-project true && \
  poetry install --only main --no-root && \
  poetry run playwright install chromium --with-deps

# Copy the application code
COPY . .

# Expose the necessary ports
EXPOSE 8000 6379

# Copy the entrypoint script and set permissions
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Ensure the poetry virtual environment is used
ENV PATH="/code/.venv/bin:$PATH"
# Set the entrypoint for the container
CMD ["/entrypoint.sh"]
