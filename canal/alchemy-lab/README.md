# Alchemy Lab

Identificador: `alchemy-lab` · idioma: `pt-BR`.

> **Leia primeiro a [estratégia editorial deste canal](ESTRATEGIA.md).** Ela complementa as regras compartilhadas do projeto e é obrigatória para futuras propostas de pauta, roteiro, artes e análise.
>
> **Direção editorial:** laboratório de doramas em pt-BR, com mini-histórias originais, romances, dilemas e reviravoltas ilustrados por IA. Pesquisar tendências verificáveis, testar formatos e registrar aprendizados sem afirmar performance inexistente. O `gerador_padrao` atual é apenas provisório e não significa que o gerador de dorama já exista.

- `canal.json`: identidade, parâmetros e modelo padrão; YouTube desconectado e uploads desabilitados.
- `editorial/candidatos.json`: pautas pesquisadas (atualmente vazio).
- `editorial/reservas.json`: reservas antirrepetição (atualmente vazio).
- `editorial/pesquisas/`: futuras fontes públicas datadas, sem inventar métricas.
- `conteudos/indice.json`: índice de referências, não fila de geração.
- `videos/<video-id>/video.json`: configuração de cada vídeo (ainda não existe um vídeo aprovado).
- `output/alchemy-lab/videos/<video-id>/` (na raiz do projeto): MP4, mídias e QA fora do Git.

**Estado:** Canal catalogado; sem integração de geração nem YouTube. Nenhuma produção nem aprovação editorial está implícita nestes arquivos.


## Produção em andamento: dorama MMORPG original — Conquiste a Princesa

- [Roteiro revisado](videos/mmorpg-conquiste-a-princesa-ep01/roteiro.md), [direção técnica por rigs/Remotion](videos/mmorpg-conquiste-a-princesa-ep01/direcao-rig-remotion.json) e [plano técnico de separação](videos/mmorpg-conquiste-a-princesa-ep01/PLANO-ARTE-RIG-EP01.md).
- [Assets arquivados neste canal](videos/mmorpg-conquiste-a-princesa-ep01/assets/): 14 PNGs de imagens-mãe, referência dos personagens, fundo reconstruído e candidatos RGBA com origem e SHA256. As cenas 02 e 03 e a camada conjunta têm apontamentos de QA/reprovação.
- [12 partes separadas de Kael, somente por pixels existentes](videos/mmorpg-conquiste-a-princesa-ep01/assets/cena-01/rig-drafts/kael/) — QA determinístico de recomposição verificado; underlays, pivôs, halo e rig real ainda não aprovados.
- **Regra desta etapa: não gerar imagens novas.** Usar os PNGs existentes e os scripts de separação/arquivo. As oito variações feitas anteriormente no chat podem ser importadas pelo [workflow sem geração](../../.github/workflows/import-alchemy-existing-chat-assets.yml) após upload do ZIP existente.
- **Não há MP4 oficial, render aprovado, nem upload ao YouTube.** Os assets arquivados não alteram as permissões de publicação nem a regra do manual global.
