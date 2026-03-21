# {{project-name}}

{{project_description}}

# Layout

- `{{project-name}}/` - Main library crate
  - `src/` - Source
{%- if build_c_libs %}
  - `src/exports.rs` - C FFI exports
{%- endif %}
{%- if bench %}
  - `benches/` - Benchmarks
{%- endif %}
{%- if build_cli %}
- `cli/` - CLI binary
{%- endif %}
{%- if fuzz %}
- `fuzz/` - Fuzz targets
{%- endif %}
{%- if build_csharp_libs %}
- `bindings/csharp/` - C# bindings
{%- endif %}

# Code

- Optimize for CPU and memory.
- Use zero-cost abstractions, avoid allocations, prefer arrays when size is known.
- Preallocate/trim memory, prefer smaller types when possible.
- Keep modules under 500 lines (excluding tests and docs); split if larger.
- Function-local `use` only for `#[cfg]`.
{%- if no-std-by-default or std-by-default %}
- Prefer `core` over `std` where possible (e.g. `core::mem`).
{%- endif %}

# Docs

- Document public items with `///`
- Add doc examples when helpful
- Use `//!` for module docs
- Comments explain "why", not "what"
- Use [`TypeName`] links, not backticks.

# Verify

If you changed code, run `.cargo/verify.sh` or `.cargo/verify.ps1` before returning. It runs the full build/test/lint/docs/format suite.
