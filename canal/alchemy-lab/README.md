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


## Produção em andamento: dorama MMORPG — Conquiste a Princesa

**Arte em pré-produção, sem geração de novas imagens:** o episódio tem [roteiro de 14 cenas](videos/mmorpg-conquiste-a-princesa-ep01/roteiro.md), [direção de 37 planos para rigs/Remotion](videos/mmorpg-conquiste-a-princesa-ep01/direcao-rig-remotion.json) e [plano de QA](videos/mmorpg-conquiste-a-princesa-ep01/PLANO-ARTE-RIG-EP01.md).

- [55+ arquivos PNG arquivados neste canal](videos/mmorpg-conquiste-a-princesa-ep01/assets/), incluindo 14 imagens-mãe, referência de personagens, fundo reconstruído e rascunhos de recortes. A contagem verificada em 14/11/2026 é de **56 PNGs**.
- [Seleção recomendada de sprites C01](videos/mmorpg-conquiste-a-princesa-ep01/rig-selecao-artes-c01.json): Kael **alinhado à cena-mãe**, guardas com textura RGB original, lanças cruzadas originais e candidato de Aldric recortado por máscara. Nenhuma camada é considerada rig aprovada.
- [Kael alinhado e suas 12 partições](videos/mmorpg-conquiste-a-princesa-ep01/assets/cena-01/rig-drafts/kael-alinhado-partes/) substituem **para fins de pré-produção** os recortes em escala errada anteriores. A recomposição preserva os pixels visíveis, mas não resolve braços e anatomia ocultos.
- [Guardas refinados](videos/mmorpg-conquiste-a-princesa-ep01/assets/cena-01/rig-drafts/guardas-refinados/) têm versões com e sem lança (esta última possui buracos a reconstruir); [Aldric](videos/mmorpg-conquiste-a-princesa-ep01/assets/cena-01/rig-drafts/aldric-origem/) é apenas candidato devido ao contato com os braços do trono.
- **Regra máxima deste episódio:** [NÃO GERAR NOVAS IMAGENS](videos/mmorpg-conquiste-a-princesa-ep01/SEM-GERACAO-NOVAS-IMAGENS.lock). Seis workflows que chamariam IA de imagem respeitam esse bloqueio; scripts de máscara usam apenas pixels anteriores.
- As oito variações geradas no chat permanecem em [catálogo de importação pendente](videos/mmorpg-conquiste-a-princesa-ep01/IMAGENS-EXTERNAS-PENDENTES.json): o ZIP está na conversa, mas a transferência binária para este GitHub ainda precisa ocorrer pela [pasta de importação](videos/mmorpg-conquiste-a-princesa-ep01/uploads/).

**Ainda não há MP4 oficial, rig articulado aprovado ou publicação no YouTube.** As cenas 02 e 03 continuam visualmente reprovadas e não devem ser tratadas como artes validadas.
