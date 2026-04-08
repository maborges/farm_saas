---
modulo: "Agrícola"
descricao: "Módulo completo de gestão agrícola — do planejamento de safra até o beneficiamento pós-colheita"
niveis:
  essencial:
    - safras
    - operacoes-campo
    - campo-campo
  profissional:
    - planejamento-safra
    - monitoramento-ndvi
    - custos-producao
  enterprise:
    - rastreabilidade-campo
    - prescricoes-vrt
    - beneficiamento
total_submodulos_implementados: 22
---

# Módulo Agrícola — Visão Geral

## Propósito

O módulo Agrícola é o núcleo produtivo do AgroSaaS. Ele cobre todo o ciclo de vida de uma safra no contexto da agricultura brasileira: desde o planejamento e preparo do solo, passando por plantio, tratos culturais, monitoramento via satélite e campo, até a colheita, beneficiamento e rastreabilidade completa dos lotes.

Desenvolvido com base em 15 anos de experiência em sistemas de gestão agrícola brasileira, este módulo atende às necessidades específicas do produtor rural do Cerrado (MT/GO/BA), Sul (RS/PR/SC), MATOPIBA e regiões canavieiras/cafeeiras de SP/MG.

## Contexto da Agricultura Brasileira

### Culturas Principais Suportadas

| Cultura | Ciclo (dias) | Regiões Predominantes | Safra Principal | Safrinha |
|---------|--------------|----------------------|-----------------|----------|
| Soja | 90-120 | MT, GO, BA, PR, RS | Out-Dez / Jan-Mar | - |
| Milho | 110-140 | MT, GO, PR, MS | Set-Nov | Jan-Mar (safrinha) |
| Algodão | 150-180 | MT, BA, GO | Out-Dez / Mar-Mai | - |
| Café | Perene | MG, SP, ES, RO | - | Mai-Set (colheita) |
| Cana-de-açúcar | Perene | SP, MG, GO, PR | - | Abr-Nov (moagem) |
| Feijão | 70-90 | PR, MG, GO, BA | Mar-Mai, Ago-Out | Jan-Mar |
| Arroz | 120-150 | RS, SC, MA | Nov-Dez / Mar-Mai | - |
| Trigo | 110-130 | RS, PR | Mai-Jul / Set-Nov | - |

### Calendário Agrícola por Região

#### Cerrado (MT/GO/BA/MATOPIBA)
- **Set-Out**: Preparo de solo, correção, adubação de base
- **Out-Dez**: Plantio de soja (janela ideal ZARC)
- **Jan-Mar**: Colheita de soja, plantio de milho safrinha
- **Mar-Mai**: Aplicação de defensivos no milho, colheita de algodão
- **Mai-Jul**: Colheita de milho safrinha, planejamento próxima safra

#### Sul (RS/PR/SC)
- **Set-Nov**: Plantio de soja, trigo (inverno)
- **Dez-Fev**: Tratos culturais soja, colheita de trigo
- **Jan-Mar**: Colheita de soja, plantio de milho/feijão
- **Mar-Mai**: Colheita de milho/feijão, preparo para inverno

#### São Paulo (Cana/Café)
- **Abr-Nov**: Moagem de cana, colheita de café (Mai-Set)
- **Dez-Mar**: Plantio de cana, tratos culturais café

### Referências Técnicas Integradas

- **Embrapa**: Zoneamento agrícola, recomendações de cultivares, práticas de manejo
- **CONAB**: Acompanhamento de safra, preços de referência, estoques
- **ZARC (Zoneamento Agroclimático de Risco)**: Validação de épocas de plantio por município/cultura/variedade
- **MAPA**: Normas de rastreabilidade, caderno de campo, receituário agronômico (Lei 7.802/89)

## Submódulos Implementados (22)

O sistema possui os seguintes submódulos funcionais no frontend e/ou backend:

| # | Submódulo | Nível | Caminho Frontend |
|---|-----------|-------|------------------|
| 1 | Safras | Essencial | `/agricola/safras` |
| 2 | Operações de Campo | Essencial | `/agricola/operacoes` |
| 3 | Caderno de Campo (Monitoramento) | Essencial | `/agricola/monitoramento` |
| 4 | Talhões | Essencial | `/dashboard/agricola/talhoes` |
| 5 | Dashboard Agrícola | Essencial | `/agricola/dashboard` |
| 6 | Timeline de Safra | Essencial | `/agricola/timeline` |
| 7 | Fenologia | Profissional | `/agricola/fenologia` |
| 8 | Checklist de Safra | Profissional | `/agricola/safras/[id]/checklist` |
| 9 | Checklist Templates | Profissional | `/agricola/checklist-templates` |
| 10 | Planejamento de Safra | Profissional | `/agricola/planejamento` |
| 11 | Monitoramento NDVI | Profissional | `/agricola/safras/[id]/ndvi` |
| 12 | Custos de Produção | Profissional | `/agricola/custos` |
| 13 | Orçamento de Safra | Profissional | `/agricola/safras/[id]/orcamento` |
| 14 | Financeiro da Safra | Profissional | `/agricola/safras/[id]/financeiro` |
| 15 | Análises de Solo | Profissional | `/agricola/analises-solo` |
| 16 | Defensivos | Profissional | `/dashboard/agricola/defensivos` |
| 17 | Apontamentos | Profissional | `/dashboard/agricola/apontamentos` |
| 18 | Romaneios de Colheita | Essencial | `/agricola/romaneios` |
| 19 | Rastreabilidade de Lotes | Enterprise | `/agricola/rastreabilidade` |
| 20 | Prescrições VRT | Enterprise | `/dashboard/agricola/prescricoes` |
| 21 | Beneficiamento | Enterprise | `/agricola/beneficiamento` |
| 22 | RAT (Relatório de Assistência Técnica) | Enterprise | `/dashboard/agricola/rat` |

## Arquitetura de Níveis

### Essencial (incluso no plano básico)
Funcionalidades mínimas para qualquer produtor rural operar digitalmente. Registro de safras, operações e caderno de campo. Foco em produtores de soja, milho e algodão do Cerrado e Sul que precisam de controle básico e compliance com legislação de defensivos.

### Profissional (plano intermediário)
Ferramentas de planejamento, monitoramento avançado (NDVI, fenologia, solo), controle de custos e orçamento. Para produtores que buscam otimizar produtividade e margem. Ideal para médias propriedades (500-5000 ha) que precisam de gestão profissionalizada.

### Enterprise (plano completo)
Rastreabilidade campo-a-mesa, agricultura de precisão (VRT), beneficiamento pós-colheita e compliance. Para grandes propriedades, cooperativas e exportadores que atendem mercados exigentes (UE, EUA) e precisam de certificações (GlobalG.A.P., Rainforest Alliance, orgânicos).

## Dependências Core

Todos os submódulos dependem de:
- `core/auth` — autenticação e RBAC
- `core/cadastros/fazendas` — fazendas e talhões
- `core/cadastros/produtos` — culturas e insumos
- `core/tenant` — multi-tenancy

## Integração entre Níveis

```
Essencial ──► Profissional ──► Enterprise
  safras        planejamento      rastreabilidade
  operacoes     ndvi              prescricoes-vrt
  caderno       custos            beneficiamento
```

Cada nível superior consome dados do nível inferior. Um produtor no plano Essencial pode fazer upgrade sem perda de dados.

## Dores Reais do Produtor Brasileiro

1. **Safra dupla (soja + milho safrinha)**: Necessidade de gerenciar duas safras sobrepostas no mesmo talhão, com janelas apertadas entre colheita da soja e plantio do milho.

2. **Custos de insumos**: Fertilizantes e defensivos representam 60-70% do custo de produção. Produtor precisa saber custo exato por saca para negociar venda.

3. **Rastreabilidade para exportação**: União Europeia (Due Diligence Regulation 2023/1115) exige comprovação de origem sem desmatamento. EUA exigem rastreabilidade para FDA.

4. **Caderno de campo para defesa fitossanitária**: Lei 7.802/89 exige registro de aplicações de defensivos. Fiscalização do MAPA pode aplicar multas de R$ 2.000 a R$ 150.000 por irregularidade.

5. **Zoneamento ZARC**: Financiamento bancário (Plano Safra) exige respeito ao zoneamento agroclimático. Plantio fora da janela ZARC pode resultar em perda de seguro e crédito.

## Documentação Detalhada

- [Essencial: Safras](essencial/safras.md)
- [Essencial: Operações de Campo](essencial/operacoes-campo.md)
- [Essencial: Caderno de Campo](essencial/caderno-campo.md)
- [Profissional: Planejamento de Safra](profissional/planejamento-safra.md)
- [Profissional: Monitoramento NDVI](profissional/monitoramento-ndvi.md)
- [Profissional: Custos de Produção](profissional/custos-producao.md)
- [Enterprise: Rastreabilidade de Campo](enterprise/rastreabilidade-campo.md)
- [Enterprise: Prescrições VRT](enterprise/prescricoes-vrt.md)
- [Enterprise: Beneficiamento](enterprise/beneficiamento.md)
