# {{project-name}}

[![Crates.io](https://img.shields.io/crates/v/{{project-name}}.svg)](https://crates.io/crates/{{project-name}})
[![Docs.rs](https://docs.rs/{{project-name}}/badge.svg)](https://docs.rs/{{project-name}})
[![CI](https://github.com/{{gh_username}}/{{project-name}}/actions/workflows/rust.yml/badge.svg)](https://github.com/{{gh_username}}/{{project-name}}/actions)

-----------------------

## Additional Setup Required!!

Additional setup might be required.  
Once you do the stuff under this text, delete this section.  

### Code Coverage
To setup code coverage for this project. Login into [Codecov][codecov] and add this repository from your list of tracked repos.

{% if mkdocs -%}
### Setup Documentation

If you don't have a `docs/Reloaded` folder, you might need to add it manually as submodule:

```
git submodule add https://github.com/Reloaded-Project/Reloaded.MkDocsMaterial.Themes.R2.git docs/Reloaded
```

After which you can follow the [Theme Documentation](https://reloaded-project.github.io/Reloaded.MkDocsMaterial.Themes.R2/Pages/contributing.html#website-live-preview) to find out how to work with the docs.

Before you make your first commit to GitHub, you'll need to go to `Settings -> Pages` and set
`Source` to `GitHub Actions` for the documentation builds to work.

{% endif %}
{% if publish_crate_on_tag -%}
### Setup API Key (crates.io)

You'll need to set up an API key to publish to `crates.io` on tag.

- Go to `Settings -> Secrets -> Actions` in your repo and add environment secret named `CRATES_IO_TOKEN`.  
- Paste your API key generated in [crates.io (Account Settings -> API Tokens)][crates-io-key].  

{% if build_csharp_libs %}
### Setup API Key (NuGet)
You'll need to set up an API key to publish to `NuGet` on tag.

- Go to `Settings -> Secrets -> Actions` in your repo and add environment secret named `NUGET_KEY`.  
- Paste your API key generated in [Api Keys][nuget-key].  
{% endif %}
{% endif %}

-----------------------

## About

{{project_description}}
{% if mkdocs %}
You can learn more about this project in the [dedicated documentation page][docs].
{% endif %}
## Development

How to develop this project.

***Clone this Repository:***
```bash
# When cloning, make sure symlinks are enabled
git clone -c core.symlinks=true https://github.com/{{gh_username}}/{{project-name}}.git
```

***Install Rust:***
- Install the [Rust Toolchain.][rust-toolchain]  

{%- if vscode -%}
***Setup IDE***
- This repository is fully with VSCode. [Guidance below](#visual-studio-code-integration).
{% endif %}
{%- if vscode -%}

### Visual Studio Code Integration

`Code`/`VSCode` is the de-facto Rust development environment.  

The following extensions are required:  
- [rust-analyzer][rust-analyzer] for Rust support.  
- [coverage-gutters][coverage-gutters] for Coverage support.  
- [CodeLLDB][codelldb] for debugging.  
- [crates](https://marketplace.visualstudio.com/items?itemName=serayuzgur.crates) easier dependency management.  

The VSCode configuration in Reloaded projects (`.vscode`) contain the following:  
- Run Rust linter `clippy` on Save.  
- Run code format `rustfmt` on Save.  
- Tasks for common operations (generate documentation, active CI/CD etc.).  

These configurations are in the `.vscode` folder; and the tasks can be ran via `Ctrl+Shift+P -> Run Task`.  

#### Test Coverage

First install or update `tarpaulin`:

```bash
cargo install cargo-tarpaulin
```

To run Coverage, run task (`Ctrl+Shift+P -> Run Task`), you should see something similar to: 

| Task                   | Description                                                                |
| ---------------------- | -------------------------------------------------------------------------- |
| Cargo Watch Tarpaulin  | Automatically runs tests and updates coverage on save.                     |
| Generate Code Coverage | Manually generate code coverage (`cobertura.xml`, `tarpaulin-report.html`) |

The `tarpaulin-report.html` file can be opened in VSCode (`Show Preview`) for a live view.

For GUI integration, run action `Coverage Gutter: Watch` (in `Ctrl+Shift+P` actions menu).

{% if bench -%}
## Debugging Benchmarks

If you wish to debug benchmarks in VSCode, go to `Run and Debug` Menu and generate the launch 
profiles, you should get one for debugging benchmarks.

## Profiling Benchmarks

### Linux/OSX

Execute the following:

```
cargo bench --bench my_benchmark --profile profile -- --profile-time 10
```

This should give you a flamegraph in `target/criterion/<method_name>/profile`. You can open that flamegraph in a web browser.

### Windows

Execute the following:

```
cargo bench --bench my_benchmark --no-run --profile profile
```

Navigate to the executable listed in the commandline:

```
target/profile/deps/my_benchmark-eced832ac8f31257.exe
```

And run with command `my_benchmark-eced832ac8f31257.exe --bench --profile-time 10` under an external profiler, such as Visual Studio.  (in VS, Debug -> Performance Profiler)

![example](./assets/profile_example.png)

{% endif -%}
{% endif -%}

{% if build_c_libs -%}

## Building C Libraries Locally

Reloaded-based C libraries are built with `panic=abort` and self-built STD to minimize binary size.

First get the prerequisites (nightly rust).

```
rustup toolchain install nightly
rustup component add rust-src --toolchain nightly
```

To build C library locally, run the following command:

```
RUSTFLAGS="-C panic=abort -C lto=fat -C embed-bitcode=yes" cargo +nightly rustc -Z build-std=std,panic_abort -Z build-std-features=panic_immediate_abort --crate-type cdylib --crate-type staticlib --target x86_64-unknown-linux-gnu
```

Replace `x86_64-unknown-linux-gnu` with your [target triple][target-triple].

## Optimizing for Size when Creating C Libraries

1. Add `"cdylib"` crate type to `Cargo.toml` (temporarily!! do not commit)

```
[lib]
crate-type = ["cdylib"]
```

Install `cargo-bloat`, `nightly toolchain` and `build-std`:

```
cargo install cargo-bloat
rustup toolchain install nightly
rustup component add rust-src --toolchain nightly
```

Run `cargo-bloat` the following command to calculate package size:

```
RUSTFLAGS="-C panic=abort -C lto=fat -C embed-bitcode=yes" cargo +nightly bloat -Z build-std=std,panic_abort -Z build-std-features=panic_immediate_abort --target x86_64-pc-windows-gnu --profile profile --crate-type cdylib -n 100 --features c-exports
```

Change `--target` if needed for your platform.  
This should produce binaries more appropriate for dynamic linking from C.  

{% endif -%}

{% if build_c_libs-with-pgo -%}

## PGO (Profile Guided Optimization) on C Libraries

This Reloaded-based library is built with [Profile Guided Optimization (PGO)](https://doc.rust-lang.org/rustc/profile-guided-optimization.html).

PGO is a compiler optimization technique that uses data from profiling runs to improve the quality of the generated code.

Details of the PGO implementation in this project are as follows:

- We collect PGO data by running the `benchmarks` with the `pgo` feature enabled.
- This is done in CI, before building the final C library.

You should ensure that only realistic representative workloads are used to collect the PGO data.

For example, if this was a compression library, you should run the 'compress' and 'decompress' methods
on real files (not random data) as part of your benchmarks. 

Non-realistic/representative workloads in benchmarks should be excluded through the 'pgo' feature flag,
for example an unrealistic benchmark can be excluded like this:

```rust
#[cfg(not(feature = "pgo"))]
{
    bench_create_dict(c);
}
```

### Testing PGO

PGO isn't guaranteed to always provide an improvement, after adding representative workloads, always test.

We will test with `cargo pgo`.

First, install the following:

```
cargo install cargo-pgo
rustup toolchain install nightly
rustup component add llvm-tools-preview
```

Then run an 'instrumented' benchmark, this will run your code in `pgo_benchmark` and collect some data:

```
cargo +nightly pgo instrument bench
```

After that run a regular benchmark to create a 'baseline' number:

```
cargo +nightly bench
```

And run the PGO optimized build:

```
cargo +nightly pgo optimize bench
```

If most of the results are equal or show an improvement, PGO has helped.
Otherwise disable PGO from the library by editing the [rust.yml](./.github/workflows/rust.yml) workflow.

{% endif -%}

{% if build_csharp_libs -%}
## C# Bindings for {{crate_name}}

This Reloaded-based project provides C# bindings, as [{{crate_name}}.Net.Sys](https://www.nuget.org/packages/{{crate_name}}.Net.Sys).

These are the raw bindings to the C exports of this Rust library, and are automatically generated.

The project is inside `bindings/csharp` folder. 
It shouldn't be modified. 

Instead, if you want to make a 'friendlier' API, make a separate project with 
[{{crate_name}}.Net.Sys](https://www.nuget.org/packages/{{crate_name}}.Net.Sys) as a dependency,
and provide high level bindings.
{% endif %}
## File Layout

The following is the expected file layout for your project:

```
{%- if vscode %}
.vscode/{%- endif %}
{%- if mkdocs %}
docs/{%- endif %}
src/
Cargo.toml
{%- if mkdocs %}
mkdocs.yml{%- endif %}
```

{% if mkdocs -%}
The `docs` folder, and `mkdocs.yml` contain [MkDocs Material documentation][mkdocs-material] for your project.  
{% endif -%}
The `src` folder should contains all source code for your project.  

`Cargo.toml` should be in the root of the project.  
{% if xplat -%}

## Cross Platform Targeting

Some templates allow for cross platform development.  

To work with cross-platform code, where you need to access OS specific APIs, some helper scripts are provided.  

### Including All Code Paths

To include all code paths for local builds, consider editing `.cargo/config.toml`.

```toml
[build]
# Note: This breaks IntelliJ Rust. Remove this line temporarily if working from that IDE.
target = ['x86_64-unknown-linux-gnu','x86_64-apple-darwin','x86_64-pc-windows-gnu']
```

You might need to install the targets first:

```bash
rustup target add x86_64-unknown-linux-gnu
rustup target add x86_64-apple-darwin
rustup target add x86_64-pc-windows-gnu
```

Now when you run `cargo build`, it will build code for all platforms; and you'll get your compiler errors, warnings etc.

### Cross Testing on Local Machine

#### Prerequisites (Windows)

- Install [Docker Desktop](https://www.docker.com/products/docker-desktop/).  
- Disable WSL 2 (Docker Desktop -> Settings -> General -> Use the WSL 2 based engine).  

#### Prerequisites (Linux)

- Install [Podman](https://podman.io) from your package manager.  

#### Prerequisites (Common)

Install cross

```
cargo install cross
```

#### Running Cross-Platform Tests

Use the provided `pwsh` scripts in `scripts` folder.

- `./test-wine-x64.ps1`: Tests your code in Wine on x86_64.  
- `./test-linux-x64.ps1`: Tests your code in Linux on x86_64.  
- `./test-linux-x86.ps1`: Tests your code in Linux on x86.  

These scripts can be used on any platform given the prerequisites are met.  
If you need to test Apple stuff without an Apple machine, you're generally out of luck outside of using CI/CD for testing.  
{% endif %}
## Releasing a New Version

Make a tag, aptly named after the current version of the project. For instance, if you are publishing version `0.1.0`, the tag should be `0.1.0`. This will create a GitHub release for you automatically.

## Contributing

See [CONTRIBUTING](CONTRIBUTING.MD) for guidance on how to contribute to this project.  

{%- if mkdocs %}
## Updating the Documentation

For the latest instructions on updating the documentation (docs), see the [Relevant Doc Page].
{%- endif %}

## License

Licensed under [{{license}}](./LICENSE).  

[Learn more about Reloaded's general choice of licensing for projects.][reloaded-license].  

[codecov]: https://about.codecov.io/
[codelldb]: https://marketplace.visualstudio.com/items?itemName=vadimcn.vscode-lldb
[coverage-gutters]: https://marketplace.visualstudio.com/items?itemName=ryanluker.vscode-coverage-gutters 
[crates-io-key]: https://crates.io/settings/tokens
[nuget-key]: https://www.nuget.org/account/apikeys
[target-triple]: https://doc.rust-lang.org/nightly/rustc/platform-support.html
{%- if mkdocs %}
[docs]: https://{{gh_reponame}}.github.io/{{gh_reponame}}
[mkdocs-material]: https://squidfunk.github.io/mkdocs-material/
[Relevant Doc Page]: https://{{gh_reponame}}.github.io/{{gh_reponame}}/Reloaded/Pages/contributing {%- endif %}
[reloaded-license]: https://reloaded-project.github.io/Reloaded.MkDocsMaterial.Themes.R2/Pages/license/
[rust-analyzer]: https://marketplace.visualstudio.com/items?itemName=rust-lang.rust-analyzer
[rust-toolchain]: https://www.rust-lang.org/tools/install
