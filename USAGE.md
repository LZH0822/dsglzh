# Docker Ansible Dashboard - Usage Guide

This document provides detailed instructions on how to use the Docker Ansible Dashboard.

## Initial Setup

1. Make sure you have SSH key authentication set up for your target hosts:
   ```
   ssh-keygen -t rsa  # If you don't have an SSH key
   ssh-copy-id root@192.168.31.201
   ssh-copy-id root@192.168.31.202
   ```

2. Run the setup script to configure the network and start the containers:
   ```
   cd docker-ansible-dashboard
   ./setup.sh
   ```

3. Verify connectivity between containers and hosts:
   ```
   ./check_connectivity.sh
   ```

## Accessing the Dashboard

Open your web browser and navigate to `http://YOUR_SERVER_IP` (where YOUR_SERVER_IP is the IP address of your server).

## Dashboard Features

### System Status

The top section of the dashboard shows:
- Total number of hosts
- Number of online hosts
- Number of offline hosts
- Progress bar showing the percentage of online/offline hosts

### Resource Usage

The resource usage chart displays:
- CPU cores per host
- Memory usage per host
- Disk usage per host

### Host Status Table

The host status table shows detailed information about each host:
- Hostname
- IP address
- Online/offline status
- Operating system
- CPU cores
- Memory (MB)
- Disk space (GB)
- Uptime (hours)
- Actions (edit/delete)

### Host Cards

Each host has a card displaying:
- Hostname and IP
- Status (online/offline)
- System information
- Edit and delete buttons

## Managing Hosts

### Adding a Host

1. Click the "Add Host" button in the top right corner
2. Enter the hostname, IP address, and username
3. Click "Save Host"

### Editing a Host

1. Click the edit button (pencil icon) on a host card or in the host table
2. Modify the hostname, IP address, or username
3. Click "Update Host"

### Deleting a Host

1. Click the delete button (trash icon) on a host card or in the host table
2. Confirm the deletion when prompted

## Troubleshooting

### Dashboard Not Loading

If the dashboard doesn't load:
1. Check if the containers are running:
   ```
   docker ps
   ```
2. Check container logs:
   ```
   docker-compose logs
   ```

### Hosts Not Showing Up

If hosts are not appearing in the dashboard:
1. Verify the Ansible hosts file:
   ```
   cat ansible/hosts
   ```
2. Check SSH connectivity:
   ```
   ssh root@192.168.31.201
   ```
3. Test Ansible connectivity:
   ```
   docker exec -it docker-ansible-dashboard_ansible_1 ansible all -m ping
   ```

### Network Issues

If containers can't communicate with each other or with the hosts:
1. Run the network configuration script again:
   ```
   ./network_config.sh
   ```
2. Restart the containers:
   ```
   docker-compose down
   docker-compose up -d
   ``` 