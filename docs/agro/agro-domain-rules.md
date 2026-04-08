# Agro Domain Rules (Regras de Domínio Agro)

Este documento define as **regras conceituais imutáveis** do domínio
agro para evitar erros estruturais na modelagem do SaaS.

------------------------------------------------------------------------

## 1. Estrutura Organizacional

### Organização (Tenant)

-   Representa o cliente do SaaS.
-   Pode possuir múltiplos grupos produtivos.

### Grupo Produtivo

-   Agrupa fazendas e áreas produtivas.
-   Pode representar holding, grupo familiar ou operação empresarial.

### Fazenda / Sítio / Arrendamento

-   Unidade operacional.
-   Pode ser própria ou arrendada.
-   Possui áreas produtivas.

------------------------------------------------------------------------

## 2. Estrutura Física da Terra

Hierarquia:

Grupo Produtivo → Fazenda → Gleba → Talhão → Subtalhão / Zona de Manejo
→ (Piquete -- pecuária)

### Gleba

Grande divisão territorial com características semelhantes.

### Talhão

Unidade operacional agrícola.

### Subtalhão

Subdivisão operacional do talhão.

### Zona de Manejo

Área baseada em variabilidade agronômica.

### Piquete

Unidade de pastejo da pecuária.

------------------------------------------------------------------------

## 3. Regras Fundamentais

-   Custos são **temporais (Safra/Ciclo)** e NÃO espaciais.
-   Talhões executam operações.
-   Safras acumulam custos.
-   Uma área pode mudar de uso ao longo do tempo.
-   Agricultura e pecuária compartilham a mesma estrutura territorial.

------------------------------------------------------------------------

## 4. Regras de Custos

Custos pertencem a: - Safra (agricultura) - Ciclo Pecuário (pecuária)

Nunca diretamente à terra.

------------------------------------------------------------------------

## 5. Princípios Modernos

-   Separar espaço físico de tempo produtivo.
-   Histórico imutável.
-   Multiatividade (agricultura + pecuária).
-   Suporte a agricultura de precisão.
