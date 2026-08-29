# Miri - Undefined Behaviour Detection

Detect memory bugs and undefined behaviour in your Rust code before they cause crashes or security vulnerabilities. Miri is a testing tool that catches subtle bugs that normal tests might miss.

Here's an example of something Miri can catch:

```rust
fn buggy_function() {
    let data = vec![1, 2, 3];
    unsafe {
        // BUG: Accessing index 5 when only indices 0-2 exist
        // This might "work" in normal tests but is undefined behaviour
        let value = *data.as_ptr().add(5);
        println!("Value: {}", value);
    }
}
```

**What's wrong?** The code tries to read memory beyond the end of the array. This might read random memory values or crash.

**What Miri detects:** `error: Undefined Behaviour: out-of-bounds pointer use`

## Key Features
- **[What is Miri?](#what-is-miri)**: Understanding Miri and undefined behaviour
- **[Additional Examples](#additional-examples)**: Real-world bugs Miri catches
- **[Manually Running Miri](#manually-running-miri)**: Command-line usage and cross-platform testing
- **[Integrate with Non-Template Projects](#integrate-with-non-template-projects)**: VSCode integration for easy testing

## What is Miri?

!!! info "Miri in Simple Terms"
    **Miri** is a testing tool that checks your Rust code for hidden bugs that can cause crashes, data corruption, or security problems.

**What is Undefined Behaviour?**

Undefined behaviour (UB) refers to bugs where your program's behaviour becomes unpredictable. These bugs might:

- Work fine on your computer but crash on someone else's
- Appear to work but corrupt data silently
- Create security vulnerabilities that attackers can exploit
- Only show up months later in production

**What is Unsafe Code?**

Rust normally prevents many types of bugs automatically through its safety checks. However, sometimes you need to write "unsafe" code that bypasses these checks (for performance or when interfacing with hardware/other languages). Unsafe code can introduce undefined behaviour if not written carefully.

**When Do You Need Miri?**

!!! tip "When to Use Miri"
    Miri is primarily useful for projects writing advanced, unsafe, or mission-critical code.
    
    Consider using Miri if your project:
    
    - Uses `unsafe` code blocks
    - Writes low-level code (operating systems, drivers, game engines)
    - Requires extra confidence in code safety for mission-critical applications

## Additional Examples

Here are more real-world bugs that Miri catches which normal tests might miss:

### Example 1: Misaligned Memory Access

```rust
fn misaligned_access() {
    let data = [0u8; 8];
    unsafe {
        // BUG: Creating a pointer to u64 that's not properly aligned
        // Some CPUs require specific memory alignment and will crash
        let ptr = data.as_ptr().add(1) as *const u64;
        let value = *ptr;
        println!("Value: {}", value);
    }
}
```

**What's wrong?** The code creates a pointer to a 64-bit integer at an address that's not aligned to 8 bytes. Some processors crash when accessing misaligned data.

**What Miri detects:** `error: Undefined Behaviour: accessing memory with alignment 1, but alignment 8 is required`

!!! tip "Important for Reloaded Projects"
    Critical for Reloaded code targeting old consoles, homebrew, or esoteric platforms requiring big endian support and strict memory alignment.

### Example 2: Arithmetic Overflow (Unchecked)

```rust
fn unchecked_arithmetic() {
    unsafe {
        // BUG: Using unchecked arithmetic that can overflow
        // If x + y exceeds i32::MAX, behaviour is undefined
        let x: i32 = i32::MAX;
        let y: i32 = 1;
        let result = x.unchecked_add(y);
        println!("Result: {}", result);
    }
}
```

**What's wrong?** The code uses `unchecked_add` which promises the operation won't overflow, but it does. This breaks the function's contract and causes undefined behaviour.

**What Miri detects:** `error: Undefined Behaviour: overflow executing unchecked_add`

!!! warning "Real-World Impact"
    Undefined behaviour like unexpected overflow can lead to [subtle bugs][prs-rs-bug].

!!! info "What Miri Detects"
    For a complete list of undefined behaviour that Miri can detect, visit the [Miri GitHub Repository][miri-github-repo].

## Manually Running Miri

**Using VSCode Tasks (Recommended):**

Press `Ctrl+Shift+P` → "Run Task" → Select `Run Tests to Detect Undefined Behaviour`

For big-endian testing, select `Run Tests to Detect Undefined Behaviour (Big Endian)` instead.

**Using Command Line:**

First, install Miri (one-time setup):

```bash
rustup +nightly component add miri
```

Run Miri on your tests:

```bash
cargo +nightly miri test
```

**Cross-Platform Testing (Big-Endian):**

Miri can also test big-endian architectures to catch undefined behaviour in arithmetic operations, unaligned reads/writes, or code that assumes specific memory layout.

Computers store numbers in memory differently:

- **Little-endian**: Most common (Intel, AMD, ARM) - stores numbers with the smallest byte first
- **Big-endian**: Less common (some game consoles, network protocols) - stores numbers with the largest byte first

To test with big-endian emulation via command line:

```bash
cargo +nightly miri test --target powerpc64-unknown-linux-gnu
```

!!! warning "Miri is Slower Than Normal Tests"
    Miri thoroughly checks every memory operation, making tests run much slower than normal. This is expected - the extra time ensures safety.

## Integrate with Non-Template Projects

!!! info
    If your project was not built on Reloaded template, here's how you can add Miri testing.

**Install Miri:**

```bash
rustup +nightly component add miri
```

**Run Miri on your tests:**

```bash
cargo +nightly miri test
```

**Test with big-endian emulation:**

```bash
cargo +nightly miri test --target powerpc64-unknown-linux-gnu
```

### VSCode Tasks Setup

!!! tip "Add Miri Tasks to VSCode"
    For convenient one-click Miri testing, add these tasks to your `.vscode/tasks.json` file.

Add these task configurations to your `.vscode/tasks.json` (create the file if it doesn't exist):

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Run Tests to Detect Undefined Behaviour",
      "type": "shell",
      "command": "rustup +nightly component add miri && cargo +nightly miri test",
      "group": "test",
      "presentation": {
        "reveal": "always"
      },
      "problemMatcher": [],
      "options": {
        "cwd": "${workspaceFolder}/src"
      }
    },
    {
      "label": "Run Tests to Detect Undefined Behaviour (Big Endian)",
      "type": "shell",
      "command": "rustup +nightly component add miri && cargo +nightly miri test --target powerpc64-unknown-linux-gnu",
      "group": "test",
      "presentation": {
        "reveal": "always"
      },
      "problemMatcher": [],
      "options": {
        "cwd": "${workspaceFolder}/src"
      }
    }
  ]
}
```

!!! info "Using the Tasks"
    After adding the tasks, press `Ctrl+Shift+P` → "Run Task" → Select `Run Tests to Detect Undefined Behaviour` to run Miri.

These tasks automatically:

1. Install Miri if not already installed
2. Run your tests with Miri's checking enabled
3. Report any undefined behaviour detected

[miri-github-repo]: https://github.com/rust-lang/miri
[prs-rs-bug]: https://github.com/Sewer56/prs-rs/releases/tag/2.0.2
