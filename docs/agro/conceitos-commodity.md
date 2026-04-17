# 🌾 Contexto de Commodities no SaaS Agro

## 🎯 Objetivo

Definir de forma completa e consistente o conceito de **commodities** dentro de um sistema SaaS agro, incluindo:

- definição conceitual
- separação entre produção e mercado
- modelo de dados
- regras de negócio
- boas práticas

---

# 🧠 Conceito de Commodity

> **Commodity é uma categoria padronizada de mercado utilizada para comercialização.**

Exemplos:
- soja
- milho
- café
- boi gordo
- leite

---

## ⚠️ Importante

Commodity **NÃO é o resultado da safra**.

---

# 🌱 Separação de conceitos (ESSENCIAL)

## Estrutura correta

Safra
└── Cultivo
└── Produção
└── Produto
└── Commodity


---

## 📊 Definições

| Conceito | Descrição |
|--------|----------|
| Safra | período produtivo |
| Cultivo | plantio em talhão |
| Produção | resultado colhido |
| Produto | item classificado |
| Commodity | padrão de mercado |

---

# 🔄 Momento em que vira Commodity

> O produto se torna commodity **no momento da padronização para comercialização**

Fluxo:
Produção → Classificação → Padronização → Comercialização


---

# 🧱 Modelo de Dados — Commodity

Commodity

id (uuid)
nome (string, obrigatório)
codigo (string, único)
descricao (text)
tipo (enum)
AGRICOLA | PECUARIA | FLORESTAL
unidade_padrao (enum)
SACA_60KG | TONELADA | KG | ARROBA | LITRO | CABECA
peso_unidade (decimal, opcional)
possui_cotacao (boolean)
bolsa_referencia (string)
codigo_bolsa (string)
ativo (boolean)
created_at
updated_at



---

# ⚠️ Regra CRÍTICA — Peso da Unidade

> Nem toda unidade possui peso fixo.

---

## ✅ Quando usar peso_unidade

| Unidade | Exemplo | Valor |
|--------|--------|------|
| Saca | Soja | 60 |
| Arroba | Boi gordo | 15 |
| Tonelada | Grãos | 1000 |

---

## ❌ Quando NÃO usar

| Unidade | Motivo |
|--------|-------|
| Cabeça | peso varia por animal |
| Litro | unidade de volume |

---

# 🐄 Exemplos

## Boi Gordo
nome: Boi Gordo
codigo: BOI_GORDO
tipo: PECUARIA
unidade_padrao: ARROBA
peso_unidade: 15
possui_cotacao: true


---

## Bezerro

nome: Bezerro
codigo: BEZERRO
tipo: PECUARIA
unidade_padrao: CABECA
peso_unidade: null


👉 Peso controlado em:
- animal
- lote

---

## 🥛 Leite

### Simples (recomendado)

unidade_padrao: LITRO
peso_unidade: null


### Avançado

peso_unidade: 1.03


---

## 🌱 Soja

nome: Soja
codigo: SOJA
tipo: AGRICOLA
unidade_padrao: SACA_60KG
peso_unidade: 60


---

## ☕ Café (caso especial)

### ❗ Importante

Commodity: Café
Produto: Café Conilon ou Arábica


👉 Conilon NÃO é commodity

---

# 🔗 Relacionamentos
Commodity
└── Produto
└── Classificacao
└── Producao
└── Comercializacao


---

# ⚠️ Regras de Negócio

1. nome deve ser único por tenant  
2. codigo deve ser único  
3. unidade_padrao é obrigatória  
4. peso_unidade só pode ser usado em unidades fixas  
5. não permitir exclusão física  
6. usar campo `ativo`  

---

# ❌ NÃO incluir na Commodity

- qualidade
- umidade
- impureza
- tipo comercial

👉 Isso pertence a:
- Produto
- Classificação

---

# 🧠 Boas Práticas

- separar produção de mercado  
- evitar peso fixo em unidades variáveis  
- padronizar unidades  
- usar enums  
- preparar para integração com mercado  

---

# 🚀 Evolução futura

## Conversão de unidades

ConversaoUnidade

- unidade_origem
- unidade_destino
- fator


---

# ⭐ Insight de Arquitetura

Separar claramente:
Produção → Produto → Commodity → Comercialização


👉 Isso garante:
- rastreabilidade
- flexibilidade
- consistência financeira
- integração com mercado

---

# 🔥 Regra de Ouro

> **Commodity define como o produto é negociado, não como ele é produzido.**