# Modelos de produção — reutilizáveis entre canais

Cada receita mora em `modelos/<id>/modelo.json` e indica se está operacional. **Modelo técnico de produção não é modelo de IA.** Nenhuma credencial fica nessa pasta.

- [imagem-estatica/modelo.json](imagem-estatica/modelo.json): disponível no MVP para montar imagens e narração fornecidas com FFmpeg.
- [camadas-animadas/modelo.json](camadas-animadas/modelo.json): planejado; não declara cenas ou personagens animados como concluídos.

Precedência: `video.json.modelo` (opcional) > `canal.json.modelo_padrao`.
O renderizador verifica a existência e o estado do modelo e rejeita pedidos incompatíveis antes de processar arquivos. Os provedores e geradores especializados serão configurados somente após o MP4 de produção funcionar.
