#!/usr/bin/env bash
# Post-change verification script
# All steps must pass without warnings
# Keep in sync with verify.ps1

set -e

ORIGINAL_DIR="$(pwd)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

trap 'cd "$ORIGINAL_DIR"' EXIT

EXIT_CODE=0
FAILED_COMMANDS=()

run_cmd() {
  echo "$*"

  if "$@"; then
    return 0
  fi

  local status=$?
  printf 'Command failed with exit code %s: %s\n' "$status" "$*" >&2
  FAILED_COMMANDS+=("$*")
  if [ "$EXIT_CODE" -eq 0 ]; then
    EXIT_CODE=$status
  fi

  return 0
}

echo "Building..."
run_cmd cargo build --workspace --all-features --all-targets --quiet

echo "Testing..."
run_cmd cargo test --workspace --all-features --quiet

echo "Clippy..."
run_cmd cargo clippy --workspace --all-features --quiet -- -D warnings

echo "Docs..."
run_cmd env RUSTDOCFLAGS="-D warnings" cargo doc --workspace --all-features --no-deps --document-private-items --quiet

echo "Formatting..."
run_cmd cargo fmt --all --quiet

echo "Publish dry-run..."
run_cmd cargo publish --dry-run --allow-dirty --quiet --workspace

if [ "$EXIT_CODE" -eq 0 ]; then
  echo "All checks passed!"
else
  echo "Verification failed."
  echo "Failed commands:"
  printf ' - %s\n' "${FAILED_COMMANDS[@]}"
fi

exit "$EXIT_CODE"
