#!/bin/bash

# Build the Docker image
echo "Building Docker image..."
docker build -t flowstate:1.0 .

# Run the Docker container with port mapping
echo "Running Docker container..."
docker run --rm -i -p 8080:8080 flowstate:1.0 --url "https://www.youtube.com/watch?v=EUcxq8eWke8" --serve