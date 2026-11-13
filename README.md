# VideoForge IA — reconstrução orientada a MP4

Novo projeto: **primeiro entregar um MP4 verificável**, depois conectar
pesquisa, agentes, modelos de imagem e YouTube Analytics. O repositório
anterior permanece como histórico; não é dependência deste projeto.

## Estado da primeira versão

- **Compositor de vídeo real**: recebe imagens e narrações fornecidas,
  redimensiona para 1080 × 1920, adiciona legendas visíveis por cena,
  combina as faixas de áudio e salva um MP4 H.264 + AAC.
- **QA automático**: verifica áudio, vídeo, duração, resolução e SHA-256.
- **Smoke test real**: gera um MP4 de aproximadamente 5 segundos com
  imagens e tons **sintéticos**, rotulado como teste, no GitHub Actions.
  **Este artefato não é um vídeo de produção do Otaku Multicena.**
- **Sem uso de créditos de IA, sem segredos e sem publicação no YouTube.**
- Primeira produção de Otaku Multicena exige **90 a 180 segundos**;
  imagens e vozes reais precisam ser fornecidas no manifesto.

## Executar

Requer Python 3.12+ e FFmpeg/FFprobe no PATH. Não precisa instalar pacotes Python.

Teste técnico:

    python -m unittest discover -s tests -v
    python -m videoforge.mvp smoke --output dist/smoke.mp4

Renderização de produção, após fornecer assets e um manifesto válido:

    python -m videoforge.mvp render --manifest projects/otaku-br/episodio-001.json --output dist/episodio-001.mp4

Exemplo do formato (os arquivos abaixo devem existir ao lado do JSON):

    {
      "schema": "videoforge/mvp/v1",
      "channel": "otaku-br",
      "youtube_upload": false,
      "scenes": [
        {"image": "imagens/cena-01.png", "audio": "voz/cena-01.mp3", "caption": "Legenda original 1"},
        {"image": "imagens/cena-02.png", "audio": "voz/cena-02.mp3", "caption": "Legenda original 2"},
        {"image": "imagens/cena-03.png", "audio": "voz/cena-03.mp3", "caption": "Legenda original 3"}
      ]
    }

O programa mede a duração total das narrações. Para produção, a soma deve
ficar entre 90 e 180 segundos. O exemplo é apenas um esquema, não contém
arquivos de áudio/imagem e não pode ser renderizado sem eles.

## Próximos marcos

1. Validar o **MP4 técnico real** em GitHub Actions.
2. Renderizar um vídeo de 90–180s com **imagens e áudio reais**, fornecidos
   por um provedor explicitamente configurado, sem depender do Proxy anterior.
3. Acrescentar pesquisa e três agentes independentes (Pesquisador, Diretor,
   Produtor) somente depois que o render estiver funcionando.
4. Integrar métricas do YouTube, revisão humana e, separadamente, upload.

**Importante:** todo artefato recebe QA técnico; isso não constitui aprovação
visual ou editorial. Não usar o vídeo de teste como vídeo do canal.
