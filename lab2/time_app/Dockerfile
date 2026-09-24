FROM python:3.11-slim

RUN groupadd -g 799 nyu && \
    useradd -r -u 999 -g nyu nyu

WORKDIR /app

RUN pip install --no-cache-dir Flask

COPY --chown=nyu:nyu . .

USER nyu

CMD ["python", "./run.py"]