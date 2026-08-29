---
hide:
  - toc
---

<div align="center">
	<h1>Reloaded Rust Templates</h1>
	<img src="assets/reloaded-logo.avif" width="150" align="center" />
	<br/> <br/>
    Opinionated Rust project generators for libraries and binaries.
    <br/>
    Built with <a href="https://github.com/cargo-generate/cargo-generate">cargo-generate</a>.
    <br/>
    Used by <a href="https://sewer56.dev">Sewer's Projects</a> and the <a href="https://reloaded-project.github.io/Reloaded-III/">Reloaded-III</a> framework.
</div>

## About

This template repository provides opinionated [Rust](https://www.rust-lang.org/) project generators for libraries and binaries using the [cargo-generate](https://github.com/cargo-generate/cargo-generate) tool.

These templates provide various features for getting up and running with cross platform Rust library or Reloaded3 mod development:

- Standardized README, Contributing Guidelines & Project Layout
- GitHub Issue and Pull Request templates
- VSCode Workflow & Integration with sane defaults
- Test, lint, audit, and code coverage via [Codecov](https://about.codecov.io/) GitHub Action workflows
- A choice of Apache, MIT, LGPLv3 or GPLv3 licenses
- [`cargo-bench`](https://doc.rust-lang.org/cargo/commands/cargo-bench.html) integration (*optional*)
- Cross-compilation & testing; including testing for Wine on Linux (*optional*)
- Profile Guided Optimization (*optional*)
- Native C exports (*optional*), and C# exports

## Project Templates

This repository contains two sub-templates:

- `general`: for generating a rust library, webserver, or binary/executable project
- `reloaded3`: for generating a [Reloaded-III](https://reloaded-project.github.io/Reloaded-III/) mod written in Rust. ~~2024~~, ~~2025~~, god knows

## Getting Started

Install [cargo-generate](https://github.com/cargo-generate/cargo-generate) via `cargo install cargo-generate`, and create project from template:

```bash
# This might take a while
cargo install cargo-generate
cargo generate --git https://github.com/Reloaded-Project/reloaded-templates-rust.git
```

The above command requires user input. For avoiding user input (important for automated usage), try something like:

```bash
cargo generate \
  --git https://github.com/Reloaded-Project/reloaded-templates-rust.git \
  templates/general \
  --name my-project \
  --destination . \
  --define gh_username=YourUsername \
  --define gh_reponame=my-project \
  --define "project_description=A brief description of your project" \
  --define mkdocs=false \
  --define vscode=true \
  --define xplat=false \
  --define wine=false \
  --define bench=false \
  --define miri=false \
  --define fuzz=false \
  --define build_c_libs=false \
  --define build_cli=false \
  --define publish_crate_on_tag=true \
  --define license=MIT \
  --define no_std_support=STD
```

!!! note "The `--destination` folder must already exist; it will not be auto-created."

More installation options are available [here](https://github.com/cargo-generate/cargo-generate#installation).

The experience running through the template should look something like this:

![cargo-generate Rust Binary Application Screenshot](assets/example-create.avif)

Once you generate a template, further instructions might await in your project's README file 😉.

!!! info "Code Editor Setup"

    After generating a project, open the project root in your code editor for development.

    Visit the manual generated in your project's README for editor setup details.

## Technical Questions

If you have questions/bug reports/etc. feel free to [Open an Issue](https://github.com/Reloaded-Project/reloaded-templates-rust/issues/new).

Happy Documenting ❤️