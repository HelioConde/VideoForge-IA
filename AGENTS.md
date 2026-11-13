# AGENTS.md — VideoForge IA (reconstrução)

## Instruções obrigatórias para cada tarefa

**Ler nesta ordem, antes de pesquisar ou produzir qualquer vídeo:** `README.md`, `AGENTS.md`, `docs/ARQUITETURA.md`, `docs/REGRAS-EDITORIAIS.md`, `canal/README.md`, `canal/<id>/README.md`, histórico e reservas do canal e, se útil, `docs/referencias/CATALOGO-CURSOS-YOUTUBE.md`.

**Hierarquia com precedência:** a estrutura canônica é **`canal/` no singular**, conforme `docs/ARQUITETURA.md`. Não criar `canais/` alternativo. Separar rigorosamente canais; dados do vídeo em `canal/<id>/videos/<video-id>/editorial.json`, manifesto renderizável em `video.json`, índice de histórico em `canal/<id>/editorial/historico-videos.json`. Não substituir o formato técnico do manifesto. Conferir histórico e temas relacionados antes de criar nova pauta. Não presumir que o índice inicial vazio comprova ausência de vídeos no YouTube.

Os cursos listados são **fontes sugeridas para estudo**, não prova de acesso, aprendizado ou método validado. Não inventar conteúdo das aulas. Não registrar geração, QA ou publicação sem evidências.

## Objetivo inicial

Entregar e comprovar um vídeo MP4 vertical do Otaku Multicena com
90–180 segundos, áudio audível, legendas e identidade visual consistente.
Primeiro validar renderizador; agentes e escritório só depois.

## Regras de execução

- O comando smoke usa mídia sintética para testar tecnologia; **jamais**
  registrar esse clipe como produção realizada por agentes.
- O comando render só usa mídia real explicitamente fornecida;
  não inventar identidade de personagem, fontes ou artefatos.
- Sem upload para YouTube e sem chamadas pagas de IA nesta etapa.
- Jamais adicionar credenciais, respostas privadas, imagens geradas,
  áudio de produção ou MP4s ao Git.
- Registrar origem, orçamento e autorização antes de integrar provedores
  de imagem, voz ou pesquisa; não contornar 429 com repetição cega.
- Manter QA fail-closed; qualquer falha de áudio, duração, resolução
  ou integridade bloqueia declaração de vídeo concluído.
- Alterar código em branch/PR e verificar CI antes de integrar.
- Não tocar no repositório antigo. Organizar arquivos por canal,
  preservar documentação e não introduzir agentes visuais fictícios.

## Validação

    python -m unittest discover -s tests -v
    python -m videoforge.mvp smoke --output dist/smoke.mp4

Conferir artefato de Actions: video H.264, áudio AAC, 1080 × 1920 e QA JSON.
Esse teste não autoriza vídeo público nem consumo de IA.

## Organização permanente — mesmo contrato do VideoForge anterior

Sempre consultar `README.md` e `docs/ARQUITETURA.md` antes de editar.
A estrutura do repositório anterior `HelioConde/video-forge-ia2` é a
referência **apenas para organização**, sem copiar credenciais, pipelines
complexos nem trabalhos fictícios.

- Cada canal vive exclusivamente em `canal/<id>/`; seus dados não podem
  migrar nem ser misturados com os de outro canal.
- Em `canal/<id>/`, manter `canal.json`, `README.md`, 
  `conteudos/indice.json`, `editorial/candidatos.json`,
  `editorial/reservas.json` e `videos/README.md`.
- Pesquisas com fontes ficam em `editorial/pesquisas/YYYY-MM-DD.json`.
  Pastas de arquivo editorial têm valor histórico, **não são fila de produção**.
- Cada vídeo real usa `canal/<id>/videos/<video-id>/video.json`. O modelo
  técnico padrão vem de `canal.json.modelo_padrao`, com sobrescrita opcional
  em `video.json.modelo`; modelos reutilizáveis em `modelos/<id>/modelo.json`.
- Geradores específicos de nicho podem viver em `geradores/<id>/` somente
  quando houver implementação e testes reais; não inferir trabalho ativo a
  partir de arquivos de configuração.
- Manter resultados e dados temporários em `output/<id>/editorial/` ou
  `output/<id>/videos/<video-id>/`, nunca versionados.
- O MVP só processa `otaku-br` e `imagem-estatica` fornecida. O modelo
  `camadas-animadas` está **planejado, não implementado**. 
- `videoforge/paths.py` deve falhar antes de gerar mídia se o canal,
  diretório, receita técnica ou destino de saída estiverem incorretos.
- Em toda mudança: organizar antes e depois, atualizar docs,
  testar regressões, verificar Actions; nunca editar outros repositórios,
  gastar IA ou publicar YouTube sem autorização explícita.
