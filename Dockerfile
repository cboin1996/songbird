FROM ubuntu:20.04
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
  ffmpeg \
  git \
  python3.10 \
  python3-pip \
  && rm -rf /var/lib/apt/lists/* \
  && pip install --upgrade pip


WORKDIR /app
COPY app/requirements.txt .
ENV PATH="/root/.local/bin:${PATH}"
RUN pip install -r requirements.txt
COPY app .


ENTRYPOINT ["python3", "main.py"]