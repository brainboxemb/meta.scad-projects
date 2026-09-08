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

if (-not (Test-Path ".gitmodules")) {
    throw ".gitmodules not found."
}

foreach ($submodule in Get-Submodules) {
    $path = $submodule.Path

    if (Test-Path $path) {
        if (Test-Path (Join-Path $path ".git")) {
            Write-Host "Reusing existing Git checkout: $path"
            continue
        }

        if ((Get-ChildItem -Force $path | Measure-Object).Count -gt 0) {
            throw "Cannot initialize $path because non-Git files already exist there."
        }
    }

    $tracked = git ls-files --stage -- $path
    if ($tracked -match '^160000 ') {
        Write-Host "Initializing pinned submodule: $path"
        git submodule update --init -- $path
        continue
    }

    Write-Host "Registering submodule: $path"
    git submodule add --force $submodule.Url $path
}

git submodule sync
git submodule update --init

Write-Host "SCAD ecosystem repositories are initialized."
