# Post-change verification script
# All steps must pass without warnings
# Keep in sync with verify.sh

$originalDir = Get-Location
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Join-Path $scriptDir ".."
$originalRustdocFlags = $env:RUSTDOCFLAGS
Set-Location $projectRoot -ErrorAction Stop

$script:exitCode = 0
$script:failedCommands = @()

function Register-CommandFailure {
    param(
        [string]$DisplayCommand,
        [int]$Code,
        [string]$Message = ""
    )

    Write-Host ("Command failed with exit code " + $Code + ": " + $DisplayCommand)
    if ($Message -ne "") {
        Write-Host $Message
    }

    $script:failedCommands += $DisplayCommand
    if ($script:exitCode -eq 0) {
        $script:exitCode = $Code
    }
}

function Invoke-LoggedCommand {
    param(
        [string]$Command,
        [string[]]$Arguments
    )

    $displayCommand = if ($Arguments.Count -gt 0) {
        $Command + " " + ($Arguments -join " ")
    } else {
        $Command
    }

    Write-Host $displayCommand

    try {
        & $Command @Arguments
        $commandExitCode = $LASTEXITCODE
    } catch {
        Register-CommandFailure $displayCommand 1 $_.Exception.Message
        return
    }

    if ($commandExitCode -ne 0) {
        Register-CommandFailure $displayCommand $commandExitCode
    }
}

try {
    Write-Host "Building..."
    Invoke-LoggedCommand "cargo" @("build", "--workspace", "--all-features", "--all-targets", "--quiet")

    Write-Host "Testing..."
    Invoke-LoggedCommand "cargo" @("test", "--workspace", "--all-features", "--quiet")

    Write-Host "Clippy..."
    Invoke-LoggedCommand "cargo" @("clippy", "--workspace", "--all-features", "--quiet", "--", "-D", "warnings")

    Write-Host "Docs..."
    $env:RUSTDOCFLAGS = "-D warnings"
    try {
        Invoke-LoggedCommand "cargo" @("doc", "--workspace", "--all-features", "--no-deps", "--document-private-items", "--quiet")
    } finally {
        $env:RUSTDOCFLAGS = $originalRustdocFlags
    }

    Write-Host "Formatting..."
    Invoke-LoggedCommand "cargo" @("fmt", "--all", "--quiet")

    Write-Host "Publish dry-run..."
    Invoke-LoggedCommand "cargo" @("publish", "--dry-run", "--allow-dirty", "--quiet", "--workspace")
} finally {
    $env:RUSTDOCFLAGS = $originalRustdocFlags
    Set-Location $originalDir
}

if ($script:exitCode -eq 0) {
    Write-Host "All checks passed!"
} else {
    Write-Host "Verification failed."
    Write-Host "Failed commands:"
    foreach ($failedCommand in $script:failedCommands) {
        Write-Host (" - " + $failedCommand)
    }
}

exit $script:exitCode
