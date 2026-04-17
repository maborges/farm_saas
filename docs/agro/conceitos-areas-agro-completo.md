
# 🌾 Conceitos de Áreas em Sistemas de Gestão Agro (SaaS) — Versão Completa

Este documento define de forma **completa, consistente e orientada a produto** os conceitos de áreas
em um sistema SaaS agro moderno.

O objetivo é servir como base para:
- modelagem de banco de dados
- regras de negócio
- validações automáticas
- integração com mapas (GIS)
- uso por IA e motores de decisão

---

# 🎯 PRINCÍPIO FUNDAMENTAL

> A área real do sistema deve vir da **estrutura territorial (polígonos)**  
> e não de campos digitados manualmente.

---

# 🧱 1. ÁREA TOTAL

## Conceito
Área total da unidade produtiva, incluindo **todas as áreas internas**.

## Fonte correta
- polígono da propriedade (recomendado)
OU
- soma de todas as áreas cadastradas

## Inclui
- áreas produtivas
- APP
- reserva legal
- infraestrutura
- áreas improdutivas

---

# 🌱 2. ÁREA PRODUTIVA

## Conceito
Área efetivamente utilizada para produção agropecuária.

## Fonte correta (OBRIGATÓRIO)
Área Produtiva = soma das áreas de TALHÕES ativos

## Inclui
- lavouras
- pastagens
- culturas permanentes

## Não inclui
- APP
- reserva legal
- sede
- estradas
- áreas improdutivas

---

# 🌿 3. APP (Área de Preservação Permanente)

## Conceito
Área protegida por lei ambiental.

## Características
- uso restrito
- obrigatória preservação
- vinculada ao CAR

## Exemplos
- margens de rios
- nascentes
- encostas

---

# 🌳 4. RESERVA LEGAL

## Conceito
Área com vegetação nativa obrigatória.

## Características
- percentual da propriedade
- pode permitir manejo sustentável

---

# 🏗️ 5. INFRAESTRUTURA

## Conceito
Áreas ocupadas por estruturas operacionais.

## Exemplos
- sede
- armazém
- curral
- estradas

---

# ⛰️ 6. ÁREAS IMPRODUTIVAS

## Conceito
Áreas sem uso produtivo por limitação natural.

## Exemplos
- rochas
- brejos
- áreas degradadas

---

# 🧮 7. MODELO DE CÁLCULO (OFICIAL DO SISTEMA)

Área Total =
    Produtiva + APP + Reserva + Infraestrutura + Improdutiva

Área Produtiva =
    soma(Talhões)

APP =
    soma(áreas tipo APP)

Reserva Legal =
    soma(áreas tipo RESERVA_LEGAL)

---

# ⚠️ 8. ERROS QUE DEVEM SER EVITADOS

❌ calcular área produtiva como A - (APP + RL)  
❌ permitir edição manual da área produtiva  
❌ misturar infraestrutura com área rural  
❌ não validar sobreposição de áreas  

---

# 🔐 9. REGRAS DE VALIDAÇÃO (ENGINE DE CONSISTÊNCIA)

## Regra 1
APP + Reserva ≤ Área Total

## Regra 2
Área Produtiva ≤ Área Total

## Regra 3
Nenhuma área pode ultrapassar os limites da fazenda

## Regra 4
Áreas não devem se sobrepor (exceto quando permitido)

---

# 🗺️ 10. INTEGRAÇÃO COM MAPA

O sistema deve permitir:

- desenho de polígonos
- importação (KML, SHP)
- cálculo automático de área
- validação espacial

---

# ⭐ 11. MODELO FINAL RECOMENDADO

UnidadeProdutiva
   └── AreaRural (fonte da verdade)
         ├── Talhões → produção
         ├── APP / Reserva → ambiental
         ├── Infraestrutura → operação
         └── Improdutivas

---

# 🚜 12. REGRA DE OURO

> Se a área não vem da estrutura territorial, ela não é confiável.

---

# 📌 CONCLUSÃO

A correta modelagem das áreas permite:

- controle real da produção
- cálculo correto de custos
- compliance ambiental
- escalabilidade do SaaS

Este documento deve ser tratado como **regra base do domínio agro**.
