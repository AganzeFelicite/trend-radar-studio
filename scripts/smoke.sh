#!/usr/bin/env bash
# Smoke test: every service answers. Run after `docker compose up -d --build`.
set -euo pipefail
get() { curl -fsS --retry 15 --retry-connrefused --retry-all-errors --retry-delay 2 "$1"; }

api=$(get http://127.0.0.1:8400/health)
echo "api      $api"
jq -e '.status == "ok" and .workers >= 1' <<<"$api" >/dev/null || { echo "FAIL: api unhealthy or no worker"; exit 1; }

echo "renderer $(get http://127.0.0.1:3500/health)"
get http://127.0.0.1:3400/ | grep -q 'id="api-status">ok<' || { echo "FAIL: admin can't see api"; exit 1; }
echo "admin    ok (sees api)"
echo "ALL OK"
