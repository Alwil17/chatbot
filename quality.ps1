param(
    [string]$Command = "all"
)

function Clean {
    Write-Host "Cleaning up..." -ForegroundColor Blue
    Remove-Item -Path ".venv" -Recurse -ErrorAction SilentlyContinue
    Remove-Item -Path "**/__pycache__" -Recurse -ErrorAction SilentlyContinue
    Remove-Item -Path "*.egg-info" -Recurse -ErrorAction SilentlyContinue
    Remove-Item -Path ".pytest_cache" -Recurse -ErrorAction SilentlyContinue
    Remove-Item -Path ".mypy_cache" -Recurse -ErrorAction SilentlyContinue
    Remove-Item -Path ".coverage" -ErrorAction SilentlyContinue
    Remove-Item -Path "htmlcov" -Recurse -ErrorAction SilentlyContinue
}

function CreateVenv {
    Write-Host "Creating virtual environment..." -ForegroundColor Blue
    python -m venv .venv
}

function Install {
    Write-Host "Installing dependencies..." -ForegroundColor Blue
    .\.venv\Scripts\pip install -r requirements.txt
}

function Format {
    Write-Host "Formatting code with black..." -ForegroundColor Blue
    .\.venv\Scripts\black src\ tests\
}

function Lint {
    Write-Host "Linting code with flake8..." -ForegroundColor Blue
    .\.venv\Scripts\flake8 src\ tests\
}

function TypeCheck {
    Write-Host "Type checking with mypy..." -ForegroundColor Blue
    .\.venv\Scripts\mypy src\ tests\
}

function RunTests {
    Write-Host "Running tests..." -ForegroundColor Blue
    .\.venv\Scripts\pytest
}

function Quality {
    Format
    Lint
    TypeCheck
    Write-Host "All quality checks completed!" -ForegroundColor Green
}

# Exécution des commandes
switch ($Command.ToLower()) {
    "clean" { Clean }
    "venv" { CreateVenv }
    "install" { Install }
    "format" { Format }
    "lint" { Lint }
    "type-check" { TypeCheck }
    "test" { RunTests }
    "quality" { Quality }
    "all" {
        Clean
        CreateVenv
        Install
        Quality
    }
    default {
        Write-Host "Unknown command: $Command" -ForegroundColor Red
        Write-Host @"
Available commands:
- clean: Remove temporary files and directories
- venv: Create virtual environment
- install: Install dependencies
- format: Format code with black
- lint: Check code style with flake8
- type-check: Check types with mypy
- test: Run tests
- quality: Run all quality checks
- all: Clean, create venv, install deps, and run quality checks
"@ -ForegroundColor Yellow
    }
} 