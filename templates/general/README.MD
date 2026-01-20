# {{project-name}}

## Additional Setup Required!!

<!-- DELETE THIS SECTION AFTER COMPLETING SETUP -->

Additional setup might be required.
Once you do the stuff under this text, delete this section.

### Code Coverage
To setup code coverage for this project:

1. Go to [Codecov][codecov], add your project.
2. Go to [Settings -> Secrets and variables -> Actions][gh-actions-secrets] in your repo and add a repository secret named `CODECOV_TOKEN`.
3. Do the same in [Settings -> Secrets and variables -> Dependabot][gh-actions-dependabot].

The instructions on the Codecov page will provide the token to use.

{% if mkdocs -%}
### Setup Documentation

Before you make your first commit to GitHub, you'll need to go to [Settings -> Pages][gh-pages] and set
`Source` to `GitHub Actions` for the documentation builds to work.

{% endif %}
{% if publish_crate_on_tag -%}
### Setup API Key (crates.io)

You'll need to set up an API key to publish to `crates.io` on tag.

- Generate your API key in [crates.io (Account Settings -> API Tokens)][crates-io-key].
- Go to [Settings -> Secrets and variables -> Actions][gh-actions-secrets] in your repo and add environment secret named `CRATES_IO_TOKEN`.
- Paste your API key.

{% if build_csharp_libs %}
### Setup API Key (NuGet)
You'll need to set up an API key to publish to `NuGet` on tag.

- Generate your API key in [Api Keys][nuget-key].
- Go to [Settings -> Secrets and variables -> Actions][gh-actions-secrets] in your repo and add a repository secret named `NUGET_KEY`.
{% endif %}
{% endif %}

### Enable Auto-Delete Merged Branches

Enable automatic deletion of merged branches:

```bash
gh repo edit --delete-branch-on-merge
```

Or via UI: **Settings > General > check "Automatically delete head branches"**

### Fill in README Documentation

This repository uses a two-level README structure:

| File | Purpose | What to Write |
|------|---------|---------------|
| `README.MD` (this file) | GitHub landing page | Project overview, quick start example, badges |
| [`src/{{project-name}}/README.MD`](./src/{{project-name}}/README.MD) | crates.io page | Detailed features, installation, comprehensive usage examples |

-----------------------

[![Crates.io](https://img.shields.io/crates/v/{{project-name}}.svg)](https://crates.io/crates/{{project-name}})
[![Docs.rs](https://docs.rs/{{project-name}}/badge.svg)](https://docs.rs/{{project-name}})
[![CI](https://github.com/{{gh_username}}/{{project-name}}/actions/workflows/rust.yml/badge.svg)](https://github.com/{{gh_username}}/{{project-name}}/actions)

{{project_description}}

## Quick Start

Add to your `Cargo.toml`:

```toml
[dependencies]
{{project-name}} = "0.1.0"
```

```rust
// TODO: Add a minimal example showing the most common use case
```

{%- if mkdocs %}
For detailed usage guides, see the [documentation][docs].
{%- else %}
See the [{{project-name}} crate documentation](./src/{{project-name}}/README.MD) for detailed usage.
{%- endif %}

## Crates

- [{{project-name}}](./src/{{project-name}}/README.MD): Core library <!-- TODO: Update description -->
{%- if build_cli %}
- [cli](./src/cli/README.MD): Command-line interface <!-- TODO: Update description -->
{%- endif %}

## Developer Manual

For step-by-step development guidance, see the [Developer Manual](https://reloaded-project.github.io/reloaded-templates-rust/manual/).

## Contributing

We welcome contributions! See the [Contributing Guide](https://reloaded-project.github.io/reloaded-templates-rust/manual/#contributing) for details.

## License

Licensed under [{{license}}](./LICENSE).

[codecov]: https://app.codecov.io
[gh-actions-secrets]: https://github.com/{{gh_username}}/{{project-name}}/settings/secrets/actions
[gh-actions-dependabot]: https://github.com/{{gh_username}}/{{project-name}}/settings/secrets/dependabot
[gh-pages]: https://github.com/{{gh_username}}/{{project-name}}/settings/pages
[crates-io-key]: https://crates.io/settings/tokens
[nuget-key]: https://www.nuget.org/account/apikeys
{%- if mkdocs %}
[docs]: https://{{gh_reponame}}.github.io/{{gh_reponame}} {%- endif %}
