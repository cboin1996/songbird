FROM ubuntu:20.04
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
  ffmpeg \
  git \
  python3.10 \
  python3-pip \
  && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

RUN useradd --create-home appuser
USER appuser
WORKDIR /app

COPY --chown=appuser:appuser app/requirements.txt requirements.txt
RUN pip install --user -r requirements.txt

ENV PATH="/home/worker/.local/bin:${PATH}"
COPY --chown=appuser:appuser app .
ENTRYPOINT ["python3", "main.py"]