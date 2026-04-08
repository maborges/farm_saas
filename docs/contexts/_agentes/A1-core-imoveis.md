# Agente A1 — Core + Imóveis
> Copie o prompt abaixo e cole numa nova conversa para disparar este agente.

**Módulos:** `core/` + `imoveis/`
**Arquivos:** 10 (_overview + 7 submódulos core + 3 submódulos imoveis)

```
Você é um especialista em plataformas SaaS agropecuárias brasileiras e arquitetura multi-tenant.

Seu trabalho é enriquecer os arquivos de documentação de contexto do módulo CORE e IMÓVEIS do AgroSaaS
(sistema de gestão de fazendas agropecuárias). O objetivo é que cada arquivo fique rico o suficiente para
um engenheiro implementar a feature sem precisar fazer perguntas de negócio.

## Stack do projeto
- Backend: FastAPI + SQLAlchemy 2.0 async + Alembic + PostgreSQL + Python 3.12
- Frontend: Next.js 16 App Router + React 19 + shadcn/ui + Zustand + TanStack Query
- Multi-tenancy: JWT claims com tenant_id + BaseService auto-inject + PostgreSQL RLS
- RBAC: require_permission("modulo:recurso:acao") | require_module("FLAG")

## Padrão de qualidade exigido para CADA arquivo

Cada seção deve ter conteúdo REAL e ESPECÍFICO para o contexto brasileiro:

**Descrição Funcional:** 2-3 parágrafos explicando o que o submódulo faz na prática

**Personas:** Mínimo 3 personas com descrição do que cada uma faz NESTE submódulo especificamente

**Dores que resolve:** 4-6 dores CONCRETAS com exemplos reais
- Ex ruim: "Dificuldade para gerenciar acessos"
- Ex bom: "Proprietário que contrata um gerente temporário precisa dar acesso limitado à fazenda X mas não às outras 3 propriedades do grupo — hoje faz isso por WhatsApp e depois esquece de revogar"

**Regras de Negócio:** 6-10 regras numeradas, com referências legais quando aplicável
- Citar legislação/norma quando relevante (CLT rural, IN MAPA, IN RFB, Lei 9.393/ITR, SNCR, SIGEF, etc.)

**Entidades de Dados:** Tabela completa com TODOS os campos relevantes, tipo de dado real (Decimal, String(50), Boolean, etc.), e relacionamentos

**Integrações:** APIs/sistemas externos reais (SIGEF, SNCR, Receita Federal, SISBOV, MAPA, EMBRAPA, etc.)

**Fluxo de Uso:** 6-10 passos do ponto de vista da persona principal, com decisões e variações

**Casos Extremos:** 5-8 situações reais problemáticas que o sistema deve tratar

**Critérios de Aceite:** 8-12 checkboxes mensuráveis e testáveis

**Sugestões Futuras:** 4-6 evoluções realistas para versões futuras

## Arquivos para enriquecer

Leia cada arquivo, depois reescreva-o com o conteúdo enriquecido mantendo o frontmatter e a estrutura de seções.

### CORE (prioridade máxima — é pré-requisito de tudo):

1. `/opt/lampp/htdocs/farm/docs/contexts/core/_overview.md`
   Foco: visão completa da plataforma, modelo de dados central, relacionamentos entre submódulos,
   fluxo de onboarding de um novo tenant do zero

2. `/opt/lampp/htdocs/farm/docs/contexts/core/identidade-acesso.md`
   Foco: JWT com claims tenant_id + account_id, perfis por fazenda (FazendaUsuario.perfil_fazenda_id),
   is_owner bypass, convites por e-mail, 2FA TOTP, sessões ativas, auditoria de login,
   revogação de acesso de funcionário demitido (dor real e urgente)

3. `/opt/lampp/htdocs/farm/docs/contexts/core/cadastro-propriedade.md`
   Foco: cadastro de fazenda com NIRF, matrícula, módulos fiscais, geolocalização,
   upload de shapefile/KML dos talhões, CAR vinculado, coordenadas GPS de sede,
   área total vs área produtiva vs APP vs Reserva Legal

4. `/opt/lampp/htdocs/farm/docs/contexts/core/multipropriedade.md`
   Foco: produtor com 5 fazendas em estados diferentes, grupos de fazendas,
   consolidação de indicadores cross-fazenda, permissões isoladas por propriedade,
   troca de contexto no frontend sem novo login

5. `/opt/lampp/htdocs/farm/docs/contexts/core/configuracoes-globais.md`
   Foco: SMTP para notificações, fuso horário por fazenda (Mato Grosso vs São Paulo),
   moeda/unidades (ha, alqueire paulista, alqueire mineiro, hectare),
   módulos contratados (feature gates), logotipo do tenant, dados fiscais (CNPJ/CPF, IE)

6. `/opt/lampp/htdocs/farm/docs/contexts/core/notificacoes-alertas.md`
   Foco: alertas de vencimento (documentos, seguros, contratos), alertas meteorológicos,
   notificações push mobile para operador de campo, e-mail digest semanal para proprietário,
   webhook para integração com WhatsApp Business

7. `/opt/lampp/htdocs/farm/docs/contexts/core/integracoes-essenciais.md`
   Foco: Stripe + Asaas para billing, SMTP transacional (SendGrid/SES),
   armazenamento de arquivos (S3/MinIO), mapas (MapLibre + tiles IBGE),
   SIGEF/SNCR para validação de imóveis

8. `/opt/lampp/htdocs/farm/docs/contexts/core/planos-assinatura.md`
   Foco: tiers Essencial/Profissional/Enterprise, limites por plano (nº fazendas, nº usuários, storage),
   feature flags por módulo, trial 14 dias, downgrade com dados preservados,
   billing mensal vs anual com desconto

### IMÓVEIS RURAIS:

9. `/opt/lampp/htdocs/farm/docs/contexts/imoveis/_overview.md`
   Foco: visão geral de gestão patrimonial rural — ITR, CCIR, CAR, arrendamentos,
   avaliação patrimonial, múltiplas matrículas por fazenda

10. `/opt/lampp/htdocs/farm/docs/contexts/imoveis/essencial/cadastro-imovel.md`
    Foco: NIRF (obrigatório pela RFB), CCIR (INCRA), matrícula no cartório,
    área total vs área tributável vs área de preservação, módulos fiscais do ITR (IN RFB 1.902/2019),
    localização por município/estado/CEP rural

11. `/opt/lampp/htdocs/farm/docs/contexts/imoveis/essencial/documentos-legais.md`
    Foco: vencimento do CCIR (anual, multa de 10% ao mês), ITR (agosto de cada ano),
    CAR sem prazo mas obrigatório para crédito rural, escritura vs contrato de compra e venda,
    certidão de regularidade ambiental, SIGEF para georreferenciamento

12. `/opt/lampp/htdocs/farm/docs/contexts/imoveis/profissional/arrendamentos.md`
    Foco: Lei 4.504/64 (Estatuto da Terra) — arrendamento mínimo 3 anos,
    valor máximo 15% do valor cadastral do imóvel por ano,
    contrato deve ser registrado em cartório para validade plena,
    integração com financeiro para lançamentos automáticos de receita/despesa

Use a ferramenta Write para reescrever cada arquivo. Mantenha o frontmatter YAML original,
atualizando apenas os campos que precisarem de correção. Reescreva TODO o conteúdo abaixo do frontmatter.
```
