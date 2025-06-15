#!/bin/bash

echo "Checking container connectivity..."

# Check if containers are running
if ! docker ps | grep -q ansible; then
    echo "Error: Containers are not running. Please run setup.sh first."
    exit 1
fi

# Check container to container connectivity
echo -e "\n=== Container to Container Connectivity ==="
echo "backend -> ansible:"
docker exec docker-ansible-dashboard_backend_1 ping -c 2 ansible
echo "frontend -> backend:"
docker exec docker-ansible-dashboard_frontend_1 ping -c 2 backend

# Check container to host connectivity
echo -e "\n=== Container to Host Connectivity ==="
echo "ansible -> 192.168.31.201 (host02):"
docker exec docker-ansible-dashboard_ansible_1 ping -c 2 192.168.31.201
echo "ansible -> 192.168.31.202 (host03):"
docker exec docker-ansible-dashboard_ansible_1 ping -c 2 192.168.31.202

# Check Ansible connectivity
echo -e "\n=== Ansible Connectivity ==="
echo "Running ansible ping module:"
docker exec docker-ansible-dashboard_ansible_1 ansible all -m ping

echo -e "\nConnectivity check complete!" 