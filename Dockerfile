# Use a Python base image
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
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
RUN mkdir /code
WORKDIR /code
COPY . /code

# Install Poetry
RUN pip install poetry

# Configure Poetry to create virtualenvs inside the project folder
RUN poetry config virtualenvs.in-project true

# Install dependencies using Poetry
RUN poetry install --only main --no-root

# Install Playwright browsers
RUN poetry run playwright install chromium --with-deps

# Ensure the poetry virtual environment is used
ENV PATH="/code/.venv/bin:$PATH"

# Expose ports
EXPOSE 6379 8000

# Default command for the web container
CMD ["poetry", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]
