# Histórico de desenvolvimento — Alchemy Lab / Conquiste a Princesa EP01

Registro cronológico de fatos verificáveis. **Não sobrescrever eventos antigos.** O ponto de retomada, que deve estar sempre atualizado na branch `main`, é [ESTADO-ATUAL.md](ESTADO-ATUAL.md).

## 14/11/2026 — plano cinematográfico, 37 planos e C12

- [Run 43653702785](https://github.com/HelioConde/VideoForge-IA/actions/runs/43653702785) — **PASSOU**: auditoria da timeline e testes de rigor de planos; nenhum MP4 criado por essa execução.
- [Run 43654314863](https://github.com/HelioConde/VideoForge-IA/actions/runs/43654314863) — **PASSOU**: validação do compositor ThreeCanvas/Remotion e malhas C12 de 5 partes, 512 triângulos; sem renderizar MP4.
- [qa-c12-rig-malha-v2.json](qa-c12-rig-malha-v2.json) — documento anterior registra uma prévia local `alchemy_c12_mesh_rig_v2_aprovacao.mp4`, 12 segundos, 360 frames e SHA-256 `e08f79924e6f09bab195e54d49c32b588c2438d28faf2e1db12d626bba018016`. **O arquivo binário original não está no repositório.** Não oferecer o hash como download.
- [PR #49](https://github.com/HelioConde/VideoForge-IA/pull/49), commit de integração `466852e88b23f7a042a0a76fc7bca78164ca049f` — **INTEGRADO À MAIN**: C12 compositor técnico P02+P03, importação de PNGs antigos por SHA e workflow de MP4 de 8 segundos.
- [Run 43658221156](https://github.com/HelioConde/VideoForge-IA/actions/runs/43658221156) — **BLOQUEADO (ASSETS_PENDING)**: zero dos nove arquivos C12 disponíveis nos caminhos esperados; o artifact contém preflight, não vídeo. Registrado em [qa-c12-render-bloqueio-2026-11-14.json](qa-c12-render-bloqueio-2026-11-14.json).
- [PR #50](https://github.com/HelioConde/VideoForge-IA/pull/50) — **ABERTO na consulta**, pipeline alternativo C12 com validação de SHA e preflight. [Run 43659001910](https://github.com/HelioConde/VideoForge-IA/actions/runs/43659001910) passou no contrato mas deixou render ignorado; não equivale a MP4. **Reconciliar** antes de incorporar, evitando duplicar pipelines incompatíveis.

## 14/11/2026 — C01 rig articulado e MP4

- [Run 43630118130](https://github.com/HelioConde/VideoForge-IA/actions/runs/43630118130) — **PASSOU** em prévia técnica C01-P03, 3 s, 1080×1920, 30fps. Defeitos de recorte/lanças visíveis e recomposição incompleta; não aprovado.
- [Run 43633018544](https://github.com/HelioConde/VideoForge-IA/actions/runs/43633018544) — **PASSOU** com correção da costura da cintura de Kael (recuperação de 84 pixels da fonte original e ancoragem). Preservar essa melhoria.
- [PR #51](https://github.com/HelioConde/VideoForge-IA/pull/51), commit `693212eeb32ede9c0dc8f1c6de94a92638b0dc60` — **INTEGRADO À MAIN**: motor C01 de direção por keyframes, pivôs hierárquicos, malhas independentes e workflow.
- [Run 43660106313](https://github.com/HelioConde/VideoForge-IA/actions/runs/43660106313) — **PASSOU** na main: gerou MP4 de prévia técnica C01-P03 e relatório QA; artifact temporário `directed-rig-alchemy-lab-mmorpg-conquiste-a-princesa-ep01-C01-P03-43660106313`, ID `14139373365`; não é o episódio oficial.
- [Run 43660106308](https://github.com/HelioConde/VideoForge-IA/actions/runs/43660106308) — **PASSOU** em TypeScript e testes Remotion.
- A implementação original de C01 continua aberta no [PR #48](https://github.com/HelioConde/VideoForge-IA/pull/48), mas **o núcleo útil já foi portado à main pelo PR #51**. Não mesclar cegamente a branch antiga.

## 14/11/2026 — checkpoint persistente (esta atualização)

- Criados `ESTADO-ATUAL.md`, `HISTORICO-DESENVOLVIMENTO.md` e manifesto legível por máquina `estado-atual.json` na pasta do vídeo; `AGENTS.md` e `README.md` devem apontar para o estado atual na branch `main`.
- **Próximo passo não resolvido:** recuperar os originais RGB, sete PNGs técnicos e executar C12 após os hashes baterem; depois continuar QA das bordas C01. Não habilitar geração de imagem ou upload do YouTube.

## Como acrescentar progresso

Acrescentar uma seção datada com: objetivo e cena, arquivos alterados, commit realmente presente na `main`, run/workflow com resultado, mídia/artifact e SHA se houver, problemas abertos e próxima ação. Se ainda for apenas PR/branch, identificar explicitamente como **NÃO INTEGRADO**. Atualizar [ESTADO-ATUAL.md](ESTADO-ATUAL.md) **no mesmo lote de mudanças**; usar `estado-atual.json` para leitura programática. Nenhum agente deve depender do histórico de chats para reconstruir o projeto.
