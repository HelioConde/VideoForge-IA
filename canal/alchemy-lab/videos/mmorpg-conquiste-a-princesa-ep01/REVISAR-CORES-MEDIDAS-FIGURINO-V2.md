# EP01 V2 — cores medidas em pixels RGBA (QA offline)

Aldric continua REPROVADO por inversão de cores e barba; Elara real continua REPROVADA pelo painel roxo, conforme relato do proprietário.

As porcentagens abaixo medem apenas pixels **visíveis em camadas RGBA**. O algoritmo NÃO sabe quais pixels são especificamente da barba, do centro da roupa ou do corpete.

| Personagem | Fonte | Tipo de medição | Vermelho | Muito escuro | Roxo ou magenta |
|---|---|---|---:|---:|---:|
| aldric | roupa_mista | unlabeled_rgba_layer_measured | 24.24% | 45.84% | 0.02% |
| aldric | cabeca_coroa_cabelo_mistos | unlabeled_rgba_layer_measured | 22.81% | 25.08% | 0.21% |
| aldric | manto_esquerdo | unlabeled_rgba_layer_measured | 2.76% | 74.89% | 0.04% |
| aldric | manto_direito | unlabeled_rgba_layer_measured | 6.1% | 65.14% | 0.07% |
| elara | close_rgb_sem_mascara | no_trusted_subject_mask | não atribuível | não atribuível | não atribuível |
| elara | c12_rgb_multiplos_personagens | no_trusted_subject_mask | não atribuível | não atribuível | não atribuível |

## O que estes valores NÃO demonstram

- A máscara da roupa é um recorte V1 misto, não uma máscara separada de EXTERIOR versus CENTRO e nem um par sentado versus em pé.
- A máscara da cabeça inclui cabelo, rosto e coroa: não oferece uma medida EXCLUSIVA da barba.
- As fontes de Elara são RGB e incluem fundo/pessoas; sem máscara do corpete, contar roxo seria enganoso.
- A imagem reprovada permanece reprovada, com ou sem percentuais. SHA e histogramas não são prova de fidelidade visual.

## Para habilitar reprovação por pixels

- [ ] Máscaras individuais de barba, roupa exterior e centro do rei em ambas as poses
- [ ] Máscaras de peitoral do traje real de Elara nas duas imagens
- [ ] Mesma variante, registro de cada SHA e verificação das áreas semânticas

Fonte: [filtro e reprovações registrados](RELATORIO-APROVACAO-REPROVACAO-FIGURINO.md).
Nenhuma imagem paga ou vídeo novo foi gerado nesta auditoria.
