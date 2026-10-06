FROM restic/restic:0.19.1

RUN apk add --no-cache python3

WORKDIR /app
COPY run.py .

ENTRYPOINT ["python3", "-u", "/app/run.py"]
