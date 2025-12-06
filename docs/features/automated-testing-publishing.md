# Automated Testing & Publishing

Automated testing, publishing, and code quality checks that run when you update your code, ensuring your rust code works across all platforms.

![PR Checks](../assets/pr-checks.avif)
/// caption
Automated checks running on pull requests
///

## Key Features
- **[Cross-platform testing](#cross-platform-testing)**: Linux, Windows, macOS
- **[Automated code coverage](#code-coverage-reports)**: How much of your code is tested? (Codecov)
- **[Semantic version checking](#semantic-version-checks)**: Prevents breaking changes
- **[Tag-based publishing](#publishing-your-library)**: crates.io, NuGet
- **[PGO optimization](#cross-platform-testing)**: Better performance
- **[Wine testing](#testing-on-wine)**: Linux gaming compatibility

## Testing Your Code

### Cross-Platform Testing

!!! info
    Out of the box, the template is configured to test on a variety of platforms:

#### Standard Targets
- **Linux**: x86_64, i686
- **Windows**: x86_64, i686 (MSVC toolchain)
- **macOS**: x86_64 (Intel), aarch64 (Apple Silicon)

#### Optional Extended Targets

!!! tip
    You can opt in to testing on less standard platforms for comprehensive compatibility.
    
    [Reloaded3](https://reloaded-project.github.io/Reloaded-III/) uses extended targets and `no_std` to ensure compatibility with hard platforms like consoles.

<div class="annotate" markdown>

- **Linux**: aarch64, armv7 (ARM variants use cross-compilation)
- **Big Endian & Aligned Memory** (1):
    - powerpc64-unknown-linux-gnu
    - powerpc-unknown-linux-gnu

</div>

1.  Required for mods/code targeting older game consoles

### Testing on Wine

!!! example
    The development of Reloaded helped identify these two Wine bugs through automated testing: [#56357](https://bugs.winehq.org/show_bug.cgi?id=56357) and [#56362](https://bugs.winehq.org/show_bug.cgi?id=56362).
    
    This helps the rest of the modding ecosystem ensure mods run on Linux.

The `test-on-wine` job ensures your code runs correctly inside Wine, which is crucial for low level development; which integrates tightly with the OS.

This is helpful when your code is expected to run in a Windows environment from Linux; such as being part of game mods.

## Code Quality & Coverage

### Code Coverage Reports

!!! info "Track Your Test Coverage"
    See how much of your code is actually tested and find missing test cases.

![Codecov Dashboard](../assets/coverage-codecov.avif)
/// caption
Codecov dashboard provides detailed coverage analytics and trend tracking
///

![Coverage Pills](../assets/coverage-pills.avif)
/// caption
Coverage pills on README.md show project health at a glance - click them to go to the relevant page
///

The default CI configuration collects and uploads coverage reports to Codecov for all supported platforms, showing you which parts of your code need more tests.

#### Excluding Crates from Coverage

!!! tip "When to Exclude Crates"
    You might want to exclude certain crates from coverage when they contain CLI tools or other binaries.

To exclude specific crates from coverage, use the `--workspace --exclude <crate-name>` flags with cargo-tarpaulin:

**GitHub Actions Configuration**
```yaml
- name: Run Tests and Upload Coverage
  uses: Reloaded-Project/devops-rust-test-and-coverage@v1
  with:
    additional-tarpaulin-flags: "--workspace --exclude my-cli-tool"
```

**VS Code Tasks**

Update your `.vscode/tasks.json` to include the exclusion flags:

```diff
{
  "label": "Auto Coverage on Save",
- "command": "cargo install cargo-tarpaulin --quiet && cargo watch -x \"tarpaulin --skip-clean --out Xml --out Html --engine llvm --target-dir target/coverage-build\" -w src/"
+ "command": "cargo install cargo-tarpaulin --quiet && cargo watch -x \"tarpaulin --skip-clean --out Xml --out Html --engine llvm --target-dir target/coverage-build --workspace --exclude my-cli-tool\" -w src/"
}
```

The task automatically runs in the `src/` directory, so you don't need to manually navigate when using VSCode tasks.

### Semantic Version Checks
Automatically checks if your changes might break code for people who use your library. If you make changes that could break other people's code, you'll need to update your version number. This prevents accidental breaking changes from reaching your users.

!!! info "[What is Semantic Versioning?](https://semver.org)"

    Semantic Versioning (SemVer) helps users understand the impact of updates:

    - **MAJOR**: Incompatible changes (1.0.0 → 2.0.0)
    - **MINOR**: New features, backward compatible (1.0.0 → 1.1.0)  
    - **PATCH**: Bug fixes, backward compatible (1.0.0 → 1.0.1)

    For versions < 1.0.0, the project is considered unstable and the minor version may include breaking changes.

    *[Incompatible changes]: Changes that may break things for people using your code, such as:<br/>- Removing or renaming functions<br/>- Changing parameters to a function
    
    *This check is performed using the `cargo-semver-checks` tool.*

### Automated Quality Controls

!!! info "Three quality gates run automatically on pull requests and tagged releases"

- **Documentation**: Verifies `cargo doc` compiles without errors
- **Linter**: Treats `cargo clippy` warnings as errors
- **Formatter**: Ensures code matches `rustfmt` standards

!!! info "When Do These Checks Run?"
    By default, these checks run on **pull requests** and **tagged releases**.

## Publishing Your Library

!!! tip "How to Publish?"
    In order to make a release, you should push a tag that's named after the version, for example `1.0.0` for version `1.0.0`. Do not use a `v` prefix.

### How Publishing Works

When you push a version tag, the CI workflow automatically handles your release process.

### What Gets Published

Depending on your template options, the following may happen:

- **crates.io**: Publishes your Rust library to the official Rust package registry
- **GitHub Release**: Creates a GitHub release with changelog

*Optional features (if enabled):*

- **NuGet**: Publishes .NET bindings for C# developers
- **C/C++ Headers**: Generates header files for cross-language interoperability

All releases are gated by successful tests and quality checks, ensuring only stable code reaches your users.

## Integrate with Non-Template Projects
!!! info
    If your project was not built on Reloaded template, here's how you can recreate the CI workflow parts.

Run the template again with your desired options to generate a customized `rust.yml` file, then copy it to your project:

```bash
cargo generate --git https://github.com/Reloaded-Project/reloaded-templates-rust.git
```

See the [main documentation](../index.md#getting-started) for more details on getting started with `cargo-generate`.