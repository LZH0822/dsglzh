#!/bin/bash

echo "Setting up Docker Ansible Dashboard..."

# Make sure we're in the right directory
cd "$(dirname "$0")"

# Check if SSH key exists, if not create one
if [ ! -f ~/.ssh/id_rsa ]; then
    echo "SSH key not found. Creating one..."
    ssh-keygen -t rsa -N "" -f ~/.ssh/id_rsa
    echo "SSH key created."
fi

# Run network configuration script
echo "Configuring network..."
chmod +x network_config.sh
./network_config.sh

# Build and start containers
echo "Building and starting containers..."
docker-compose build
docker-compose up -d

# Get host IP for access
HOST_IP=$(ip route get 1 | awk '{print $7;exit}')

echo "Setup complete!"
echo "Access the dashboard at http://$HOST_IP"
echo ""
echo "Don't forget to set up SSH key authentication to your target hosts:"
echo "ssh-copy-id root@192.168.31.201"
echo "ssh-copy-id root@192.168.31.202" 