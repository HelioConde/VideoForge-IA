# Capa ao vento — malha SVG / Remotion (Otaku Multicena)

## O que mudou

O movimento anterior usava uma senoide fraca, praticamente uniforme. Agora o modo **opt-in** `cape_mesh.wind` cria movimento de tecido com ondas propagadas, rajadas de intensidade variável e atraso crescente na ponta. São equações determinísticas de deformação, não uma simulação física de colisão.

- A linha superior da malha (fixação ao ombro) não se move, evitando que a capa se solte do corpo.
- A deformação cresce do ombro à ponta por uma potência da distância vertical.
- O meio reage antes da ponta; um atraso de até `tipLagSeconds` dá impressão de inércia.
- A componente horizontal acompanha vento predominante, com ondulações suaves e três rajadas assimétricas ao longo da duração da cena.
- A componente vertical produz um pouco de levantamento, principalmente nas rajadas.
- A capa frontal usa somente 64% da força e um pequeno atraso adicional, para não abrir o peito artificialmente.
- Clipes SVG de triângulos mantêm a sobreposição para evitar frestas entre faces. **Não há colisão real com corpo, braço ou telhado**; essas partes exigem revisão visual.
- Na ausência de `wind`, o cálculo é **idêntico ao modo antigo**, inclusive os parâmetros.

## Parâmetros candidatos da cena

Arquivo canônico: `canal/otaku-br/videos/teste-proxy-20261113/rig-plan.json` (não alterado para outros canais).

```json
{
  "cape_mesh": {
    "amplitude_px": 10.5,
    "wind": {
      "direction": -1,
      "baseStrength": 0.85,
      "gustStrength": 1.15,
      "flutterStrength": 0.65,
      "tipLagSeconds": 0.34,
      "liftStrength": 0.62
    }
  }
}
```

O vento da direita para a esquerda (`direction = -1`) foi escolhido pela orientação da capa já desenhada atrás do aventureiro. A configuração não é universal: outros personagens, câmeras e cortes devem ter seus próprios bounds e perfil. `amplitude_px` está em coordenadas da imagem 1024×1536, não pixels do player.

O validador Python rejeita direção diferente de -1/+1, campos ausentes/desconhecidos, NaN, amplitudes absurdas e valores fora de limites. O renderer TypeScript calcula tudo usando `frame/fps`, sem timers, `Math.random`, dependências npm extras ou WebGL obrigatório. As condições de segurança e de aprovação do rig permanecem como eram.

## Como assistir ao teste real (sem gastar IA)

O workflow `rig-wind-preview.yml` reutiliza a cena original do run **43437992955** e os **olhos fechados gerados por IA já existentes** do run **43512529516**. O PR aciona o fluxo de teste automaticamente. O workflow:

1. Confere hashes de origem, identidade do canal e estado de rascunho dos PNGs.
2. Lê o perfil de vento do `rig-plan.json` do mesmo canal, verifica SHA da cena e mantém o antigo `rig.json` intacto.
3. Gera quadros com vento (0, 55, 95, 145, 190, 225, 239) e os correspondentes sem vento (95, 190).
4. Compara visualmente mudanças de pixels na região da capa; o teste só passa se houver alteração perceptível e calculada.
5. Renderiza MP4 H.264 de 8 s com marca d'água **RASCUNHO** e uma versão leve H.264 baseline 540×960 com `faststart`.
6. Confere codecs, movimento, `cape_wind_active=true`, `eye_closed_from_original_ai_edit=true`, `publishable=false` e `youtube_uploaded=false`.

Os arquivos binários são publicados exclusivamente como artifacts temporários de revisão do GitHub Actions, sem commitar MP4 na `main` nem publicar vídeos em plataformas.

## Critérios para revisão manual

Compare os frames com e sem vento: a linha do ombro deve permanecer fixada, a ponta deve reagir depois e com amplitude superior, a silhueta não pode aparecer recortada ou multiplicada e a capa dianteira não pode atravessar o peito. O movimento deve ter variações de rajadas, sem balanço metronômico ou estalos no primeiro/último frame. Revise também o piscar dos olhos, que **não foi refeito**.

Os testes automatizados comprovam geometria, limites de amplitude, ausência de inversão de triângulos e diferença entre quadros; não comprovam naturalidade ou colisões. **A obra inteira segue como rascunho** enquanto ombros/costas ocultos e oclusões ainda precisarem de correção.

Código: [mesh-rig.tsx](../motion-remotion/src/mesh-rig.tsx); testes: [mesh-rig.test.cjs](../motion-remotion/tests/mesh-rig.test.cjs); perfil: [rig-plan.json](../canal/otaku-br/videos/teste-proxy-20261113/rig-plan.json).
