#!/bin/bash

# Get the host's IP address and network information
HOST_IP=$(ip route get 1 | awk '{print $7;exit}')
HOST_SUBNET=$(ip -o -f inet addr show | grep $HOST_IP | awk '{print $4}')
HOST_GATEWAY=$(ip route | grep default | awk '{print $3}')
HOST_DNS=$(grep nameserver /etc/resolv.conf | awk '{print $2}' | head -1)

echo "Host IP: $HOST_IP"
echo "Host Subnet: $HOST_SUBNET"
echo "Host Gateway: $HOST_GATEWAY"
echo "Host DNS: $HOST_DNS"

# Determine a suitable subnet for Docker network
# Use 172.20.0.0/16 if it doesn't conflict with host network
DOCKER_SUBNET="172.20.0.0/16"
DOCKER_GATEWAY="172.20.0.1"

# Check if the host subnet conflicts with our Docker subnet
if [[ $HOST_SUBNET == 172.20.* ]]; then
  # If there's a conflict, use an alternative subnet
  DOCKER_SUBNET="192.168.100.0/16"
  DOCKER_GATEWAY="192.168.100.1"
fi

# Update docker-compose.yml with the determined network settings
sed -i "s|- subnet: .*|- subnet: $DOCKER_SUBNET|g" docker-compose.yml
sed -i "s|gateway: .*|gateway: $DOCKER_GATEWAY|g" docker-compose.yml

echo "Docker network configured with subnet: $DOCKER_SUBNET and gateway: $DOCKER_GATEWAY"

# Make sure the script has execute permissions
chmod +x $0 