# Otaku Multicena

Identificador: `otaku-br` · idioma: `pt-BR`.

> **Leia primeiro a [estratégia editorial deste canal](ESTRATEGIA.md).** Ela complementa as regras compartilhadas do projeto e é obrigatória para futuras propostas de pauta, roteiro, artes e análise.
>
> **Direção editorial:** explicações, curiosidades e teorias de animes em pt-BR a partir de pesquisas verificadas, sem repetir temas do histórico. Novas pautas de **Death Note** estão pausadas até orientação contrária. Imagens de IA sempre coerentes entre cenas.

- `canal.json`: identidade, parâmetros e modelo padrão; YouTube desconectado e uploads desabilitados.
- `editorial/candidatos.json`: pautas pesquisadas (atualmente vazio).
- `editorial/reservas.json`: reservas antirrepetição (atualmente vazio).
- `editorial/pesquisas/`: futuras fontes públicas datadas, sem inventar métricas.
- `conteudos/indice.json`: índice de referências, não fila de geração.
- `videos/<video-id>/video.json`: configuração de cada vídeo (ainda não existe um vídeo aprovado).
- `output/otaku-br/videos/<video-id>/` (na raiz do projeto): MP4, mídias e QA fora do Git.

**Estado:** Neste MVP usa imagem-estatica. O camadas-animadas original permanece planejado e não será fingido como operacional. Nenhuma produção nem aprovação editorial está implícita nestes arquivos.
