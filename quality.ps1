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

function RunTests {
    Write-Host "Running tests..." -ForegroundColor Blue
    New-Item -ItemType Directory -Force -Path "test-results"
    .\.venv\Scripts\pytest --junitxml=test-results/junit.xml --cov=src --cov-report=xml:test-results/coverage.xml --cov-report=html:test-results/htmlcov
}

function SecurityScan {
    Write-Host "Running security scans..." -ForegroundColor Blue
    .\.venv\Scripts\safety scan
    .\.venv\Scripts\bandit -r src\ -f json -o bandit-report.json
}

function Quality {
    Format
    Lint
    Write-Host "All quality checks completed!" -ForegroundColor Green
}

# Exécution des commandes
switch ($Command.ToLower()) {
    "clean" { Clean }
    "venv" { CreateVenv }
    "install" { Install }
    "format" { Format }
    "lint" { Lint }
    "test" { RunTests }
    "security" { SecurityScan }
    "quality" { Quality }
    "all" {
        Clean
        CreateVenv
        Install
        Quality
        SecurityScan
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
- test: Run tests
- security: Run security scans
- quality: Run all quality checks
- all: Clean, create venv, install deps, run quality checks and security scans
"@ -ForegroundColor Yellow
    }
} 