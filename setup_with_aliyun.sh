#!/bin/bash

echo "使用阿里云镜像设置 Docker Ansible Dashboard..."

# 确保我们在正确的目录
cd "$(dirname "$0")"

# 检查 Docker 是否运行
if ! docker info > /dev/null 2>&1; then
  echo "错误: Docker 未运行，请先启动 Docker"
  exit 1
fi

# 检查是否已登录阿里云
echo "请确保您已登录阿里云容器镜像服务:"
echo "docker login --username=您的阿里云账号 registry.cn-hangzhou.aliyuncs.com"
echo ""
read -p "是否已登录? (y/n): " LOGGED_IN
if [ "$LOGGED_IN" != "y" ]; then
  echo "请先登录阿里云容器镜像服务后再运行此脚本"
  exit 1
fi

# 检查 SSH 密钥
if [ ! -f ~/.ssh/id_rsa ]; then
    echo "SSH 密钥不存在，正在创建..."
    ssh-keygen -t rsa -N "" -f ~/.ssh/id_rsa
    echo "SSH 密钥已创建"
fi

# 运行网络配置脚本
echo "配置网络..."
chmod +x network_config.sh
./network_config.sh

# 从阿里云拉取镜像
echo "从阿里云拉取镜像..."
docker pull registry.cn-hangzhou.aliyuncs.com/ansible-dashboard/ansible:latest
docker pull registry.cn-hangzhou.aliyuncs.com/ansible-dashboard/backend:latest
docker pull registry.cn-hangzhou.aliyuncs.com/ansible-dashboard/frontend:latest

# 使用阿里云镜像启动容器
echo "启动容器..."
docker-compose -f docker-compose-aliyun.yml up -d

# 获取主机 IP 以便访问
HOST_IP=$(ip route get 1 | awk '{print $7;exit}')

echo "安装完成！"
echo "访问数据大屏: http://$HOST_IP"
echo ""
echo "别忘了为目标主机设置 SSH 密钥认证:"
echo "ssh-copy-id root@192.168.31.201"
echo "ssh-copy-id root@192.168.31.202" 