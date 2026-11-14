# Upload seguro das 3 imagens originais do dorama Alchemy Lab para GitHub.
# Nao gera nem altera imagens. Verifica hashes SHA-256 de cada PNG dentro do ZIP.
# Executar no Windows com gh + git autenticados.
param(
    [string]$ZipPath = (Join-Path $HOME 'Downloads\alchemy-ep01-cinema-3-originais.zip')
)

$ErrorActionPreference = 'Stop'
$repo = 'HelioConde/VideoForge-IA'
$destRel = 'uploads/alchemy-ep01-cinema-3-originais.zip'
$expected = @{
    'kael-close-salao.png' = 'edb751cdb1c1511e56cd8c8f314a788d9adfb9d4338085cead281efa931ed65f'
    'elara-close-trono.png' = 'bf199f3e3315fc8357e9fdec7e17db47f2a56c6fca6225b7f4983201fc2fcd6a'
    'confronto-trono-c12-p02.png' = '01eb7c127b0699d2e502d29dacec0bb39c0e1e23bf8205fdcf6fb70976e70535'
}

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    throw 'GitHub CLI (gh) nao encontrado. Instale e execute: gh auth login'
}
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw 'Git nao encontrado. Instale Git for Windows.'
}
$fullZip = (Resolve-Path -LiteralPath $ZipPath -ErrorAction Stop).Path
if ((Get-Item -LiteralPath $fullZip).Length -gt 11000000) {
    throw 'ZIP grande demais. Baixe novamente o pacote de 3 imagens do chat.'
}

Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip = [System.IO.Compression.ZipFile]::OpenRead($fullZip)
try {
    $entries = @($zip.Entries)
    if ($entries.Count -ne 3) { throw 'O ZIP precisa conter exatamente 3 PNGs.' }
    foreach ($entry in $entries) {
        if (-not $expected.ContainsKey($entry.FullName)) {
            throw "Arquivo inesperado no ZIP: $($entry.FullName)"
        }
        if ($entry.Length -gt 6000000 -or $entry.Length -lt 1024) {
            throw "Tamanho inesperado de $($entry.FullName)"
        }
        $stream = $entry.Open()
        $sha = [System.Security.Cryptography.SHA256]::Create()
        try {
            $digest = -join ($sha.ComputeHash($stream) | ForEach-Object { $_.ToString('x2') })
        } finally {
            $stream.Dispose()
            $sha.Dispose()
        }
        if ($digest -ne $expected[$entry.FullName]) {
            throw "Hash errado para $($entry.FullName). ZIP original necessario."
        }
        Write-Host "SHA OK: $($entry.FullName)"
    }
} finally { $zip.Dispose() }

& gh auth status
if ($LASTEXITCODE -ne 0) { throw 'Faça login antes: gh auth login' }

$work = Join-Path ([System.IO.Path]::GetTempPath()) ("videoforge-cinema-" + [guid]::NewGuid().ToString('N'))
$success = $false
try {
    & gh repo clone $repo $work -- --branch main --single-branch --depth 1
    if ($LASTEXITCODE -ne 0) { throw 'Nao foi possivel clonar o repositorio.' }
    $uploadDir = Join-Path $work 'uploads'
    New-Item -Path $uploadDir -ItemType Directory -Force | Out-Null
    $out = Join-Path $uploadDir 'alchemy-ep01-cinema-3-originais.zip'
    Copy-Item -LiteralPath $fullZip -Destination $out -Force

    & git -C $work add -- $destRel
    if ($LASTEXITCODE -ne 0) { throw 'git add falhou.' }
    & git -C $work diff --cached --quiet
    if ($LASTEXITCODE -eq 0) {
        Write-Host 'ZIP ja esta igual no GitHub. Nenhum commit necessario.'
        $success = $true
    } else {
        & git -C $work -c user.name='VideoForge Cinema Import' -c user.email='videoforge-import@users.noreply.github.com' commit -m 'assets(alchemy): importar 3 PNGs originais para QA de SHA'
        if ($LASTEXITCODE -ne 0) { throw 'git commit falhou.' }
        for ($attempt = 1; $attempt -le 3; $attempt++) {
            & git -C $work push origin HEAD:main
            if ($LASTEXITCODE -eq 0) {
                $success = $true
                break
            }
            if ($attempt -lt 3) {
                & git -C $work fetch origin main
                if ($LASTEXITCODE -ne 0) { break }
                & git -C $work rebase origin/main
                if ($LASTEXITCODE -ne 0) { break }
            }
        }
        if (-not $success) { throw "Push falhou. Clone preservado em $work para revisao; nao force push." }
        Write-Host 'ZIP enviado ao GitHub. O workflow fara extracao e validacao por SHA.'
    }
    Write-Host "Workflow: https://github.com/$repo/actions/workflows/qa-alchemy-chat-cinematic-references.yml"
    Write-Host 'A importacao NAO aprova rigs nem permite gerar novas imagens.'
} finally {
    if ($success -and (Test-Path -LiteralPath $work)) {
        Remove-Item -LiteralPath $work -Recurse -Force
    }
}
