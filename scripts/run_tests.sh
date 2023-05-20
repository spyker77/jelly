#!/usr/bin/env bash

set -e

COMPOSE_FILE=docker-compose.tests.yml

# This won't work when `source` the script, execute instead with `./run_tests.sh`.
# See the difference: https://superuser.com/a/176788
trap 'echo "Clean up..."; docker-compose -f "$COMPOSE_FILE" down -v && docker image prune -f' EXIT SIGINT SIGTERM

echo "Build imeages..."
docker-compose -f "$COMPOSE_FILE" build --pull

echo "Run tests..."
docker-compose -f "$COMPOSE_FILE" run --rm web_tests pytest
