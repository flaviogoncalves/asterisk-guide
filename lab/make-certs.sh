#!/usr/bin/env bash
# Generate a self-signed TLS cert for the Asterisk HTTP server (WebRTC / WSS).
# Browsers will warn on the self-signed cert — accept it for the lab, or use a
# real (Let's Encrypt) cert in production.
set -euo pipefail
cd "$(dirname "$0")/asterisk/etc"
mkdir -p keys
if [ -f keys/asterisk.crt ]; then echo "keys/asterisk.crt already exists — skipping"; exit 0; fi

# CN=localhost + SANs so wss://localhost:8089 works; add your LAN IP if needed.
openssl req -x509 -newkey rsa:2048 -nodes \
  -keyout keys/asterisk.key -out keys/asterisk.crt \
  -days 825 -subj "/CN=localhost/O=Astbook Lab" \
  -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"
chmod 600 keys/asterisk.key
echo "Generated keys/asterisk.crt and keys/asterisk.key"
