# Make sure you have Docker/Podman first
cargo install cross
rustup target add i686-unknown-linux-gnu
cross build --target i686-unknown-linux-gnu
cross test --target i686-unknown-linux-gnu