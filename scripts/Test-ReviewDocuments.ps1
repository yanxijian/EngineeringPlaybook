[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$DesignPath,

    [string]$ReviewPath,

    [switch]$RequireDesignResponses
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-DocumentText {
    param([string]$Path)

    return [System.IO.File]::ReadAllText((Resolve-Path -LiteralPath $Path), [System.Text.Encoding]::UTF8)
}

function Add-Error {
    param([string]$Message)

    $script:errors.Add($Message)
}

$errors = [System.Collections.Generic.List[string]]::new()
$warnings = [System.Collections.Generic.List[string]]::new()

if (-not (Test-Path -LiteralPath $DesignPath -PathType Leaf)) {
    Add-Error "Design document not found: $DesignPath"
}
else {
    $designPath = (Resolve-Path -LiteralPath $DesignPath).Path
    $design = Get-DocumentText -Path $designPath
}

if ($errors.Count -eq 0) {
    $feedbackHeading = [string]::Concat(
        [char]0x8BC4, [char]0x5BA1, [char]0x53CD, [char]0x9988,
        [char]0x4E0E, [char]0x91C7, [char]0x7EB3, [char]0x8BF4, [char]0x660E)
    $evidenceHeading = [string]::Concat(
        [char]0x8BC4, [char]0x5BA1, [char]0x4F9D, [char]0x636E,
        [char]0x5BFC, [char]0x822A)

    if ($design -notmatch ('(?m)^##\s+' + [regex]::Escape($feedbackHeading) + '\s*$')) {
        Add-Error 'Design document is missing the review feedback and adoption section.'
    }
    if ($design -notmatch ('(?m)^##\s+' + [regex]::Escape($evidenceHeading) + '\s*$')) {
        Add-Error 'Design document is missing the review evidence navigation section.'
    }
}

if ([string]::IsNullOrWhiteSpace($ReviewPath)) {
    if ($errors.Count -eq 0) {
        Write-Output 'Design preflight passed. No review report was supplied.'
    }
}
elseif (-not (Test-Path -LiteralPath $ReviewPath -PathType Leaf)) {
    Add-Error "Review report not found: $ReviewPath"
}
elseif ($errors.Count -eq 0) {
    $reviewPath = (Resolve-Path -LiteralPath $ReviewPath).Path
    $review = Get-DocumentText -Path $reviewPath
    $expectedReviewName = "$([System.IO.Path]::GetFileNameWithoutExtension($designPath))-review.md"

    if ([System.IO.Path]::GetDirectoryName($designPath) -ine [System.IO.Path]::GetDirectoryName($reviewPath)) {
        Add-Error 'Review report must be in the same directory as the design document.'
    }
    if ([System.IO.Path]::GetFileName($reviewPath) -ine $expectedReviewName) {
        Add-Error "Review report name must be $expectedReviewName for this design document."
    }

    $feedbackMatch = [regex]::Match(
        $design,
        ('(?ms)^##\s+' + [regex]::Escape($feedbackHeading) + '\s*$\r?\n(.*?)(?=^##\s|\z)'))
    $feedback = if ($feedbackMatch.Success) { $feedbackMatch.Groups[1].Value } else { '' }

    $allIds = @([regex]::Matches($review, '(?m)^#{2,4}\s+((?:P[1-3]|D)-\d{2})\b') |
        ForEach-Object { $_.Groups[1].Value })
    $duplicateIds = @($allIds | Group-Object | Where-Object Count -gt 1 | ForEach-Object Name)
    $findingIds = @($allIds | Where-Object { $_ -match '^P[1-3]-\d{2}$' } | Sort-Object -Unique)
    $designIds = @($allIds | Where-Object { $_ -match '^D-\d{2}$' } | Sort-Object -Unique)

    if ($findingIds.Count -eq 0) {
        Add-Error 'Review report has no P1-01, P2-01, or P3-01 finding IDs.'
    }
    foreach ($duplicateId in $duplicateIds) {
        Add-Error "Review report contains a duplicate ID: $duplicateId"
    }
    foreach ($findingId in $findingIds) {
        if ($feedback -notmatch ('(?m)^\|\s*' + [regex]::Escape($findingId) + '\s*\|')) {
            Add-Error "Design feedback section does not respond to finding: $findingId"
        }
    }
    foreach ($designId in $designIds) {
        if ($feedback -notmatch ('(?m)^\|\s*' + [regex]::Escape($designId) + '\s*\|')) {
            $message = "Design feedback section does not respond to design suggestion: $designId"
            if ($RequireDesignResponses) {
                Add-Error $message
            }
            else {
                $warnings.Add($message)
            }
        }
    }
}

$warnings | ForEach-Object { Write-Output "WARNING: $_" }
$errors | ForEach-Object { Write-Output "ERROR: $_" }
if ($errors.Count -gt 0) {
    exit 1
}

if (-not [string]::IsNullOrWhiteSpace($ReviewPath)) {
    Write-Output "Review document structure passed. Findings checked: $($findingIds.Count)."
}

exit 0