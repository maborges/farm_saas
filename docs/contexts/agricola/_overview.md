---
modulo: "Agr\xEDcola"
descricao: "M\xF3dulo completo de gest\xE3o agr\xEDcola \u2014 do planejamento de safra at\xE9 o beneficiamento p\xF3s-colheita"
niveis:
  essencial:
    - safras
    - operacoes-campo
    - caderno-campo
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

# Modulo Agricola — Visao Geral

## Proposito

O modulo Agricola e o nucleo produtivo do AgroSaaS. Ele cobre todo o ciclo de vida de uma safra: desde o planejamento e preparo do solo, passando por plantio, tratos culturais, monitoramento via satelite e campo, ate a colheita, beneficiamento e rastreabilidade completa dos lotes.

## Submodulos Implementados (22)

O sistema ja possui os seguintes submodulos funcionais no frontend e/ou backend:

| # | Submodulo | Nivel | Caminho Frontend |
|---|-----------|-------|------------------|
| 1 | Safras | Essencial | `/agricola/safras` |
| 2 | Operacoes de Campo | Essencial | `/agricola/operacoes` |
| 3 | Caderno de Campo (Monitoramento) | Essencial | `/agricola/monitoramento` |
| 4 | Talhoes | Essencial | `/dashboard/agricola/talhoes` |
| 5 | Dashboard Agricola | Essencial | `/agricola/dashboard` |
| 6 | Timeline de Safra | Essencial | `/agricola/timeline` |
| 7 | Fenologia | Profissional | `/agricola/fenologia` |
| 8 | Checklist de Safra | Profissional | `/agricola/safras/[id]/checklist` |
| 9 | Checklist Templates | Profissional | `/agricola/checklist-templates` |
| 10 | Planejamento de Safra | Profissional | `/agricola/planejamento` |
| 11 | Monitoramento NDVI | Profissional | `/agricola/safras/[id]/ndvi` |
| 12 | Custos de Producao | Profissional | `/agricola/custos` |
| 13 | Orcamento de Safra | Profissional | `/agricola/safras/[id]/orcamento` |
| 14 | Financeiro da Safra | Profissional | `/agricola/safras/[id]/financeiro` |
| 15 | Analises de Solo | Profissional | `/agricola/analises-solo` |
| 16 | Defensivos | Profissional | `/dashboard/agricola/defensivos` |
| 17 | Apontamentos | Profissional | `/dashboard/agricola/apontamentos` |
| 18 | Romaneios de Colheita | Essencial | `/agricola/romaneios` |
| 19 | Rastreabilidade de Lotes | Enterprise | `/agricola/rastreabilidade` |
| 20 | Prescricoes VRT | Enterprise | `/dashboard/agricola/prescricoes` |
| 21 | Beneficiamento | Enterprise | `/agricola/beneficiamento` |
| 22 | RAT (Relatorio de Assistencia Tecnica) | Enterprise | `/dashboard/agricola/rat` |

## Arquitetura de Niveis

### Essencial (incluso no plano basico)
Funcionalidades minimas para qualquer produtor rural operar digitalmente. Registro de safras, operacoes e caderno de campo.

### Profissional (plano intermediario)
Ferramentas de planejamento, monitoramento avancado (NDVI, fenologia, solo), controle de custos e orcamento. Para produtores que buscam otimizar produtividade e margem.

### Enterprise (plano completo)
Rastreabilidade campo-a-mesa, agricultura de precisao (VRT), beneficiamento pos-colheita e compliance. Para grandes propriedades, cooperativas e exportadores.

## Dependencias Core

Todos os submodulos dependem de:
- `core/auth` — autenticacao e RBAC
- `core/cadastros/fazendas` — fazendas e talhoes
- `core/cadastros/produtos` — culturas e insumos
- `core/tenant` — multi-tenancy

## Integracao entre Niveis

```
Essencial ──► Profissional ──► Enterprise
  safras        planejamento      rastreabilidade
  operacoes     ndvi              prescricoes-vrt
  caderno       custos            beneficiamento
```

Cada nivel superior consome dados do nivel inferior. Um produtor no plano Essencial pode fazer upgrade sem perda de dados.

## Documentacao Detalhada

- [Essencial: Safras](essencial/safras.md)
- [Essencial: Operacoes de Campo](essencial/operacoes-campo.md)
- [Essencial: Caderno de Campo](essencial/caderno-campo.md)
- [Profissional: Planejamento de Safra](profissional/planejamento-safra.md)
- [Profissional: Monitoramento NDVI](profissional/monitoramento-ndvi.md)
- [Profissional: Custos de Producao](profissional/custos-producao.md)
- [Enterprise: Rastreabilidade de Campo](enterprise/rastreabilidade-campo.md)
- [Enterprise: Prescricoes VRT](enterprise/prescricoes-vrt.md)
- [Enterprise: Beneficiamento](enterprise/beneficiamento.md)
