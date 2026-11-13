# Canais do VideoForge IA

Mesma organização do projeto anterior: **cinco canais isolados**, cada um com identidade, editorial, índice de conteúdos e vídeos próprios.

| Canal | Pasta | Modelo padrão atual | Situação |
| --- | --- | --- | --- |
| Otaku Multicena | [otaku-br/](otaku-br/README.md) | `imagem-estatica` | Render MVP a partir de assets fornecidos |
| Otaku Reframe | [otaku-en/](otaku-en/README.md) | `imagem-estatica` | Cadastro, sem executor |
| Conde Games | [gamer/](gamer/README.md) | `imagem-estatica` | Cadastro, sem executor |
| Emanuelly Kids | [manu-kids/](manu-kids/README.md) | `camadas-animadas` | Modelo planejado, sem executor |
| Alchemy Lab | [alchemy-lab/](alchemy-lab/README.md) | `imagem-estatica` | Cadastro, sem executor |

## Regra permanente

- `canal/<id>/canal.json`: identidade, idioma, modelo padrão e YouTube desabilitado.
- `canal/<id>/conteudos/indice.json`: catálogo editorial, jamais fila de jobs.
- `canal/<id>/editorial/candidatos.json`, `reservas.json`, `pesquisas/`: pesquisa, decisões e controle de repetição **por canal**.
- `canal/<id>/videos/<video-id>/video.json`: manifesto versionável do vídeo real. Mídias e dados privados nunca entram no Git.
- `modelos/<id>/modelo.json`: receita reutilizável e opcionalmente sobrescrita no vídeo.
- `output/<id>/editorial/` ou `output/<id>/videos/<video-id>/`: saídas temporárias, ignoradas pelo Git.

Os dados públicos catalogados não comprovam acesso OAuth, pesquisa da equipe, reserva real ou publicação.

**Diferença intencional:** o Otaku Multicena usava `camadas-animadas` como padrão provisório no projeto anterior. Aqui usa `imagem-estatica` até a primeira produção estar operacional; o modelo de camadas continua cadastrado como **não implementado**.
