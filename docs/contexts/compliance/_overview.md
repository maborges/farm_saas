---
modulo: Compliance Ambiental
descricao: Gestão de conformidade ambiental para propriedades rurais
niveis:
  essencial:
    - car-gestao
    - app-reserva-legal
    - documentos-ambientais
  profissional:
    - monitoramento-desmatamento
    - gestao-residuos
    - relatorios-esg
  enterprise:
    - carbono
    - due-diligence
    - biodiversidade
---

# Compliance Ambiental

## Visão Geral

O módulo de Compliance Ambiental auxilia o produtor rural a manter-se em conformidade com a legislação ambiental brasileira e exigências internacionais. Abrange desde a gestão básica do CAR (Cadastro Ambiental Rural) e monitoramento de APPs e Reserva Legal, até créditos de carbono, due diligence ambiental para exportação e monitoramento de biodiversidade.

## Problema de Mercado

O produtor rural brasileiro opera sob um dos marcos regulatórios ambientais mais complexos do mundo:
- **Código Florestal (Lei 12.651/2012):** APP, Reserva Legal, CAR, PRA
- **Licenciamento ambiental:** Licenças estaduais com requisitos variados
- **Outorgas de uso de água:** ANA e órgãos estaduais
- **Agrotóxicos:** Logística reversa de embalagens (Lei 7.802/89)
- **EUDR:** Regulamentação europeia anti-desmatamento
- **Mercado de carbono:** Lei 15.042/2024 (Sistema Brasileiro de Comércio de Emissões)

Sem sistema integrado, o produtor corre risco de multas (que podem chegar a R$ 50 milhões), embargo de áreas, perda de acesso a crédito rural e bloqueio de exportações.

## Proposta de Valor por Nível

### Essencial
Gestão do CAR, monitoramento de APP/Reserva Legal e controle de documentos ambientais (licenças, outorgas, vencimentos). Atende o mínimo legal e evita multas por documentação vencida.

### Profissional
Alertas de desmatamento (PRODES/DETER), gestão de resíduos (embalagens de agrotóxicos) e relatórios ESG simplificados. Para produtores que vendem para mercados exigentes ou buscam acesso a linhas de crédito verde.

### Enterprise
Créditos de carbono com inventário de GEE, due diligence ambiental para EUDR e monitoramento de biodiversidade. Para grandes operações que acessam mercados internacionais e programas de carbono.

## Dependências Principais

- `core/fazendas` — cadastro de fazendas com geolocalização
- `core/talhoes` — mapeamento de talhões com shapefile/KML
- `agricola/operacoes` — operações que impactam meio ambiente
- `operacional/estoque` — estoque de agrotóxicos e embalagens
- `rastreabilidade/essencial/historico-aplicacoes` — uso de defensivos
