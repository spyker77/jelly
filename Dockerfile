###########
# BUILDER #
###########

# Pull official base image
FROM python:3.11-slim-buster as builder

# Set working directory
WORKDIR /code

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential netcat curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY poetry.lock .
COPY pyproject.toml .
RUN pip install --upgrade pip \
    && curl -sSL https://install.python-poetry.org | python3 - --version 1.4.0 \
    && export PATH="/root/.local/bin:$PATH" \
    && poetry export -f requirements.txt --output requirements.txt --with dev --without-hashes \
    && pip wheel --no-cache-dir --no-deps --wheel-dir /code/wheels -r requirements.txt


#########
# FINAL #
#########

# Pull official base image
FROM python:3.11-slim-buster

# Set working directory
WORKDIR /home/app/web

# Create the app user
RUN addgroup --system app \
    && adduser --system --group app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential netcat \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY --from=builder /code/wheels /wheels
COPY --from=builder /code/requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache /wheels/*

# Add app
COPY . .

# Chown all the files to the app user
RUN chown -R app:app /home/app

# Change to the app user
USER app

# Run the server
CMD ["gunicorn", "-b", "0.0.0.0", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "app.main:app"]
