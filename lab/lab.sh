#!/usr/bin/env bash
# Astbook Asterisk 22 lab control + verification helper.
set -euo pipefail
cd "$(dirname "$0")"

COMPOSE="docker compose"

usage() {
  cat <<EOF
Usage: ./lab.sh <command>
  up        build (if needed) and start the lab
  down      stop and remove the lab
  cli       open the Asterisk CLI
  status    show PJSIP endpoints / transports / dialplan
  verify    run the headless SIPp smoke test (call to 9000) and assert success
  logs      tail Asterisk logs
EOF
}

wait_healthy() {
  echo "Waiting for Asterisk to become healthy..."
  for i in $(seq 1 30); do
    if $COMPOSE exec -T asterisk asterisk -rx 'core show version' >/dev/null 2>&1; then
      echo "Asterisk is up: $($COMPOSE exec -T asterisk asterisk -rx 'core show version')"
      return 0
    fi
    sleep 2
  done
  echo "ERROR: Asterisk did not become healthy in time" >&2
  return 1
}

case "${1:-}" in
  up)
    $COMPOSE up -d --build
    wait_healthy
    ;;
  down)    $COMPOSE down ;;
  cli)     $COMPOSE exec asterisk asterisk -rvvv ;;
  status)
    $COMPOSE exec -T asterisk asterisk -rx 'pjsip show endpoints'
    $COMPOSE exec -T asterisk asterisk -rx 'pjsip show transports'
    $COMPOSE exec -T asterisk asterisk -rx 'dialplan show internal'
    ;;
  verify)
    wait_healthy
    echo "== Endpoints =="
    $COMPOSE exec -T asterisk asterisk -rx 'pjsip show endpoints'
    echo "== Placing SIPp call to extension 9000 =="
    # exec into the already-running sipp container (compose run would clash on the static IP).
    # one call, stop on success; non-zero exit if the call fails
    $COMPOSE exec -T sipp \
      sipp -sf /sipp/uac_9000.xml 172.30.0.10:5060 \
           -m 1 -r 1 -timeout 20s -trace_err \
           -nostdin >/tmp/sipp.out 2>&1 && rc=0 || rc=$?
    cat /tmp/sipp.out 2>/dev/null || true
    if [ "${rc:-1}" -eq 0 ]; then
      echo "VERIFY: PASS — call to 9000 completed (200 OK)."
    else
      echo "VERIFY: FAIL — SIPp exit $rc" >&2
      exit 1
    fi
    ;;
  logs)    $COMPOSE exec asterisk tail -f /var/log/asterisk/full ;;
  *)       usage; exit 1 ;;
esac
