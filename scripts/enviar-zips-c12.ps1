# Enviar os dois ZIPs EXISTENTES do dorama para a main do VideoForge-IA.
# Nunca gera imagens e nunca publica video.
# Requer PowerShell, Python 3.12+, Git e gh autenticado.
param(
    [string]$OriginalZip = (Join-Path $HOME "Downloads\alchemy-ep01-cinema-3-originais.zip"),
    [string]$TechnicalZip = (Join-Path $HOME "Downloads\alchemy_c12_rig_camadas_tecnicas_v2.zip")
)
$ErrorActionPreference = 'Stop'
$repo = 'HelioConde/VideoForge-IA'
$success = $false

foreach ($cmd in @('python', 'gh', 'git')) {
    if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
        throw "Ferramenta obrigatoria nao encontrada: $cmd"
    }
}
$orig = (Resolve-Path -LiteralPath $OriginalZip -ErrorAction Stop).Path
$tech = (Resolve-Path -LiteralPath $TechnicalZip -ErrorAction Stop).Path
if ($orig -eq $tech) { throw 'Os dois ZIPs devem ser diferentes.' }
& gh auth status
if ($LASTEXITCODE -ne 0) { throw 'Autentique o GitHub CLI: gh auth login' }

$work = Join-Path ([System.IO.Path]::GetTempPath()) ("videoforge-c12-" + [guid]::NewGuid().ToString('N'))
try {
    & gh repo clone $repo $work -- --branch main --single-branch --depth 1
    if ($LASTEXITCODE -ne 0) { throw 'Falha ao clonar a main.' }

    Push-Location $work
    try {
        & python -m videoforge.c12_upload_existing_zips --originals $orig --technical $tech --root $work
        if ($LASTEXITCODE -ne 0) {
            throw 'Hashes SHA dos PNGs originais nao conferem ou pacote invalido. Nenhum commit realizado.'
        }

        $relative = @(
          'uploads/alchemy-ep01-cinema-3-originais.zip',
          'uploads/alchemy-c12-rig-camadas-tecnicas-v2.zip'
        )
        & git add -f -- $relative[0] $relative[1]
        if ($LASTEXITCODE -ne 0) { throw 'Git add falhou.' }
        & git diff --cached --quiet
        if ($LASTEXITCODE -eq 0) {
            Write-Host 'Arquivos identicos ja estao no GitHub. Sem commit novo.'
            $success = $true
        } elseif ($LASTEXITCODE -eq 1) {
            & git -c 'user.name=VideoForge Asset Import' -c 'user.email=videoforge-import@users.noreply.github.com' commit -m 'assets(alchemy): enviar ZIPs originais SHA-256 C12 sem IA'
            if ($LASTEXITCODE -ne 0) { throw 'Git commit falhou.' }
            for ($try = 1; $try -le 3; $try++) {
                & git push origin HEAD:main
                if ($LASTEXITCODE -eq 0) {
                    $success = $true
                    break
                }
                if ($try -ge 3) { break }
                & git fetch origin main
                if ($LASTEXITCODE -ne 0) { break }
                & git rebase origin/main
                if ($LASTEXITCODE -ne 0) { break }
            }
            if (-not $success) {
                throw "Nao foi possivel enviar para a main. Clone preservado em $work."
            }
        } else {
            throw 'Nao foi possivel verificar o estado de git diff.'
        }
    } finally {
        Pop-Location
    }
    Write-Host 'ZIPs originais SHA-verificados e enviados (ou ja presentes).'
    Write-Host "Importadores: https://github.com/$repo/actions"
    Write-Host 'O coordenador apos-importacao verifica 9 arquivos e inicia somente o MP4 tecnico C12.'
    Write-Host 'Sem novas imagens, sem video oficial e sem publicacao YouTube.'
} finally {
    if ($success -and (Test-Path -LiteralPath $work)) {
        Remove-Item -LiteralPath $work -Recurse -Force
    }
}
