# Docker Containers Backup

This repository provides a solution to back up and recreate Docker containers, networks, and volumes running on a host system. It generates the necessary `docker` commands to recreate the current state of all running containers, including their configurations, custom networks, and named volumes.

## Features

1. **Generate `docker run` Commands**:
   - Recreates all running containers with their configurations, including:
     - Container name
     - Image name
     - Volumes
     - Environment variables
     - Devices
     - User
     - Restart policy
     - Network settings (including containers using another container's network)
     - Hostname
     - DNS settings
     - Shared memory size (`--shm-size`) if greater than 64MB
     - CPU limits (`--cpus`) if not using all available CPUs

2. **Generate `docker volume create` Commands**:
   - Recreates all named and CIFS volumes with their drivers and options.

3. **Generate `docker network create` Commands**:
   - Recreates all custom networks with their drivers, options, and IPAM configurations (e.g., subnet, gateway).

4. **Output to a Single Script**:
   - All generated commands are saved in a single shell script (`docker_commands.sh`) for easy execution.

## How to Use

### Prerequisites
- Docker must be installed and running on the host system.
- The Docker socket (`/var/run/docker.sock`) must be accessible to the container running this script.

### Steps

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/sudipmandal/docker-containers-backup.git
   cd docker-containers-backup
   ```
2. **Build the Docker Container**
   ```bash
   docker build -t docker-containers-backup:v1.0 .
   ```
3. **Run the Container**
   ```bash
   docker run --rm \
    -v /var/run/docker.sock:/var/run/docker.sock:ro \
    -v /path/to/backup/folder/on/host:/output \
    docker-containers-backup:v1.0
   ```
4. **View the Output**
   The generated commands will be saved in the /path/to/backup/folder/on/host/docker_commands.sh file. You can inspect the file:
   ```bash
   cat /path/to/backup/folder/on/host/docker_commands.sh
   ```

## Notes

- Ensure the Docker socket is mounted as a read-only volume (/var/run/docker.sock) when running the container.
- The script handles containers using another container's network (--network container:<container_name>).
- Shared memory size (--shm-size) and CPU limits (--cpus) are included in the docker run commands if applicable.

## Limitations
- The script does not back up container data stored in anonymous volumes. Ensure you back up any important data separately.
- The script assumes the Docker socket is accessible and the user has sufficient permissions to interact with it.

## Contributing
- Contributions are welcome! Feel free to submit pull requests to improve this repository.

## License
This project is licensed under the **GNU General Public License v3.0**. See the LICENSE file for details.
