# EP01 V2 — comparação semântica por região

O comparador foi instalado. Ele reprova diferenças cromáticas fortes somente após validação de dois PNGs SHA, pose/variante e polígonos da MESMA parte do corpo.

| Personagem | Região | Resultado |
|---|---|---|
| aldric | barba | EVIDENCIA_INSUFICIENTE |
| aldric | tecido_externo | EVIDENCIA_INSUFICIENTE |
| aldric | painel_central | EVIDENCIA_INSUFICIENTE |
| elara | corpete_roxo_palacio | EVIDENCIA_INSUFICIENTE |

Sem verificação semântica da barba, exterior/centro e do corpete, o resultado é evidência insuficiente; NÃO aprovado.
Uma diferença numérica pequena ainda não comprova que a roupa, o rosto ou a barba estão corretos.
O filtro de cores usa limiar inicial de 40 pontos percentuais de diferença por grupo e deve ser calibrado com exemplos rotulados.
A reprovação prévia do rei e da princesa permanece ativa.
Ver [pranchas de anotação](REVISAR-ROI-FIGURINOS-V2.md) e [contrato em JSON](CONTRATO-ROI-SEMANTICAS-V2.json).
