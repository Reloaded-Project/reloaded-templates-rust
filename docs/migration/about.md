# About

This is the documentation for the Reloaded Rust templates.

## Migration Guides

!!! important "Migration Order"
    If you need to migrate across multiple versions, please follow the migration guides in chronological order.
    
    Each guide assumes you have completed all previous migrations.

For information about migrating between template versions, see the following guides:

- **[v1.0.0]** - Migrate from pre-v1 versions to v1.0.0
- **[v1.0.1]** - Update AGENTS.md post-change verification commands
- **[v1.1.0]** - Script-based verification, auto-delete branches, lighter docs
- **[v1.1.1]** - Code guideline clarifications for performance and memory
- **[v1.1.2]** - Add publish dry-run verification with --allow-dirty
- **[v1.1.3]** - Fix verification scripts, disable YAML format-on-save, split CLI builds
- **[v1.1.4]** - Simplified AGENTS.md structure, separated formatter CI job, review guidance files
- **[v1.1.5]** - Remove conditional from documentation check for rustdoc cache effectiveness
- **[v1.2.0]** - Move documentation into `src/`
- **[v1.3.0]** - Project root becomes the workspace: docs to `doc/`, manifest to root, `.cargo` to `.llm`
- **[v1.4.0]** - Add rust-llm-tidy CI: auto-tidies changed files on pull requests
- **[v1.4.1]** - Remove root `AGENTS.md` shim, move style rule to `.llm/general.md`
- **[v1.4.2]** - Slim `.llm` guidance, tidy in verify, `core` over `std` lint
- **[v1.4.3]** - Verify scripts run the file-altering steps first

[v1.0.0]: v1.0.0.md
[v1.0.1]: v1.0.1.md
[v1.1.0]: v1.1.0.md
[v1.1.1]: v1.1.1.md
[v1.1.2]: v1.1.2.md
[v1.1.3]: v1.1.3.md
[v1.1.4]: v1.1.4.md
[v1.1.5]: v1.1.5.md
[v1.2.0]: v1.2.0.md
[v1.3.0]: v1.3.0.md
[v1.4.0]: v1.4.0.md
[v1.4.1]: v1.4.1.md
[v1.4.2]: v1.4.2.md
[v1.4.3]: v1.4.3.md
