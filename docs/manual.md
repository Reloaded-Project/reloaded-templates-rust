# Template Manual

This guide walks you through common development tasks-from getting started to advanced optimization-with links to detailed documentation as needed.

## Prerequisites

### Install Rust

!!! tip "If you don't have Rust installed, follow the instructions for your operating system"

=== "Windows"

    Download and run the installer from [rustup.rs](https://rustup.rs/).

    Alternatively, install via Chocolatey or Scoop:

    ```powershell
    choco install rust  # Chocolatey
    scoop install rustup  # Scoop
    ```

=== "Linux & macOS"

    Run the installer script:

    ```bash
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
    ```

### Code Editor Setup

#### VSCode

Install these recommended extensions:

- [rust-analyzer](https://marketplace.visualstudio.com/items?itemName=rust-lang.rust-analyzer) - Rust language server for IDE features
- [Coverage Gutters](https://marketplace.visualstudio.com/items?itemName=ryanluker.vscode-coverage-gutters) - Visualize code coverage in your editor
- [Crates](https://marketplace.visualstudio.com/items?itemName=serayuzgur.crates) - Manage crate dependencies and versions

VSCode will prompt you to install these when you open the project, or install manually via the Extensions panel (`Ctrl+Shift+X`).

## What are you editing?

Choose what you want to work on:

- [Editing Code](#editing-code) - Build, run, test, optimize, and create bindings
- [Editing Documentation](#editing-documentation) - Write and preview docs

## Editing Code

!!! note "Optional Features"

    Some features below (e.g. `benchmarks`, `fuzzing`, `bindings`) are only included in certain project configurations.<br/>
    You can use the `Integrate with Non-Template Projects` section(s) under the `Features` pages to add them to an existing project.

Open the `src` folder in your code editor for source development.

**For CLI users:** All commands below assume you're in the `src` directory.

### How to Build

**Using VSCode:**

Press `Ctrl+Shift+B` to open the build task menu. Select `rust: cargo build`.

**From Command Line:**

```bash
cd src
cargo build  # for debug builds
cargo build --release  # for optimized release builds
```

### How to Run

**Using VSCode:**

**While in a Rust file**, press `F5` or click the "Run and Debug" button to execute your project with debugging enabled.

!!! question "Not seeing Rust-specific options?"
    If prompted with a list of languages/technologies, select `CodeLLDB`.

**From Command Line:**

```bash
cd src
cargo run  # run debug build
cargo run --release  # run optimized release build
```

### How to Debug

**If using VSCode:**

Install the `CodeLLDB` extension for native debugging support. Debug profiles are automatically created when the extension is installed.

![VSCode Debugging](assets/vscode-debug.avif)
/// caption
Debugging Rust applications with CodeLLDB in VSCode
///

!!! tip "For more info, see [VSCode Integration](features/vscode-integration.md)"

### How to Test

**Using VSCode:**

Access pre-configured testing tasks via `Ctrl+Shift+P` → "Run Task":

- **Auto Test on Save** - Automatically run tests when files change

![Run Task](assets/run-task.avif)
/// caption
Access tasks via Ctrl+Shift+P → "Run Task"
///

![Available Tasks](assets/reloaded-tasks.avif)
/// caption
Pre-configured development tasks for testing and coverage
///

**From Command Line:**

```bash
cd src
cargo test  # run all tests
```

When you push code, GitHub Actions automatically runs tests on Linux, Windows, and macOS-check the "Actions" tab to see results.

![PR Checks](assets/pr-checks.avif)

!!! tip "For more info, see [Automated Testing & Publishing](features/automated-testing-publishing.md)"

### How to Lint

!!! question "What is linting?"
    Linting automatically checks your code for common mistakes, style issues, and potential bugs.<br/>
    It's like a spell-checker for code that catches problems before you run your program.

**Using VSCode:**

Linting runs automatically in VSCode with the `rust-analyzer` extension. You'll see warnings and suggestions directly in your editor as you type.

![Clippy Linting](assets/clippy-lints.avif)
/// caption
Clippy integration provides advanced linting out of the box
///

**From Command Line:**

```bash
cd src
cargo clippy  # run linter checks
```

Clippy will show warnings and suggestions to improve your code quality.

### How to Check Coverage

!!! question "What is coverage?"
    Coverage shows which parts of your code are tested (green) and which aren't (red).<br/>
    This helps you find gaps in your tests and improve code quality.

**Using VSCode:**

Access pre-configured coverage tasks via `Ctrl+Shift+P` → "Run Task":

- **Auto Coverage on Save** - Automatically generate coverage reports when files change

![Run Coverage Task](assets/run-coverage-task.avif)
/// caption
Run "Auto Coverage on Save" task via Ctrl+Shift+P → "Run Task"
///

You can preview coverage in the IDE directly with 'Coverage Gutters':

- **Coverage Gutters: Preview Coverage Report** - View HTML coverage report in browser

![Preview Coverage Report](assets/coverage-report.avif)
/// caption
Preview coverage report via Ctrl+Shift+P → "Coverage Gutters: Preview Coverage Report"
///

- **Coverage Gutters: Watch** - Live coverage visualization in editor (shows green/red lines)

![Coverage Gutters](assets/coverage-gutters.avif)
/// caption
Coverage show covered (green) and uncovered (red) lines in editor.<br/>
Activate with `Ctrl+Shift+P` → `Coverage Gutter: Watch`
///

When you push code, use the Codecov dashboard (click the coverage badge in your README) to track coverage trends and find untested code:

![Codecov Dashboard](assets/coverage-codecov.avif)

![Coverage Pills](assets/coverage-pills.avif)

!!! tip "For more info, see [Automated Testing & Publishing](features/automated-testing-publishing.md)"

### How to Check for Unsafe Code Issues and Undefined Behaviour

!!! question "What is Miri?"
    Miri detects memory bugs and undefined behaviour that normal tests miss.<br/>
    Critical for mission-critical applications, low-level code, and projects using `unsafe` blocks.<br/>
    Examples: out-of-bounds access, misaligned memory, arithmetic overflow.

**Using VSCode:**

Press `Ctrl+Shift+P` → "Run Task" → Select `Run Tests to Detect Undefined Behaviour` to run Miri tests.

**From Command Line:**

First install Miri (one-time setup):

```bash
rustup +nightly component add miri
```

Run Miri tests in your project:

```bash
cd src
cargo +nightly miri test

# Run a single test
cargo +nightly miri test test_name
```

!!! warning "Miri is MUCH slower than normal tests"
    This is expected-Miri thoroughly checks every memory operation. Use it primarily for projects with unsafe code, FFI bindings, or mission-critical applications.

!!! tip "For more info, see [Miri Testing](features/miri-testing.md)"

### How to Benchmark

!!! question "What is benchmarking?"
    Benchmarking measures how fast your code runs.<br/>
    Helps you track performance improvements and compare different implementations.

**Run benchmarks:**

```bash
cd src
cargo bench  # run all benchmarks
```

This generates detailed HTML reports in `target/criterion/report/index.html`.

![Benchmark CLI Output](assets/benchmark-cli.avif)
/// caption
CLI output when running benchmarks
///

![Benchmark Report](assets/benchmark-report.avif)
/// caption
Example generated HTML report showing performance trends
///

![Benchmark Comparison](assets/benchmark-violin-plot.avif)
/// caption
Violin plot comparing different files or implementations
///

**Add benchmarks:**

Create benchmark modules in `benches/` directory. Example structure:

```
benches/
├── main.rs          # Entry point
└── my_bench.rs      # Your benchmarks
```

In `main.rs`:

```rust
mod my_bench;
use criterion::{criterion_group, criterion_main, Criterion};
use my_bench::bench_my_function;

fn criterion_benchmark(c: &mut Criterion) {
    bench_my_function(c);
}

criterion_group!(benches, criterion_benchmark);
criterion_main!(benches);
```

In `my_bench.rs`:

```rust
use criterion::Criterion;

pub fn bench_my_function(c: &mut Criterion) {
    c.bench_function("my_function", |b| {
        b.iter(|| {
            // Code to benchmark here
        })
    });
}
```

!!! tip "For more info, see [Performance Benchmarking & Profiling](features/performance-benchmarking-profiling.md)"

### How to Profile

!!! question "What is profiling?"
    Profiling identifies which parts of your code are slow (bottlenecks).<br/>
    Use after benchmarking shows performance issues.

Install [cargo-flamegraph](https://github.com/flamegraph-rs/flamegraph) globally (one-time setup):

```bash
cargo install cargo-flamegraph
# if on Linux, ensure `perf` and `objdump` are available/installed
```

Generate flamegraph:

=== "Linux & macOS"

    ```bash
    cd src
    cargo flamegraph --bench my_benchmark --profile profile -- --bench
    ```

=== "Windows"

    ```bash
    cd src
    # Requires administrator privileges - run in admin command prompt or with sudo
    sudo cargo flamegraph --bench my_benchmark --profile profile -- --bench
    ```

Open the generated `flamegraph.svg` in your web browser to explore the interactive visualization.

![Flamegraph Example](assets/flamegraph.avif)
/// caption
Interactive flamegraph showing function call hierarchy and time spent
///

!!! tip "Profiled function not visible in flamegraph?"
    The compiler may inline your benchmarked function into the benchmark runner. Wrap it with `#[no_mangle]` to make it visible:

    ```rust
    #[no_mangle]
    fn my_function_wrapper(input: &[u8]) -> usize {
        my_actual_function(input)
    }
    ```

**Platform-specific tools:**

=== "Linux"

    After running the flamegraph command, a `perf.data` file will be created in your `src/` directory.
    
    Analyze it with `perf report` or Hotspot GUI:

    ```bash
    perf report perf.data
    ```

    ![Linux Perf CLI](assets/profiling-linux-perf.avif)
    /// caption
    Linux perf command-line analysis
    ///

    ![Linux Hotspot](assets/profiling-linux-hotspot.avif)
    /// caption
    Hotspot GUI tool for visualizing perf profile data
    ///

=== "Windows"

    Use Visual Studio Profiler for detailed analysis. First, build benchmarks:

    ```bash
    cd src
    cargo bench --no-run
    ```

    You will see the built binaries in the console (you want `my_benchmark-*`)

    ```
    Executable benches src\lib.rs (target\release\deps\prs_rs-228ebe72bddc28dc.exe)
    Executable benches\my_benchmark\main.rs (target\release\deps\my_benchmark-9a1672a43f9d48fa.exe)
    Executable benches src\main.rs (target\release\deps\prs_rs_cli-1da5d3ab6bcc4d35.exe)
    ```

    Then in Visual Studio:

    1. Open Visual Studio → "Continue without code"

        ![Visual Studio Start](assets/profiling-windows-vs-tutorial-1.avif)
        /// caption
        Visual Studio start screen
        ///

    2. Select `Debug` → `Performance Profiler`

        ![Performance Profiler Menu](assets/profiling-windows-vs-tutorial-2.avif)
        /// caption
        Select Debug → Performance Profiler
        ///

    3. Choose `Executable` → Navigate to `target/profile/deps/my_benchmark-....exe`

        ![Select Executable](assets/profiling-windows-vs-tutorial-3.avif)
        /// caption
        Select the benchmark executable
        ///

        ![Navigate to Binary](assets/profiling-windows-vs-tutorial-4.avif)
        /// caption
        Navigate to target/profile/deps/
        ///

    4. Enable `CPU Usage` → Click `Start`

        ![Start Profiling](assets/profiling-windows-vs-tutorial-5.avif)
        /// caption
        Enable CPU Usage and start profiling
        ///

        ![Visual Studio Profiler](assets/profiling-windows-visualstudio.avif)
        /// caption
        Visual Studio 2022 Community Profiler showing CPU usage
        ///

!!! tip "For more info, see [Performance Benchmarking & Profiling](features/performance-benchmarking-profiling.md)"

### How to Use Profile Guided Optimization (PGO)

!!! question "What is PGO?"
    Profile Guided Optimization uses runtime statistics to make your code run faster.<br/>
    The compiler learns how your code actually runs, then optimizes based on that data.

Install [cargo-pgo](https://github.com/Kobzol/cargo-pgo) globally (one-time setup):

```bash
cargo install cargo-pgo
rustup component add llvm-tools-preview
```

**Use in your project:**

```bash
cd src
cargo pgo instrument test  # collect profiling data
cargo bench  # establish baseline
cargo pgo optimize bench  # build with PGO and compare
```

![cargo pgo info](assets/pgo-cargo-pgo-info.avif)
/// caption
Verify cargo-pgo installation with `cargo pgo info`
///

![Benchmark CLI](assets/benchmark-cli.avif)
/// caption
Run baseline benchmark without PGO
///

![cargo pgo optimize result](assets/pgo-cargo-pgo-result.avif)
/// caption
Results showing performance improvement from PGO
///

!!! tip "For more info, see [Profile Guided Optimization](features/profile-guided-optimization.md)"

### How to Analyze Binary Size

!!! question "What is cargo bloat?"
    [cargo-bloat](https://github.com/RazrFalcon/cargo-bloat) identifies which crates and functions contribute most to your binary size.<br/>
    Use it to find optimization opportunities and reduce your final binary footprint.

Install globally (one-time setup):

```bash
cargo install cargo-bloat
```

**Use in your project:**

=== "Bash (Linux & macOS)"

    ```bash
    RUSTFLAGS="-Z unstable-options -C panic=immediate-abort" cargo bloat --profile release -Z build-std=std --target x86_64-unknown-linux-gnu -p <project-name>
    ```

=== "PowerShell (Windows)"

    ```powershell
    $env:RUSTFLAGS="-Z unstable-options -C panic=immediate-abort"; cargo bloat --profile release -Z build-std=std --target x86_64-pc-windows-msvc -p <project-name>
    ```

=== "CMD (Windows)"

    ```cmd
    set RUSTFLAGS=-Z unstable-options -C panic=immediate-abort && cargo bloat --profile release -Z build-std=std --target x86_64-pc-windows-msvc -p <project-name>
    ```

!!! info "Change target to match your platform"
    Remember to change the `--target` parameter to match your platform:
    
    - Linux: `x86_64-unknown-linux-gnu`
    - macOS: `x86_64-apple-darwin` or `aarch64-apple-darwin`
    - Windows: `x86_64-pc-windows-msvc`

- `-p <project-name>`: Specifies which package to analyze
- `--crates`: Shows per-crate size breakdown (omit for per-function breakdown)
- `-n <count>`: Controls how many items are shown

**Example output:**

```
 File  .text     Size Crate
 5.9%  25.5%  36.5KiB std
 3.5%  15.1%  21.7KiB rayon_core
 3.1%  13.4%  19.2KiB core
 2.0%   8.7%  12.4KiB walkdir
 1.8%   7.6%  10.9KiB prs_rs_cli
 1.3%   5.8%   8.3KiB argh_shared
 1.0%   4.3%   6.2KiB argh
 0.9%   3.9%   5.6KiB prs_rs
 0.8%   3.3%   4.7KiB alloc
 0.6%   2.7%   3.8KiB crossbeam_deque
 0.6%   2.4%   3.5KiB rust_fuzzy_search
 0.5%   2.3%   3.4KiB crossbeam_epoch
 0.5%   2.2%   3.1KiB rayon
 0.1%   0.6%     900B [Unknown]
 0.1%   0.5%     663B csbindgen
 0.0%   0.1%     201B same_file
 0.0%   0.1%      86B proc_macro
 0.0%   0.1%      77B __rustc
23.3% 100.0% 143.3KiB .text section size, the file size is 616.0KiB
```

!!! warning "File size accuracy varies by platform"
    - **Linux**: The file size shown includes debug symbols. Run `strip` on the binary for actual release size.
    - **Windows**: Should be about the same on MSVC.

**For accurate final binary size measurement, make a size optimized build:**

=== "Bash (Linux & macOS)"

    ```bash
    RUSTFLAGS="-Z unstable-options -C panic=immediate-abort" cargo rustc --profile release -Z build-std=std --target x86_64-unknown-linux-gnu -p <project-name>
    ```

=== "PowerShell (Windows)"

    ```powershell
    $env:RUSTFLAGS="-Z unstable-options -C panic=immediate-abort"; cargo rustc --profile release -Z build-std=std --target x86_64-pc-windows-msvc -p <project-name>
    ```

=== "CMD (Windows)"

    ```cmd
    set RUSTFLAGS=-Z unstable-options -C panic=immediate-abort && cargo rustc --profile release -Z build-std=std --target x86_64-pc-windows-msvc -p <project-name>
    ```

!!! tip "Stripped binaries are significantly smaller"
    The example above shows 616.0KiB because of debug symbols, but the final build size and stripped binary size is ~185.3kB. Remember, what you're optimizing is making `.text` smaller.

### How to Build for Other Platforms

!!! question "Why cross-compile?"
    Sometimes you want to build for other platforms, e.g. test Windows builds on Linux.<br/>
    Cross-compilation lets you do this without switching operating systems.

**Install globally (one-time setup):**

```bash
cargo install cross --git https://github.com/cross-rs/cross
```

**Use in your project:**

```bash
cd src
cross build --target x86_64-pc-windows-gnu  # build for Windows
cross test --target aarch64-unknown-linux-gnu --release  # test for ARM64 Linux
```

The `cross` tool uses [Docker](https://www.docker.com/) or [Podman](https://podman.io/) containers to handle cross-compilation automatically. Simply replace `cargo` with `cross` and specify your target platform.

!!! tip "For more info, see [Cross Compilation](features/cross-compilation.md)"

### How to Create C/C++ Bindings

!!! question "Why create bindings?"
    Sometimes you may want to run your Rust code outside of Rust.<br/>
    C/C++ bindings let you call your Rust functions from C, C++, or any language with C interop.

**Export functions:**

Use `#[no_mangle]` and `extern "C"` to make functions callable from C/C++:

```rust
#[no_mangle]
pub extern "C" fn add_numbers(a: i32, b: i32) -> i32 {
    a + b
}
```

**Generate bindings:**

!!! note "Manual generation is only needed when adjusting configuration."
    
    Headers are auto-generated in automated builds and published in releases.

Using VSCode, press `Ctrl+Shift+P` → "Run Task" → Select one of:

- **Generate C Bindings** - Generate C headers only
- **Generate C++ Bindings** - Generate C++ headers only

Or from command line:

```bash
cd src

# Install cbindgen (one-time setup)
cargo install cbindgen

# Generate C bindings
cbindgen --config ../.github/cbindgen_c.toml --output bindings/c/your-project.h your-project

# Generate C++ bindings
cbindgen --config ../.github/cbindgen_cpp.toml --output bindings/cpp/your-project.hpp your-project
```

Replace `your-project` with your actual project name. Configuration files are located in `.github/`:

- `.github/cbindgen_c.toml` - C bindings configuration
- `.github/cbindgen_cpp.toml` - C++ bindings configuration

![C Bindings Releases](assets/c-bindings-releases.avif)
/// caption
Headers automatically attached to GitHub releases
///

!!! tip "For more info, see [C/C++ Bindings](features/bindings/cpp-bindings.md)"
    In particular, check out the [How to Export Functions](features/bindings/cpp-bindings.md#how-to-export-functions) section for useful patterns.

### How to Create C# Bindings

**Export functions:**

!!! note "C# bindings are autogenerated from C bindings"
    See the [C/C++ Bindings section](#how-to-create-cc-bindings) above for how to export functions with `#[no_mangle]` and `extern "C"`.

Bindings are generated when you build into `bindings/csharp/NativeMethods.g.cs`.
Customize generation in `build.rs` using [csbindgen](https://github.com/Cysharp/csbindgen).

!!! tip "For more info, see [C# Bindings](features/bindings/csharp-bindings.md)"

### How to Fuzz

!!! question "What is fuzzing?"
    Fuzzing automatically generates random inputs to find crashes, bugs, and security vulnerabilities.<br/>
    It's especially useful for testing parsers, file format handlers, and untrusted input processing.<br/>
    Examples: buffer overflows, panics on malformed data, edge case failures.

**Using VSCode:**

Press `Ctrl+Shift+P` → "Run Task" → Select `List Fuzz Targets` to see available targets.

Then run a target from the command line using the command shown in the target file's header comment.

**From Command Line:**

First install cargo-fuzz (one-time setup):

```bash
cargo install cargo-fuzz
```

Run a fuzz target in your project:

```bash
cd src
cargo +nightly fuzz run fuzz_example

# List available fuzz targets
cargo +nightly fuzz list
```

!!! warning "Fuzzing requires nightly Rust"
    Fuzzing uses unstable compiler features. Use `cargo +nightly` to select the nightly toolchain.

!!! info "Windows Users"
    Follow the [Windows setup guide](https://rust-fuzz.github.io/book/cargo-fuzz/windows/setup.html) first.
    Run fuzz commands from **Developer PowerShell for VS 20XX** or **x64 Native Tools Command Prompt for VS 20XX**.

!!! tip "For more info, see [Fuzzing](features/fuzzing.md)"

## Editing Documentation

!!! tip "Documentation lives in the doc/ folder"
    It uses [MkDocs](https://www.mkdocs.org/) for building static sites.

**If using VSCode:**

Open the `doc/` folder in a new VSCode window (File → Open Folder) for formatting rules to apply.

Open a terminal and run:

```bash
python start_docs.py
# or `python3 start_docs.py`
```

Ctrl+click the `http://localhost:8000` link in the terminal output to open the docs in your browser.

**From Command Line:**

To preview documentation locally:

```bash
cd doc
python start_docs.py
# or `python3 start_docs.py`
```

This starts a local server at `http://localhost:8000` with live reload.

See `doc/README.md` for more information.

## Contributing

!!! question "Want to contribute?"
    Follow these guidelines to keep the project history clean and organized.<br/>
    These practices make code review easier and help maintain project quality.<br/>
    Not sure about something? Just ask-whether it's "is it okay to work on this?" or "how do I do this?"

### One Change Per PR

Keep pull requests focused and atomic. Try to do one logical change per pull request rather than bundling multiple unrelated changes together.

### Commit Names

When writing commit messages, follow the [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) style to help maintain clear project history:

- **Added** - for new features
- **Changed** - for changes in existing functionality
- **Deprecated** - for soon-to-be removed features
- **Removed** - for now removed features
- **Fixed** - for any bug fixes
- **Security** - in case of vulnerabilities

Example commit messages:
```
Added support for async operations
Fixed memory leak in parser
Changed API parameter order (breaking change)
```

### Why Use Pull Requests?

!!! tip "Pull requests let you take a second look at your code before merging, helping you catch mistakes early."

In addition, PRs trigger automated quality checks that don't run on direct pushes:

- **Documentation**: Verifies `cargo doc` compiles without errors
- **Linter**: Treats `cargo clippy` warnings as errors  
- **Formatter**: Ensures code matches `rustfmt` standards

!!! tip "Releases (Tags) also run these checks"
    Publishing is blocked until quality standards are met.

## Publishing Releases

Publishing releases is largely automated through the CI workflow.

### Customizing the Changelog

First, customize the release notes by editing `.github/changelog.hbs`.<br/>
The default template uses [Handlebars](https://handlebarsjs.com/guide/) syntax and includes:

- Section for release notes (update before release)
- Download links to artifacts
- Auto-generated changelog from commits

### Creating a Release

!!! tip "When you're ready to publish a release, create and push a git tag."

```bash
git tag 1.0.0
git push origin 1.0.0
```

This triggers the CI workflow which will:

1. **Build and test** across all platforms (Linux, Windows, macOS)
2. **Generate changelog** from commit history using the `.github/changelog.hbs` template
3. **Create GitHub Release** with all built artifacts attached

!!! info "Depending on template/project configuration, additional steps may occur."

    - **Publish to crates.io**: Lets other Rust developers use your library with `cargo`.
    - **Publish to NuGet**: Lets C# developers use your library.

## Miscellaneous

### GitHub Workflows

The `.github` folder contains pre-configured issue templates, PR templates, and CI/CD workflows.

You may want to edit these to match your project's needs:

- **Issue templates** - Located in `.github/ISSUE_TEMPLATE/`
- **Workflow files** - Located in `.github/workflows/`

When you push code, these workflows automatically run tests on Linux, Windows, and macOS.

![GitHub Template Selector](assets/issue-template.avif)
/// caption
Template selector for bug reports and feature requests
///

![Bug Report Template](assets/bug-report-template.avif)
/// caption
Pre-configured bug report template with structured fields
///

!!! tip "For more info, see [GitHub Templates](features/github-templates.md)"
