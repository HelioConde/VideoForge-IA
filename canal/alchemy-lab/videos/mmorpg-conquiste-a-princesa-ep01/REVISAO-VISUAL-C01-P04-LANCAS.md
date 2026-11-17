# C01-P04 — Inspeção visual assistida da cena-mãe e lanças (17/11/2026)

**Estado: candidata REPROVADA para rig por erro narrativo de postura.** Este julgamento visual do assistente é inspeção preliminar, não aprovação humana do proprietário.

## Evidências
- [Prancha de inspeção com quatro painéis](QA-C01-P04-LANCAS-CONTATO.jpg).
- [SHA e metodologia dos closes](QA-C01-P04-LANCAS-CONTATO.json).
- Mãe original arquivada: `assets/geracoes/production-scene-mother-v2/44075357179/c01-p04-scene-mother.png`; SHA `156a9376298166045654706e75b876a20b7f8201c70d6d494ae9a2b7465f5ab3`; 941×1672; [execução #44075357179](https://github.com/HelioConde/VideoForge-IA/actions/runs/44075357179) sucesso.
- [QA offline #44079489181](https://github.com/HelioConde/VideoForge-IA/actions/runs/44079489181) sucesso técnico, sem edição de arte, IA paga ou rig.

## Observações visuais
1. **Erro impeditivo:** **Kael está em pé** à frente do trono, com pernas esticadas e tronco ereto. A tomada C01-P04 foi planejada como revelação do rei e dois guardas **atrás de Kael ajoelhado**. Fere a progressão C01-P03 → C01-P04 e o roteiro; câmera ou pivôs de rig não corrigem a composição original.
2. **Lanças em X alto:** aparecem cruzadas geometricamente à frente da escadaria. Não há evidência óbvia de lança flutuante no preview inteiro.
3. **Pegada dos dois guardas:** as luvas parecem envolver as hastes **mais perto da base/terço inferior** do que das pontas, como pedido. Porém o close ainda não demonstra individualmente todo polegar e dedos fechados; **não aprovar contato anatômico final** só pelo preview.
4. **Figurino do rei Aldric:** parece consistente em cor vinho e bordados dourados dentro deste enquadramento, mas comparação entre tomadas ainda é necessária. Não afirmar figurino global aprovado.
5. **Correção necessária:** pedir ao proxy **nova imagem-mãe C01-P04 V2 versionada** com Kael ajoelhado no plano inferior, guardas laterais e rei sentado; manter o X alto e as mãos próximas à base, estilo e identidades da Bíblia. Preservar V1 integral e seu SHA.

## Restrições de produção
- Nenhuma das imagens-mãe C01-P03 V1 ou C01-P04 V1 pode ser usada como fonte de rig final após inspeção visual assistida (C01-P03: escala/elenco; C01-P04: Kael em pé).
- **Não produzir as peças animáveis a partir da V1 rejeitada.** A nova V2 deverá servir de referência para **novos PNGs isolados gerados pelo proxy** (fundo, personagens, lanças, underlays), nunca recortes manuais/locais.
- Registrar `human_visual_approval=false`, `rig_ready=false`, `mp4_generated=false`, `youtube_uploaded=false`.
