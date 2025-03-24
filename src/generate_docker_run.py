import docker
import os

def generate_docker_volume_create_commands(client):
    """Generate docker volume create commands for all named and CIFS volumes."""
    volumes = client.volumes.list()
    commands = []

    for volume in volumes:
        volume_name = volume.name
        driver = volume.attrs['Driver']
        options = volume.attrs.get('Options', {})

        # Build the docker volume create command
        command = f"docker volume create --name {volume_name} --driver {driver}"

        # Add driver options if available
        if options:
            for key, value in options.items():
                command += f" --opt {key}={value}"

        commands.append(command)

    return commands


def generate_docker_network_create_commands(client):
    """Generate docker network create commands for all custom networks."""
    networks = client.networks.list()
    commands = []

    for network in networks:
        if network.name in ["bridge", "host", "none"]:
            # Skip default networks
            continue

        network_name = network.name
        driver = network.attrs['Driver']
        options = network.attrs.get('Options', {})
        ipam_config = network.attrs.get('IPAM', {}).get('Config', [])

        # Build the docker network create command
        command = f"docker network create --driver {driver} {network_name}"

        # Add driver options if available
        if options:
            for key, value in options.items():
                command += f" --opt {key}={value}"

        # Add IPAM configuration if available
        for config in ipam_config:
            if 'Subnet' in config:
                command += f" --subnet {config['Subnet']}"
            if 'Gateway' in config:
                command += f" --gateway {config['Gateway']}"

        commands.append(command)

    return commands


def generate_docker_run_commands(client):
    """Generate docker run commands for all running containers."""
    containers = client.containers.list()
    commands = []

    for container in containers:
        container_info = container.attrs
        name = container_info['Name'].lstrip('/')
        image = container_info['Config']['Image']
        env_vars = container_info['Config']['Env']
        volumes = container_info['Mounts']
        devices = container_info.get('HostConfig', {}).get('Devices', [])
        user = container_info['Config'].get('User', '')
        restart_policy = container_info['HostConfig']['RestartPolicy'].get('Name', '')
        network_mode = container_info['HostConfig']['NetworkMode']
        hostname = container_info['Config'].get('Hostname', '')
        dns = container_info['HostConfig'].get('Dns', [])
        shm_size = container_info['HostConfig'].get('ShmSize', 0)
        cpus = container_info['HostConfig'].get('NanoCpus', 0) / 1e9  # Convert NanoCpus to CPUs

        # Build the docker run command
        command = f"docker run -d --name {name} --hostname {hostname}"

        # Add environment variables
        if env_vars:
            for env in env_vars:
                command += f" -e {env}"

        # Add volumes
        if volumes:
            for volume in volumes:
                command += f" -v {volume['Source']}:{volume['Destination']}"

        # Add devices
        if devices:
            for device in devices:
                command += f" --device {device['PathOnHost']}:{device['PathInContainer']}"

        # Add user
        if user:
            command += f" -u {user}"

        # Add restart policy
        if restart_policy:
            command += f" --restart {restart_policy}"

        # Handle network mode
        if network_mode.startswith("container:"):
            # Extract the container ID and get its name
            network_container_id = network_mode.split(":")[1]
            try:
                network_container = client.containers.get(network_container_id)
                network_container_name = network_container.name
                command += f" --network container:{network_container_name}"
            except docker.errors.NotFound:
                command += f" --network container:{network_container_id}"  # Fallback to container ID
        else:
            # Add network (if available)
            networks = container_info['NetworkSettings']['Networks']
            if networks:
                network = list(networks.keys())[0]  # Get the first network
                command += f" --network {network}"

        # Add DNS
        if dns:
            for dns_entry in dns:
                command += f" --dns {dns_entry}"

        # Add shared memory size if greater than 64MB
        if shm_size > 64 * 1024 * 1024:  # 64MB in bytes
            command += f" --shm-size {shm_size // (1024 * 1024)}m"

        # Add CPU limits if not using all CPUs
        if cpus > 0:
            command += f" --cpus {cpus:.2f}"

        # Add image
        command += f" {image}"

        commands.append(command)

    return commands


if __name__ == "__main__":
    client = docker.DockerClient(base_url='unix://var/run/docker.sock')

    # Generate volume create commands
    volume_commands = generate_docker_volume_create_commands(client)

    # Generate network create commands
    network_commands = generate_docker_network_create_commands(client)

    # Generate run commands
    run_commands = generate_docker_run_commands(client)

    # Combine all commands
    all_commands = volume_commands + network_commands + run_commands

    # Write the commands to the output file
    output_file = "/output/docker_commands.sh"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, "w") as f:
        for cmd in all_commands:
            f.write(cmd + "\n")

    print(f"Docker commands have been written to {output_file}")
