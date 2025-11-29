#!/bin/bash

set -o xtrace

# Cleanup container and image
docker container stop gear-calc
docker container rm gear-calc
docker image rm gear-calc

# Build image and tag it
docker build -t gear-calc .

# Create data directory on host if it doesn't exist
mkdir -p ~/code/container_data

# Create and run container
docker run -d \
  --name=gear-calc \
  --log-driver json-file \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  -e TZ=Europe/Stockholm \
  -v ~/code/container_data:/app/data \
  --restart unless-stopped \
  -p 8005:8005 \
  gear-calc