FROM restic/restic:0.19.1

RUN apk add --no-cache python3 docker-cli

WORKDIR /app
COPY src/ .

ENTRYPOINT ["python3", "-u", "/app/run.py"]
