FROM alpine:edge

WORKDIR /app

RUN apk add --update py3-pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 80

CMD ["python3", "server.py"]