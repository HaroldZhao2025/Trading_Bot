#!/usr/bin/env bash
set -euo pipefail

if [[ $# -gt 0 ]]; then
  exec "$@"
fi

CONFIG="${FT_CONFIG:-/freqtrade/config/config.json}"
STRATEGY="${FT_STRATEGY:-GridSimple}"
CMD="${FT_CMD:-trade}"

export FT_USERDATA_DIR="/freqtrade/user_data"

DATA_DIR="${DATA_DIR:-$FT_USERDATA_DIR/runtime}"
mkdir -p "$DATA_DIR"

if [[ "$CMD" == "arb-scan" ]]; then
  exec python -m olares.main arb-scan
fi

if [[ "${DISABLE_TRADING:-0}" == "1" ]]; then
  echo "DISABLE_TRADING=1 -> forcing dry_run"
  exec python -m freqtrade.main "$CMD" -c "$CONFIG" -s "$STRATEGY" --dry-run
fi

exec python -m freqtrade.main "$CMD" -c "$CONFIG" -s "$STRATEGY"