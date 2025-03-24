import docker
import os

def generate_docker_run_commands():
    client = docker.DockerClient(base_url='unix://var/run/docker.sock')
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

        # Add image
        command += f" {image}"

        commands.append(command)

    return commands


if __name__ == "__main__":
    commands = generate_docker_run_commands()
    output_file = "/output/docker_run_commands.sh"

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Write the commands to a file
    with open(output_file, "w") as f:
        for cmd in commands:
            f.write(cmd + "\n")

    print(f"Docker run commands have been written to {output_file}")
