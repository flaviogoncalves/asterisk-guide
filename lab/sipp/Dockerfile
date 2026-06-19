# SIPp test driver (headless call generation/verification).
FROM debian:12-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends sip-tester \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /sipp
COPY . /sipp
# kept alive so the lab can `exec`/`run` scenarios on demand
CMD ["sleep", "infinity"]
