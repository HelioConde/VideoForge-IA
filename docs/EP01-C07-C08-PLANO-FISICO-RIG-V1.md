# EP01 — C07/C08 — plano físico do carrinho e correção de eixo (proposta V1)

**Status:** `proposal_only_not_rig_approved` · **Sem render de animação, sem inferência, sem geração de imagem e sem publicação.**

Esta proposta complementa a [auditoria visual e documental](EP01-C07-C08-CONTINUIDADE-AUDITORIA-ASTRA.md) e preserva o manifesto original `CONTINUIDADE-C07-C08-V2.json`.

**Contrato executável:** [`PROPOSTA-MOVIMENTO-C07-C08-V1.json`](../canal/alchemy-lab/videos/mmorpg-conquiste-a-princesa-ep01/PROPOSTA-MOVIMENTO-C07-C08-V1.json).

**Verificador:** `python -m videoforge.ep01_continuity_motion --output output/c07-c08-rig-readiness.json`. CI [#44393373939](https://github.com/HelioConde/VideoForge-IA/actions/runs/44393373939) passou em **9 testes Python** e **TypeScript Remotion**, com source SHA-256 real validado e relatório `ep01-c07-c08-rig-readiness-44393373939`.

## 1. C07-P03: encontro de Elara e Kael

**Frames 2250–2339 (1:15 a 1:18).** Elara deve entrar da esquerda e chegar a Kael na direita junto ao carrinho estacionado; o diálogo só começa na tomada seguinte, **C07-P04**.

O QA visual da prévia C07-P03 mostrou leitura de movimento no sentido contrário. **Pan, zoom, espelhamento e deslocamento do PNG completo não corrigem a orientação corporal**, e podem quebrar a identidade do cenário. A tomada precisa de revisão de blocking pelo Agente 03, seguida de avaliação do Agente 04 e do Supervisor 12 sobre usar uma fonte realmente adequada. Não refazer automaticamente imagens aprovadas.

## 2. C08-P02: empurrão e giro físico do carrinho

**Frames 2550–2679 (1:25 a 1:29,33).** O plano não requer poses independentes para cada quadro. Usa uma **única mãe aprovada, recortes animáveis, ossos/malha e keyframes**. Não separar mãos independentes: o conjunto braço/pegada de Kael deve preservar o contato anatômico com a alça.

| Frame relativo | Frame EP01 | Fase | Ângulo mundial proposto |
|---:|---:|---|---:|
| 0 | 2550 | Contato inicial e preparo | 0° |
| 18 | 2568 | Transferência de peso | 0° |
| 43 | 2593 | Carrinho sai da parede | 7° |
| 67 | 2617 | Giro em curso | 34° |
| 93 | 2643 | Giro avançado | 68° |
| 115 | 2665 | Carrinho se estabiliza | 90° |
| 129 | 2679 | Barricada concluída | 90° |

Estes são **alvos em coordenadas de mundo, ainda não calibrados para a perspectiva da imagem**. Não aplicar yaw diretamente sobre uma textura inteira: o giro de 90° requer representação articulada coerente, reconstrução de áreas ocultas e verificação de profundidade.

Regras não negociáveis:

- **Somente Kael** empurra. Nenhum soldado, perseguidor ou princesa participa da ação.
- Mãos e alças permanecem conectadas; rodas permanecem no chão e giram de acordo com o deslocamento.
- Chassi rígido, sem distorção elástica nem teletransporte.
- O carrinho mantém a mesma identidade e acabamento da Bíblia Visual.
- Não simular o giro usando zoom de câmera, corte disfarçado ou movimento de uma imagem inteira.

## 3. C08-P03: carrinho vira barricada

**Frames 2680–2789 (1:29,33 a 1:33).** A tomada começa com o **mesmo carrinho perpendicular, sem salto de posição ou mudança de identidade**. Kael está no lado seguro direito; os dois mascarados ficam presos do lado esquerdo e nunca tocam ou ajudam a mover a carroça. Elara já saiu do quadro.

A conexão entre C08-P02 e C08-P03 deve ser verificada em frames consecutivos, **2679 → 2680**. Um PNG do carrinho pronto atrás do corte não prova o movimento anterior.

## 4. Camadas obrigatórias antes de animar

O Agente 06 deve entregar camadas verdadeiras com transparência e recomposição validada; o Agente 07 só poderá rigar depois de sua aprovação:

1. `alley_reconstructed_rgba` — beco sem buracos após retirar objetos móveis.
2. `kael_connected_body_rgba` — corpo e figurino contínuos.
3. `cart_chassis_rgba` — chassi rígido separado.
4. `wheel_left_rgba` e `wheel_right_rgba` — rodas animáveis com pivôs.
5. `kael_grip_integrated_rgba` — conjunto de contato integrado; **sem mãos isoladas**.
6. `cart_front_occlusion_rgba` — oclusão frontal correta, para preservar profundidade.

O manifesto de camadas futuro está previsto em `assets/rig/c07-c08-cart-v1/layers-manifest.json`. **Esse arquivo ainda não existe e não deve ser simulado para desbloquear o QA.**

A [Bíblia Visual do carrinho](../canal/alchemy-lab/biblia-visual/objetos/carrinho/status.json) registra `aprovacao_mestra: false`. O sistema também exige aprovação explícita dessa referência antes de permitir a montagem de produção.

## 5. Integrado ao renderizador de prévia

O gerador `videoforge/ep01_continuity_v2.py` agora acrescenta `continuity_gate` a C07-P03, C08-P02 e C08-P03. O Remotion exibe **avisos de QA pendente na prévia técnica**, sem disfarçar defeitos como movimentos concluídos.

O `fingerprint` do `ep01_camera_batch.py` inclui este plano JSON e o verificador Python, forçando invalidação do cache quando o contrato mudar.

**Esses avisos não corrigem as imagens e não representam rig funcional.** Se houver um novo MP4 câmera-only, ele continuará explicitamente identificado como prévia.

## 6. Responsáveis pela próxima entrega

| Agente | Próxima tarefa verificável |
|---|---|
| 03 — Diretor de Cenas | Fixar orientação de Elara no encontro C07-P03 |
| 04 — Diretor de Arte | Conferir e submeter referência mestra do carrinho à aprovação |
| 06 — Camadas | Extrair RGBA sem cortar corpo, mão, cabelo ou carrinho; reconstruir beco |
| 07 — Rig 2D | Criar pivôs, chassi, rodas e contato; testar juntas e pesos |
| 08 — Animador | Aplicar keyframes com antecipação, giro e estabilização |
| 09 — Câmera | Manter enquadramento e eixo; não esconder defeitos |
| 12 — QA | Revisar contato, piso, fundo, continuidade 2679→2680 e transições em todos os frames |

**Próximo marco técnico:** camadas e máscaras aprovadas. Somente depois produzir um primeiro MP4 animado de C08-P02→C08-P03 para revisão independente. O vídeo completo EP01, áudio e YouTube permanecem bloqueados até aprovação humana.
