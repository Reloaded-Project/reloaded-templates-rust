#!/usr/bin/env python3
"""
Template testing script for cargo-generate templates.

This script generates Rust projects from templates and validates:
- File structure (conditional includes/excludes)
- File formats (JSON, TOML, YAML)
- Jinja2 template rendering completion
- Build validation (cargo check, build, test)
- MkDocs documentation builds
"""

import argparse
import json
import logging
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional, Tuple

# Import TOML parser (tomllib for Python 3.11+, tomli for older versions)
if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError:
        print(
            "Error: tomli package required for Python <3.11. Install with: pip install tomli",
            file=sys.stderr,
        )
        sys.exit(1)

# Import YAML parser
try:
    import yaml
except ImportError:
    print(
        "Error: PyYAML package required. Install with: pip install PyYAML",
        file=sys.stderr,
    )
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class TemplateTestConfig:
    """Configuration for template generation and testing."""

    def __init__(self, args: argparse.Namespace):
        self.project_name = args.project_name
        self.mkdocs = args.mkdocs
        self.vscode = args.vscode
        self.xplat = args.xplat
        self.big_endian = args.big_endian
        self.wine = args.wine
        self.bench = args.bench
        self.miri = args.miri
        self.fuzz = args.fuzz
        self.build_c_libs = args.build_c_libs
        self.build_csharp_libs = args.build_csharp_libs
        self.build_with_pgo = args.build_with_pgo
        self.build_cli = args.build_cli
        self.publish_crate_on_tag = args.publish_crate_on_tag
        self.license = args.license
        self.no_std = args.no_std


class TemplateValidator:
    """Validates generated template projects."""

    def __init__(self, project_path: Path, config: TemplateTestConfig):
        self.project_path = project_path
        self.config = config

    def validate_file_structure(self) -> bool:
        """Validate conditional file inclusion/exclusion."""
        logger.info("Validating file structure...")
        errors = 0

        # MkDocs validation (FIX: only check doc/mkdocs.yml, NOT root mkdocs.yml)
        if self.config.mkdocs:
            errors += self._check_exists("doc/mkdocs.yml", "Doc mkdocs.yml")
            errors += self._check_exists("doc/docs", "MkDocs source directory")
        else:
            errors += self._check_not_exists("doc", "Documentation directory")
            errors += self._check_not_exists(
                ".github/workflows/deploy-mkdocs.yml", "MkDocs deployment workflow"
            )

        # VSCode validation
        if self.config.vscode:
            errors += self._check_exists("src/.vscode/settings.json", "VSCode settings")
            errors += self._check_exists("src/.vscode/tasks.json", "VSCode tasks")
            if self.config.mkdocs:
                errors += self._check_exists(
                    "doc/.vscode/settings.json", "Doc VSCode settings"
                )
        else:
            errors += self._check_not_exists("src/.vscode", "VSCode directory")
            if self.config.mkdocs:
                errors += self._check_not_exists("doc/.vscode", "Doc VSCode directory")

        # C library validation
        if self.config.build_c_libs:
            errors += self._check_exists(
                f"src/{self.config.project_name}/src/exports.rs", "C exports file"
            )
            errors += self._check_exists(".github/cbindgen_c.toml", "cbindgen C config")
            errors += self._check_exists(
                ".github/cbindgen_cpp.toml", "cbindgen C++ config"
            )
        else:
            errors += self._check_not_exists(
                f"src/{self.config.project_name}/src/exports.rs", "C exports file"
            )
            errors += self._check_not_exists(
                ".github/cbindgen_c.toml", "cbindgen C config"
            )
            errors += self._check_not_exists(
                ".github/cbindgen_cpp.toml", "cbindgen C++ config"
            )
            errors += self._check_not_exists(
                "src/bindings/csharp", "C# bindings directory"
            )

        # C# bindings validation
        if self.config.build_csharp_libs and self.config.build_c_libs:
            errors += self._check_exists(
                "src/bindings/csharp/csharp.csproj", "C# project file"
            )
            errors += self._check_exists(
                "src/bindings/csharp/NativeMethods.cs", "C# native methods"
            )
        elif self.config.build_c_libs:
            errors += self._check_not_exists(
                "src/bindings/csharp", "C# bindings directory"
            )

        # Benchmark validation
        if self.config.bench:
            errors += self._check_exists(
                f"src/{self.config.project_name}/benches/my_benchmark",
                "Benchmark directory",
            )
            errors += self._check_exists(
                f"src/{self.config.project_name}/benches/my_benchmark/main.rs",
                "Benchmark main file",
            )
        else:
            errors += self._check_not_exists(
                f"src/{self.config.project_name}/benches", "Benchmark directory"
            )

        # Wine/Nix validation
        if self.config.wine:
            errors += self._check_exists("flake.nix", "Nix flake file")
        else:
            errors += self._check_not_exists("flake.nix", "Nix flake file")

        # Fuzz validation
        if self.config.fuzz:
            errors += self._check_exists("src/fuzz/Cargo.toml", "Fuzz Cargo.toml")
            errors += self._check_exists(
                "src/fuzz/fuzz_targets/fuzz_example.rs", "Fuzz example target"
            )
            errors += self._validate_fuzz_target_header()
            errors += self._validate_fuzz_tasks()
        else:
            errors += self._check_not_exists("src/fuzz", "Fuzz directory")

        # CLI validation
        if self.config.build_cli:
            errors += self._check_exists("src/cli/Cargo.toml", "CLI Cargo.toml")
            errors += self._check_exists("src/cli/src/main.rs", "CLI main.rs")
        else:
            errors += self._check_not_exists("src/cli", "CLI directory")

        # License validation
        errors += self._check_exists("LICENSE", "Main license file")
        errors += self._validate_license_content()
        errors += self._validate_license_cleanup()

        # Essential files validation
        errors += self._check_exists("src/Cargo.toml", "Workspace Cargo.toml")
        errors += self._check_exists(
            f"src/{self.config.project_name}/Cargo.toml", "Package Cargo.toml"
        )
        errors += self._check_exists(
            f"src/{self.config.project_name}/src/lib.rs", "Main library file"
        )
        errors += self._check_exists(".github/workflows/rust.yml", "Rust CI workflow")
        errors += self._check_exists(
            ".github/artifact-groups.yml", "Artifact groups config"
        )
        errors += self._check_exists(".github/changelog.hbs", "Changelog template")

        if errors == 0:
            logger.info("✓ File structure validation passed")
            return True
        else:
            logger.error(f"✗ File structure validation failed with {errors} error(s)")
            return False

    def _check_exists(self, path: str, description: str) -> int:
        """Check if a file or directory exists."""
        full_path = self.project_path / path
        if full_path.exists():
            logger.debug(f"✓ {description} exists")
            return 0
        else:
            logger.error(f"✗ {description} does not exist (expected: {path})")
            return 1

    def _check_not_exists(self, path: str, description: str) -> int:
        """Check if a file or directory does not exist."""
        full_path = self.project_path / path
        if not full_path.exists():
            logger.debug(f"✓ {description} does not exist (as expected)")
            return 0
        else:
            logger.error(f"✗ {description} exists but should not (found: {path})")
            return 1

    def _validate_license_content(self) -> int:
        """Validate LICENSE file contains expected content."""
        license_path = self.project_path / "LICENSE"
        if not license_path.exists():
            logger.error("✗ LICENSE file not found")
            return 1

        try:
            content = license_path.read_text()
            license_upper = self.config.license.upper()

            if license_upper == "MIT":
                if "MIT License" not in content:
                    logger.error("✗ LICENSE does not contain MIT License text")
                    return 1
            elif license_upper == "APACHE 2.0":
                if "Apache License" not in content:
                    logger.error("✗ LICENSE does not contain Apache License text")
                    return 1
            elif license_upper.startswith("GPL"):
                if (
                    "GNU General Public License" not in content
                    and "GNU GENERAL PUBLIC LICENSE" not in content
                ):
                    logger.error("✗ LICENSE does not contain GPL License text")
                    return 1
            elif license_upper.startswith("LGPL"):
                if (
                    "GNU Lesser General Public License" not in content
                    and "GNU LESSER GENERAL PUBLIC LICENSE" not in content
                ):
                    logger.error("✗ LICENSE does not contain LGPL License text")
                    return 1

            logger.debug(f"✓ License content valid for {self.config.license}")
            return 0
        except Exception as e:
            logger.error(f"✗ Error reading LICENSE file: {e}")
            return 1

    def _validate_license_cleanup(self) -> int:
        """Validate unused license files were deleted."""
        errors = 0
        license_upper = self.config.license.upper()

        # Map of license files that should NOT exist based on selected license
        if license_upper == "MIT":
            unwanted = [
                "LICENSE-APACHE",
                "LICENSE-GPL3",
                "LICENSE-GPL3-R",
                "LICENSE-LGPL3",
            ]
        elif license_upper == "APACHE 2.0":
            unwanted = [
                "LICENSE-MIT",
                "LICENSE-GPL3",
                "LICENSE-GPL3-R",
                "LICENSE-LGPL3",
            ]
        elif license_upper == "GPL V3":
            unwanted = [
                "LICENSE-MIT",
                "LICENSE-APACHE",
                "LICENSE-GPL3-R",
                "LICENSE-LGPL3",
            ]
        elif license_upper == "GPL V3 (WITH RELOADED FAQ)":
            unwanted = [
                "LICENSE-MIT",
                "LICENSE-APACHE",
                "LICENSE-GPL3",
                "LICENSE-LGPL3",
            ]
        elif license_upper == "LGPL V3":
            unwanted = [
                "LICENSE-MIT",
                "LICENSE-APACHE",
                "LICENSE-GPL3",
                "LICENSE-GPL3-R",
            ]
        else:
            unwanted = []

        for license_file in unwanted:
            errors += self._check_not_exists(license_file, f"Unused {license_file}")

        return errors

    def _validate_fuzz_target_header(self) -> int:
        """Validate fuzz target file has proper header comment."""
        fuzz_target = self.project_path / "src/fuzz/fuzz_targets/fuzz_example.rs"
        if not fuzz_target.exists():
            logger.error("✗ Fuzz target file not found for header validation")
            return 1

        try:
            content = fuzz_target.read_text()
            errors = 0

            # Check for tutorial URL
            if (
                "https://rust-fuzz.github.io/book/cargo-fuzz/tutorial.html"
                not in content
            ):
                logger.error("✗ Fuzz target missing cargo-fuzz tutorial URL in header")
                errors += 1

            # Check for run command
            if "cargo +nightly fuzz run fuzz_example" not in content:
                logger.error("✗ Fuzz target missing run command in header")
                errors += 1

            if errors == 0:
                logger.debug("✓ Fuzz target header validation passed")
            return errors
        except Exception as e:
            logger.error(f"✗ Error reading fuzz target file: {e}")
            return 1

    def _validate_fuzz_tasks(self) -> int:
        """Validate VSCode tasks for fuzzing."""
        if not self.config.vscode:
            return 0

        tasks_file = self.project_path / "src/.vscode/tasks.json"
        if not tasks_file.exists():
            logger.error("✗ VSCode tasks.json not found for fuzz task validation")
            return 1

        try:
            with open(tasks_file, "r") as f:
                content = f.read()

            errors = 0

            # Check that "Run Fuzzer" task is NOT present
            if '"label": "Run Fuzzer"' in content:
                logger.error("✗ tasks.json should not contain 'Run Fuzzer' task")
                errors += 1

            # Check that "List Fuzz Targets" task IS present
            if '"label": "List Fuzz Targets"' not in content:
                logger.error("✗ tasks.json missing 'List Fuzz Targets' task")
                errors += 1

            if errors == 0:
                logger.debug("✓ Fuzz tasks validation passed")
            return errors
        except Exception as e:
            logger.error(f"✗ Error reading tasks.json: {e}")
            return 1

    def validate_file_formats(self) -> bool:
        """Validate all JSON, TOML, and YAML files are well-formed."""
        logger.info("Validating file formats...")
        errors = 0

        # Validate JSON files
        for json_file in self.project_path.rglob("*.json"):
            if "vendor" in json_file.parts:
                continue
            logger.debug(f"Checking JSON: {json_file.relative_to(self.project_path)}")
            try:
                with open(json_file, "r") as f:
                    json.load(f)
            except Exception as e:
                logger.error(
                    f"✗ Invalid JSON: {json_file.relative_to(self.project_path)}: {e}"
                )
                errors += 1

        # Validate TOML files
        for toml_file in self.project_path.rglob("*.toml"):
            if "vendor" in toml_file.parts:
                continue
            logger.debug(f"Checking TOML: {toml_file.relative_to(self.project_path)}")
            try:
                with open(toml_file, "rb") as f:
                    tomllib.load(f)
            except Exception as e:
                logger.error(
                    f"✗ Invalid TOML: {toml_file.relative_to(self.project_path)}: {e}"
                )
                errors += 1

        # Validate YAML files (skip mkdocs.yml - contains MkDocs-specific YAML tags)
        for yaml_file in list(self.project_path.rglob("*.yml")) + list(
            self.project_path.rglob("*.yaml")
        ):
            # Skip mkdocs.yml specifically (contains MkDocs-specific !!python/name: tags)
            if yaml_file.name == "mkdocs.yml":
                continue
            logger.debug(f"Checking YAML: {yaml_file.relative_to(self.project_path)}")
            try:
                with open(yaml_file, "r") as f:
                    yaml.safe_load(f)
            except Exception as e:
                logger.error(
                    f"✗ Invalid YAML: {yaml_file.relative_to(self.project_path)}: {e}"
                )
                errors += 1

        if errors == 0:
            logger.info("✓ File format validation passed")
            return True
        else:
            logger.error(f"✗ File format validation failed with {errors} error(s)")
            return False

    def check_jinja2_remnants(self) -> bool:
        """Check for unconverted Jinja2 template syntax.

        This method detects Jinja2 template remnants ({{ }} and {% %}) in generated files
        while excluding GitHub Actions expressions (${{ }}) to avoid false positives.
        """
        logger.info("Checking for Jinja2 template remnants...")

        patterns = [r"\{%", r"\{\{"]
        extensions = ["*.yml", "*.yaml", "*.toml", "*.json", "*.rs", "*.md"]

        remnants = []
        for ext in extensions:
            for file_path in self.project_path.rglob(ext):
                # Skip vendor directories
                if "vendor" in file_path.parts or ".git" in file_path.parts:
                    continue

                try:
                    content = file_path.read_text()
                    for i, line in enumerate(content.splitlines(), 1):
                        # Skip comments (simple heuristic)
                        if line.strip().startswith("#") or line.strip().startswith(
                            "//"
                        ):
                            continue

                        # Skip lines with GitHub Actions expressions
                        if "${{" in line:
                            continue

                        for pattern in patterns:
                            if re.search(pattern, line):
                                remnants.append(
                                    f"{file_path.relative_to(self.project_path)}:{i}: {line.strip()}"
                                )
                except Exception as e:
                    logger.warning(f"Could not read {file_path}: {e}")

        if remnants:
            logger.error("✗ Found Jinja2 template remnants:")
            for remnant in remnants:
                logger.error(f"  {remnant}")
            return False
        else:
            logger.info("✓ No Jinja2 remnants found")
            return True

    def validate_builds(self) -> bool:
        """Run cargo check, build, and test."""
        logger.info("Validating Rust builds...")

        src_dir = self.project_path / "src"
        if not src_dir.exists():
            logger.error("✗ src/ directory not found")
            return False

        # Run cargo check
        logger.info("Running cargo check...")
        result = subprocess.run(
            ["cargo", "check"],
            cwd=src_dir,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if result.returncode != 0:
            logger.error("✗ cargo check failed")
            logger.error(result.stderr)
            return False
        logger.info("✓ cargo check passed")

        # Run cargo build
        logger.info("Running cargo build...")
        result = subprocess.run(
            ["cargo", "build"],
            cwd=src_dir,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if result.returncode != 0:
            logger.error("✗ cargo build failed")
            logger.error(result.stderr)
            return False
        logger.info("✓ cargo build passed")

        # Run cargo test
        logger.info("Running cargo test...")
        result = subprocess.run(
            ["cargo", "test"],
            cwd=src_dir,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if result.returncode != 0:
            logger.error("✗ cargo test failed")
            logger.error(result.stderr)
            return False
        logger.info("✓ cargo test passed")

        return True

    def validate_v1_1_4_template_updates(self) -> bool:
        """Validate v1.1.4 template changes: format-check job, simplified AGENTS.md, guidance files, verify headers."""
        logger.info("Validating v1.1.4 template updates...")
        errors = 0

        workflow_path = self.project_path / ".github" / "workflows" / "rust.yml"
        if workflow_path.exists():
            workflow_text = workflow_path.read_text()

            if "format-check:" not in workflow_text:
                logger.error("✗ Missing format-check job in workflow")
                errors += 1

            if "Run formatter check" in workflow_text:
                lines_after_build = False
                for line in workflow_text.splitlines():
                    if "build-and-test:" in line:
                        lines_after_build = True
                    if lines_after_build and "Run formatter check" in line:
                        logger.error(
                            "✗ Formatter step still present in build-and-test job"
                        )
                        errors += 1
                        break

            if "needs:" in workflow_text:
                found_publish_needs = False
                for line in workflow_text.splitlines():
                    stripped = line.strip()
                    if (
                        "needs:" in stripped
                        and "format-check" in stripped
                        and "build-and-test" in stripped
                    ):
                        found_publish_needs = True
                        break
                if not found_publish_needs:
                    logger.error("✗ publish-crate needs does not include format-check")
                    errors += 1
        else:
            logger.error("✗ Workflow file not found")
            errors += 1

            agents_path = self.project_path / "src" / "AGENTS.md"
            if agents_path.exists():
                agents_text = agents_path.read_text().strip()
                expected_lines = [
                    "After changes, run `.cargo/verify.{sh,ps1}` before returning.",
                    "If relevant to your review task, read `.cargo/{general,performance,documentation}.md`.",
                ]
                actual_lines = agents_text.splitlines()
                if actual_lines != expected_lines:
                    logger.error(
                        f"✗ src/AGENTS.md content mismatch. Got {len(actual_lines)} lines: {actual_lines}"
                    )
                    errors += 1
            else:
                logger.error("✗ src/AGENTS.md not found")
                errors += 1

        guidance_files = [
            ("src/.cargo/general.md", "# General Rules"),
            ("src/.cargo/performance.md", "# Performance Rules"),
            ("src/.cargo/documentation.md", "# Documentation Rules"),
        ]
        for rel_path, heading in guidance_files:
            file_path = self.project_path / rel_path
            if not file_path.exists():
                logger.error(f"✗ Guidance file not found: {rel_path}")
                errors += 1
            else:
                content = file_path.read_text()
                if heading not in content:
                    logger.error(
                        f"✗ Guidance file {rel_path} missing heading: {heading}"
                    )
                    errors += 1

        gitignore_path = self.project_path / ".gitignore"
        if gitignore_path.exists():
            gitignore_text = gitignore_path.read_text()
            if "src/.vscode/local-reviews/" not in gitignore_text:
                logger.error("✗ .gitignore missing local-reviews path")
                errors += 1
        else:
            logger.error("✗ .gitignore not found")
            errors += 1

        for verify_rel in ["src/.cargo/verify.sh", "src/.cargo/verify.ps1"]:
            verify_path = self.project_path / verify_rel
            if verify_path.exists():
                verify_text = verify_path.read_text()
                if (
                    "Script is relative to git repo root; search if not found"
                    not in verify_text
                ):
                    logger.error(f"✗ {verify_rel} missing new path comment")
                    errors += 1
            else:
                logger.error(f"✗ {verify_rel} not found")
                errors += 1

        if errors == 0:
            logger.info("✓ v1.1.4 template updates validation passed")
            return True
        else:
            logger.error(
                f"✗ v1.1.4 template updates validation failed with {errors} error(s)"
            )
            return False

    def validate_mkdocs(self) -> bool:
        """Validate MkDocs documentation builds."""
        if not self.config.mkdocs:
            logger.debug("Skipping MkDocs validation (mkdocs=false)")
            return True

        logger.info("Validating MkDocs build...")

        doc_dir = self.project_path / "doc"
        if not doc_dir.exists():
            logger.error("✗ doc/ directory not found")
            return False

        # Run mkdocs build --strict
        logger.info("Running mkdocs build --strict...")
        result = subprocess.run(
            [sys.executable, "-m", "mkdocs", "build", "--strict"],
            cwd=doc_dir,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if result.returncode != 0:
            logger.error("✗ mkdocs build failed")
            logger.error(result.stderr)
            return False
        logger.info("✓ mkdocs build passed")

        return True


def generate_project(
    config: TemplateTestConfig, temp_dir: Path
) -> Tuple[bool, Optional[Path]]:
    """Generate project using cargo-generate."""
    logger.info("Generating project with cargo-generate...")
    logger.info(
        f"Configuration: project={config.project_name}, mkdocs={config.mkdocs}, vscode={config.vscode}"
    )

    # Get repository root (two levels up from .github/tests/)
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent.parent
    template_path = repo_root / "templates" / "general"

    if not template_path.exists():
        logger.error(f"Template path not found: {template_path}")
        return False, None

    # Build cargo-generate command
    # FIX: Use --name for project name and --destination for output directory
    cmd = [
        "cargo",
        "generate",  # Two separate words, not hyphenated
        "--path",
        str(template_path),
        "--name",
        config.project_name,  # Project name (NOT a path)
        "--destination",
        str(temp_dir),  # Where to generate
        "--define",
        f"gh_username=test-user",
        "--define",
        f"gh_reponame=test-repo",
        "--define",
        f"project_description=Test project for template validation",
        "--define",
        f"mkdocs={str(config.mkdocs).lower()}",
        "--define",
        f"vscode={str(config.vscode).lower()}",
        "--define",
        f"xplat={str(config.xplat).lower()}",
        "--define",
        f"wine={str(config.wine).lower()}",
        "--define",
        f"bench={str(config.bench).lower()}",
        "--define",
        f"miri={str(config.miri).lower()}",
        "--define",
        f"fuzz={str(config.fuzz).lower()}",
        "--define",
        f"build_c_libs={str(config.build_c_libs).lower()}",
        "--define",
        f"build_cli={str(config.build_cli).lower()}",
        "--define",
        f"publish_crate_on_tag={str(config.publish_crate_on_tag).lower()}",
        "--define",
        f"license={config.license}",
        "--define",
        f"no_std_support={config.no_std}",
    ]

    # Add conditional parameters
    if config.xplat:
        cmd.extend(["--define", f"big_endian={str(config.big_endian).lower()}"])

    if config.build_c_libs:
        cmd.extend(
            ["--define", f"build_csharp_libs={str(config.build_csharp_libs).lower()}"]
        )

    if config.bench and (config.build_c_libs or config.build_cli):
        cmd.extend(["--define", f"build_with_pgo={str(config.build_with_pgo).lower()}"])

    logger.debug(f"Running: {' '.join(cmd)}")

    # Run cargo-generate
    result = subprocess.run(
        cmd, capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    if result.returncode != 0:
        logger.error("✗ cargo-generate failed")
        logger.error(result.stderr)
        return False, None

    generated_path = temp_dir / config.project_name
    if not generated_path.exists():
        logger.error(f"✗ Generated project not found at {generated_path}")
        return False, None

    logger.info(f"✓ Project generated successfully at {generated_path}")
    return True, generated_path


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Test cargo-generate library template generation and validation"
    )

    # Required arguments
    parser.add_argument(
        "--project-name",
        required=True,
        help="Project name (must be valid Rust crate name)",
    )

    # Boolean configuration flags
    parser.add_argument(
        "--mkdocs",
        type=lambda x: x.lower() == "true",
        default=True,
        help="Include external documentation (default: true)",
    )
    parser.add_argument(
        "--vscode",
        type=lambda x: x.lower() == "true",
        default=True,
        help="Include VSCode configurations (default: true)",
    )
    parser.add_argument(
        "--xplat",
        type=lambda x: x.lower() == "true",
        default=True,
        help="Include cross-platform testing (default: true)",
    )
    parser.add_argument(
        "--big-endian",
        type=lambda x: x.lower() == "true",
        default=False,
        help="Include big-endian support (default: false)",
    )
    parser.add_argument(
        "--wine",
        type=lambda x: x.lower() == "true",
        default=True,
        help="Run tests against Wine (default: true)",
    )
    parser.add_argument(
        "--bench",
        type=lambda x: x.lower() == "true",
        default=True,
        help="Include benchmark configuration (default: true)",
    )
    parser.add_argument(
        "--miri",
        type=lambda x: x.lower() == "true",
        default=False,
        help="Include Miri for unsafe code detection (default: false)",
    )
    parser.add_argument(
        "--fuzz",
        type=lambda x: x.lower() == "true",
        default=False,
        help="Include fuzz testing configuration (default: false)",
    )
    parser.add_argument(
        "--build-c-libs",
        type=lambda x: x.lower() == "true",
        default=True,
        help="Build C libraries in CI (default: true)",
    )
    parser.add_argument(
        "--build-csharp-libs",
        type=lambda x: x.lower() == "true",
        default=False,
        help="Build C# bindings (default: false)",
    )
    parser.add_argument(
        "--build-with-pgo",
        type=lambda x: x.lower() == "true",
        default=True,
        help="Enable PGO (Profile Guided Optimization) (default: true)",
    )
    parser.add_argument(
        "--build-cli",
        type=lambda x: x.lower() == "true",
        default=False,
        help="Include CLI executable wrapper project (default: false)",
    )
    parser.add_argument(
        "--publish-crate-on-tag",
        type=lambda x: x.lower() == "true",
        default=True,
        help="Publish to crates.io on tag (default: true)",
    )

    # String configuration flags
    parser.add_argument(
        "--license",
        default="GPL v3 (with Reloaded FAQ)",
        help="License type (default: 'GPL v3 (with Reloaded FAQ)')",
    )
    parser.add_argument(
        "--no-std", default="STD", help="no_std support option (default: 'STD')"
    )

    return parser.parse_args()


def main() -> int:
    """Main entry point."""
    args = parse_args()
    config = TemplateTestConfig(args)

    # Create temporary directory
    temp_dir = Path(tempfile.mkdtemp(prefix="template-test-"))
    logger.info(f"Using temporary directory: {temp_dir}")

    try:
        # Generate project
        success, project_path = generate_project(config, temp_dir)
        if not success or project_path is None:
            return 1

        # Validate project
        validator = TemplateValidator(project_path, config)

        all_passed = True
        all_passed &= validator.validate_file_structure()
        all_passed &= validator.validate_file_formats()
        all_passed &= validator.check_jinja2_remnants()
        all_passed &= validator.validate_v1_1_4_template_updates()
        all_passed &= validator.validate_builds()
        all_passed &= validator.validate_mkdocs()

        if all_passed:
            logger.info("✨ All validations passed!")
            return 0
        else:
            logger.error("❌ Some validations failed")
            return 1

    finally:
        # Always cleanup
        logger.info(f"Cleaning up temporary directory: {temp_dir}")
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
