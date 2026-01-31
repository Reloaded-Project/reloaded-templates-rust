# Post-change verification script
# All steps must pass without warnings
# Keep in sync with verify.sh

$ErrorActionPreference = "Stop"

Write-Host "Building..."
cargo build --workspace --all-features --all-targets --quiet

Write-Host "Testing..."
cargo test --workspace --all-features --quiet

Write-Host "Clippy..."
cargo clippy --workspace --all-features --quiet -- -D warnings

Write-Host "Docs..."
$env:RUSTDOCFLAGS = "-D warnings"
cargo doc --workspace --all-features --no-deps --document-private-items --quiet

Write-Host "Formatting..."
cargo fmt --all

Write-Host "Publish dry-run..."
cargo publish --dry-run --allow-dirty --quiet --workspace

Write-Host "All checks passed!"
