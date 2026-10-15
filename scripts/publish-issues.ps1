param(
  [Parameter(Mandatory = $true)]
  [ValidatePattern('^[A-Za-z0-9_.-]+/practiceloop$')]
  [string]$Repository,
  [switch]$Apply
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
Push-Location (Split-Path $PSScriptRoot -Parent)
try {
  if (-not (Get-Command gh -ErrorAction SilentlyContinue)) { throw 'Install GitHub CLI and authenticate first' }
  & gh repo view $Repository --json nameWithOwner,isPrivate
  if ($LASTEXITCODE -ne 0) { throw 'Target repository is inaccessible; no changes applied' }
  $tasks = Get-Content -LiteralPath docs/development/backlog.json -Raw -Encoding UTF8 | ConvertFrom-Json
  if (-not $Apply) {
    $tasks | Select-Object id,title,type,priority,status | Format-Table
    Write-Output 'Preview only. After owner approval rerun with -Apply against the confirmed repository.'
    return
  }
  $labels = @('Feature','Bug','Documentation','Testing','Infrastructure','Security','Architecture',
    'P0','P1','P2','Backlog','Ready','In Progress','In Review','Blocked','Done')
  $existingLabels = @(& gh label list --repo $Repository --limit 1000 --json name --jq '.[].name')
  if ($LASTEXITCODE -ne 0) { throw 'Could not read labels' }
  foreach ($label in $labels) {
    if ($existingLabels -notcontains $label) {
      & gh label create $label --repo $Repository --color '506B8A'
      if ($LASTEXITCODE -ne 0) { throw "Label creation failed: $label" }
    }
  }
  $raw = & gh issue list --repo $Repository --state all --limit 1000 --json title,url,number
  if ($LASTEXITCODE -ne 0) { throw 'Could not read Issues' }
  $existing = @($raw | ConvertFrom-Json)
  if ($existing.Count -ge 1000) { throw 'Issue listing limit reached; inspect pagination before publishing' }
  New-Item -ItemType Directory -Path .local -Force | Out-Null
  $mapping = @()
  foreach ($task in $tasks) {
    $title = "[$($task.id)] $($task.title)"
    $found = @($existing | Where-Object { $_.title -ceq $title })
    if ($found.Count -gt 1) { throw "Duplicate title already exists: $title" }
    if ($found.Count -eq 1) {
      $mapping += [pscustomobject]@{ id=$task.id; url=$found[0].url }
      continue
    }
    $criteria = ($task.acceptance | ForEach-Object { "- [ ] $_" }) -join "`n"
    $body = @"
Type: $($task.type)
Priority: $($task.priority)
Status: $($task.status)
Agent: unassigned
Human owner: unassigned
Suggested pairing: $($task.pairing)
Branch: assign after real Issue number exists
Dependencies: $($task.dependencies -join ', ')
Related PRs: none

## Scope
$($task.scope)

## Acceptance criteria
$criteria

## Definition of Done
Follow docs/agents/WORKFLOW.md: CI, independent review, human approval, merge and Issue closure are required.
"@
    $bodyPath = Join-Path '.local' ($task.id + '.md')
    [IO.File]::WriteAllText((Join-Path (Get-Location) $bodyPath), $body, [Text.UTF8Encoding]::new($false))
    $url = & gh issue create --repo $Repository --title $title --body-file $bodyPath --label $task.type --label $task.priority --label $task.status
    if ($LASTEXITCODE -ne 0) { throw "Issue creation failed: $title" }
    $mapping += [pscustomobject]@{ id=$task.id; url=($url -join '').Trim() }
    $mapping | ConvertTo-Json | Set-Content -LiteralPath .local/issue-map.json -Encoding utf8
  }
  $mapping | ConvertTo-Json | Set-Content -LiteralPath .local/issue-map.json -Encoding utf8
  Write-Output 'Issues published or reused. Review .local/issue-map.json; no assignees or access changes applied.'
} finally {
  Pop-Location
}
