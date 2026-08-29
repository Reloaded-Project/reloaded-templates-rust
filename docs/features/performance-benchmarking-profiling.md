# Performance Benchmarking & Profiling

While Rust provides excellent performance out of the box, measuring and optimizing that performance requires proper tooling and setup.

The template provides the essential building blocks for benchmarking and profiling with [Criterion](https://github.com/bheisler/criterion.rs).

!!! info
    Benchmarking is optional during project generation. Enable it by selecting "Include Benchmark Configuration" when prompted.

## Quick Start
Run your first benchmark with a single command:

```bash
cargo bench
```

![Benchmark CLI Output](../assets/benchmark-cli.avif)
/// caption
Example CLI output when running benchmarks
///

This executes all benchmarks and generates detailed HTML reports in `target/criterion/report/index.html`.

![Benchmark Report](../assets/benchmark-report.avif)
/// caption
Example generated HTML report
///

Open the file in your web browser or right-click → "Show Preview" in VSCode.

## Running Benchmarks
Below are some useful additional benchmark commands:

```bash
# Run a specific benchmark
cargo bench "fib 20"

# Run a specific benchmark function
cargo bench "can_decompress_file_Model.bin"

# Run all benchmarks in a group
cargo bench "File Compression"

# Run all benchmarks beginning with a prefix
cargo bench "compress_"

# Run benchmarks with native CPU optimizations (for benchmarking specialized algorithms)
RUSTFLAGS="-C target-cpu=native" cargo bench
```

## Understanding Benchmark Code

### File Structure

```
benches/
├── main.rs              # [mandatory] Main benchmark entry point
├── util.rs              # [example] Utility functions for loading test data
├── compress.rs          # [example] Compression benchmarks
├── decompress.rs        # [example] Decompression benchmarks
└── gen_pgo_data.rs      # [example] PGO data generation
```

### Main Benchmark File

The `main.rs` file serves as the entry point for all benchmarks:

```rust
// Import individual benchmark modules
mod compress;
mod decompress;
mod gen_pgo_data;
mod util;

// Import required items
use compress::bench_compress_file;
use criterion::{criterion_group, criterion_main, Criterion};
use decompress::bench_decompress;
#[cfg(feature = "pgo")]
use gen_pgo_data::generate_pgo_data;

fn criterion_benchmark(c: &mut Criterion) {
    // Regular benchmarks - excluded from PGO
    #[cfg(not(feature = "pgo"))]
    {
        bench_decompress(c);
        bench_compress_file(c);
    }

    // PGO data generation - only runs during PGO builds
    #[cfg(feature = "pgo")]
    {
        generate_pgo_data();
    }
}

criterion_group! {
    name = benches;
    config = Criterion::default();
    targets = criterion_benchmark
}

criterion_main!(benches);
```

Add additional modules using `mod` at the top of the file, just like in regular Rust programs.

### Adding Benchmarks

Create individual benchmark functions in separate modules. Here's an example of a well-structured benchmark:

```rust
use crate::util::{get_compressed_file_path, load_sample_file};
use criterion::{Criterion, Throughput};
use prs_rs::decomp::{prs_calculate_decompressed_size, prs_decompress_unsafe};

pub fn bench_decompress(c: &mut Criterion) {
    let file_names = vec!["Model.bin", "ObjectLayout.bin", "WorstCase.bin"];
    let mut group = c.benchmark_group("File Decompression");

    for file_name in file_names {
        let compressed = load_sample_file(get_compressed_file_path(file_name));
        let decompressed_len = unsafe { prs_calculate_decompressed_size(compressed.as_slice()) };
        let mut decompressed = vec![0_u8; decompressed_len];
        group.throughput(Throughput::Bytes(decompressed_len as u64));
        group.bench_function(format!("can_decompress_file_{file_name}"), |b| {
            b.iter(|| unsafe {
                prs_decompress_unsafe(compressed.as_slice(), decompressed.as_mut_slice())
            })
        });
    }

    group.finish();
}
```

Best practices for adding benchmarks:

- **Use benchmark groups** - Organize related benchmarks together
- **Set throughput metrics** - Use throughput setting when appropriate
- **Test multiple scenarios** - Benchmark with different input sizes/types when appropriate
- **Only benchmark code in iter block** - Load test data outside the iteration to avoid measuring setup time

![Benchmark Comparison](../assets/benchmark-violin-plot.avif)
/// caption
Violin plot generated from the "File Decompression" benchmark group, comparing two files with the same size but different content
///

!!! tip
    Violin plots compare different data (same size) or different implementations.
    
    For code that processes external data like decompression, ensure same data size for fair comparisons.

??? info "Profile-Guided Optimization (PGO)"
    Sometimes benchmarks are used during the build process to collect performance data that helps the compiler optimize your code. You can exclude benchmarks from this process using conditional compilation:
    
    ```rust
    #[cfg(not(feature = "pgo"))]
    fn benchmark_excluded_from_pgo() {
        // Benchmark code here
    }
    ```

## Profiling

### Generating Profile
Generate performance profiles of your benchmarks using cargo flamegraph.

**Install globally (one-time setup):**

```bash
cargo install cargo-flamegraph
# if on Linux, ensure `perf` and `objdump` are available/installed
```

**Profile a benchmark:**

```bash
cargo flamegraph --bench my_benchmark --profile profile -- --bench --profile-time 10 can_decompress_file_Model
# On Windows this requires `sudo cargo`, or administrator command prompt
```

!!! tip "Profiled function not visible in flamegraph?"
    The compiler may inline your benchmarked function into the benchmark runner, making it invisible in profiler output. To prevent this, wrap your code in a function with `#[no_mangle]` or `#[inline(never)]`:

    ```rust
    #[no_mangle]
    fn my_function_wrapper(input: &[u8]) -> usize {
        // Call your actual benchmarked function here
        my_actual_function(input)
    }
    ```

    Call the wrapper in your benchmark instead of the original function. The `#[no_mangle]` attribute forces the compiler to keep it as a distinct symbol in the profile.

### Inspecting Flamegraph

!!! warning "The 'profile' profile is mandatory"
    The `--profile profile` is required. This is the release profile but with debug symbols, which will be necessary for accurate results.
Explore the interactive flamegraph visualization to identify performance bottlenecks.

![Flamegraph Example](../assets/flamegraph.avif)
/// caption
Interactive flamegraph showing function call hierarchy
///

Open the generated `flamegraph.svg` in your web browser to explore the interactive visualization.

Click on any segment to zoom into that function's call stack and identify performance bottlenecks.

??? warning "Open the SVG in a web browser"
    The `flamegraph.svg` is a webpage with JavaScript, not just an image. Opening it in an image viewer, including VSCode by default, may render it not interactive.

### Inspecting Profile Data
Analyze detailed profile data with specialized tools for deep performance investigation.

#### Linux
Linux users can analyze `perf.data` files (created after running `cargo flamegraph`) with Hotspot or the perf CLI.

![Linux Perf CLI](../assets/profiling-linux-perf.avif)
/// caption
Linux perf command-line analysis with `perf report perf.data`
///

You can enable original code view with `S` (capital) after pressing `/` + `Enter`, and then selecting a function. Perf is real powerful but requires some minimal discovery around the web for more guidance.

![Linux Hotspot](../assets/profiling-linux-hotspot.avif)
/// caption
Hotspot GUI tool for visualizing perf profile data
///
#### Windows
!!! tip "On Windows you should use a standalone profiling tool."

We'll show Visual Studio here since you will already likely have it installed after setting up Rust.

![Visual Studio Profiler](../assets/profiling-windows-visualstudio.avif)
/// caption
Visual Studio 2022 Community Profiler showing CPU usage
///

Build the benchmark binary without running it:

```bash
cargo bench --no-run
```

You will see the built binaries in the console log:

```
Executable benches src\lib.rs (target\release\deps\prs_rs-228ebe72bddc28dc.exe)
Executable benches\my_benchmark\main.rs (target\release\deps\my_benchmark-9a1672a43f9d48fa.exe)
Executable benches src\main.rs (target\release\deps\prs_rs_cli-1da5d3ab6bcc4d35.exe)
```

Follow these steps to profile your benchmark in Visual Studio:

1. In the Visual Studio start pop-up, select 'Continue without code' in the bottom right.

    ![Visual Studio Start](../assets/profiling-windows-vs-tutorial-1.avif)

2. From the top menu, select `Debug` -> `Performance Profiler`.

    ![Performance Profiler Menu](../assets/profiling-windows-vs-tutorial-2.avif)

3. Select `Executable`, then navigate to `target/profile/deps/my_benchmark-....exe` (or similar).

    ![Select Executable](../assets/profiling-windows-vs-tutorial-3.avif)

    ![Navigate to Binary](../assets/profiling-windows-vs-tutorial-4.avif)

4. Tick `CPU Usage`, then hit `Start`.

    ![Start Profiling](../assets/profiling-windows-vs-tutorial-5.avif)

#### macOS
!!! info "Contributions Welcome"
    I (sewer) never owned an Apple device, so I can't provide good guidance here. Please contribute if you have macOS experience.

## Integrate with Non-Template Projects
!!! info
    If your project was not built on Reloaded template, here's how you can recreate the benchmarking parts.

Add benchmarking to existing Rust projects in 3 steps:

### 1. Create Benchmark Directory
```bash
mkdir benches
```

### 2. Add to Cargo.toml
```toml
[dev-dependencies]
criterion = "0.7.0"

[[bench]]
name = "my_benchmark"
harness = false

# Profile Build
[profile.profile]
inherits = "release"
debug = true
strip = false

# Benchmark Build  
[profile.bench]
inherits = "profile"
```

### 3. Create Basic Benchmark
`benches/my_benchmark.rs`:
```rust
use criterion::{black_box, criterion_group, criterion_main, Criterion};

fn fibonacci(n: u64) -> u64 {
    match n {
        0 => 1,
        1 => 1,
        n => fibonacci(n-1) + fibonacci(n-2),
    }
}

fn criterion_benchmark(c: &mut Criterion) {
    c.bench_function("fib 20", |b| b.iter(|| fibonacci(black_box(20))));
}

criterion_group!(benches, criterion_benchmark);
criterion_main!(benches);
```

Run with:

```bash
cargo bench
```

### 4. Update .gitignore
```gitignore
# Profiling files
perf.data.old
perf.data
flamegraph.svg
```