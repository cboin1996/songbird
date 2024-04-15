FROM python:3.11-slim AS builder

WORKDIR /app

# make sure we use the venv
ENV PATH="/venv/bin:$PATH"

RUN apt-get update && apt-get install -y --no-install-recommends build-essential gcc git && \
    rm -rf /var/lib/apt/lists/*

# setup venv
RUN python -m venv /venv

COPY songbirdcli/requirements.txt .

# install dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -U git+https://github.com/cboin1996/songbirdcore@main

FROM python:3.11-slim as build-image

ENV PATH="/venv/bin:$PATH"

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg chromium && \
    rm -rf /var/lib/apt/lists/*

# copy venv
COPY --from=builder /venv /venv
# copy app contents 
COPY ./songbirdcli/ ./songbirdcli
COPY pyproject.toml .
# install package locally
RUN pip install .

# used for caching chromium across docker runs
ENV PATH="/root/.local/bin:${PATH}"
CMD ["python3", "songbirdcli/cli.py"]
