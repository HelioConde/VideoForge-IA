# Regras editoriais, registro e ordem de pastas

Atualizado em **13/11/2026**. Este documento detalha a organização de pesquisas, vídeos e fontes para o VideoForge IA, **sem habilitar agentes ou publicação no YouTube**.

## Ordem de leitura obrigatória

1. `README.md`: estado e objetivo MP4-first.
2. `AGENTS.md`: regras de integridade, segurança e QA.
3. `docs/ARQUITETURA.md`: hierarquia técnica e isolamento.
4. Este documento: procedimento editorial e metadados de vídeo.
5. `canal/README.md`, `canal/<id>/README.md`, `canal/<id>/canal.json`, os índices e reservas do canal.
6. `docs/referencias/CATALOGO-CURSOS-YOUTUBE.md` e `docs/referencias/GUIA-OFICIAL-YOUTUBE-CREATORS.md`, quando a atividade envolver pesquisa, crescimento, SEO, storytelling, edição, Shorts, direitos e uso de IA. **Não alegar que as aulas já foram assistidas.** As orientações oficiais foram consultadas; as aulas dos cursos não foram verificadas.

## Hierarquia que não pode ser quebrada

A fonte de verdade é **`canal/` (singular)**. Os cinco canais cadastrados na reconstrução são `otaku-br` (Otaku Multicena), `otaku-en` (Otaku Reframe), `gamer` (Conde Games), `manu-kids` (Emanuelly Kids) e `alchemy-lab` (Alchemy Lab). **Não criar `canais/`**, nem adicionar canais ou aliases com base apenas em um nome parecido. Os modelos de produção continuam exclusivamente em `modelos/`, os geradores em `geradores/`, e os cursos em `docs/referencias/`.

```text
canal/<id>/
├── canal.json
├── README.md
├── conteudos/indice.json               # referências do canal, não jobs
├── editorial/
│   ├── candidatos.json                  # pesquisas futuras verificadas
│   ├── reservas.json                    # controle de assuntos
│   ├── historico-videos.json            # ID/assunto/estado dos vídeos
│   └── pesquisas/YYYY-MM-DD.json        # somente após pesquisa real
└── videos/
    ├── README.md
    └── <video-id>/
        ├── editorial.json              # informações de criação e desempenho
        └── video.json                  # manifesto técnico do MVP, quando houver assets
```

A pasta de um vídeo só deve ser criada quando existir pauta ou produção **real e identificável**. O `editorial.json` é um registro **opcional para o código atual, obrigatório para a organização de novas pautas**; seu modelo fica em `docs/modelos/REGISTRO-EDITORIAL-VIDEO.template.json`. Não sobrescrever o formato `videoforge/mvp/v1` de `video.json`. Os dados binários reais ficam fora do Git conforme `AGENTS.md`.

## Processo obrigatório por vídeo

1. **Inventário e pesquisa:** revisar `editorial/historico-videos.json`, `reservas.json`, `conteudos/indice.json` e vídeos reais publicados via fonte oficial, quando houver conexão autorizada. Anotar URLs, consultas e datas; dados de YouTube/vidIQ não verificados não entram como fatos.
2. **Antirrepetição:** comparar assunto, obra/anime, personagens, promessa, roteiro, tags e temas próximos. Só prosseguir com justificativa documentada. Histórico vazio **não equivale** a histórico verificado.
3. **Decisão editorial:** registrar hipótese de audiência, formato, duração prevista, tema, gancho, ângulo original, roteiro, aprovação e responsáveis.
4. **SEO:** guardar pesquisa de palavras-chave, fontes, título, descrição, tags/hashtags, plano de thumbnail, data e motivos. Os 23 cursos catalogados são sugestões de estudo, não prova de que suas técnicas funcionam.
5. **Consistência de arte:** fixar guia visual (estilo, personagens, cenário, cores, referências e prompts) para todas as cenas; não misturar imagens realistas e ilustradas sem decisão explícita.
6. **Produção e QA:** só chamar produção com assets existentes e autorização apropriada; registrar URLs/hashes de artefatos, dados de QA e falhas comprovadas. Smoke técnico nunca é vídeo editorial.
7. **Publicação e aprendizado:** guardar ID/URL e data reais do vídeo, métricas com fonte/data (CTR, impressões, retenção, views, inscritos, comentários); quando não houver dados, usar `null`, nunca inventar números. Atualizar índice e notas para decisões futuras.

## Estados

Usar estados descritivos e verificáveis: `ideia`, `pesquisa`, `roteiro`, `assets_pendentes`, `renderizado`, `qa_aprovado`, `publicado`, `pausado` ou `falhou`. Um vídeo não passa para `renderizado` sem arquivo real; não passa para `qa_aprovado` sem relatório; e não passa para `publicado` sem evidência do YouTube.

## Segurança e observações

Não guardar secrets, tokens, credenciais OAuth, vídeos MP4, áudios, frames ou imagens binárias de produção no Git. Manter somente textos, dados não sensíveis e referências verificadas. A criação destes índices **não instala agentes, não consulta APIs, não cria vídeo e não habilita upload**. Continuar respeitando o requisito do Otaku Multicena (90–180 segundos) e as restrições do MVP do `README.md`.

## Aplicar a análise oficial YouTube Creators

Antes de decidir tema, duração, roteiro, SEO ou melhorias, consultar [Guia oficial YouTube Creators](referencias/GUIA-OFICIAL-YOUTUBE-CREATORS.md). Priorizar satisfação/retencao do espectador, títulos e miniaturas fiéis, uso de Analytics por canal e originalidade, não a produção de volume genérico.

**Checklist antes de eventual publicação:** política vigente de Shorts até 3 min; reivindicações de Content ID em Shorts de mais de 1 min; direitos de músicas e vídeos; classificação de conteúdo feito para crianças; declaração necessária de IA realista/sintética; regras de conteúdo reutilizado e massificado. Links oficiais têm precedência sobre páginas antigas que ainda mencionem Shorts de 60 segundos. Esse checklist não habilita upload, não substitui revisão humana e não comprova estado de vídeos.
