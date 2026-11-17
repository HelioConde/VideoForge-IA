# Revisão visual assistida — C03-P01 → C03-P02 → C04-P01 → C04-P02 (17/11/2026)

**Status: melhora de continuidade espacial do quarto, mas ainda SEM APROVAÇÃO para animação.** Avaliação preliminar do assistente, não aceite humano.

## Evidências

- [Prancha real de quatro quadros](QA-C03-C04-CONTINUIDADE-QUARTO.jpg); [proveniência e SHAs](QA-C03-C04-CONTINUIDADE-QUARTO.json).
- [QA offline #44086630803](https://github.com/HelioConde/VideoForge-IA/actions/runs/44086630803) **success**, zero chamadas de geração, zero recortes como sprites.
- C03-P01 `b0c416e3c0dd10883e2de37a5c2652ee02030d1f6925ec6f47d9a6d56ade09f3` — reflexo azul no olho, quadro original.
- C03-P02 `116fab14bb7d910a73f5fc61e12dac92efc73d3988f0648ee4b336c9fb241c3c` — quarto gamer e luz azul, gerado com Kael casual V2 e referências corretas.
- C04-P01 `d4c51415314823c5e7092aa4e45bbc9f8fce9092352e4a18560e118f40488d1a` — Kael no computador.
- C04-P02 `9755e8457dac710abafdddca3da17cd5102d03385cc686711981e236015716bf` — monitor separado como assunto principal da imagem-mãe.

## Análise visual preliminar

1. **C03-P01 → C03-P02:** a cor azul do reflexo ocular cria ponte visual plausível para a luz da tela. As cenas foram geradas em quadros distintos, sem split-screen. O plano C03-P01 continua enquadrando quase todo o rosto e não apenas a íris; requer close mais fechado se o proprietário quiser um macro real.
2. **C03-P02 / ambiente moderno:** a geração corresponde a quarto moderno com Kael em jaqueta escura, monitor azul, luminária e janela de pôr do sol. Não foi observada armadura, trono ou lança medieval nesta prancha. O prompt e as fontes medievais incorretas foram substituídos ANTES de gerar a tomada.
3. **C04-P01 / mudança de postura:** Kael está **sentado** com mão direita junto ao mouse e mão esquerda no teclado, enquanto em C03-P02 aparece **em pé** ao lado da mesa. Isso pode ser um corte de tempo, mas sem plano intermediário há salto de postura. Precisa de decisão editorial, não corrigir com rig deformando o corpo.
4. **Possível descontinuidade de ferimentos:** o Kael casual de C04-P01 parece ter marcas no rosto mais evidentes do que o Kael casual em C03-P02. Como a cena do quarto pode representar o Kael ANTES da história de fantasia, conferir se qualquer ferimento deveria existir neste momento.
5. **C04-P02 / monitor:** a tela está limpa/azul, apropriada para colocar a interface de conexão interrompida no Remotion. Luminária, mesa, tons azul e âmbar e janela mantêm identidade semelhante. Verificar modelo exato de moldura/base nos PNGs antes de gerar objetos isolados.
6. **Contato de mão e teclado/mouse:** o painel reduzido sugere mãos e objetos presentes, mas não verifica anatomia dos cinco dedos/encaixe ao mouse no nível de detalhe necessário para rig.

## Próximas ações e travas

- Preservar todas as mães e suas referências SHA; **não reusar partes animáveis de outra tomada**.
- Confirmar intenção temporal entre Kael em pé (C03-P02) e sentado (C04-P01). Se não houver passagem de tempo, pedir variante de cena-mãe corrigida pelo proxy, versionada.
- Validar continuidade de marcas faciais e figurino de Kael casual com a Bíblia; considerar correção de C04-P01 antes de gerar peças.
- Quando houver mãe escolhida/validada, pedir ao proxy **novas imagens independentes** do background, Kael, monitor e mãos, jamais recortes locais. QA de recomposição, depois rig e câmera.
- Nenhuma aprovação humana registrada: `human_visual_approval=false`, `rig_ready=false`, `mp4_generated=false`, `youtube_uploaded=false`.
