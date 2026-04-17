# ❓ FAQ & Troubleshooting — Safra de Café

---

## 📋 Perguntas Frequentes

### **Planejamento & Orçamento**

**P: Por que devo fazer orçamento?**
R: Para saber quanto vai gastar e comparar depois com o real. Se orçou R$10.000 e gastou R$12.000, você vê que ultrapassou 20%. Ajuda a tomar decisões melhores na próxima safra.

**P: Posso mudar o orçamento depois?**
R: Sim! Clica no ✏️ para editar qualquer item. O sistema mostra "Orçado" vs "Realizado" automaticamente.

**P: E se não souber quanto vai gastar?**
R: Use valores aproximados (pesquise preços no mercado). Depois atualiza conforme gasta de verdade.

---

### **Colheita (Romaneios)**

**P: O que é "Romaneio"?**
R: Documento que registra cada lote colhido. Data, peso, umidade, etc. Essencial para rastreabilidade.

**P: Quanto devo colher por dia?**
R: Depende do seu equipamento. Registra o que colheu cada dia mesmo que seja pouco.

**P: Posso registrar colheita de 1 semana por vez?**
R: Não recomendado. Registra sempre no mesmo dia ou no máximo 1 dia depois. Senão perde detalhes.

**P: Qual é a umidade ideal na colheita?**
R: Depende do método:
- **NATURAL (cereja):** 55-65% umidade
- **LAVADO:** 50-60% umidade
- **HONEY:** 50-60% umidade
- **DESCASCADO (coco):** 30-40% umidade

Use **umidômetro** para medir. Se não tiver, estime.

---

### **Beneficiamento (Processamento)**

**P: Como começo a processar?**
R: Vai em Romaneios → Clica botão 🏭 "Processar" → Lote criado em Beneficiamento.

**P: Qual método de processamento escolho?**
R: 
- **NATURAL:** Mais fácil, cor mais escura, corpo maior
- **LAVADO:** Mais caro, sabor mais limpo, acidez
- **HONEY:** Equilibrado, gosto adocicado
- **DESCASCADO:** Mais rápido, melhor controle

Se não tiver experiência, comece com **NATURAL**.

**P: Quanto tempo demora processar?**
R:
- **Secagem:** 15-21 dias (depende do clima)
- **Descascamento:** 1 dia
- **Classificação:** 1 dia
- **Total:** 3-4 semanas

**P: O que é "Perda Detalhada"?**
R: Breakdown do que foi perdido durante processamento:
- **Secagem:** Água que evaporou (50-60% do peso inicial)
- **Quebra:** Grãos que racharam (5-10%)
- **Defeito:** Grãos pretos, fermentados, verdes (2-5%)

Soma tudo = perda total esperada (~40% do peso inicial).

**P: Qual é o rendimento esperado?**
R: De 100kg de cereja (60% umidade) → ~25kg de café beneficiado
- Esse fator de **4:1** é normal
- Se rendimento < 3.5:1 = problema na colheita ou processamento
- Se rendimento > 4.5:1 = talvez medição errada

**P: Posso processar diferentes métodos juntos?**
R: Não. Manter lotes separados. Cada método tem processamento e tempo diferentes.

---

### **Venda (Comercialização)**

**P: O que é "Status RASCUNHO"?**
R: Venda criada mas não finalizada. Você ainda pode:
- Adicionar comprador
- Mudar quantidade
- Adicionar preço
- Gerar nota fiscal

**P: Como finalizo uma venda?**
R: Vai em Financeiro → Comercialização → Preenche dados do comprador → Salva como "CONFIRMADO"

**P: Posso vender só parte do lote?**
R: Sim! Na hora de criar venda, digita a quantidade desejada. O resto fica no estoque.

**P: Como sei se café está pronto para vender?**
R: Status do lote deve ser **ARMAZENADO**. Café tem umidade entre 11-12%.

---

## 🔧 Troubleshooting (Problemas & Soluções)

### **❌ Botão "Processar" não aparece**

**Possíveis causas:**
1. Romaneio ainda está sendo carregado
2. Você não tem permissão (fale com admin)

**Solução:**
- Atualize a página (F5)
- Aguarde 2 segundos
- Se ainda não aparecer, saia e entre novamente

---

### **❌ Lote não aparece em Beneficiamento**

**Possíveis causas:**
1. Página não foi atualizada
2. Lote foi criado em safra diferente

**Solução:**
```
1. Volte para Romaneios
2. Clique no romaneio que processou
3. Verifique a safra dele (qual é o ID)
4. Vá em Safras → Clique a safra correta → Beneficiamento
```

---

### **❌ "Gerar Venda" diz que safra não tem commodity**

**Causa:** Safra não foi vinculada a nenhuma commodity (tipo de produto).

**Solução:**
1. Vá em Safras → Clique a safra
2. Procure campo "Commodity" ou "Produto"
3. Selecione "Café" ou variante
4. Salve
5. Volte para Beneficiamento e tente novamente

---

### **❌ Números não batem (peso entrada ≠ peso saída)**

**Esperado:** Entrada (100kg) → Saída (~25kg) = normal!

**Se saída > entrada:** ❌ Erro de medição
- Revise peso_entrada_kg
- Revise peso_saida_kg
- Use balança de novo

**Se saída muito pequena (< 20kg de 100kg entrada):** ⚠️ Possível problema
- Revisar método de processamento
- Verificar se café não queimou na secagem
- Consultar agrônomo

---

### **❌ Status preso em SECAGEM (não muda)**

**Causa:** Usuário esqueceu de preencher data final de secagem.

**Solução:**
1. Clique ✏️ para editar lote
2. Preencha "Data Fim Secagem"
3. Preencha "Peso Saída (kg)"
4. Mude status para "CLASSIFICACAO"
5. Salve

---

### **❌ Perda Detalhada muito alta (> 50%)**

**Possíveis causas:**
1. Café colhido muito verde ou muito maduro
2. Umidade inicial errada
3. Secagem muito longa ou muito rápida
4. Problema na colheita (muita terra/folha)

**Solução:**
- Verifique umidade inicial (deve estar 50-65%)
- Revise método (NATURAL costuma ter mais perda)
- Próxima colheita: colha só frutos maduros
- Consulte agrônomo se perda > 60%

---

### **❌ Não consigo editar lote**

**Possíveis causas:**
1. Lote já está VENDIDO (imutável)
2. Você não tem permissão
3. Sessão expirou

**Solução:**
- Se VENDIDO: não pode editar (é arquivo histórico)
- Faça logout e login novamente
- Se ainda não funciona: contate admin

---

## 📈 Checklist Diário

**Manhã (durante colheita):**
- [ ] Colheu café? Preenche peso e umidade em Romaneios
- [ ] Tem anotações? Salva em "Observações"

**À noite (ao terminar o dia):**
- [ ] Registrou tudo em Romaneios?
- [ ] Próxima etapa: Processamento (transferir para secador)

**Durante Processamento:**
- [ ] Acompanha umidade diariamente
- [ ] Registra data final quando seco
- [ ] Atualiza status em Beneficiamento

**Fim de Processamento:**
- [ ] Café está pronto? (umidade 11-12%)
- [ ] Gera venda
- [ ] Procura compradores

---

## 🎓 Termos Explicados (Glossário Mínimo)

| Termo | O Que É |
|-------|---------|
| **Safra** | Um ciclo completo: plantio → colheita → beneficiamento → venda |
| **Romaneio** | Documento que registra cada lote colhido |
| **Cereja** | Café colhido (fruto com polpa) |
| **Coco** | Cereja seca (com casca ainda) |
| **Umidade** | Água no café (mede com aparelho) |
| **Beneficiamento** | Processo que tira casca e prepara para vender |
| **Secagem** | Reduzir umidade de 60% para 12% |
| **Descascamento** | Tirar casca do café |
| **Classificação** | Separar por tamanho/qualidade |
| **Peneira** | Número que indica tamanho (17, 15/16, 13/14) |
| **SCA** | Pontuação de qualidade (0-100, ≥80 = premium) |
| **Commodity** | Produto padronizado pronto para vender |

---

## 📞 Ainda Tem Dúvida?

1. **Releia o [Guia Rápido](GUIA_RAPIDO_SAFRA_CAFE.md)** (5 min)
2. **Veja o [Manual Completo](MANUAL_SAFRA_CAFE_USUARIO.md)** (20 min)
3. **Procure neste FAQ** (2 min)
4. **Contate suporte:** suporte@fazenda.app

---

**Última atualização:** 2026-04-15  
**Versão:** 1.0
