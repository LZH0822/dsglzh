FROM python:3.8-slim

WORKDIR /app

RUN apt-get update && apt-get install -y openssh-client && mkdir -p /etc/ansible

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"] 