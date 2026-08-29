#!/usr/bin/env python3
"""
Test runner for template testing suite.
Creates virtual environment and runs tests locally.

This script handles:
- Virtual environment creation and dependency installation
- Integration test execution with multiple configurations
- Cross-platform support (Windows, Linux, macOS, NixOS)
"""

import argparse
import subprocess
import sys
import os
import time
from pathlib import Path
from typing import Dict, Any, Optional


class Colors:
    """ANSI color codes for terminal output."""
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'


def print_success(message: str) -> None:
    """Print success message in green."""
    print(f"{Colors.GREEN}OK {message}{Colors.RESET}")


def print_error(message: str) -> None:
    """Print error message in red."""
    print(f"{Colors.RED}FAIL {message}{Colors.RESET}")


def print_info(message: str) -> None:
    """Print info message in cyan."""
    print(f"{Colors.CYAN}INFO {message}{Colors.RESET}")


def print_warning(message: str) -> None:
    """Print warning message in yellow."""
    print(f"{Colors.YELLOW}WARN {message}{Colors.RESET}")


def print_section(message: str) -> None:
    """Print section header in magenta."""
    print(f"\n{Colors.MAGENTA}{'=' * 72}{Colors.RESET}")
    print(f"{Colors.MAGENTA}  {message}{Colors.RESET}")
    print(f"{Colors.MAGENTA}{'=' * 72}{Colors.RESET}\n")


def run_command(cmd: list, cwd: Optional[Path] = None, check: bool = True, verbose: bool = False) -> subprocess.CompletedProcess:
    """Run a command and handle errors."""
    if verbose:
        print_info(f"Running: {' '.join(str(c) for c in cmd)}")
    
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            check=check,
            capture_output=not verbose,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        return result
    except subprocess.CalledProcessError as e:
        if not verbose:
            print_error(f"Command failed: {' '.join(str(c) for c in cmd)}")
            if e.stdout:
                print(e.stdout)
            if e.stderr:
                print(e.stderr)
        raise


def create_venv(script_dir: Path, verbose: bool = False) -> Path:
    """Create virtual environment if it doesn't exist."""
    venv_dir = script_dir / "venv"
    
    if venv_dir.exists():
        print_info("Virtual environment already exists")
        return venv_dir
    
    print_info("Creating virtual environment...")
    run_command([sys.executable, "-m", "venv", str(venv_dir)], verbose=verbose)
    print_success("Virtual environment created")
    
    return venv_dir


def get_venv_executables(venv_dir: Path) -> tuple[Path, Path]:
    """Get paths to Python and pip executables in venv."""
    if os.name == 'nt':  # Windows
        python_exe = venv_dir / "Scripts" / "python.exe"
        pip_exe = venv_dir / "Scripts" / "pip.exe"
    else:  # Unix-like
        python_exe = venv_dir / "bin" / "python"
        pip_exe = venv_dir / "bin" / "pip"
    
    return python_exe, pip_exe


def install_dependencies(venv_dir: Path, script_dir: Path, verbose: bool = False) -> bool:
    """Install Python dependencies in venv."""
    print_info("Installing Python dependencies...")
    
    python_exe, pip_exe = get_venv_executables(venv_dir)
    requirements_file = script_dir / "requirements.txt"
    
    if not requirements_file.exists():
        print_error(f"requirements.txt not found at: {requirements_file}")
        return False
    
    try:
        # Install from test requirements
        print_info("Installing test dependencies from requirements.txt...")
        run_command([str(pip_exe), "install", "-r", str(requirements_file)], verbose=verbose)
        
        # Install from template documentation requirements
        print_info("Installing template documentation dependencies...")
        template_docs_requirements = script_dir.parent.parent / "templates" / "general" / "doc" / "docs" / "requirements.txt"
        if template_docs_requirements.exists():
            run_command([str(pip_exe), "install", "-r", str(template_docs_requirements)], verbose=verbose)
        else:
            print_warning(f"Template docs requirements.txt not found: {template_docs_requirements}")
        
        print_success("Python dependencies installed")
        return True
    except Exception as e:
        print_error(f"Failed to install dependencies: {e}")
        return False


def run_integration_test(
    python_exe: Path,
    script_dir: Path,
    config_name: str,
    config: Dict[str, Any],
    verbose: bool = False
) -> bool:
    """Run integration test with specific configuration."""
    print_section(f"Running Integration Test: {config['DisplayName']}")
    
    test_script = script_dir / "test_template.py"
    
    if not test_script.exists():
        print_error(f"Test script not found: {test_script}")
        return False
    
    try:
        print_info(f"Configuration: {config_name}")
        print_info(f"  Project: {config['ProjectName']}")
        print_info(f"  MkDocs: {config['Mkdocs']}")
        print_info(f"  VSCode: {config['VSCode']}")
        print_info(f"  Cross-Platform: {config['XPlat']}")
        print_info(f"  Big-Endian: {config['BigEndian']}")
        print_info(f"  C Libraries: {config['BuildCLibs']}")
        print_info(f"  C# Bindings: {config['BuildCSharpLibs']}")
        print_info(f"  CLI: {config['BuildCli']}")
        print_info(f"  Fuzz: {config['Fuzz']}")
        print()
        
        # Build command line arguments
        cmd = [
            str(python_exe),
            str(test_script),
            "--project-name", config['ProjectName'],
            f"--mkdocs={'true' if config['Mkdocs'] else 'false'}",
            f"--vscode={'true' if config['VSCode'] else 'false'}",
            f"--xplat={'true' if config['XPlat'] else 'false'}",
            f"--big-endian={'true' if config['BigEndian'] else 'false'}",
            f"--wine={'true' if config['Wine'] else 'false'}",
            f"--bench={'true' if config['Bench'] else 'false'}",
            f"--miri={'true' if config['Miri'] else 'false'}",
            f"--build-c-libs={'true' if config['BuildCLibs'] else 'false'}",
            f"--build-csharp-libs={'true' if config['BuildCSharpLibs'] else 'false'}",
            f"--build-with-pgo={'true' if config['BuildWithPgo'] else 'false'}",
            f"--build-cli={'true' if config['BuildCli'] else 'false'}",
            f"--publish-crate-on-tag={'true' if config['PublishCrateOnTag'] else 'false'}",
            f"--license={config['License']}",
            f"--no-std={config['NoStd']}",
            f"--fuzz={'true' if config['Fuzz'] else 'false'}"
        ]
        
        # Run the test
        start_time = time.time()
        result = run_command(cmd, check=False, verbose=verbose)
        end_time = time.time()
        duration = end_time - start_time
        
        if result.returncode == 0:
            print_success(f"Integration test '{config_name}' passed (took {duration:.1f}s)")
            return True
        else:
            print_error(f"Integration test '{config_name}' failed")
            if not verbose and result.stdout:
                print(result.stdout)
            if not verbose and result.stderr:
                print(result.stderr)
            return False
    except Exception as e:
        print_error(f"Error running integration test: {e}")
        return False


def get_test_configurations() -> Dict[str, Dict[str, Any]]:
    """Return dict of all test configurations."""
    return {
        'defaults': {
            'DisplayName': 'Default Configuration',
            'ProjectName': 'test_defaults',
            'Mkdocs': True,
            'VSCode': True,
            'XPlat': True,
            'BigEndian': False,
            'Wine': True,
            'Bench': True,
            'Miri': False,
            'Fuzz': False,
            'BuildCLibs': True,
            'BuildCSharpLibs': False,
            'BuildWithPgo': True,
            'BuildCli': False,
            'PublishCrateOnTag': True,
            'License': 'GPL v3 (with Reloaded FAQ)',
            'NoStd': 'STD'
        },
        'all_on': {
            'DisplayName': 'All Features Enabled',
            'ProjectName': 'test_all_on',
            'Mkdocs': True,
            'VSCode': True,
            'XPlat': True,
            'BigEndian': True,
            'Wine': True,
            'Bench': True,
            'Miri': True,
            'Fuzz': True,
            'BuildCLibs': True,
            'BuildCSharpLibs': True,
            'BuildWithPgo': True,
            'BuildCli': True,
            'PublishCrateOnTag': True,
            'License': 'MIT',
            'NoStd': 'STD'
        },
        'all_off': {
            'DisplayName': 'Minimal Features (Quick Test)',
            'ProjectName': 'test_all_off',
            'Mkdocs': False,
            'VSCode': False,
            'XPlat': False,
            'BigEndian': False,
            'Wine': False,
            'Bench': False,
            'Miri': False,
            'Fuzz': False,
            'BuildCLibs': False,
            'BuildCSharpLibs': False,
            'BuildWithPgo': False,
            'BuildCli': False,
            'PublishCrateOnTag': False,
            'License': 'Apache 2.0',
            'NoStd': 'STD'
        },
        'c_bindings': {
            'DisplayName': 'C# Bindings with C Libraries',
            'ProjectName': 'test_c_bindings',
            'Mkdocs': True,
            'VSCode': True,
            'XPlat': True,
            'BigEndian': False,
            'Wine': True,
            'Bench': True,
            'Miri': False,
            'Fuzz': False,
            'BuildCLibs': True,
            'BuildCSharpLibs': True,
            'BuildWithPgo': True,
            'BuildCli': False,
            'PublishCrateOnTag': True,
            'License': 'GPL v3 (with Reloaded FAQ)',
            'NoStd': 'STD'
        },
        'pgo_enabled': {
            'DisplayName': 'Profile-Guided Optimization',
            'ProjectName': 'test_pgo',
            'Mkdocs': True,
            'VSCode': True,
            'XPlat': True,
            'BigEndian': False,
            'Wine': True,
            'Bench': True,
            'Miri': False,
            'Fuzz': False,
            'BuildCLibs': True,
            'BuildCSharpLibs': False,
            'BuildWithPgo': True,
            'BuildCli': False,
            'PublishCrateOnTag': True,
            'License': 'GPL v3 (with Reloaded FAQ)',
            'NoStd': 'STD'
        },
        'big_endian': {
            'DisplayName': 'Big-Endian Support',
            'ProjectName': 'test_big_endian',
            'Mkdocs': True,
            'VSCode': True,
            'XPlat': True,
            'BigEndian': True,
            'Wine': True,
            'Bench': True,
            'Miri': False,
            'Fuzz': False,
            'BuildCLibs': True,
            'BuildCSharpLibs': False,
            'BuildWithPgo': True,
            'BuildCli': False,
            'PublishCrateOnTag': True,
            'License': 'GPL v3 (with Reloaded FAQ)',
            'NoStd': 'STD'
        }
    }


def check_prerequisites(verbose: bool = False) -> bool:
    """Check if required tools are installed."""
    print_section("Checking Prerequisites")
    
    # Always install cargo-generate (quietly)
    print_info("Installing cargo-generate...")
    try:
        subprocess.run(
            ["cargo", "install", "cargo-generate", "--quiet"],
            check=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        print_success("cargo-generate ready")
    except subprocess.CalledProcessError:
        print_error("Failed to install cargo-generate")
        return False
    
    print_success("All prerequisites met")
    return True


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Run all template integration tests locally with virtual environment',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Run all test configurations
  %(prog)s --verbose                 # Show detailed output
        """
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    # Print banner
    print(f"""
{Colors.CYAN}+---------------------------------------------------------------+
|                                                               |
|         Reloaded Templates Rust - Local Test Runner           |
|                                                               |
+---------------------------------------------------------------+{Colors.RESET}
""")
    
    # Get script directory
    script_dir = Path(__file__).parent
    print_info(f"Tests directory: {script_dir}")
    
    # Track results
    results = {
        'integration_tests': {}
    }
    
    start_time = time.time()
    
    # Check prerequisites
    if not check_prerequisites(args.verbose):
        print_error("Prerequisites check failed")
        return 1
    
    # Create virtual environment
    print_section("Setting Up Virtual Environment")
    venv_dir = create_venv(script_dir, args.verbose)
    
    # Install dependencies
    if not install_dependencies(venv_dir, script_dir, args.verbose):
        print_error("Dependency installation failed")
        return 1
    
    # Get Python executable from venv
    python_exe, _ = get_venv_executables(venv_dir)
    
    # Run integration tests
    test_configs = get_test_configurations()
    
    for config_name in ['defaults', 'all_on', 'all_off', 'c_bindings', 'pgo_enabled', 'big_endian']:
        config_data = test_configs[config_name]
        results['integration_tests'][config_name] = run_integration_test(
            python_exe,
            script_dir,
            config_name,
            config_data,
            args.verbose
        )
    
    # Print summary
    end_time = time.time()
    total_duration = end_time - start_time
    
    print_section("Test Summary")
    
    # Integration tests summary
    print(f"\n{Colors.CYAN}Integration Tests:{Colors.RESET}")
    passed_count = 0
    failed_count = 0
    
    test_configs = get_test_configurations()
    for config_name in sorted(results['integration_tests'].keys()):
        passed = results['integration_tests'][config_name]
        display_name = test_configs[config_name]['DisplayName']
        
        if passed:
            print_success(f"  {display_name} ({config_name}): PASSED")
            passed_count += 1
        else:
            print_error(f"  {display_name} ({config_name}): FAILED")
            failed_count += 1
    
    print()
    print_info(f"Passed: {passed_count} / {len(results['integration_tests'])}")
    if failed_count > 0:
        print_error(f"Failed: {failed_count} / {len(results['integration_tests'])}")
    
    print()
    print_info(f"Total time: {total_duration:.1f}s")
    
    # Determine exit code
    exit_code = 0
    
    for result in results['integration_tests'].values():
        if not result:
            exit_code = 1
            break
    
    if exit_code == 0:
        print(f"\n{Colors.GREEN}* All tests passed! *{Colors.RESET}\n")
    else:
        print(f"\n{Colors.RED}X Some tests failed X{Colors.RESET}\n")
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
