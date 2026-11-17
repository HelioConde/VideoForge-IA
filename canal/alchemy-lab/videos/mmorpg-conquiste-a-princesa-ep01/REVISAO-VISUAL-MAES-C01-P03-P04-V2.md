# Revisão visual assistida — cenas-mãe corrigidas C01-P03 e C01-P04 (17/11/2026)

**Estado: melhoradas, candidatas em revisão, SEM APROVAÇÃO HUMANA, SEM RIG.**

## Referências reais verificadas
- [Prancha de quatro painéis V1/V2 das duas tomadas](QA-MAES-C01-P03-P04-V2.jpg), gerada sem nova IA no [QA #44080972625](https://github.com/HelioConde/VideoForge-IA/actions/runs/44080972625).
- [Metadados SHA e alterações](QA-MAES-C01-P03-P04-V2.json).
- [Cena-mãe V2 C01-P03](assets/geracoes/production-scene-mother-repair-v2/44080234599/c01-p03-scene-mother-v2.png), SHA `bfc1249dc1f83b004b620c333f5aa81689b0ba0c23a3e7573d57c09dcf3539e3`, 941×1672, run #44080234599 sucesso.
- [Cena-mãe V2 C01-P04 original do proxy](assets/geracoes/production-scene-mother-repair-v2/44080462345/c01-p04-scene-mother-v2.png), SHA `cf19543377960b2100148846f9d77852ca94510c949c62c27b9390e4fbee0f84`, 941×1671, original preservado, geração concluída mas QA de canvas rejeitou.
- [C01-P04 V2 alinhada sem IA](assets/geracoes/production-scene-mother-v2-aligned/44080887693/c01-p04-scene-mother-v2-native-aligned-v1.png), SHA `2d11099a536999409a33dae2fc30c517e260c4ad640e41c6942c85b9db499ec5`, 941×1672, 1 linha inferior repetida, todos os pixels originais intocados; QA #44080887693 sucesso.

## Observações por tomada

### C01-P03
- A V2 **retirou ambos os guardas, as lanças cruzadas e a espada enorme no primeiro plano**, preservando escada, trono, vitrais e luz do salão.
- Kael permanece **ajoelhado diante do rei**, visto por trás. Aldric aparece no centro ao fundo, de pé diante do trono; isso corresponde à intenção de Kael submetido ao julgamento.
- O resultado é uma **melhora visual real**, mas ainda precisa de inspeção de detalhes no traje, textura, rosto do rei e comparação com as referências SHA da Bíblia.
- **Os PNGs separados de Kael/Aldric/background produzidos da MÃE V1 e reprovados por escala NÃO servem nesta V2.** Depois da seleção da mãe aprovada, gerar novas imagens separadas com o proxy e coordenadas restritas; não transportar sprites V1 para a V2.

### C01-P04
- A V1 mostrava **Kael em pé**, erro impeditivo de continuidade. Na V2, Kael está visivelmente **ajoelhado no chão** com mão junto ao piso e perna flexionada.
- Rei Aldric permanece sentado, e dois guardas laterais sustentam as lanças fazendo X elevado diante das escadas.
- As pegadas parecem estar na **metade inferior/parte próxima da base**, mas não é possível atestar com esta prancha a quantidade/contato anatômico de todos os dedos nos extremos de animação. Revisar close em resolução nativa antes de rig.
- A altura da V2 original saiu 941×1671. Foi criada cópia **alinhada** em 941×1672 adicionando apenas uma linha inferior, sem mudar escala/postura/ânngulo; não equivale a aprovação artística.

## Conclusão e gates
- As duas V2 **parecem corrigir os erros narrativos principais observados nas V1**; a aprovação definitiva do proprietário **não foi registrada**.
- Próxima etapa depois de aprovação: proxy deve gerar **NOVAS imagens independentes** de background, Kael, Aldric, cada guarda/lança e partes de rig quando animadas, com referência à mãe V2 e Bíblia. **Não recortar/local segmentar** os pixels da mãe para criar partes animáveis.
- Manter `human_visual_approval=false`, `rig_ready=false`, `mp4_generated=false`, `youtube_uploaded=false`. Conservar todos os PNGs originais/hashes/relatórios rejeitados, para auditoria.

**Não mudar o produtor das 39 tomadas silenciosamente para utilizar uma V2 sem gate humano.**
