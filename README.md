# VideoForge IA — reconstrução orientada a MP4

Novo projeto: **primeiro entregar um MP4 verificável**, depois conectar
pesquisa, agentes, modelos de imagem e YouTube Analytics. O repositório
anterior, agora `HelioConde/video-forge-ia2`, permanece intacto e serve
somente como referência para organização.

## Estratégia editorial de Shorts

Os materiais de crescimento/SEO enviados em 2026-11-13 foram sintetizados
em [Estratégia de YouTube Shorts](docs/ESTRATEGIA_SHORTS.md), que inclui
pesquisa, antirrepetição por canal, retenção, consistência visual,
métricas e fontes oficiais atualizadas. **Leia o guia antes de planejar**;
essas práticas ainda não são automações implementadas.

## O que já funciona

- Compositor FFmpeg de **imagens e narrações fornecidas**, com legendas,
  MP4 H.264/AAC vertical 1080 × 1920.
- QA automático de vídeo, áudio, duração, resolução e SHA-256.
- Smoke test no GitHub Actions produz clipe técnico sintético de ~5 segundos
  (não é vídeo editorial, não é produção de agentes, sem IA paga).
- Produção do primeiro Otaku Multicena exige **90–180 segundos**
  e a autorização humana para qualquer integração futura de IA.
- Não há publicação no YouTube, nem credenciais no Git.

## Pastas — igual ao VideoForge anterior

```text
canal/
  otaku-br/                         # Otaku Multicena, piloto
    canal.json                      # opções / modelo padrão
    conteudos/indice.json           # referências, não fila automática
    editorial/
      candidatos.json               # pesquisas autenticadas futuras
      reservas.json                 # antirrepetição, começa vazio
      pesquisas/YYYY-MM-DD.json     # futuro, só pesquisa verificável
    videos/
      <video-id>/video.json         # manifesto por vídeo
  otaku-en/                         # Otaku Reframe
  gamer/                            # Conde Games
  manu-kids/                        # Emanuelly Kids
  alchemy-lab/                      # Alchemy Lab
modelos/
  imagem-estatica/modelo.json       # implementado: imagens fornecidas
  camadas-animadas/modelo.json      # PLANEJADO, ainda não implementado
geradores/                          # receitas de nicho futuras
videoforge/                         # código reutilizável
tests/                              # testes offline e FFmpeg
docs/ARQUITETURA.md                 # regra permanente de organização
output/
  <channel>/videos/<video-id>/      # MP4 e QA; ignorado pelo Git
```

Confira [regras dos canais](canal/README.md),
[modelos](modelos/README.md) e
[arquitetura](docs/ARQUITETURA.md).

**Isolamento:** nenhum vídeo, métrica, pauta ou reserva de um canal pode ser
usado como se fosse de outro. O código valida canal e modelo, e bloqueia
o destino de saída fora de seu diretório.

## Executar

Requer Python 3.12+ e FFmpeg/FFprobe no PATH, sem dependências Python extras.

```bash
python -m unittest discover -s tests -v
python -m videoforge.mvp smoke --output dist/smoke.mp4
```

Após fornecer **mídia realmente existente** e o manifesto aprovado:

```bash
python -m videoforge.mvp render --video canal/otaku-br/videos/episodio-001/video.json
```

Esse comando gera o arquivo e relatório QA em:
`output/otaku-br/videos/episodio-001/video.mp4` e
`output/otaku-br/videos/episodio-001/video.qa.json`.

O manifesto `video.json` tem este formato **ilustrativo**:

```json
{
  "schema": "videoforge/mvp/v1",
  "channel": "otaku-br",
  "modelo": "imagem-estatica",
  "youtube_upload": false,
  "scenes": [
    {"image": "imagens/cena-01.png", "audio": "voz/cena-01.mp3", "caption": "Legenda 1"},
    {"image": "imagens/cena-02.png", "audio": "voz/cena-02.mp3", "caption": "Legenda 2"},
    {"image": "imagens/cena-03.png", "audio": "voz/cena-03.mp3", "caption": "Legenda 3"}
  ]
}
```

Os arquivos de imagens e voz devem existir ao lado de `video.json` nos
respectivos subdiretórios, mas **não são versionados**. A narração somada
precisa durar 90–180 segundos. O manifesto de exemplo **não contém mídia
nem aprova a escolha do tema**.

`modelo` é opcional no vídeo e usa por padrão `canal.json.modelo_padrao`.
O Otaku Multicena tinha `camadas-animadas` como padrão provisório no antigo
projeto; nesta reconstrução usa `imagem-estatica` **temporariamente** para
entregar um MP4 real primeiro. O modelo de camadas ainda está desativado.

## Próximos marcos

1. Preservar o MP4 técnico aprovado pelo CI após organização por canal.
2. Renderizar vídeo de 90–180s com áudio e imagens reais, sem falar em
   agentes até haver evidências dos trabalhos deles.
3. Só depois implementar pesquisa, três agentes independentes,
   provedores de IA com limites, identidade visual e animações.
4. YouTube Analytics, QA editorial e publicação são etapas separadas;
   nunca enviar conteúdo automaticamente.

**QA técnico não é aprovação editorial ou visual.**
