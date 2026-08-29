# Profile Guided Optimization

Profile Guided Optimization (PGO) is a compiler feature that uses runtime statistics to make your code run faster, resulting in small performance improvements for your Rust applications.

To use PGO, we first create an instrumented build that collects runtime statistics, then build the final optimized version using those statistics.

!!! warning "Only use PGO if your project outputs binaries."
    PGO test cases cannot be easily transferred when your project is included as a dependency via crates.io.

## Locally Testing PGO

!!! info "[cargo-pgo](https://github.com/Kobzol/cargo-pgo) makes local testing with PGO easy"

Before enabling PGO in CI, you should test it locally to ensure it provides actual performance benefits.

!!! tip "Always Test PGO"

    PGO isn't guaranteed to always provide an improvement.<br/>
    After adding representative workloads, always test the results.

### Installation

**Install globally (one-time setup):**

```bash
cargo install cargo-pgo
rustup component add llvm-tools-preview
```

Verify that cargo pgo is installed correctly:

```bash
cargo pgo info
```

![cargo pgo info](../assets/pgo-cargo-pgo-info.avif)
/// caption
Verifying cargo-pgo installation
///

### Testing Workflow

The testing process involves three steps: baseline measurement, profiling collection, and optimized build comparison.

#### 1. Collect Profiling Data

Run an instrumented benchmark to collect profiling data:

```bash
cargo pgo instrument test -- --bench my_benchmark --features pgo
```

This may also run the regular tests.

#### 2. Run Baseline Benchmark

Establish a performance baseline without PGO:

```bash
cargo bench
```

![Benchmark CLI](../assets/benchmark-cli.avif)
/// caption
Initial benchmark run to establish performance baseline
///

#### 3. Build with PGO Optimization

Create the PGO-optimized build and compare results:

```bash
cargo pgo optimize bench
```

![cargo pgo optimize result](../assets/pgo-cargo-pgo-result.avif)
/// caption
Results after running cargo pgo optimize
///

!!! success "Evaluating Results"
    It's normal if some results show a regression. If the overall is a net improvement, keep PGO. Otherwise disable it in CI by setting `build-with-pgo: false` in your workflow configuration.

## Configuring Benchmarks for PGO

PGO works by collecting statistics from representative workloads during benchmark execution. The key is ensuring your benchmarks reflect realistic usage patterns.

!!! info "Representative Workloads"
    You should ensure that only realistic representative workloads are used to collect the PGO data.
    
    For example, if this was a compression library, you should run the 'compress' and 'decompress' methods on real files (***NOT RANDOM DATA***) as part of your benchmarks.

### Benchmark Configuration

!!! tip "Two Approaches to PGO Benchmark Configuration"

#### Method 1: Exclude Specific Benchmarks

Update your benchmark code to exclude unrealistic workloads from PGO runs using conditional compilation:

```rust
fn criterion_benchmark(c: &mut Criterion) {
    // Excluded from PGO.
    #[cfg(not(feature = "pgo"))]
    {
        bench_create_dict(c);
    }
}
```

In this configuration you run your regular benchmarks for PGO, excluding ones that run on unrealistic data.

#### Method 2: Separate PGO Code

Alternatively, separate code entirely for PGO data collection, working on real data:

```rust
fn criterion_benchmark(c: &mut Criterion) {
    // Excluded from PGO.
    #[cfg(not(feature = "pgo"))]
    {
        bench_estimate(c);
        bench_decompress(c);
        bench_compress_file(c);
        bench_create_dict(c);
    }

    // Only runs during PGO data collection.
    #[cfg(feature = "pgo")]
    {
        generate_pgo_data();
    }
}
```

This gives you more control over PGO data collection: use custom data, exclude unrealistic cases, or test multiple components together.

## Integrate with Non-Template Projects
!!! info
    If your project was not built on Reloaded template, here's how you can recreate the PGO parts.

Adding PGO support to existing Rust projects requires coordinated changes across build configuration and source code.

### Environment Variable Setup

Add the PGO environment variable to your GitHub Actions workflow:

```yaml
env:
  build-with-pgo: true  # Set to true to enable PGO builds
```

### Build Matrix Configuration

Modify your build matrix to include the `use-pgo` parameter and call the GitHub action:

```yaml
strategy:
  matrix:
    include:
      - os: ubuntu-latest
        target: x86_64-unknown-linux-gnu
        use-pgo: true
        use-cross: false
      - os: windows-latest
        target: x86_64-pc-windows-msvc
        use-pgo: true
        use-cross: false

- name: Build C Libraries and Run Tests
  uses: Reloaded-Project/devops-rust-lightweight-binary@v1
  with:
    crate-name: ${{ github.event.repository.name }}
    target: ${{ matrix.target }}
    use-pgo: ${{ matrix.use-pgo && env.build-with-pgo }}
    use-cross: ${{ matrix.use-cross }}
    features: "c-exports"
    build-library: true
```

!!! warning "Cross-Compilation Limitations"
    PGO is disabled for cross-compilation targets where native runners aren't available, as statistics collection would be impractical.

### Adding PGO to Cargo.toml

Add the PGO feature to your `Cargo.toml`:

```toml
[features]
pgo = []
```

### Adding Benchmarks

If you don't already have benchmarks, add them to your project. See the [Configuring Benchmarks for PGO](#configuring-benchmarks-for-pgo) section for details on setting up benchmarks with PGO support.

