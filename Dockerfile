FROM ubuntu:23.04 AS builder

WORKDIR /app

# make sure we use the venv
ENV PATH="/venv/bin:$PATH"

RUN apt-get update && apt-get install -y --no-install-recommends build-essential gcc git python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

# setup venv
RUN python3 -m venv /venv

COPY songbirdcli/requirements.txt .

# install dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -U git+https://github.com/cboin1996/songbirdcore@main \
    pip install --no-cache-dir -U git+https://github.com/cboin1996/requests-html@dev

FROM ubuntu:23.04 as build-image

ENV PATH="/venv/bin:$PATH"

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg python3-pip \
    # playwright deps
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libatspi2.0-0 \
    libxcomposite1 \
    libxdamage1 && \
    # clear cache
    rm -rf /var/lib/apt/lists/*

# copy venv
COPY --from=builder /venv /venv
# copy app contents 
COPY ./songbirdcli/ ./songbirdcli
COPY pyproject.toml .

# install package locally, and setup playwright
RUN pip install . && playwright install chromium

CMD ["python3", "songbirdcli/cli.py"]
