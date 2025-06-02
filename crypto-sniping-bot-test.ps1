# crypto-sniping-bot-test.ps1
# Comprehensive test script for Crypto Sniping Bot
# Run in PowerShell: .\crypto-sniping-bot-test.ps1

# 1. Environment Setup
Write-Host "[Setup] Setting up environment..." -ForegroundColor Cyan
python -m venv .venv
. .\.venv\Scripts\Activate.ps1          # <-- dot-source, same session!
pip install -r requirements.txt
pip install pytest web3                 # ensure test deps (optional)

# 2. Generate Test Configuration
Write-Host "[Config] Creating test configuration..." -ForegroundColor Cyan
$envContent = @"
# Test configuration
BSC_NODE="wss://bsc-testnet.publicnode.com"
FLASH_SNIPER_ADDR="0x0000000000000000000000000000000000000000"
ENCRYPTION_KEY="test_encryption_key_12345"
PRIVATE_KEY="encrypted:gAAAAABmD8z5C5b5Q9X4Zz3Y2VqF7wE6lGjKpRtSxUvWnOyP3cBvR1aAeBcDdEfGhIjKlMn"
"@
Set-Content -Path .\.env -Value $envContent

# 3. Contract Tests
Write-Host "[Contracts] Testing smart contracts..." -ForegroundColor Cyan

# Install Node.js dependencies if needed
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing Node.js dependencies..."
    npm install -g truffle
    npm install @openzeppelin/contracts @truffle/hdwallet-provider
}

# Run contract tests
truffle test --network bsc_testnet

# 4. Python Bot Tests – run from sniper-bot folder so requirements.txt is correct
Set-Location .\sniper-bot
pytest tests\unit

# Unit tests
Write-Host "Running unit tests..."
pytest tests/unit

# Integration test
Write-Host "Running integration test..."
Start-Job -ScriptBlock {
    param($envFile)
    Set-Content -Path .\.env -Value $envFile
    python sniping_bot.py
} -ArgumentList $envContent | Out-Null

Write-Host "Bot started in background. Waiting 10 seconds..."
Start-Sleep -Seconds 10

# Check if bot is running
$botProcess = Get-Process | Where-Object {
    $_.ProcessName -eq "python" -and $_.CommandLine -like "*sniping_bot.py*"
}
if ($botProcess) {
    Write-Host "[SUCCESS] Bot is running (PID: $($botProcess.Id))" -ForegroundColor Green
    Stop-Process -Id $botProcess.Id
} else {
    Write-Host "[FAIL] Bot failed to start" -ForegroundColor Red
}

# 5. Security Checks
Write-Host "[Security] Running security checks..." -ForegroundColor Cyan

# Check for secrets in code
Write-Host "Scanning for exposed secrets..."
$secretsFound = Select-String -Path "*.py","*.sol" -Pattern "private_key|mnemonic|secret" -CaseSensitive
if ($secretsFound) {
    Write-Host "[FAIL] Potential secrets found in code:" -ForegroundColor Red
    $secretsFound | Format-Table -AutoSize
} else {
    Write-Host "[SUCCESS] No secrets detected in code" -ForegroundColor Green
}

# Run Slither security analysis
if (Get-Command slither -ErrorAction SilentlyContinue) {
    Write-Host "Running Slither security analysis..."
    slither ./contracts --exclude naming-convention
} else {
    Write-Host "[WARNING] Slither not installed. Install with: pip install slither-analyzer"
}

# 6. Performance Test
Write-Host "[Performance] Testing RPC latency..." -ForegroundColor Cyan

$latency = Measure-Command {
    python -c "from web3 import Web3; w3 = Web3(Web3.WebsocketProvider('wss://bsc-testnet.publicnode.com')); print('Connected:', w3.is_connected())"
}

Write-Host ("Blockchain connection latency: {0:N0} ms" -f $latency.TotalMilliseconds)

# 7. Cleanup
Write-Host "[Cleanup] Removing temporary files..." -ForegroundColor Cyan
Remove-Item .\.env -Force -ErrorAction SilentlyContinue
deactivate

Write-Host "`nAll tests completed.`n" -ForegroundColor Green
