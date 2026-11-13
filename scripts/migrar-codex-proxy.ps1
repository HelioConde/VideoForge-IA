#requires -Version 5.1
<#
.SYNOPSIS
  Migra contas do proxy local para VideoForge-IA sem mostrar tokens.
.DESCRIPTION
  GitHub nao permite recuperar valores de secrets antigos.
  Usa proxy Docker local ou backup privado. Requer gh autenticado no GitHub.
  Nao instala Go e nao faz login no Codex.
.EXAMPLE
  .\scripts\migrar-codex-proxy.ps1
.EXAMPLE
  .\scripts\migrar-codex-proxy.ps1 -Container chatgpt-codex-proxy
.EXAMPLE
  .\scripts\migrar-codex-proxy.ps1 -ArquivoContas 'C:\privado\accounts.json'
#>
[CmdletBinding()]
param([string]$Container, [string]$ArquivoContas)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$Repositorio = 'HelioConde/VideoForge-IA'
$estadoBruto = $null
$chave = $null

function Require-Command([string]$name) {
    $cmd = Get-Command $name -ErrorAction SilentlyContinue
    if (-not $cmd) { throw "Necessario '$name' no PATH para migrar sem expor segredos." }
    return $cmd.Source
}

function Set-SecretFromMemory([string]$name, [string]$value, [string]$gh) {
    $info = New-Object System.Diagnostics.ProcessStartInfo
    $info.FileName = $gh
    $info.Arguments = "secret set $name --repo $Repositorio --app actions"
    $info.UseShellExecute = $false
    $info.RedirectStandardInput = $true
    $info.RedirectStandardOutput = $true
    $info.RedirectStandardError = $true
    $info.CreateNoWindow = $true
    $info.StandardInputEncoding = New-Object System.Text.UTF8Encoding($false)
    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $info
    try {
        if (-not $process.Start()) { throw 'Falha ao iniciar o GitHub CLI.' }
        $process.StandardInput.Write($value)
        $process.StandardInput.Close()
        $null = $process.StandardOutput.ReadToEnd()
        $null = $process.StandardError.ReadToEnd()
        $process.WaitForExit()
        if ($process.ExitCode -ne 0) {
            throw "Falha ao salvar $name. Confira permissoes para Actions Secrets."
        }
    } finally {
        if (-not $process.HasExited) { $process.Kill() }
        $process.Dispose()
    }
}

try {
    $gh = Require-Command 'gh'
    & $gh auth status 1>$null 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "GitHub CLI nao autenticado. Execute 'gh auth login' (nao e login no Codex)."
    }
    & $gh repo view $Repositorio --json nameWithOwner --jq '.nameWithOwner' 1>$null 2>$null
    if ($LASTEXITCODE -ne 0) { throw "Sem acesso ao repositorio $Repositorio." }

    if ($ArquivoContas) {
        if (-not (Test-Path -LiteralPath $ArquivoContas -PathType Leaf)) {
            throw 'Arquivo de contas inexistente.'
        }
        $caminho = (Resolve-Path -LiteralPath $ArquivoContas).Path
        $estadoBruto = [System.IO.File]::ReadAllText($caminho, [System.Text.Encoding]::UTF8)
        Write-Host 'Origem: arquivo privado local.'
    } else {
        $null = Require-Command 'docker'
        if (-not $Container) {
            $ativos = @(& docker ps --format '{{.Names}}' 2>$null)
            if ($LASTEXITCODE -ne 0) { throw 'Docker nao esta acessivel.' }
            $candidatos = @($ativos | Where-Object { $_ -match '(?i)(codex.*proxy|proxy.*codex)' })
            if ($candidatos.Count -eq 0) {
                throw 'Nao encontrei proxy em execucao. Inicie-o ou informe -ArquivoContas.'
            }
            if ($candidatos.Count -gt 1) {
                throw 'Varios proxies encontrados; informe -Container com o nome correto.'
            }
            $Container = [string]$candidatos[0]
        }
        $linhas = @(& docker exec $Container sh -c 'cat /app/data/accounts.json' 2>$null)
        if ($LASTEXITCODE -ne 0 -or $linhas.Count -eq 0) {
            throw 'Nao consegui ler accounts.json do proxy. Use -ArquivoContas para um backup local.'
        }
        $estadoBruto = [string]::Join([Environment]::NewLine, $linhas)
        Write-Host "Origem: container '$Container' (tokens ocultos)."
    }

    if ([System.Text.Encoding]::UTF8.GetByteCount($estadoBruto) -gt 45000) {
        throw 'Arquivo de contas grande demais para migrar automaticamente.'
    }
    try { $estado = $estadoBruto | ConvertFrom-Json -ErrorAction Stop }
    catch { throw 'O estado das contas nao e JSON valido.' }
    if (-not $estado -or -not $estado.records) {
        throw 'O arquivo nao possui records.'
    }
    $registros = @($estado.records)
    if ($registros.Count -lt 1 -or $registros.Count -gt 20) {
        throw 'Quantidade de contas inesperada.'
    }
    foreach ($registro in $registros) {
        if (-not $registro.token -or
            [string]::IsNullOrWhiteSpace([string]$registro.token.access_token) -or
            [string]::IsNullOrWhiteSpace([string]$registro.token.refresh_token)) {
            throw 'Tokens invalidos ou ausentes. Nenhum foi exibido.'
        }
    }

    $bytes = New-Object byte[] 48
    $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    try { $rng.GetBytes($bytes) } finally { $rng.Dispose() }
    $chave = [Convert]::ToBase64String($bytes).TrimEnd('=').Replace('+','-').Replace('/','_')

    Set-SecretFromMemory 'CODEX_PROXY_ACCOUNTS_JSON' $estadoBruto $gh
    Set-SecretFromMemory 'CODEX_PROXY_API_KEY' $chave $gh

    Write-Host "Secrets configurados em $Repositorio (valores nao exibidos)."
    Write-Host ("Contas importadas: {0}" -f $registros.Count)
    Write-Host 'GitHub > Actions > Codex Proxy - validar ou gerar imagem > Run workflow'
    Write-Host 'Teste: modo=ephemeral e operacao=health (nao gera imagem).'
    Write-Host 'Se os tokens estiverem expirados, pode ser necessaria nova autorizacao.'
} finally {
    $estadoBruto = $null
    $chave = $null
}
