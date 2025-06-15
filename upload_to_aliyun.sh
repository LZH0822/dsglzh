#!/bin/bash

# 上传 Docker 镜像到阿里云容器镜像服务
# 使用方法: ./upload_to_aliyun.sh [阿里云镜像仓库命名空间] [阿里云镜像仓库地址]
# 例如: ./upload_to_aliyun.sh myproject registry.cn-hangzhou.aliyuncs.com

echo "开始上传 Docker 镜像到阿里云..."

# 检查参数
NAMESPACE=${1:-"ansible-dashboard"}
REGISTRY=${2:-"registry.cn-hangzhou.aliyuncs.com"}

# 确保我们在正确的目录
cd "$(dirname "$0")"

# 检查 Docker 是否运行
if ! docker info > /dev/null 2>&1; then
  echo "错误: Docker 未运行，请先启动 Docker"
  exit 1
fi

# 检查是否已登录阿里云
echo "请确保您已登录阿里云容器镜像服务:"
echo "docker login --username=您的阿里云账号 ${REGISTRY}"
echo ""
read -p "是否已登录? (y/n): " LOGGED_IN
if [ "$LOGGED_IN" != "y" ]; then
  echo "请先登录阿里云容器镜像服务后再运行此脚本"
  exit 1
fi

# 构建镜像（如果尚未构建）
echo "构建本地镜像..."
docker-compose build

# 获取镜像列表
IMAGES=(
  "docker-ansible-dashboard_ansible"
  "docker-ansible-dashboard_backend"
  "docker-ansible-dashboard_frontend"
)

# 为每个镜像添加标签并推送到阿里云
echo "开始上传镜像到阿里云..."
for IMAGE in "${IMAGES[@]}"; do
  # 从镜像名称中提取服务名称
  SERVICE=$(echo $IMAGE | sed 's/docker-ansible-dashboard_//')
  
  # 添加阿里云镜像标签
  ALIYUN_IMAGE="${REGISTRY}/${NAMESPACE}/${SERVICE}:latest"
  echo "为 ${IMAGE} 添加标签: ${ALIYUN_IMAGE}"
  docker tag ${IMAGE} ${ALIYUN_IMAGE}
  
  # 推送到阿里云
  echo "推送 ${ALIYUN_IMAGE} 到阿里云..."
  docker push ${ALIYUN_IMAGE}
  
  if [ $? -eq 0 ]; then
    echo "✅ ${SERVICE} 镜像上传成功"
  else
    echo "❌ ${SERVICE} 镜像上传失败"
  fi
  echo ""
done

echo "镜像上传完成！"
echo ""
echo "使用以下命令从阿里云拉取镜像:"
for IMAGE in "${IMAGES[@]}"; do
  SERVICE=$(echo $IMAGE | sed 's/docker-ansible-dashboard_//')
  echo "docker pull ${REGISTRY}/${NAMESPACE}/${SERVICE}:latest"
done

echo ""
echo "更新 docker-compose.yml 文件中的镜像引用，替换为阿里云镜像地址"
echo "例如:"
echo "  ansible:"
echo "    image: ${REGISTRY}/${NAMESPACE}/ansible:latest" 