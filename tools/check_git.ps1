# Check if .gitignore exists
if (Test-Path ".gitignore") {
    Get-Content ".gitignore"
} else {
    Write-Output "No .gitignore found"
}
