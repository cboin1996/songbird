FROM ubuntu:20.04
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
  git \
  python3.10 \
  python3-pip \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --upgrade pip && pip3 install -r requirements.txt

WORKDIR /app

RUN useradd --create-home appuser
USER appuser
ENTRYPOINT ["python3", "main.py"]