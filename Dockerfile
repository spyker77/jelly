###########
# BUILDER #
###########

# Pull official base image
FROM python:3.11-slim-buster as builder

# Set working directory
WORKDIR /code

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc curl libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY poetry.lock pyproject.toml ./
RUN pip install --upgrade pip && \
    curl -sSL https://install.python-poetry.org | python3 - --version 1.4.2 && \
    export PATH="/root/.local/bin:$PATH" && \
    poetry export -f requirements.txt --output requirements.txt --with dev --without-hashes && \
    pip wheel --no-cache-dir --no-deps --wheel-dir /code/wheels -r requirements.txt


#########
# FINAL #
#########

# Pull official base image
FROM python:3.11-slim-buster

# Set working directory
WORKDIR /home/app/web

# Create the app user
RUN addgroup --system app && \
    adduser --system --group app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq5 && \
    rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY --from=builder /code/wheels /wheels
COPY --from=builder /code/requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache --no-binary :all: /wheels/*

# Add app with specified ownership
COPY --chown=app:app . .

# Change to the app user
USER app
