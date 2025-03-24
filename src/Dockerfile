FROM python:3.9-slim

# Install necessary tools
RUN apt-get update && apt-get install -y docker.io && apt-get clean

# Copy the script into the container
COPY generate_docker_run.py /usr/local/bin/generate_docker_run.py

# Create the /output directory
RUN mkdir -p /output

# Expose the /output folder as a volume
VOLUME ["/output"]

# Set the script as the entrypoint
ENTRYPOINT ["python", "/usr/local/bin/generate_docker_run.py"]
