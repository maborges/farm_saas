# 🌾 CONTEXTO MESTRE — AGROSaaS

## 🎯 Objetivo

Definir o modelo conceitual completo para um sistema SaaS de gestão agrícola e pecuária, garantindo consistência entre estrutura física, operações, custos, produção e análise financeira.

Este documento serve como base única para desenvolvimento, IA, modelagem de dados e regras de negócio.

---

# 🧠 PRINCÍPIOS FUNDAMENTAIS

1. Talhão representa espaço físico  
2. Safra representa tempo  
3. Cultivo representa a ocupação real (tempo + espaço)  
4. Custos, operações e produção pertencem ao cultivo  
5. Cada cultura é tratada como um negócio independente  
6. Tudo que acontece no tempo de um talhão deve ser registrado  

---

# 🏢 ESTRUTURA ORGANIZACIONAL

Tenant (Produtor / Empresa)
→ representa o cliente do SaaS

Um tenant pode possuir múltiplas unidades produtivas.

---

# 🚜 UNIDADE PRODUTIVA

Representa uma entidade operacional rural:

- Fazenda  
- Sítio  
- Arrendamento  
- Parceria  

A unidade produtiva pode ou não possuir infraestrutura própria.

---

# 🌍 ESTRUTURA ESPACIAL (HIERARQUIA)

Unidade Produtiva
→ Área Rural (estrutura única e hierárquica)

Tipos de área:

- GLEBA (raiz)
- TALHÃO (produção agrícola)
- PASTAGEM (pecuária)
- PIQUETE (subdivisão da pastagem)
- APP (área de preservação permanente)
- RESERVA LEGAL
- INFRAESTRUTURA (sede, armazém, etc.)

---

# 📏 CONCEITO DE ÁREAS

- Área Total = área completa da unidade  
- APP = área protegida  
- Reserva Legal = área obrigatória  
- Área Produtiva = Área Total - (APP + Reserva Legal)  

A área produtiva pode ser subdividida em talhões e pastagens.

---

# 🌱 SAFRA (TEMPO)

Safra representa um período produtivo.

- possui data início e fim  
- pode se sobrepor a outras safras  
- não ocupa espaço físico  

---

# 🌿 CULTIVO (OCUPAÇÃO REAL)

Cultivo é a entidade central do sistema.

Representa:

- uma cultura  
- em um talhão  
- durante um período  
- com uma área definida  

Estrutura:

- safra_id  
- talhao_id  
- cultura_id  
- area  
- data_inicio  
- data_fim  
- consorciado (boolean)  

---

# 🌾 REGRAS DE OCUPAÇÃO

Para um talhão:

- soma das áreas simultâneas ≤ área do talhão  
- exceção: consórcio  

---

# 🌿 CONSÓRCIO

Consórcio ocorre quando duas culturas ocupam a mesma área ao mesmo tempo.

Regras:

- consorciado = true  
- permite sobreposição total ou parcial  
- não mistura custos nem produção  

---

# 🔁 ROTAÇÃO DE CULTURAS

Alternância de culturas ao longo do tempo no mesmo talhão.

Exemplo:
- Soja → Milho → Braquiária  

---

# 🌿 POUSIO (DESCANSO)

Período sem produção agrícola.

Deve ser modelado como cultivo técnico:

- cultura = POUSIO  

Permite:

- manter histórico  
- registrar custos  
- análise agronômica  

---

# ⚙️ OPERAÇÕES

Toda operação deve estar associada a um cultivo.

Tipos:

- plantio  
- pulverização  
- adubação  
- colheita  

---

## 🔁 OPERAÇÕES COMPARTILHADAS

Quando uma operação impacta múltiplos cultivos:

- deve ser rateada  

Estrutura:

OperacaoRateio:
- operacao_id  
- cultivo_id  
- percentual  

---

# 💰 CUSTOS

Todo custo pertence ao cultivo.

Tipos:

- direto (100% do cultivo)  
- indireto (rateado)  

---

## 🔁 RATEIO DE CUSTOS

Critérios:

- por área (padrão)  
- manual  
- por uso  

---

# 🌾 COLHEITA

Sempre por cultivo.

- produção separada por cultura  
- unidade específica (saca, kg, litro, etc.)  

---

# 📦 COMMODITIES

Representam o produto final disponível para comercialização.

Origem:

- resultado da colheita  

Atributos:

- tipo (grão, animal, leite, etc.)  
- unidade  
- peso por unidade  
- qualidade  
- rastreabilidade  

---

# 🐄 PECUÁRIA

Estrutura baseada em:

- Pastagem  
- Piquete  
- Lotes de animais  

Produção:

- peso (kg)  
- volume (litros)  

---

# 💰 APURAÇÃO DE RESULTADO

Baseada no cultivo:

- custo total  
- produção total  
- receita  
- lucro  

---

# 📊 REGRA DE OURO DE CUSTO

Custos são apurados por safra e por cultivo, nunca apenas por talhão.

---

# 🔄 FLUXO OPERACIONAL

1. Criar unidade produtiva  
2. Criar estrutura (gleba, talhão, etc.)  
3. Criar safra  
4. Criar cultivos  
5. Associar área e período  
6. Registrar operações  
7. Registrar custos  
8. Registrar colheita  
9. Gerar commodities  
10. Apurar resultados  

---

# 🧠 VALIDAÇÕES ESSENCIAIS

- não permitir área excedente  
- validar sobreposição de período  
- permitir consórcio  
- garantir rastreabilidade  

---

# 🚀 NÍVEL AVANÇADO

## 🌍 SUBÁREA (CultivoArea)

Permite dividir talhão logicamente.

- cultivo_area_id  
- geometria (opcional)  

---

## 🗺️ GEOREFERENCIAMENTO

Permite:

- mapas  
- agricultura de precisão  
- controle espacial real  

---

## 🔄 AUTOMAÇÃO

- rateio automático  
- sugestão de cultura  
- análise de solo  
- previsão de produtividade  

---

# 🌐 VISÃO DE ECOSSISTEMA

Evolução do sistema:

- marketplace de insumos  
- venda de produção  
- serviços agrícolas  
- crédito rural  
- profissionais e empregos  

---

# 🔥 INSIGHT FINAL

O sistema deve tratar cada cultivo como uma unidade de negócio independente, garantindo controle total de tempo, espaço, custo e produção.

---

# 📌 CONCLUSÃO

Este modelo garante:

- consistência de dados  
- rastreabilidade completa  
- análise financeira real  
- base para inteligência agrícola  

Este é o fundamento para construção de um SaaS agro moderno, escalável e orientado a dados.