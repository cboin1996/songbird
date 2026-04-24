ARG UBUNTU_VERSION="24.04"
FROM ubuntu:${UBUNTU_VERSION} AS builder

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

RUN apt-get update && apt-get install -y --no-install-recommends build-essential gcc git python3 && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./
COPY ./songbirdcli/ ./songbirdcli

# install dependencies
RUN uv sync --frozen --no-dev

FROM ubuntu:${UBUNTU_VERSION} AS build-image

ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates curl unzip ffmpeg python3 \
    # playwright deps
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libatspi2.0-0 \
    libxcomposite1 \
    libxdamage1 && \
    # install deno for yt-dlp youtube extraction
    curl -fsSL "https://github.com/denoland/deno/releases/latest/download/deno-x86_64-unknown-linux-gnu.zip" -o /tmp/deno.zip && \
    unzip /tmp/deno.zip -d /usr/local/bin && \
    rm /tmp/deno.zip && \
    # clear cache
    rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
# copy venv
COPY --from=builder /app/.venv /app/.venv
# copy app contents
COPY ./songbirdcli/ ./songbirdcli
COPY pyproject.toml uv.lock .

# setup playwright
RUN playwright install chromium && deno --help

CMD ["python3", "songbirdcli/cli.py"]

# RUN tests to confirm built code runs as expected
FROM build-image AS test

RUN uv sync --frozen --extra dev
COPY tests ./tests

WORKDIR /app
RUN ENV=dev pytest ./tests/unit/
