#requires -Version 5.1
<#
.SYNOPSIS
  Renova OAuth do Codex em um proxy Docker TEMPORARIO e importa secrets no GitHub.
.DESCRIPTION
  Nao depende de PROXY_API_KEY no container local: usa imagem do proxy que ja
  passou no GitHub Actions, com chave efemera nova e volume Docker temporario.
  O container informado em -Container nunca e alterado; o parametro permanece
  por compatibilidade com o comando utilizado anteriormente.
  O login por dispositivo requer aprovacao pelo navegador do responsavel.
  Nao imprime nem grava tokens no repositorio, nao gera imagens diretamente.
.EXAMPLE
  .\scripts\renovar-sessao-videoforge.ps1 -Container chatgpt-codex-proxy
#>
[CmdletBinding()]
param([string]$Container = 'chatgpt-codex-proxy')

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$secretKey = $null
$headers = $null
$auth = $null
$tempContainer = $null
$tempVolume = $null

function Invoke-DockerSafe([string[]]$Arguments) {
    & docker @Arguments | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw 'Operacao Docker falhou. Confira Docker Desktop, a conexao ao GHCR e as permissoes.'
    }
}

try {
    foreach ($name in @('docker', 'gh')) {
        if (-not (Get-Command $name -ErrorAction SilentlyContinue)) {
            throw "Comando '$name' nao encontrado no PATH."
        }
    }
    & gh auth status 1>$null 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "GitHub CLI precisa estar autenticado. Execute gh auth login."
    }
    & docker info 1>$null 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw 'Docker Desktop nao esta funcionando. Inicie-o antes de executar.'
    }

    Write-Host "Container original '$Container' preservado (nenhuma mudanca nele)."
    Write-Host 'Iniciando proxy descartavel com chave propria, sem depender de PROXY_API_KEY local.'
    $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    $secretBytes = New-Object byte[] 48
    try { $rng.GetBytes($secretBytes) } finally { $rng.Dispose() }
    try {
        $secretKey = [Convert]::ToBase64String($secretBytes).TrimEnd('=').Replace('+','-').Replace('/','_')
    } finally {
        [Array]::Clear($secretBytes, 0, $secretBytes.Length)
    }

    $suffix = '{0}-{1}' -f $PID, [Guid]::NewGuid().ToString('N').Substring(0, 12)
    $tempContainer = "vf-oauth-login-$suffix"
    $tempVolume = "vf-oauth-login-state-$suffix"
    $image = 'ghcr.io/helioconde/videoforge-codex-proxy:upstream-02f8ce3581c1'

    & docker pull $image | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw 'Nao foi possivel baixar a imagem GHCR. Se estiver privada, use gh auth token | docker login ghcr.io -u HelioConde --password-stdin e execute novamente.'
    }

    Invoke-DockerSafe @('volume','create',$tempVolume)
    $argsDocker = @(
        'run', '--detach', '--name', $tempContainer,
        '--read-only', '--tmpfs', '/tmp:rw,nosuid,size=32m',
        '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges',
        '-p', '127.0.0.1::8080',
        '-e', "PROXY_API_KEY=$secretKey", '-e', 'DATA_DIR=/app/data',
        '-e', 'DEBUG_LOG_PAYLOADS=false',
        '-v', ($tempVolume + ':/app/data:rw'),
        $image
    )
    Invoke-DockerSafe $argsDocker
    $argsDocker = $null

    $ports = @(& docker port $tempContainer '8080/tcp' 2>$null)
    if ($LASTEXITCODE -ne 0) { throw 'Nao foi possivel consultar porta do proxy temporario.' }
    $port = $null
    foreach ($entry in $ports) {
        if ([string]$entry -match '^127[.]0[.]0[.]1:(\d{2,5})$') {
            $port = [int]$Matches[1]
            break
        }
    }
    if (-not $port -or $port -gt 65535) {
        throw 'Proxy temporario nao publicou uma porta restrita a localhost.'
    }
    $url = "http://127.0.0.1:$port"
    $headers = @{ Authorization = "Bearer $secretKey"; Accept = 'application/json' }
    $ready = $false
    for ($i=0; $i -lt 25; $i++) {
        try {
            $health = Invoke-RestMethod -Uri "$url/health/live" -Method Get -TimeoutSec 3
            if ($health.status -eq 'ok') { $ready = $true; break }
        } catch {
            # Somente aguardar readiness; sem requests de geracao e sem mostrar respostas.
        }
        Start-Sleep -Seconds 2
    }
    if (-not $ready) { throw 'O proxy temporario nao iniciou corretamente.' }

    Write-Host 'Solicitando autenticacao oficial em dispositivo (sem revelar tokens).'
    $auth = Invoke-RestMethod -Uri "$url/admin/accounts/device-login/start" -Method Post -Headers $headers -Body '{}' -ContentType 'application/json' -TimeoutSec 40
    if (-not $auth.login_id -or -not $auth.auth_url -or -not $auth.user_code) {
        throw 'Proxy nao retornou informacoes validas para o login por dispositivo.'
    }
    $authUrl = [Uri]([string]$auth.auth_url)
    if ($authUrl.Scheme -ne 'https' -or $authUrl.Host -ne 'auth.openai.com' -or
        $authUrl.Port -ne 443 -or -not [string]::IsNullOrEmpty($authUrl.UserInfo)) {
        throw 'URL de autenticacao nao corresponde ao provedor oficial.'
    }
    Write-Host ("Pagina oficial: {0}" -f $authUrl.AbsoluteUri)
    Write-Host ("Codigo do dispositivo: {0}" -f $auth.user_code)
    Start-Process $authUrl.AbsoluteUri
    Write-Host 'Autorize a conta pelo navegador; o proxy verificara a conclusao.'
    $limit = [DateTime]::UtcNow.AddMinutes(10)
    $status = ''
    while ([DateTime]::UtcNow -lt $limit) {
        Start-Sleep -Seconds 5
        $reply = Invoke-RestMethod -Uri "$url/admin/accounts/device-login/$($auth.login_id)" -Method Get -Headers $headers -TimeoutSec 25
        $status = [string]$reply.status
        if ($status -eq 'ready') { break }
        if ($status -eq 'expired' -or $status -eq 'error') {
            throw 'O login foi recusado ou expirou. Nenhum secret foi atualizado.'
        }
    }
    if ($status -ne 'ready') {
        throw 'O login nao foi concluido. Nenhum secret foi atualizado.'
    }

    Write-Host 'Login confirmado; importando as novas credenciais sem exibir o conteudo.'
    & (Join-Path $PSScriptRoot 'migrar-codex-proxy.ps1') -Container $tempContainer
    if (-not $?) { throw 'Falha ao importar as credenciais ao GitHub.' }

    Write-Host 'Validando no GitHub e preparando retomada unica da referencia V2.'
    & gh workflow run proxy-health-official.yml --repo HelioConde/VideoForge-IA --ref main -f resume_remake=true
    if ($LASTEXITCODE -ne 0) {
        throw 'Credenciais importadas, mas workflow nao disparou; verifique GitHub Actions.'
    }
    Write-Host 'Configuracao concluida. Acompanhe a validacao/retomada no GitHub Actions.'
    Write-Host 'https://github.com/HelioConde/VideoForge-IA/actions/workflows/proxy-health-official.yml'
} finally {
    # Never persist the disposable OAuth account state beyond this login.
    if ($tempContainer) { & docker rm -f $tempContainer 1>$null 2>$null }
    if ($tempVolume) { & docker volume rm -f $tempVolume 1>$null 2>$null }
    $secretKey = $null
    $headers = $null
    $auth = $null
    $argsDocker = $null
    $secretBytes = $null
}
