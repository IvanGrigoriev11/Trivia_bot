# syntax=docker/dockerfile:1

FROM python:3.10-slim-buster

WORKDIR /src

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY src .

CMD ["python", "main.py", "server", "https://ec2-3-19-61-96.us-east-2.compute.amazonaws.com/handleUpdate",
"0.0.0.0", "443", "--cert-path", "/home/ubuntu/keys/cert.pem", "--key-path", "/home/ubuntu/keys/key.key", "--inmemory"]