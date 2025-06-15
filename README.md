# Docker Ansible Dashboard

A data visualization dashboard for Ansible hosts, deployed using Docker containers.

## Features

- Docker deployment with automatic network configuration
- Ansible host monitoring with ping status
- System information collection and visualization
- Host management (add, edit, delete)
- Beautiful data visualization dashboard
- Responsive design

## Requirements

- Docker and Docker Compose
- SSH access to target hosts
- SSH key authentication set up

## Quick Start

1. Clone this repository
2. Run the network configuration script:
   ```
   ./network_config.sh
   ```
3. Start the containers:
   ```
   docker-compose up -d
   ```
4. Access the dashboard at http://localhost:80

## Project Structure

```
docker-ansible-dashboard/
├── ansible/
│   └── hosts              # Ansible inventory file
├── backend/
│   ├── app.py             # Flask API for Ansible operations
│   ├── Dockerfile         # Backend container definition
│   └── requirements.txt   # Python dependencies
├── docker/
│   └── Dockerfile         # Ansible container definition
├── frontend/
│   ├── dist/              # Static frontend files
│   ├── Dockerfile         # Frontend container definition
│   └── nginx.conf         # Nginx configuration
├── docker-compose.yml     # Service definitions
├── network_config.sh      # Network auto-configuration script
└── README.md              # This file
```

## Configuration

### Ansible Hosts

Edit the `ansible/hosts` file to add or remove hosts:

```
[hosts]
192.168.31.201 ansible_ssh_host=192.168.31.201 ansible_ssh_user=root hostname=host02
192.168.31.202 ansible_ssh_host=192.168.31.202 ansible_ssh_user=root hostname=host03

[all:vars]
ansible_ssh_private_key_file=/root/.ssh/id_rsa
ansible_python_interpreter=/usr/bin/python3
```

### SSH Keys

Make sure your SSH keys are properly set up:

```
ssh-keygen -t rsa  # If you don't have an SSH key
ssh-copy-id root@192.168.31.201
ssh-copy-id root@192.168.31.202
```

## API Endpoints

- `GET /api/ping` - Ping all hosts
- `GET /api/hosts` - List all hosts
- `POST /api/hosts` - Add a new host
- `PUT /api/hosts/{ip}` - Update a host
- `DELETE /api/hosts/{ip}` - Delete a host
- `GET /api/system-info` - Get system information for all hosts

## Troubleshooting

### Container Networking

If containers can't communicate with each other or with the host network:

1. Check the network configuration:
   ```
   docker network inspect ansible_net
   ```
2. Run the network configuration script again:
   ```
   ./network_config.sh
   ```

### Ansible Connection Issues

If Ansible can't connect to hosts:

1. Verify SSH key authentication:
   ```
   ssh root@192.168.31.201
   ```
2. Check the Ansible hosts file:
   ```
   cat ansible/hosts
   ```
3. Test Ansible connection manually:
   ```
   docker exec -it docker-ansible-dashboard_ansible_1 ansible all -m ping a
   ```

## License

MIT 