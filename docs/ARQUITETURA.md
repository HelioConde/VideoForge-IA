# Arquitetura do VideoForge IA — pastas por responsabilidade

Esta reconstrução preserva **as regras de diretórios** do repositório anterior `HelioConde/video-forge-ia2`, mas não copia código legado, secrets, estado de contas nem jobs automáticos.

```text
VideoForge-IA/
├── canal/
│   ├── otaku-br/
│   │   ├── canal.json
│   │   ├── README.md
│   │   ├── conteudos/indice.json
│   │   ├── editorial/
│   │   │   ├── candidatos.json
│   │   │   ├── reservas.json
│   │   │   └── pesquisas/YYYY-MM-DD.json (somente quando houver pesquisa real)
│   │   └── videos/<video-id>/video.json
│   ├── otaku-en/
│   ├── gamer/
│   ├── manu-kids/
│   └── alchemy-lab/
├── modelos/<id>/modelo.json
├── geradores/ (futuro, sem execução paga)
├── videoforge/ (código Python reutilizável)
├── tests/ (sem IA paga)
├── docs/
└── output/<id>/videos/<video-id>/ (MP4 e QA, ignorados pelo Git)
```

## Isolamento / organização permanente

1. Nenhum dado editorial ou mídia de um canal entra na pasta de outro. Configuração no `canal.json`; dados públicos de cada canal em `editorial`; reservas reais só depois de validação.
2. Um manifesto executável usa **exatamente** `canal/<channel>/videos/<video-id>/video.json`; `channel` do JSON deve corresponder à pasta e a `canal.json.id`.
3. A saída por padrão é `output/<channel>/videos/<video-id>/video.mp4` e seu QA `video.qa.json`, não `dist/` nem outra pasta. Arquivos gerados não devem ser versionados.
4. Modelo técnico herdado de `canal.json.modelo_padrao` ou sobrescrito por `video.json.modelo`; só `imagem-estatica` está implementado no MVP, sem animações artificiais.
5. `videoforge/paths.py` valida configuração, destino e diretórios; reprova caminhos de outro canal, symlinks e modelos ausentes ou não operacionais **antes do FFmpeg**.
6. `smoke` permanece separado em `dist/smoke.mp4`, apenas simulação técnica de ~5 segundos no CI, sem conteúdo de YouTube.
7. `output/<channel>/editorial/` é reservado para relatórios temporários futuros; decisão e registros privados exigirão proteção própria antes de qualquer integração.

## Escopo atual

O renderizador de mídia já fornecida produz vídeo 1080×1920, áudio AAC, H.264, legendas e QA técnico. Falta automatizar pesquisa, roteiro, imagens, narração e animações; **não** tratar os registros dos cinco canais ou modelos planejados como agentes ativos. Publicação no YouTube desabilitada. Não alterar repositórios legados.
