FROM python:3.9

WORKDIR /app

RUN openssl req -new -newkey rsa:4096 -days 365 -nodes -x509 \
    -subj "/C=US/ST=NY/L=NY/O=citinno/CN=ec2-3-238-222-58.compute-1.amazonaws.com" \
    -keyout key.key \
    -out cert.cert

COPY requirements.txt ./
RUN pip install -U pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . ./

ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--ssl-keyfile", "/app/key.key", "--ssl-certfile", "/app/cert.cert"]
