#requires -Version 5.1
<#
.SYNOPSIS
  Reconecta a conta do Codex Proxy LOCAL via device login e reimporta secrets do VideoForge.
.DESCRIPTION
  A sessao OAuth importada em CODEX_PROXY_ACCOUNTS_JSON venceu e o refresh remoto
  falhou HTTP 502. Esta rotina exige abrir URL de login OFICIAL no navegador do
  usuario, nunca imprime access/refresh tokens, nao cria imagens nem publica YouTube.
  Usa o container Docker local em execucao, com porta 8080 publicada em localhost.
.EXAMPLE
  .\scripts\renovar-sessao-videoforge.ps1 -Container chatgpt-codex-proxy
#>
[CmdletBinding()]
param([string]$Container = 'chatgpt-codex-proxy')

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$secretKey = $null
$headers = $null
try {
    foreach ($name in @('docker', 'gh')) {
        if (-not (Get-Command $name -ErrorAction SilentlyContinue)) {
            throw "Comando $name nao encontrado."
        }
    }
    & docker inspect $Container --format '{{.State.Running}}' 2>$null | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "Container $Container nao encontrado/inativo." }
    $rawEnv = & docker inspect $Container --format '{{json .Config.Env}}' 2>$null
    if ($LASTEXITCODE -ne 0) { throw 'Nao foi possivel inspecionar o container local.' }
    $vars = @($rawEnv | ConvertFrom-Json)
    $keyPair = @($vars | Where-Object { $_ -is [string] -and $_.StartsWith('PROXY_API_KEY=') })
    if ($keyPair.Count -ne 1) { throw 'PROXY_API_KEY nao configurada no container.' }
    $secretKey = ([string]$keyPair[0]).Substring('PROXY_API_KEY='.Length)
    if ($secretKey.Length -lt 20) { throw 'PROXY_API_KEY invalida no container.' }
    $ports = @(& docker port $Container '8080/tcp' 2>$null)
    if ($LASTEXITCODE -ne 0 -or $ports.Count -lt 1) {
        throw 'Proxy precisa publicar a porta 8080 no host para autenticar localmente.'
    }
    $port = $null
    foreach ($line in $ports) {
        if ([string]$line -match ':(\d{2,5})$') { $port = [int]$Matches[1]; break }
    }
    if (-not $port -or $port -gt 65535) { throw 'Porta Docker invalida.' }
    $url = "http://127.0.0.1:$port"
    $headers = @{Authorization = "Bearer $secretKey"; Accept='application/json'}
    $live = Invoke-RestMethod -Uri "$url/health/live" -Method Get -TimeoutSec 10
    if ($live.status -ne 'ok') { throw 'Health do container local nao esta pronto.' }
    Write-Host 'Iniciando autenticacao oficial em dispositivo, sem exibir tokens.'
    $login = Invoke-RestMethod -Uri "$url/admin/accounts/device-login/start" `
        -Method Post -Headers $headers -Body '{}' -ContentType 'application/json' -TimeoutSec 35
    if (-not $login.login_id -or -not $login.auth_url -or -not $login.user_code) {
        throw 'Device login nao forneceu as instrucoes esperadas.'
    }
    $authUrl = [string]$login.auth_url
    if (-not $authUrl.StartsWith('https://auth.openai.com/')) {
        throw 'URL de autenticacao inesperada; operacao interrompida.'
    }
    Write-Host ("Acesse: {0}" -f $authUrl)
    Write-Host ("Codigo: {0}" -f $login.user_code)
    Start-Process $authUrl
    Write-Host 'Autorize no navegador com a conta que usa o Codex. O programa aguarda a conclusao.'
    $deadline = [DateTime]::UtcNow.AddMinutes(10)
    $status = ''
    while ([DateTime]::UtcNow -lt $deadline) {
        Start-Sleep -Seconds 5
        $result = Invoke-RestMethod -Uri "$url/admin/accounts/device-login/$($login.login_id)" `
            -Method Get -Headers $headers -TimeoutSec 25
        $status = [string]$result.status
        if ($status -eq 'ready') { break }
        if ($status -eq 'expired' -or $status -eq 'error') {
            throw 'Login expirou ou foi recusado; iniciar novamente.'
        }
    }
    if ($status -ne 'ready') { throw 'Login nao foi concluido; nenhum secret alterado.' }
    Write-Host 'Conta autenticada. Importando novo snapshot privado no VideoForge-IA.'
    & (Join-Path $PSScriptRoot 'migrar-codex-proxy.ps1') -Container $Container
    if (-not $?) { throw 'Falha na importacao privada dos secrets.' }
    Write-Host 'Concluido. Use o workflow proxy-health-official.yml para validar antes de gerar imagens.'
} finally {
    $secretKey = $null
    $headers = $null
    $vars = $null
    $rawEnv = $null
}
