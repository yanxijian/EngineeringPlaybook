[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$scriptPath = Join-Path $PSScriptRoot '..\Test-ReviewDocuments.ps1'
$fixtures = Join-Path $PSScriptRoot 'fixtures'

function Assert-Check {
    param(
        [string]$Name,
        [hashtable]$Parameters,
        [int]$ExpectedExitCode,
        [string]$ExpectedText
    )

    $output = & $scriptPath @Parameters 2>&1 | Out-String
    if ($LASTEXITCODE -ne $ExpectedExitCode) {
        throw "$Name returned $LASTEXITCODE instead of $ExpectedExitCode. Output: $output"
    }
    if ($output -notmatch [regex]::Escape($ExpectedText)) {
        throw "$Name did not contain '$ExpectedText'. Output: $output"
    }
}

$design = Join-Path $fixtures 'feature-plan.md'
$review = Join-Path $fixtures 'feature-plan-review.md'
$unansweredDesign = Join-Path $fixtures 'unanswered-design-suggestion-plan.md'
$unansweredReview = Join-Path $fixtures 'unanswered-design-suggestion-plan-review.md'

Assert-Check -Name 'preflight' -Parameters @{ DesignPath = $design } -ExpectedExitCode 0 -ExpectedText 'Design preflight passed'
Assert-Check -Name 'review' -Parameters @{ DesignPath = $design; ReviewPath = $review } -ExpectedExitCode 0 -ExpectedText 'Findings checked: 1'
Assert-Check -Name 'design suggestion warning' -Parameters @{ DesignPath = $unansweredDesign; ReviewPath = $unansweredReview } -ExpectedExitCode 0 -ExpectedText 'WARNING: Design feedback section does not respond'
Assert-Check -Name 'required design suggestion response' -Parameters @{ DesignPath = $unansweredDesign; ReviewPath = $unansweredReview; RequireDesignResponses = $true } -ExpectedExitCode 1 -ExpectedText 'ERROR: Design feedback section does not respond'

Write-Host 'Review document fixtures passed.'

exit 0