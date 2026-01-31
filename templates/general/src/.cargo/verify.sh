#!/usr/bin/env bash
# Post-change verification script
# All steps must pass without warnings
# Keep in sync with verify.ps1

set -e

echo "Building..."
cargo build --workspace --all-features --all-targets --quiet

echo "Testing..."
cargo test --workspace --all-features --quiet

echo "Clippy..."
cargo clippy --workspace --all-features --quiet -- -D warnings

echo "Docs..."
RUSTDOCFLAGS="-D warnings" cargo doc --workspace --all-features --no-deps --document-private-items --quiet

echo "Formatting..."
cargo fmt --all

echo "Publish dry-run..."
cargo publish --dry-run --allow-dirty --quiet --workspace

echo "All checks passed!"
