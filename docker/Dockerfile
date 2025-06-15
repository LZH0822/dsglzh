FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Shanghai

RUN apt-get update && \
    apt-get install -y software-properties-common curl openssh-client python3 python3-pip sshpass iputils-ping net-tools && \
    apt-add-repository --yes --update ppa:ansible/ansible && \
    apt-get install -y ansible && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Ansible hosts will be mounted as a volume

CMD ["bash"] 