#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "$0")/.." && pwd)
docker build -f "$ROOT/docker/Dockerfile" -t easymongo:2.2610.0 "$ROOT"
