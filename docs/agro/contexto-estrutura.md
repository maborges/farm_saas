# Contexto Estrutural do Agro para SaaS (contexto-estrutura.md)

## Objetivo do Documento

Este documento define os conceitos fundamentais da estrutura territorial
e produtiva de uma operação agropecuária moderna, servindo como
**contexto base para IA** na construção correta de um SaaS de gestão
agro.

O foco é evitar erros conceituais comuns, principalmente:

-   Modelar custos por área física ao invés de por tempo (safra/ciclo)
-   Separar agricultura e pecuária estruturalmente
-   Misturar entidades territoriais com entidades produtivas

------------------------------------------------------------------------

# 1. Princípio Central do Modelo Agro

## Regra fundamental

> O território é permanente.\
> A produção é temporal.

A mesma área pode mudar de uso ao longo do tempo:

  Ano    Área         Uso
  ------ ------------ ----------
  2024   Talhão T01   Soja
  2025   Talhão T01   Milho
  2026   Talhão T01   Pastagem

Portanto:

-   Área ≠ Cultura
-   Área ≠ Pecuária
-   Área = entidade permanente

------------------------------------------------------------------------

# 2. Estrutura Territorial (Camada Espacial)

A organização segue uma hierarquia física.

    Grupo Rural (Propriedade SaaS)
            ↓
    Fazenda / Sítio / Arrendamento
            ↓
    Gleba
            ↓
    Unidade Operacional
       ├── Talhão (agricultura)
       ├── Piquete (pecuária)
       └── Área funcional

------------------------------------------------------------------------

## 2.1 Grupo Rural (Propriedade no SaaS)

### Conceito

Entidade administrativa usada para agrupar múltiplas fazendas.

Não representa necessariamente matrícula jurídica.

### Exemplos

-   Grupo agrícola
-   Holding rural
-   Produtor com várias fazendas

### Função no sistema

-   Consolidação financeira
-   Multiempresa
-   Governança SaaS

------------------------------------------------------------------------

## 2.2 Fazenda / Sítio / Arrendamento

### Conceito

Unidade territorial operacional reconhecida legalmente ou
contratualmente.

### Tipos

-   Fazenda (grande propriedade)
-   Sítio (menor escala)
-   Área arrendada
-   Parceria agrícola

### Atributos principais

-   Nome
-   Área total
-   Município/UF
-   Tipo de posse
-   Responsável técnico

------------------------------------------------------------------------

## 2.3 Gleba

### Conceito

Grande subdivisão interna da fazenda baseada em características
naturais.

### Critérios comuns

-   Tipo de solo
-   Topografia
-   Acesso logístico
-   Histórico produtivo

### Função

Organização macro do território.

------------------------------------------------------------------------

## 2.4 Unidade Operacional

É onde ocorre o manejo real.

Pode assumir diferentes formas conforme a atividade.

------------------------------------------------------------------------

### Talhão (Agricultura)

Área homogênea destinada ao cultivo.

Características: - mesma cultura - mesmo manejo - mesma safra

Usado para: - plantio - pulverização - colheita - produtividade

------------------------------------------------------------------------

### Piquete (Pecuária)

Área de pastejo controlado.

Características: - rotação animal - manejo de pastagem - controle
nutricional

Usado para: - entrada/saída de lote - suplementação - taxa de lotação

------------------------------------------------------------------------

### Área Funcional

Não produtiva diretamente.

Exemplos: - reserva legal - sede - estrada - curral - APP

------------------------------------------------------------------------

# 3. Camada Produtiva (Temporal)

Aqui está o maior erro comum em sistemas agro.

Custos NÃO pertencem ao talhão.

Custos pertencem ao TEMPO.

------------------------------------------------------------------------

## 3.1 Agricultura → SAFRA

Custos vinculados:

    Safra → Talhão

Exemplos: - sementes - fertilizantes - defensivos - diesel - operações

Uma safra pode usar vários talhões.

------------------------------------------------------------------------

## 3.2 Pecuária → CICLO

Custos vinculados:

    Período → Lote Animal → Piquete

Exemplos: - ração - vacina - suplementação - manejo

A pecuária é contínua no tempo.

------------------------------------------------------------------------

# 4. Integração Lavoura-Pecuária (ILP)

A mesma área muda apenas de uso produtivo.

O sistema NÃO deve recriar áreas.

Apenas registrar novos usos ao longo do tempo.

------------------------------------------------------------------------

# 5. Separação Conceitual Essencial

## Entidades Permanentes (Espaciais)

-   Grupo Rural
-   Fazenda
-   Gleba
-   Unidade Operacional

Nunca são recriadas.

------------------------------------------------------------------------

## Entidades Temporais (Produtivas)

-   Safra
-   Ciclo Pecuário
-   Cultura
-   Lote Animal
-   Operações

Mudam continuamente.

------------------------------------------------------------------------

# 6. Conceito Moderno: Unidade Produtiva

Abstração que unifica:

-   Talhão
-   Piquete
-   Área integrada

Define:

> Área + Tempo + Atividade

Permite modelagem única para todo o agro.

------------------------------------------------------------------------

# 7. Benefícios Arquiteturais para o SaaS

Essa estrutura permite:

-   Agricultura pura
-   Pecuária pura
-   Sistemas integrados
-   Custos corretos por safra
-   BI histórico confiável
-   Multi-fazenda
-   Multi-tenant
-   Escalabilidade

------------------------------------------------------------------------

# 8. Regra de Ouro para a IA

Ao construir o sistema:

1.  Nunca associar custo diretamente à área física.
2.  Sempre existir uma entidade temporal intermediária.
3.  A área representa espaço, não produção.
4.  Produção sempre depende de tempo.

------------------------------------------------------------------------

# 9. Resumo Conceitual Final

    ESPAÇO (fixo)
       +
    TEMPO (variável)
       +
    ATIVIDADE (produção)
       =
    GESTÃO AGRO CORRETA

------------------------------------------------------------------------

**Este documento deve ser tratado como regra conceitual base do
domínio.**
