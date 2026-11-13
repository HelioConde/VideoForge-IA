# Codex Proxy — infraestrutura de geração de imagens no GitHub Actions

Atualizado em 13/11/2026. Prioridade de implementação: usar `10/chatgpt-codex-proxy` como adaptador central de IA para os módulos futuros do VideoForge-IA. **O renderizador MP4 existente e a hierarquia `canal/` não mudam.**

## Fonte e verificação

- Fonte: https://github.com/10/chatgpt-codex-proxy
- Commit fixado e auditável: `02f8ce3581c15eb11b2d65daf93c3d4e3bd0e635`
- Dockerfile upstream constrói Go **dentro do estágio de build**, com runtime Alpine e binário estático.
- Imagem reutilizável: `ghcr.io/helioconde/videoforge-codex-proxy:upstream-02f8ce3581c1`.
- Interface documentada: `GET /health`, `GET /health/live`, `POST /v1/images/generations`, `POST /v1/images/edits`, `POST /v1/responses`, `GET /v1/models`.
- APIs privadas do ChatGPT/Codex usadas pelo terceiro **não são API oficial pública, podem mudar e estão sujeitas às condições e disponibilidade do serviço**. A existência da rota não comprova capacidade ou cota de sua conta.

## Evitar reinstalar Go, Docker e outras ferramentas em cada workflow

1. **`.github/workflows/proxy-image.yml`**: é executado automaticamente **uma vez** quando o arquivo de workflow entra na branch `main` (também permite execução manual) para criar imagem compilada e publicá-la no GHCR. Buildx usa cache GitHub Actions. Ao atualizar o upstream, revisar o commit, substituir SHA e tag nos dois workflows e reconstruir; nunca usar `@main` ou `:latest` em produção.
2. **`.github/workflows/proxy-images.yml`**: nunca instala Go nem recompila o proxy. No modo `ephemeral`, apenas baixa a imagem já compilada no GHCR; no modo `persistent`, acessa um serviço HTTPS existente e nem precisa baixar imagem.
3. O GitHub hospedado descarta o disco depois do job. **Não há garantia de zero downloads de imagens/binários**, mas não há reinstalação/compilação Go por execução. Para cache e sessões duráveis, usar container persistente com armazenamento seguro em VPS/self-hosted runner.
4. Não fazer `go run`, `go install`, `git clone` do upstream ou `docker build` nos jobs de geração de vídeo, imagem ou pesquisa. Esses jobs usam apenas a API do serviço ou a imagem publicada.

## Modo preferido: persistent

Manter uma instância do proxy rodando em servidor próprio, self-hosted runner ou contêiner de serviço com **volume persistente** e HTTPS. Fazer login por dispositivo **uma vez** nesse servidor; não usar contas de terceiros ou contornar controles de autenticação/quotas. No repositório VideoForge-IA, criar em **Settings → Secrets and variables → Actions → Repository secrets**:

- `CODEX_PROXY_BASE_URL`: URL HTTPS do proxy persistente, ex.: `https://proxy.seudominio.example`. Não colocar token na URL.
- `CODEX_PROXY_API_KEY`: chave longa, aleatória, idêntica à variável `PROXY_API_KEY` do servidor.

Nunca armazenar `accounts.json`, cookies, refresh/access tokens, arquivos `.env`, saída de debug ou respostas completas em Git, artifacts ou logs. Limitar acesso da instância do proxy; é uma API administrativa também. Não expor a porta sem autenticação e TLS.

Usar Actions → **Codex Proxy - validar ou gerar imagem (manual)** → `modo=persistent` e inicialmente `operacao=health` (apenas credenciais e contador de contas). Depois executar `operacao=generate` com canal e pauta reais; gera **uma imagem** por disparo manual e arquiva como artifact por 3 dias (sem fazer upload ao YouTube).

## Modo alternativo: ephemeral (somente testes)

1. Rodar `proxy-image.yml` na main; a imagem precisa existir no GHCR, e o workflow precisa de acesso ao pacote.
2. Criar `CODEX_PROXY_API_KEY` com uma chave aleatória longa.
3. Criar secret `CODEX_PROXY_ACCOUNTS_JSON` contendo o **conteúdo JSON completo** do arquivo privado `accounts.json` do seu proxy autorizado (objeto `{"records":[...], "rotation_strategy":"least_used"}`). Nunca copiar isso para a conversa, repositório ou issue.
4. Executar o workflow manual `proxy-images.yml` com `modo=ephemeral` e `operacao=health`, depois `generate` se realmente desejar.

O contêiner só expõe `127.0.0.1:18080`, roda sem privilégios e com filesystem somente leitura exceto diretório temporário de estado; ao final, é encerrado e o estado apagado. **Atenção:** se a sessão OAuth atualizar os tokens durante o job, essa atualização será perdida; o Secret original pode expirar. Uma secret no Actions **não é armazenamento de sessão persistente**. Preferir `persistent` para produção. Não tentar renovar senha ou dispositivo a cada job. Não fazer rotação cega em caso de HTTP 429.

## Destino das imagens e integridade

Uma geração bem-sucedida salva no job:

```text
output/<canal>/videos/<video-id>/imagens/<cena>.<png|jpg|webp>
output/<canal>/videos/<video-id>/imagens/<cena>.meta.json
```

O código `videoforge/proxy_images.py` valida canal, identificadores, HTTPS/loopback, imagem base64, tamanho, assinatura, hash SHA-256 e evita downloads de URLs de terceiros. Prompt e credenciais não são registrados no relatório. A arte gerada deve passar por **QA visual e consistência de personagens** antes de ir ao manifesto `canal/<id>/videos/<video-id>/video.json`; o artifact de Actions não publica e não faz commit da imagem. Para render real, assets precisam estar presentes no filesystem do renderizador.

## Regras operacionais permanentes

- **Um gateway de IA** para pesquisa/roteiro/imagens futuros; passar pelo proxy, nunca duplicar implementações de Go em cada agent.
- Geração de imagens e edição usam rotas diferentes; **só geração está implementada no cliente desta etapa**; edição permanece planejada.
- Sem chamadas de IA em PRs, pushes, smoke tests ou `health`: somente `workflow_dispatch` com `operacao=generate` gera imagem.
- Para cada cena, fixar estilo, proporções, aparência, cenário, contexto e referências; não misturar realismo/fantasia sem intenção e revisão.
- Respeitar limites/cotas e registrar falha, nunca chamar de concluído sem artifact real e QA visual. Uma imagem gerada não é vídeo MP4.
- Não confiar em outputs para inferir direitos sobre imagens de anime, músicas ou personagens. Rever políticas oficiais de conteúdo de IA e direito autoral.
- Não permitir que parâmetros de workflows substituam URLs/credenciais secretas; acesso somente a partir da configuração aprovada.
- A aprovação deste suporte **não habilita** upload público, geração de 30 imagens em lote ou consumo recorrente automático. Ampliação exige novos testes, limite/custo e revisão humana.

## Imagem de ambiente para FFmpeg e demais programas

O mesmo padrão de pré-compilação vale para o renderizador de vídeo. O Dockerfile `infra/containers/Dockerfile.media` instala Python 3.12, FFmpeg/FFprobe, fontes, git e ferramentas básicas apenas durante o **build da imagem**. O workflow `.github/workflows/media-image.yml` publica a imagem `ghcr.io/helioconde/videoforge-media-runner:ubuntu2404-ffmpeg-v2` no GHCR automaticamente quando seu Dockerfile/workflow for alterado na `main`.

**Migração em duas fases:** imagem Ubuntu 24.04/FFmpeg 6.x publicada e validada primeiro; agora o workflow `.github/workflows/mvp.yml` utiliza `jobs.<job>.container.image` com essa tag. O QA deve continuar obrigatório antes de qualquer distribuição. A imagem já pronta é baixada pelo runner em cada job novo, mas não há `apt-get install ffmpeg` ou `setup-python` a cada execução. Se a ferramenta for atualizada, versionar tag, reconstruir e validar antes de trocar consumidores.

### Compatibilidade comprovada de FFmpeg

O teste do primeiro contêiner Debian 12 com FFmpeg **5.1** falhou no QA `MP4_QA_FAILED` (workflow PR #9), embora o mesmo teste passasse no Ubuntu 24.04 do GitHub Actions. Por segurança, a base foi corrigida para **Ubuntu 24.04/FFmpeg 6.x** e tag `ghcr.io/helioconde/videoforge-media-runner:ubuntu2404-ffmpeg-v2`; não promover imagem 5.1 para MP4 sem testes. O teste deve comprovar vídeo H.264/AAC, duração e QA antes de migrar o job consumidor.
