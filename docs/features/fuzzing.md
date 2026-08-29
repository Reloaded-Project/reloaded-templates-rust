# Fuzzing

Find edge cases, crashes, and security vulnerabilities by testing your code against millions of random inputs.

Fuzzing is especially valuable for testing code that handles untrusted data like parsers, file format handlers, and network protocols.

## Key Features
- **[What is Fuzzing?](#what-is-fuzzing)**: Understanding fuzzing and its benefits
- **[When to Use Fuzzing](#when-to-use-fuzzing)**: Identifying good candidates for fuzz testing
- **[Writing Fuzz Targets](#writing-fuzz-targets)**: Creating effective fuzz tests
- **[Running Fuzz Tests](#running-fuzz-tests)**: VSCode and command-line usage
- **[Integrate with Non-Template Projects](#integrate-with-non-template-projects)**: Adding fuzzing to existing projects

## What is Fuzzing?

!!! info "Fuzzing in Simple Terms"
    **Fuzzing** is a testing technique that automatically generates random or semi-random inputs to find bugs your unit tests might miss.

Fuzzing works by:

1. Generating random input data (bytes, strings, structured data)
2. Feeding that data to your code
3. Watching for crashes, panics, or assertion failures
4. Saving inputs that cause problems so you can reproduce and fix bugs

**What Can Fuzzing Find?**

- Buffer overflows and out-of-bounds access
- Panics on malformed or unexpected input
- Infinite loops or excessive memory usage
- Integer overflows and arithmetic errors
- Logic errors in edge cases

## When to Use Fuzzing

!!! tip "When to Use Fuzzing"
    Fuzzing is most valuable for code that processes external or untrusted input.

    Consider fuzzing if your project:

    - Parses file formats (images, documents, configs)
    - Handles network protocols or serialized data
    - Processes user input that could be malformed
    - Uses `unsafe` code with complex invariants

!!! info "Fuzzing vs Unit Tests"
    Unit tests check specific cases you think of. Fuzzing explores inputs you didn't anticipate.<br/>
    Use both: unit tests for known scenarios, fuzzing to discover unknown edge cases.

## Writing Fuzz Targets

!!! info "A fuzz target is a function that receives random input and passes it to your code."

**Basic Fuzz Target:**

```rust
#![no_main]

use libfuzzer_sys::fuzz_target;

fuzz_target!(|data: &[u8]| {
    // fuzzed code goes here
});
```

**Example: Fuzzing a Parser:**

```rust
#![no_main]

use libfuzzer_sys::fuzz_target;
use my_library::parse_config;

fuzz_target!(|data: &[u8]| {
    // Convert bytes to string, ignore invalid UTF-8
    if let Ok(input) = std::str::from_utf8(data) {
        // Your parser should handle any input without panicking
        let _ = parse_config(input);
    }
});
```

!!! tip "Writing Effective Fuzz Targets"
    - Start with simple byte slice input (`&[u8]`)
    - Don't panic on invalid input-return early instead
    - Test one entry point per fuzz target
    - Use `arbitrary` crate for structured input when needed

Fuzz targets live in `fuzz/fuzz_targets/`. The template includes `fuzz_example.rs` as a starting point.

## Running Fuzz Tests

!!! warning "Fuzzing requires nightly Rust"
    Fuzzing uses unstable compiler features. Commands use `cargo +nightly` to select the nightly toolchain.

**Using VSCode Tasks:**

Press `Ctrl+Shift+P` → "Run Task" → Select **List Fuzz Targets** to see available targets.

**Using Command Line:**

```bash
cd src
# Run the default fuzz target
cargo +nightly fuzz run fuzz_example

# List all available fuzz targets
cargo +nightly fuzz list

# Run with a time limit (60 seconds)
cargo +nightly fuzz run fuzz_example -- -max_total_time=60
```

**Windows Setup:**

!!! info "Windows requires additional setup"
    Follow the [Windows setup guide](https://rust-fuzz.github.io/book/cargo-fuzz/windows/setup.html) before fuzzing on Windows.
    
    Run fuzz commands from **Developer PowerShell for VS 20XX** or **x64 Native Tools Command Prompt for VS 20XX** to ensure the MSVC linker is available.

**When a Bug is Found:**

Fuzzing saves crash-inducing inputs to `fuzz/artifacts/fuzz_example/`. Use these to reproduce and fix bugs:

```bash
# Reproduce a crash
cargo +nightly fuzz run fuzz_example fuzz/artifacts/fuzz_example/crash-xxxxx
```

## Integrate with Non-Template Projects

!!! info
    If your project was not built on Reloaded template, here's how you can add fuzzing.

**Install cargo-fuzz:**

```bash
cargo install cargo-fuzz
```

**Initialize fuzzing in your project:**

```bash
cd src  # fuzz/ is created in the current directory
cargo fuzz init
```

This creates a `fuzz/` directory with a basic fuzz target.

**Create a fuzz target:**

Edit `fuzz/fuzz_targets/fuzz_example.rs` (or create a new target):

```rust
#![no_main]

use libfuzzer_sys::fuzz_target;

fuzz_target!(|data: &[u8]| {
    // Call your code with random input
});
```

### VSCode Tasks Setup

!!! tip "Add Fuzz Tasks to VSCode"
    Add this task to your `.vscode/tasks.json` file to easily list available fuzz targets.

Add this task configuration to your `.vscode/tasks.json` (create the file if it doesn't exist):

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "List Fuzz Targets",
      "type": "shell",
      "command": "cargo install cargo-fuzz --quiet && cargo +nightly fuzz list",
      "group": "test",
      "presentation": {
        "reveal": "always"
      },
      "problemMatcher": []
    }
  ]
}
```

!!! info "Running Fuzz Targets"
    Run fuzz targets from the command line: `cargo +nightly fuzz run <target_name>`
    
    Each fuzz target file includes the run command in its header comment for easy reference.
