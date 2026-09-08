$ErrorActionPreference = "Stop"

function Get-Submodules {
    $entries = @()
    $lines = git config -f .gitmodules --get-regexp '^submodule\..*\.path$'

    foreach ($line in $lines) {
        if ($line -match '^submodule\.(.+)\.path\s+(.+)$') {
            $name = $Matches[1]
            $path = $Matches[2]
            $url = git config -f .gitmodules --get "submodule.$name.url"

            $entries += [PSCustomObject]@{
                Name = $name
                Path = $path
                Url  = $url
            }
        }
    }

    return $entries
}

function Assert-CleanSubmodule {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    $status = git -C $Path status --porcelain
    if ($status) {
        throw "Submodule '$Path' has local changes. Commit, stash or discard them before updating."
    }
}

if (-not (Test-Path ".gitmodules")) {
    throw ".gitmodules not found."
}

git submodule sync
git submodule update --init

$updates = @()

foreach ($submodule in Get-Submodules) {
    $path = $submodule.Path

    if (-not (Test-Path $path)) {
        throw "Submodule path '$path' does not exist after initialization."
    }

    Assert-CleanSubmodule -Path $path

    $oldCommit = (git -C $path rev-parse HEAD).Trim()

    git -C $path fetch --prune origin

    # Prefer the remote's configured default branch instead of assuming main.
    $remoteHead = (git -C $path symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>$null)
    if (-not $remoteHead) {
        throw "Cannot determine origin default branch for '$path'."
    }

    $branch = $remoteHead -replace '^origin/', ''

    # Move to the default branch and update it using fast-forward only.
    $localBranchExists = git -C $path show-ref --verify --quiet "refs/heads/$branch"
    if ($LASTEXITCODE -eq 0) {
        git -C $path checkout $branch
    }
    else {
        git -C $path checkout -b $branch --track "origin/$branch"
    }

    git -C $path pull --ff-only origin $branch

    $newCommit = (git -C $path rev-parse HEAD).Trim()

    $updates += [PSCustomObject]@{
        Name = $submodule.Name
        Path = $path
        Branch = $branch
        Old = $oldCommit
        New = $newCommit
        Changed = ($oldCommit -ne $newCommit)
    }
}

Write-Host ""
Write-Host "Repository update summary"
Write-Host "========================="

foreach ($update in $updates) {
    if ($update.Changed) {
        Write-Host ""
        Write-Host $update.Name
        Write-Host "  branch : $($update.Branch)"
        Write-Host "  old    : $($update.Old)"
        Write-Host "  new    : $($update.New)"
    }
    else {
        Write-Host ""
        Write-Host "$($update.Name) - unchanged ($($update.New))"
    }
}

Write-Host ""
Write-Host "Meta repository status:"
git status --short
Write-Host ""
Write-Host "Review the updated submodule pointers before committing them."
