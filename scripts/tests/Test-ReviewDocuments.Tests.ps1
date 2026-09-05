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
        [string[]]$ExpectedText
    )

    $output = & $scriptPath @Parameters 2>&1 | Out-String
    if ($LASTEXITCODE -ne $ExpectedExitCode) {
        throw "$Name returned $LASTEXITCODE instead of $ExpectedExitCode. Output: $output"
    }
    foreach ($expected in $ExpectedText) {
        if ($output -notmatch [regex]::Escape($expected)) {
            throw "$Name did not contain '$expected'. Output: $output"
        }
    }
}

$design = Join-Path $fixtures 'feature-plan.md'
$review = Join-Path $fixtures 'feature-plan-review.md'
$unansweredDesign = Join-Path $fixtures 'unanswered-design-suggestion-plan.md'
$unansweredReview = Join-Path $fixtures 'unanswered-design-suggestion-plan-review.md'
$missingFeedbackDesign = Join-Path $fixtures 'missing-feedback-plan.md'
$missingFeedbackReview = Join-Path $fixtures 'missing-feedback-plan-review.md'
$unansweredFindingDesign = Join-Path $fixtures 'unanswered-finding-plan.md'
$unansweredFindingReview = Join-Path $fixtures 'unanswered-finding-plan-review.md'
$duplicateIdDesign = Join-Path $fixtures 'duplicate-id-plan.md'
$duplicateIdReview = Join-Path $fixtures 'duplicate-id-plan-review.md'
$wrongNameReview = Join-Path $fixtures 'wrong-name-review.md'
$multipleErrorsReview = Join-Path $fixtures 'multiple-errors-review.md'

Assert-Check -Name 'preflight' -Parameters @{ DesignPath = $design } -ExpectedExitCode 0 -ExpectedText 'Design preflight passed'
Assert-Check -Name 'review' -Parameters @{ DesignPath = $design; ReviewPath = $review } -ExpectedExitCode 0 -ExpectedText 'Findings checked: 1'
Assert-Check -Name 'design suggestion warning' -Parameters @{ DesignPath = $unansweredDesign; ReviewPath = $unansweredReview } -ExpectedExitCode 0 -ExpectedText 'WARNING: Design feedback section does not respond'
Assert-Check -Name 'required design suggestion response' -Parameters @{ DesignPath = $unansweredDesign; ReviewPath = $unansweredReview; RequireDesignResponses = $true } -ExpectedExitCode 1 -ExpectedText 'ERROR: Design feedback section does not respond'
Assert-Check -Name 'missing review report' -Parameters @{ DesignPath = $design; ReviewPath = (Join-Path $fixtures 'missing-review.md') } -ExpectedExitCode 1 -ExpectedText 'ERROR: Review report not found'
Assert-Check -Name 'wrong review name' -Parameters @{ DesignPath = $design; ReviewPath = $wrongNameReview } -ExpectedExitCode 1 -ExpectedText 'ERROR: Review report name must be feature-plan-review.md'
Assert-Check -Name 'missing feedback section' -Parameters @{ DesignPath = $missingFeedbackDesign; ReviewPath = $missingFeedbackReview } -ExpectedExitCode 1 -ExpectedText 'ERROR: Design document is missing the review feedback and adoption section.'
Assert-Check -Name 'unanswered finding' -Parameters @{ DesignPath = $unansweredFindingDesign; ReviewPath = $unansweredFindingReview } -ExpectedExitCode 1 -ExpectedText 'ERROR: Design feedback section does not respond to finding: P2-01'
Assert-Check -Name 'duplicate review ID' -Parameters @{ DesignPath = $duplicateIdDesign; ReviewPath = $duplicateIdReview } -ExpectedExitCode 1 -ExpectedText 'ERROR: Review report contains a duplicate ID: P2-01'
Assert-Check -Name 'multiple diagnostics' -Parameters @{ DesignPath = $design; ReviewPath = $multipleErrorsReview } -ExpectedExitCode 1 -ExpectedText @('ERROR: Review report name must be feature-plan-review.md', 'ERROR: Review report has no P1-01, P2-01, or P3-01 finding IDs.')

Write-Host 'Review document fixtures passed.'

exit 0