# Cross Compilation Tutorial

Cross compilation allows you to build and test for platforms other than your current OS.

While most cross-compilation is handled by automated checks, you might want to do it while writing new code.

## Supported Platforms

Most repositories using this template target the following:

- **Linux**: x86_64, i686 (native), aarch64, armv7 (cross-compiled)
- **Windows**: x86_64, i686 (MSVC toolchain)
- **macOS**: x86_64 (Intel), aarch64 (Apple Silicon)

!!! info "Extended Targets"
    See [Automated Testing & Publishing](automated-testing-publishing.md#cross-platform-testing) for detailed testing workflows and extended target options.

## Cross Compilation with Cross

!!! tip "The `cross` tool provides easy cross-compilation for Rust projects using Docker or Podman containers."

### Installation

**Install globally (one-time setup):**

```bash
cargo install cross --git https://github.com/cross-rs/cross
```

!!! info "Docker/Podman Required"
    `cross` requires Docker or Podman to be installed and running for cross-compilation.

### Basic Usage

Simply replace `cargo` with `cross`:

```bash
cross build --target x86_64-pc-windows-gnu
# Windows on Linux or macOS
cross test --target x86_64-pc-windows-gnu --release
# How about something close to the GameCube?
cross test --target powerpc-unknown-linux-gnu --release
```

!!! warning "Try Release Builds"
    For some targets, debug builds may have compilation issues with `cross`.

    Use `--release` whenever possible.

## Testing with Wine on Linux

!!! info "Users on Linux can test Windows binaries by using Wine for local testing."

You can use either:

- Your local Wine installation
- `cross`, which uses a Docker image

!!! tip
    If you encounter a bug with WINE, it's recommended to test with the latest Wine on your local system before reporting bugs to WineHQ.

### Testing on Wine with Cross

`cross` can be used to test with Wine.

```bash
# Test Windows binaries on Linux using cross
cross test --target x86_64-pc-windows-gnu --release
cross test --target i686-pc-windows-gnu --release
```

### Testing on Wine with Cargo

The WINE in `cross` may sometimes be a bit out of date.

You'll need MinGW for cross compilation and WINE for running the tests.

The tests will run in your local WINE installation.

=== "Arch Linux"

    ```bash
    # Install Wine for running and MinGW for cross compilation
    sudo pacman -S wine mingw-w64-gcc

    # Add Windows target (or equivalent for your setup)
    rustup target add x86_64-pc-windows-gnu

    # Test Windows binaries on Linux using cargo
    cargo test --target x86_64-pc-windows-gnu --release
    ```

=== "NixOS"

    Use this flake I made: [rust-windows-gnu-helper-flake](https://github.com/Sewer56/rust-windows-gnu-helper-flake)

    1. Enable binfmt

        ```nix
        # Add to configuration.nix
        boot.binfmt.emulatedSystems = [ "x86_64-windows" "i686-windows" ];
        ```

    2. Install Windows targets

        ```bash
        # Can also be sourced from rust-overlay, etc.
        rustup target add x86_64-pc-windows-gnu i686-pc-windows-gnu
        ```

    3. Integrate flake with your flake

        ```nix
        {
          inputs = {
            nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
            flake-utils.url = "github:numtide/flake-utils";
            helper.url = "github:Sewer56/rust-windows-gnu-helper-flake";
          };

          outputs = { self, nixpkgs, flake-utils, helper, ... }:
            flake-utils.lib.eachDefaultSystem (system: let
              pkgs = import nixpkgs { inherit system; };
            in {
              devShells.default = pkgs.mkShell ({
                packages = [ /* your packages */ ] ++ (helper.lib.winGnuPackages pkgs);
              } // (helper.lib.winGnuEnv pkgs));
            });
        }
        ```

    4. Run tests

    ```bash
    nix develop
    cargo test --target x86_64-pc-windows-gnu --release
    ```

        !!! warning "i686 Target Broken"
            The i686-pc-windows-gnu target is currently broken until nixpkgs [PR #367564](https://github.com/NixOS/nixpkgs/pull/367564) is merged.

When Wine testing is enabled during template generation, these tests also run automatically in CI/CD.

## Automated Testing

!!! info "The provided workflows automatically build and test your library across all supported platforms."

![PR Checks](../assets/pr-checks.avif)
/// caption
Automated cross-platform checks running during pull requests
///

Cross-compilations are also tested as part of automated testing.

See [Automated Testing & Publishing](automated-testing-publishing.md) for detailed workflows and customization options.
