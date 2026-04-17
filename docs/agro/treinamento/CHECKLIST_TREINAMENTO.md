# ✅ Checklist de Treinamento — Para Facilitadores

**Objetivo:** Guia para quem vai treinar outros usuários no sistema de Safra de Café

**Público-alvo:** Gerentes, supervisores, treinadores

**Tempo de treinamento:** 30 minutos (parte 1) + 1 hora prática (parte 2)

---

## 📚 Preparação (Antes do Treinamento)

- [ ] Ler [Guia Rápido](GUIA_RAPIDO_SAFRA_CAFE.md) (5 min)
- [ ] Ler [Manual Completo](MANUAL_SAFRA_CAFE_USUARIO.md) (20 min)
- [ ] Revisar [FAQ](FAQ_TROUBLESHOOTING.md) (10 min)
- [ ] Acessar sistema e testar fluxo:
  - [ ] Criar safra teste
  - [ ] Criar orçamento
  - [ ] Criar romaneio
  - [ ] Processar em beneficiamento
  - [ ] Gerar venda
- [ ] Preparar dados reais (ou de exemplo) para usar no treinamento
- [ ] Baixar este checklist em papel ou celular

---

## 🎓 PARTE 1: Apresentação Teórica (15 minutos)

### **Bloco 1: O Grande Panorama (5 min)**

Explique aos alunos:

> "A aplicação ajuda você desde o planejamento da safra até a venda do café. Em vez de usar papel ou planilha, tudo fica organizado no sistema."

**Mostre em slides ou na tela:**

```
FLUXO VISUAL:

Safra Criada
    ↓
Orçamento Feito (quanto vai gastar)
    ↓
Colheita Registrada (romaneios)
    ↓
Café Processado (beneficiamento)
    ↓
Venda Gerada (pronto para vender)
    ↓
Relatório Final (quanto custou, quanto ganhou)
```

**Pergunte aos alunos:**
- [ ] Alguém já usou sistema assim antes?
- [ ] Quais são as maiores dificuldades de hoje sem sistema?

---

### **Bloco 2: Os 5 Passos Principais (10 min)**

Para cada passo, explique:

#### **Passo 1: Criar Safra (2 min)**
- O que é: Registro da safra (cultura, talhão, ano)
- Por que: Organizar tudo em um só lugar
- Dados necessários: Cultura, talhão, data prevista
- **Demonstre:** Abra a tela de Safras, crie uma teste

#### **Passo 2: Planejar Orçamento (2 min)**
- O que é: Estimar quanto vai gastar
- Por que: Saber se está dentro do orçamento
- Categorias: Sementes, adubo, defensivo, combustível, mão-de-obra, outros
- **Demonstre:** Abra Orçamento, adicione 2-3 itens

#### **Passo 3: Registrar Colheita (2 min)**
- O que é: Romaneio (documento de cada dia colhido)
- Por que: Rastrear quanto colheu, data, peso, umidade
- Dados: Data, talhão, peso, umidade
- **Demonstre:** Crie um romaneio de exemplo

#### **Passo 4: Processar Café (2 min)**
- O que é: Beneficiamento (tirar casca, secar, classificar)
- Por que: Transformar cereja em café pronto para vender
- Métodos: NATURAL, LAVADO, HONEY, DESCASCADO
- Perdas: O café perde ~40% do peso (normal!)
- **Demonstre:** Clique "Processar" em um romaneio

#### **Passo 5: Gerar Venda (2 min)**
- O que é: Criar venda quando café está pronto
- Por que: Documento para vender (rastreável, com nota fiscal)
- Status: RASCUNHO → CONFIRMADO
- **Demonstre:** Mude status de lote para ARMAZENADO, gere venda

---

## 👥 PARTE 2: Prática Supervisionada (45 minutos)

### **Exercício 1: Criar Safra (10 min)**

**Instrução para alunos:**
```
1. Abra a aplicação
2. Vá em: Menu → Agrícola → Safras
3. Clique "+ Nova Safra"
4. Preencha:
   ├─ Cultura: "Café"
   ├─ Talhão: (qualquer um da sua fazenda)
   ├─ Ano Safra: "2025/2026"
   └─ Data Plantio: (data de hoje)
5. Salve
```

**Enquanto os alunos fazem:**
- [ ] Circule pela sala/tela
- [ ] Responda dúvidas
- [ ] Aponte erros comuns:
  - [ ] Esquecer de selecionar talhão
  - [ ] Errar formato da data
- [ ] Elogie quem terminou primeiro

**Tempo:** 10 min (mais rápido se usar dados de teste)

---

### **Exercício 2: Planejar Orçamento (10 min)**

**Instrução para alunos:**
```
1. Na safra que criou, clique "Orçamento"
2. Clique "+ Adicionar Item" 5 vezes
3. Preencha para cada item:
   ├─ Categoria: (SEMENTE, FERTILIZANTE, etc)
   ├─ Descrição: descrição do item
   ├─ Quantidade: número
   ├─ Unidade: unidade (kg, litro, etc)
   └─ Custo Unitário: preço
4. O custo total calcula automático
```

**Enquanto os alunos fazem:**
- [ ] Verifique se estão preenchendo todos os campos
- [ ] Mostre como o sistema calcula total
- [ ] Aponte que **é normal usar estimativas**

**Tempo:** 10 min

---

### **Exercício 3: Registrar Colheita (10 min)**

**Instrução para alunos:**
```
1. Na safra, clique "Romaneios"
2. Clique "+ Novo Romaneio"
3. Preencha:
   ├─ Data Colheita: (data de hoje)
   ├─ Talhão: (mesmo da safra)
   ├─ Peso Bruto: 1000 kg (número teste)
   ├─ Umidade: 55 (para café cereja)
   └─ Observações: (se tiver problema, anota aqui)
4. Salve
```

**Enquanto os alunos fazem:**
- [ ] Explique por que umidade importa (50-65% para cereja)
- [ ] Mostre que sistema calcula sacas automaticamente
- [ ] Se alguém errar peso, mostre como editar (botão ✏️)

**Tempo:** 10 min

---

### **Exercício 4: Processar Café (10 min)**

**Instrução para alunos:**
```
1. Na tabela de Romaneios, procure o que criou
2. Clique botão 🏭 "Processar"
3. Sistema vai criar lote em Beneficiamento
4. Clique "Beneficiamento" para ver
5. Clique ✏️ no lote novo
6. Preencha:
   ├─ Método: NATURAL (padrão)
   ├─ Data Fim Secagem: 10 dias depois
   ├─ Peso Saída: 250 kg (de 1000 entrada)
   ├─ Perda Secagem: 600 kg
   ├─ Perda Quebra: 100 kg
   └─ Perda Defeito: 50 kg
7. Mude Status para "ARMAZENADO"
8. Salve
```

**Enquanto os alunos fazem:**
- [ ] Explique o fator de redução (4:1 é normal)
- [ ] Mostre que perdas somam ~40% (esperado)
- [ ] Aponte que agora café está "pronto para vender"

**Tempo:** 10 min

---

### **Exercício 5: Gerar Venda (5 min)**

**Instrução para alunos:**
```
1. Em Beneficiamento, procure lote em ARMAZENADO
2. Clique botão 🛒 "Gerar Venda"
3. Venda criada em RASCUNHO
4. Vá em Financeiro → Comercialização
5. Deve aparecer a venda nova
```

**Enquanto os alunos fazem:**
- [ ] Explique que RASCUNHO = ainda não finalizado
- [ ] Mostre que pode adicionar comprador depois
- [ ] Aponte que café virou "commodity" (produto pronto)

**Tempo:** 5 min

---

## 🔍 Verificação de Aprendizado

Após exercícios, pergunte ao grupo (ou individualmente):

- [ ] "O que é um romaneio?" (resposta esperada: documento de colheita)
- [ ] "Por que preenchemos orçamento?" (resposta: saber quanto vai gastar)
- [ ] "O que significa fator de redução 4:1?" (resposta: 4kg cereja = 1kg beneficiado)
- [ ] "Qual é a umidade ideal do café cereja?" (resposta: 50-65%)
- [ ] "Quando você gera uma venda?" (resposta: quando café está ARMAZENADO/pronto)

**Se acertar 4/5 ou mais:** ✅ Aluno aprendeu!
**Se acertar 3/5 ou menos:** ⚠️ Revise os pontos errados

---

## 💡 Dicas para um Bom Treinamento

✅ **DO:**
- Deixe alunos clicarem (não faça pelo eles)
- Use dados reais ou muito próximos de real
- Repita as explicações (cada um aprende no seu tempo)
- Mostre erros propositais ("vou preencher umidade como 100%, vê o que acontece")
- Dê tempo para perguntas
- Reconheça progresso ("ótimo! Já pega bem!")

❌ **DON'T:**
- Não faça aula só de apresentação (precisa praticar!)
- Não use dados muito fictícios (alunos não relacionam)
- Não tenha pressa (melhor ficar 1h a mais que deixar dúvida)
- Não ignore pergunta (sempre responde, mesmo se boba)
- Não assume que todos entendem ao mesmo tempo (ritmos diferentes)

---

## 📋 Checklist Pós-Treinamento

- [ ] Todos conseguiram criar safra?
- [ ] Todos conseguiram criar orçamento?
- [ ] Todos conseguiram registrar romaneio?
- [ ] Todos conseguiram processar café?
- [ ] Todos conseguiram gerar venda?
- [ ] Algum aluno ficou com dúvida? (anotar para revisão 1:1)
- [ ] Todos têm acesso ao [Guia Rápido](GUIA_RAPIDO_SAFRA_CAFE.md)?
- [ ] Todos têm acesso ao [FAQ](FAQ_TROUBLESHOOTING.md)?
- [ ] Todos sabem como contatar suporte?

---

## 📞 Suporte Pós-Treinamento

**Para os próximos dias:**
- Deixe contato disponível para dúvidas rápidas
- Revise com quem teve mais dificuldade (1:1)
- Acompanhe primeiro romaneio de cada um
- Depois de 1 semana, peça feedback

**Sinais de que alguém está com dificuldade:**
- Não registra romaneios (ou registra errado)
- Deixa lotes presos em RECEBIMENTO
- Preenche dados sem sentido (umidade 150%)
- Não acompanha o sistema

**Se isto acontecer:**
- Ofereça novo treinamento 1:1 (30 min)
- Crie post-it com os 5 passos na parede
- Agende revisão em 1 semana

---

## 📊 Relatório do Treinamento

Após o treinamento, preencha:

```
Data: ___/___/______
Facilitador: _________________
Participantes: _____ pessoas
Duração: _____ minutos

Alunos que completaram:
├─ Exercício 1 (Safra): ___/___
├─ Exercício 2 (Orçamento): ___/___
├─ Exercício 3 (Colheita): ___/___
├─ Exercício 4 (Processamento): ___/___
└─ Exercício 5 (Venda): ___/___

Dúvidas frequentes:
- ________________
- ________________
- ________________

Pontos a revisar:
- ________________
- ________________

Próximo treinamento: ___/___/______
```

---

**Obrigado por treinar o time! 🙏**

Feedback: suporte@fazenda.app
