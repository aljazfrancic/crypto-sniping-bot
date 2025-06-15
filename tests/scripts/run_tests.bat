@echo off
echo Running Crypto Sniping Bot Tests
echo.

if "%1"=="clean" (
    echo Running clean comprehensive test...
    python test_clean.py
) else if "%1"=="unit" (
    echo Running unit tests...
    python -m pytest -m unit -v
) else if "%1"=="integration" (
    echo Running integration tests...
    python -m pytest -m integration -v
) else if "%1"=="security" (
    echo Running security tests...
    python -m pytest -m security -v
) else (
    echo Running all tests with coverage...
    python -m pytest --cov=bot --cov-report=term-missing --cov-report=html:htmlcov -v
)

echo.
echo Test run completed!
pause
