# Contatos, pivôs e deformação

Consultar ao corrigir deslizamento mão/espada, pivô deslocado, juntas abertas ou tecido/cabelo deformando artificialmente. Orientações próprias de 17/11/2026; não alteram contratos ou aprovações do projeto.

Aplicar rig da tomada somente a peças geradas independentemente pelo proxy e aprovadas conforme o contrato vigente. Máscaras e recortes históricos não são peças animáveis. Na ausência da arte habilitada, restringir a implementação a mecânica/fixtures identificadas como teste.

## Contatos

Identifique pontos locais de contato da mão e do objeto, parentagem, crop/offset e intervalo de contato. Transforme ambos para o mesmo espaço após aplicar toda a hierarquia. Meça a distância final em cada frame do intervalo; escolha tolerância adequada à resolução e à ação, com justificativa. Percentuais iguais de progresso não provam contato.

Defina uma autoridade para o movimento do objeto durante o contato: por exemplo, filho da mão com offset de empunhadura, ou alvo do qual a mão deriva sua pose. Não somar deslocamento independente e herdado sem intenção. Na soltura, registre frame de detach e preserve continuidade espacial. Verifique contato após rotação do pulso, não somente translação.

Em `remake-sword-motion.ts`, `handFollow` controla proporção do deslocamento; valores diferentes de um merecem teste de contato nas transformações finais. Não corrija o parâmetro isoladamente sem conferir o contrato da ação. A bainha pode continuar fixa enquanto a lâmina sai.

## Deformação

Use pivô rígido para uma parte rígida e malha quando sua silhueta precisa deformar. Reutilize `meshGridAtFrame` e a geometria existente. Prenda raízes de cabelo e costuras, permitindo resposta maior nas pontas. Teste limites de ângulo e amplitude nos extremos previstos.

Se usar skinning, pesos devem ser válidos e normalizados; se usar deformação paramétrica, não acrescente um skeleton só para satisfazer uma checklist. Verifique vértices presos, área e orientação dos triângulos, colapsos, costuras e preservação da silhueta. Compare com a geometria neutra usando tolerância numérica apropriada.

Verifique espaços embaixo das partes nos extremos. Sem textura revelada suficiente, limite o movimento do teste e registre a lacuna; não atribua a transparência a problema do renderer sem evidência.

## Determinismo e validação

Pose deve depender do frame absoluto e das entradas fixadas. Compare avaliação crescente, decrescente e acesso direto ao mesmo frame. Se usar clips/mixer, derive o tempo de frame/FPS e confira que ações, blends e resets não dependem de frames anteriores.

Testes mecânicos usam fixtures; validação da arte exige peças reais e revisão da prévia. Use [QA temporal](../../videoforge-qa-and-checkpoint/references/temporal-qa.md) para selecionar evidências. Referência de integração: [ThreeCanvas](https://www.remotion.dev/docs/three-canvas).
