$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
Push-Location (Split-Path $PSScriptRoot -Parent)
$container = 'practiceloop-test-' + [guid]::NewGuid().ToString('N').Substring(0, 10)
try {
  & docker run --detach --name $container --env POSTGRES_PASSWORD=local-ci-only postgres:17 | Out-Null
  if ($LASTEXITCODE -ne 0) { throw 'Could not start disposable PostgreSQL' }
  $ready = $false
  for ($i = 0; $i -lt 30; $i++) {
    & docker exec $container pg_isready -U postgres 2>$null | Out-Null
    if ($LASTEXITCODE -eq 0) { $ready = $true; break }
    Start-Sleep -Seconds 1
  }
  if (-not $ready) { throw 'PostgreSQL did not become ready' }
  foreach ($file in @('supabase/tests/auth_fixture.sql', 'supabase/migrations/202610150001_initial_schema.sql', 'supabase/tests/isolation.sql')) {
    Get-Content -Raw -LiteralPath $file | & docker exec -i $container psql -U postgres -v ON_ERROR_STOP=1
    if ($LASTEXITCODE -ne 0) { throw "SQL verification failed: $file" }
  }
} finally {
  & docker rm --force $container | Out-Null
  Pop-Location
}
