---
name: videoforge-audio-editing
description: Coordenar narração, vozes, música autorizada, efeitos, sincronização, legendas e montagem do VideoForge-IA com Remotion sem inventar arquivos ou aprovar publicação.
---

# Áudio e montagem — timeline, voz, SFX e finalização

## Planejamento
Ler roteiro, `AGENTS.md`, checkpoints, timecodes em frames, planilha de tomada, autoria/licenças de mídia e QA. A edição deve preservar `shot_id`, duração em frames, FPS real e versionamento de fonte. No EP01 Alchemy Lab são **4890 frames a 30 fps (163 s)**, com **C01-P01 em preto por 60 frames (2 s)**. Referências: `videoforge/remake_episode_audio.py`, `motion-remotion/src/cinematic-timeline.ts`, `motion-remotion/src/cinematic-episode.tsx`.

## Responsabilidades
1. Registrar `voice_track`, narrador/personagem, idioma e texto, evento de SFX, fonte de música e sua licença, timestamps de início/fim (frames absolutos) e SHA-256 do arquivo real. Não reutilizar conteúdo protegido sem direitos/licença.
2. Estabelecer ordem de mixagem por trecho: diálogo inteligível acima do fundo, SFX de ação coerente com contato visual, ambiência e música sustentando ritmo; fade/ducking e transições sem cortes abruptos. Especificar ganho/picos e registrar testes de clipping, silêncio involuntário e canais.
3. Escolher mudança de tomada de acordo com fala, reação, olhar, pausa dramática e ação; indicar legendas sincronizadas como camada Remotion, **nunca impressas pelo proxy na arte-mãe**.
4. Validar duração total pelo roteiro, taxa de quadros, alinhamento de início/fim por tomada e manter consistência até o último frame. WAV/MP3 reais precisam de proveniência/licença; evento anotado em JSON ou fixture sintético **não é mídia final**.
5. Para C01-P01 usar somente o efeito original validado por `python -m videoforge.remake_episode_audio --verify-only` quando aplicável; não criar silêncio fingindo que é espada ou chamar este efeito de trilha completa do episódio.
6. A montagem deve usar composição Remotion determinística; `<Audio>` e `<Sequence>` respeitam a timeline. FFmpeg/FFprobe são permitidos para sondagem, QA e multiplexação, não para simular atuação ou rig de PNG plano.
7. Se não há áudios de voz, música licenciada ou imagens finais, entregar **EDL/roteiro de som e QA pendentes**, não MP4 oficial. A publicação depende do mesmo gate visual do vídeo.

## Entrega
Manifesto por `shot_id` com `start_frame`, `end_exclusive`, `audio_assets`, licença, SHA, sincronização, `audio_qa` e `human_approval=false` até revisão real. Anotar retrabalho, ausências e próximos passos nos arquivos principais do canal. Ver [direção](../videoforge-shot-direction/SKILL.md) para focos/cortes e [QA](../videoforge-qa-and-checkpoint/SKILL.md) para evidência de áudio e MP4.
