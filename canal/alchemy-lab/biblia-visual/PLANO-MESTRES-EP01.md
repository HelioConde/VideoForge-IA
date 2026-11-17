# Plano operacional de imagens-mestre — Conquiste a Princesa EP01

## Objetivo

Gerar referências **reutilizáveis** de personagens, cenários, objetos e interações físicas antes das 40 tomadas. Nenhuma arte é canônica só porque o workflow terminou ou foi registrada. Aplicar `INDEX-BIBLIA.json`, `REVISOES-MANUAIS.json`, `REGISTRO-GERACOES.json` e `FILA-EP01.json` como fontes verificáveis.

## Ordem de trabalho e dependências

| Ordem | Mestres a preparar | Critério para avançar |
|---|---|---|
| 1 | **Salão do trono vazio** (`sala-do-trono`) | Trono, escadaria, vitrais e perspectiva reproduzidos sem corpos, braços, sombras humanas, lanças ou roupas. Ref. C01-P04 V3 permitida **só** para estilo/arquitetura/luz. Pedido GitHub `biblia-sala-do-trono-vazio-v1`. |
| 2 | **Kael**: medieval (frente, costas, perfil), casual/antes, ferido, depois | Mesma identidade facial, volume de cabelo, olhos, cores de capa, ombreira, acessórios; variantes separadas e explicitamente catalogadas. Referência facial original SHA `edb751cd…`. |
| 3 | **Aldric**: em pé e sentado, mesmo figurino | Mesma barba, coroa e proporção; **sem inversão** entre preto/vermelho do manto/túnica. Não promover candidatos reprovados de figurino. |
| 4 | **Elara**: identidade-base, capuz/disfarce, vestido real/revelação, antes/depois | Mesmo rosto/tranças/olhos violeta. Capuz C07–C10; traje real C12+. Referência facial original SHA `bf199f3e…`. Não permitir corpete roxo divergente. |
| 5 | **Guarda esquerdo e direito**, cada qual com vista neutra sem lança, frente/perfil/costas | Armadura, pluma vinho, luvas, tamanho e escudo de cada guarda estáveis. Não utilizar V3 ou V4 como **pose** de referência. |
| 6 | **Lança real** como objeto e **luva/punho** como componentes, preferencialmente RGBA independentes | Uma haste por guarda, ponta, base e direção reconhecíveis; proporções, material, comprimento e pivôs registrados. |
| 7 | **Interação guarda + lança na BASE** para cada lado; **cruzamento de duas lanças** | Em cada mão, a luva fecha sobre o **terço inferior da haste, próximo à extremidade da base**. Seguir base→ponto de pega→haste→ponta. Mão, punho, antebraço, cotovelo e ombro conectados. Duas lanças, dois guardas, sem inversão de donos ou armas flutuantes. Aprovação **humana visual** obrigatória. |
| 8 | **Outros fundos** (quarto de Kael, estrada, mercado, beco, portão real, castelo), objetos (espada, coroa, capa, trono etc.) e coadjuvantes previstos | Um mestre para cada item usado na fila, de acordo com a dependência real da tomada. Cenário limpo, objetos e personagens em camadas separáveis. |
| 9 | **Composição da C01-P04** com mestres canônicos | Reproduzir posicionamento e atuação corretos; validar identidade, anatomia, contato e continuidade antes de marcar interação como aprovada. |
| 10 | **40 tomadas** e rigs Remotion/Three.js | Gate obrigatório: **todos** os personagens, cenários, objetos e interações dependentes da tomada aprovados por humano com SHA válido. Até lá, 37 imagens futuras continuam pausadas e nenhum MP4/YouTube é liberado. |

## Como gerar um novo mestre

1. Cadastrar `categoria/id/variantes` no índice **antes** do pedido; manter a ficha e o estado individuais no diretório da categoria.
2. Especificar o uso **permitido** de cada PNG-fonte, seu caminho e SHA; anexar bytes reais no endpoint de edição. Fonte com pose rejeitada não se torna referência de pose nem por recorte.
3. Criar ID exclusivo `biblia-<item>-<variante>-vN` em `production-art.json` e submeter **uma** solicitação rastreável em `pedido-geracao-arte.json` (1 chamada por execução).
4. Executar pelo GitHub Actions e arquivar o PNG original imutável, metadata, SHA, dimensões, fontes anexadas, run, ID e status no mesmo commit de `REGISTRO-GERACOES.json`/`.md`.
5. Exibir a candidata para comparação e registrar decisão humana explícita em `REVISOES-MANUAIS.json`. **Aprovado** requer revisor, evidência, escopo e identificação do PNG. Rejeitado permanece arquivado, sem servir de fonte canônica para a parte rejeitada.
6. Somente depois promover o `imagem_canonica` com SHA e `status.json` aprovado para um item; testá-lo via `videoforge.visual_bible_gate`. Aprovações são **específicas** por variante/identidade/pose, não transbordam automaticamente.
7. Se surgir um personagem, cenário, objeto ou interação nova durante o storyboard, incluí-lo na Bíblia e revalidar as dependências da tomada antes de gerar.

## Regras absolutas

- Não gerar uma sequência inteira de imagens e tentar corrigir a consistência depois: **mestres primeiro, tomadas depois**.
- A aprovação estética de C01-P04 V3 **não** aprova sua pegada; C01-P04 V4 está **rejeitada** pela direção e grip na base. Preservar as duas versões apenas para histórico e escopos permitidos.
- Para guardas, a pegada na **parte da base**, a direção da haste, a identidade do dono da arma e a anatomia têm prioridade sobre uma composição visual bonita.
- O rei deve manter a mesma barba e padrão do traje entre sentado e em pé; Elara deve manter a mesma identidade em todas as variantes.
- A rainha está cadastrada como personagem **futuro**, fora das 40 tomadas atuais; **não gerar ou inventar sua aparência** sem necessidade narrativa e referência.
- Não há limite editorial total de imagens, mas **cada execução** deve respeitar orçamento, rastreabilidade e política de custo; não repetir uma imagem já arquivada sem criar uma revisão Vn justificada.
- Sucesso em Actions significa no máximo sucesso técnico. Sem revisão explícita, não liberar imagem canônica, rig final, vídeo oficial ou publicação.

## Checkpoint 16/11/2026

- Bíblia já contém 39 fichas e fila de 40 tomadas; 6 PNGs históricos verificados.
- Primeiro master solicitado via commit `487071ba30737f559f26c70c1a18f24f29a5423d` ao workflow `production-art-by-request.yml`.
- Próximo marco: conferir PNG real do salão vazio, sua entrada atômica no registro e seu QA; em seguida preparar mestres individuais de personagens, sem reutilizar pega rejeitada.
