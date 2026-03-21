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

run_cmd() {
  echo "$*"
  "$@"
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

echo "All checks passed!"
