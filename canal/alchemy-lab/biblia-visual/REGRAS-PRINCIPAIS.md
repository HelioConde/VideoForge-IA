# Regras P0 da Bíblia Visual

1. Primeiro cadastrar personagem, variações (antes/depois, ferido, capuz, roupa), cenário, objeto e interação; depois gerar a cena.
2. Gerador usa referências **PNG originais anexadas com SHA** e aprovadas para aquele uso. Uma cena bonita não é aprovação de pose.
3. Estados obrigatórios: planejado, gerado, em_revisao, aprovado, rejeitado, substituido. Aprovar exige evidência e revisor humanos; hashes não aprovam.
4. **Toda imagem gerada e arquivada recebe registro obrigatório:** canal, vídeo, ID, cena/plano, asset, arquivo, SHA256, dimensão, bytes, run, fontes anexadas, estado. PNG e registro JSON/MD entram no mesmo commit. Sem registro, falha.
5. Nunca sobrescrever versões nem repetir geração já arquivada; revisar novo Vn preservando o histórico.
6. **Física:** objeto ligado ao braço→punho→mão→BASE. Guardas seguram suas lanças NA BASE com direção correta, sem hastes ou mãos flutuantes.
7. Cenários possuem fundos limpos e geometria consistente. Identidade e figurino variam só com versão registrada.
8. Imagens de rig exigem camadas RGBA, underlays e malha real; movimento de PNG único não conta como animação articulada.
9. QA concentrado nos novos mestres e erros; reutilizar referências aprovadas sem reabrir toda a análise a cada vídeo.
10. Respeitar bloqueio do EP01 enquanto a pega das lanças não estiver aprovada. Não declarar MP4 ou YouTube a partir de imagem isolada.
