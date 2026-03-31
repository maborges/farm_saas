# AgroSaaS - API Reference

**Versão:** 1.0.0  
**Última Atualização:** 2026-03-31  
**Status:** Ativo  

---

## 📋 Índice

1. [Visão Geral](#1-visão-geral)
2. [Autenticação](#2-autenticação)
3. [Core API](#3-core-api)
4. [Módulo Agrícola](#4-módulo-agrícola)
5. [Módulo Pecuária](#5-módulo-pecuária)
6. [Módulo Financeiro](#6-módulo-financeiro)
7. [Módulo Operacional](#7-módulo-operacional)
8. [Módulo RH](#8-módulo-rh)
9. [Cadastros](#9-cadastros)
10. [Backoffice](#10-backoffice)

---

## 1. Visão Geral

### Base URL

- **Development:** `http://localhost:8000/api/v1`
- **Production:** `https://api.agrosaas.com.br/api/v1`
- **Health Check:** `http://localhost:8000/health`

### Headers Obrigatórios

```http
Authorization: Bearer <JWT_TOKEN>
X-Tenant-ID: <UUID>
Content-Type: application/json
```

### Respostas Padrão

**Sucesso (200/201):**
```json
{
  "data": { /* dados */ },
  "total": 100,
  "pagina": 1,
  "por_pagina": 50
}
```

**Erro (4xx/5xx):**
```json
{
  "detail": "Mensagem de erro",
  "code": "ERROR_CODE"
}
```

### Códigos de Status HTTP

| Status | Descrição |
|--------|-----------|
| 200 | Sucesso |
| 201 | Criado |
| 400 | Bad Request |
| 401 | Não autorizado |
| 403 | Proibido (tenant violation, module not contracted) |
| 404 | Não encontrado |
| 422 | Erro de validação |
| 500 | Erro interno |

---

## 2. Autenticação

### Login

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "usuario@fazenda.com",
  "senha": "senha123"
}
```

**Resposta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "id": "uuid",
    "email": "usuario@fazenda.com",
    "nome": "Nome do Usuário"
  },
  "tenants": [
    {
      "id": "uuid",
      "nome": "Fazenda Santa Bárbara",
      "role": "admin"
    }
  ]
}
```

### Register

```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "usuario@fazenda.com",
  "senha": "senha123",
  "nome": "Nome do Usuário",
  "cpf": "123.456.789-00",
  "telefone": "(11) 99999-9999"
}
```

### Refresh Token

```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

### Logout

```http
POST /api/v1/auth/logout
Authorization: Bearer <token>
```

---

## 3. Core API

### Tenants

#### Listar Meus Tenants
```http
GET /api/v1/tenants
Authorization: Bearer <token>
```

#### Selecionar Tenant Ativo
```http
POST /api/v1/tenants/{tenant_id}/select
Authorization: Bearer <token>
```

### Fazendas

#### Listar Fazendas do Tenant
```http
GET /api/v1/fazendas
Authorization: Bearer <token>
```

#### Criar Fazenda
```http
POST /api/v1/fazendas
Authorization: Bearer <token>
Content-Type: application/json

{
  "nome": "Fazenda Santa Bárbara",
  "codigo_car": "SP1234567890",
  "area_total_ha": 1500.50,
  "geometria": {
    "type": "Polygon",
    "coordinates": [...]
  }
}
```

#### Atualizar Fazenda
```http
PATCH /api/v1/fazendas/{fazenda_id}
Authorization: Bearer <token>
```

### Grupos de Fazendas

#### Listar Grupos
```http
GET /api/v1/grupos-fazendas
Authorization: Bearer <token>
```

#### Criar Grupo
```http
POST /api/v1/grupos-fazendas
Authorization: Bearer <token>
Content-Type: application/json

{
  "nome": "Grupo Norte",
  "fazendas_ids": ["uuid1", "uuid2"]
}
```

### Team e Convites

#### Listar Membros do Tenant
```http
GET /api/v1/team/members
Authorization: Bearer <token>
```

#### Enviar Convite
```http
POST /api/v1/team/invites
Authorization: Bearer <token>
Content-Type: application/json

{
  "email": "novo@fazenda.com",
  "perfil_id": "uuid",
  "fazenda_id": "uuid" // opcional
}
```

#### Aceitar Convite
```http
POST /api/v1/team/invites/{token}/aceitar
Content-Type: application/json

{
  "senha": "nova_senha123"
}
```

### Billing e Assinaturas

#### Minha Assinatura
```http
GET /api/v1/billing/subscription
Authorization: Bearer <token>
```

#### Faturas
```http
GET /api/v1/billing/invoices
Authorization: Bearer <token>
```

#### Solicitar Mudança de Plano
```http
POST /api/v1/plan-changes/request
Authorization: Bearer <token>
Content-Type: application/json

{
  "plano_id": "uuid",
  "modulos_adicionais": ["A1_PLANEJAMENTO", "O2_ESTOQUE"]
}
```

#### Validar Cupom
```http
POST /api/v1/cupons/validate
Authorization: Bearer <token>
Content-Type: application/json

{
  "codigo": "DESCONTO10"
}
```

---

## 4. Módulo Agrícola

### Safras

#### Listar Safras
```http
GET /api/v1/agricola/planejamento/safras?cultura=Soja&status=ATIVA
Authorization: Bearer <token>
```

#### Criar Safra
```http
POST /api/v1/agricola/planejamento/safras
Authorization: Bearer <token>
Content-Type: application/json

{
  "nome": "Soja 2025/26",
  "cultura": "Soja",
  "variedade": "NS 5909",
  "ciclo": "PRINCIPAL",
  "data_inicio": "2025-10-01",
  "data_fim_prevista": "2026-03-31",
  "hectares_planejados": 500.00,
  "produtividade_meta_sc_ha": 65.0
}
```

#### Atualizar Safra
```http
PATCH /api/v1/agricola/planejamento/safras/{safra_id}
Authorization: Bearer <token>
```

#### Avançar Fase da Safra
```http
POST /api/v1/agricola/planejamento/safras/{safra_id}/avancar-fase/PREPARO_SOLO
Authorization: Bearer <token>
```

#### Resumo da Safra
```http
GET /api/v1/agricola/planejamento/safras/{safra_id}/resumo
Authorization: Bearer <token>
```

### Talhões

#### Listar Talhões
```http
GET /api/v1/agricola/talhoes?fazenda_id=uuid
Authorization: Bearer <token>
```

#### Criar Talhão
```http
POST /api/v1/agricola/talhoes
Authorization: Bearer <token>
Content-Type: application/json

{
  "fazenda_id": "uuid",
  "nome": "Talhão 01",
  "geometria": {
    "type": "Polygon",
    "coordinates": [...]
  },
  "tipo_solo": "Latossolo Vermelho",
  "irrigado": false
}
```

### Operações de Campo

#### Listar Operações
```http
GET /api/v1/agricola/operacoes?safra_id=uuid&talhao_id=uuid
Authorization: Bearer <token>
```

#### Registrar Operação
```http
POST /api/v1/agricola/operacoes
Authorization: Bearer <token>
Content-Type: application/json

{
  "safra_id": "uuid",
  "talhao_id": "uuid",
  "tipo_operacao": "PULVERIZACAO",
  "data_operacao": "2025-11-15",
  "hora_inicio": "08:00",
  "hora_fim": "12:00",
  "maquinario_id": "uuid",
  "operador_id": "uuid",
  "area_aplicada_ha": 50.0,
  "insumos": [
    {
      "produto_id": "uuid",
      "lote_estoque_id": "uuid",
      "dose_aplicada": 0.5,
      "unidade_dose": "L/ha"
    }
  ],
  "observacoes": "Aplicação preventiva"
}
```

#### Operações por Fase
```http
GET /api/v1/agricola/operacoes/safra/{safra_id}/por-fase
Authorization: Bearer <token>
```

#### Exportar Caderno de Campo (PDF)
```http
GET /api/v1/agricola/operacoes/export/pdf?safra_id=uuid
Authorization: Bearer <token>
```

### Romaneios de Colheita

#### Listar Romaneios
```http
GET /api/v1/agricola/romaneios?safra_id=uuid
Authorization: Bearer <token>
```

#### Criar Romaneio
```http
POST /api/v1/agricola/romaneios
Authorization: Bearer <token>
Content-Type: application/json

{
  "safra_id": "uuid",
  "talhao_id": "uuid",
  "data_colheita": "2026-03-15",
  "maquinario_id": "uuid",
  "operador_id": "uuid",
  "peso_bruto_kg": 52000,
  "tara_kg": 12000,
  "umidade_pct": 13.5,
  "impureza_pct": 1.0,
  "avariados_pct": 0.5,
  "preco_saca": 120.00,
  "destino": "ARMAZEM"
}
```

#### KPIs de Colheita
```http
GET /api/v1/agricola/romaneios/kpis?safra_id=uuid
Authorization: Bearer <token>
```

### Monitoramento

#### Listar Monitoramentos
```http
GET /api/v1/agricola/monitoramentos?safra_id=uuid
Authorization: Bearer <token>
```

#### Criar Monitoramento
```http
POST /api/v1/agricola/monitoramentos
Authorization: Bearer <token>
Content-Type: application/json

{
  "safra_id": "uuid",
  "talhao_id": "uuid",
  "data_monitoramento": "2025-12-10",
  "tipo": "PRAGA",
  "catalogo_id": "uuid",
  "nivel_infestacao": "MEDIO",
  "nde_ultrapassado": false,
  "acao_tomada": "MONITORAR",
  "pontos_amostragem": 10,
  "geolocalizacao": {
    "type": "Point",
    "coordinates": [-46.6333, -23.5505]
  }
}
```

#### Diagnóstico por IA
```http
POST /api/v1/agricola/monitoramentos/diagnosticar-avulso
Authorization: Bearer <token>
Content-Type: multipart/form-data

imagem: <file>
```

### Análises de Solo

#### Listar Análises
```http
GET /api/v1/agricola/analises-solo?talhao_id=uuid
Authorization: Bearer <token>
```

#### Criar Análise
```http
POST /api/v1/agricola/analises-solo
Authorization: Bearer <token>
Content-Type: application/json

{
  "talhao_id": "uuid",
  "data_coleta": "2025-09-01",
  "laboratorio": "Lab Solo",
  "ph": 5.8,
  "materia_organica_pct": 2.5,
  "fosforo_mg_dm3": 15.0,
  "potassio_mg_dm3": 0.3,
  "recomendacoes": "Aplicar 2t/ha de calcário"
}
```

---

## 5. Módulo Pecuária

### Lotes de Animais

#### Listar Lotes
```http
GET /api/v1/pecuaria/lotes-bovinos
Authorization: Bearer <token>
```

#### Criar Lote
```http
POST /api/v1/pecuaria/lotes-bovinos
Authorization: Bearer <token>
Content-Type: application/json

{
  "nome": "Lote 01 - Engorda",
  "especie": "BOVINO",
  "categoria": "BEEF",
  "quantidade_cabecas": 100,
  "peso_medio_kg": 350.0,
  "data_entrada": "2025-06-01",
  "piquete_id": "uuid"
}
```

### Animais Individuais

#### Listar Animais
```http
GET /api/v1/pecuaria/animais?lote_id=uuid&categoria=BEEF
Authorization: Bearer <token>
```

#### Cadastrar Animal
```http
POST /api/v1/pecuaria/animais
Authorization: Bearer <token>
Content-Type: application/json

{
  "numero_brinco": "BR123456",
  "especie": "BOVINO",
  "raca": "Nelore",
  "sexo": "FEMEA",
  "categoria": "MATRIZ",
  "data_nascimento": "2023-05-15",
  "pai_id": "uuid",
  "mae_id": "uuid"
}
```

### Eventos Animais

#### Listar Eventos
```http
GET /api/v1/pecuaria/manejos?animal_id=uuid&tipo=PESAGEM
Authorization: Bearer <token>
```

#### Registrar Evento
```http
POST /api/v1/pecuaria/manejos
Authorization: Bearer <token>
Content-Type: application/json

{
  "animal_id": "uuid",
  "lote_id": "uuid",
  "tipo_evento": "PESAGEM",
  "data_evento": "2025-11-20",
  "valor_numerico": 450.5,
  "observacoes": "Pesagem mensal"
}
```

### Piquetes

#### Listar Piquetes
```http
GET /api/v1/pecuaria/piquetes?fazenda_id=uuid
Authorization: Bearer <token>
```

#### Criar Piquete
```http
POST /api/v1/pecuaria/piquetes
Authorization: Bearer <token>
Content-Type: application/json

{
  "fazenda_id": "uuid",
  "nome": "Piquete 01",
  "area_ha": 25.0,
  "tipo_pastagem": "Braquiária",
  "lotacao_maxima": 50
}
```

### Produção Leiteira

#### Listar Produção
```http
GET /api/v1/pecuaria/producao-leite?animal_id=uuid&data_inicio=2025-01-01
Authorization: Bearer <token>
```

#### Registrar Produção
```http
POST /api/v1/pecuaria/producao-leite
Authorization: Bearer <token>
Content-Type: application/json

{
  "animal_id": "uuid",
  "data_ordenha": "2025-11-20",
  "turno": "MANHA",
  "volume_litros": 25.5,
  "gordura_pct": 3.8,
  "proteina_pct": 3.2,
  "ccs": 250000,
  "cbt": 100000,
  "destino": "LATICINIO",
  "preco_litro": 2.50
}
```

---

## 6. Módulo Financeiro

### Receitas

#### Listar Receitas
```http
GET /api/v1/financeiro/receitas?status=A_RECEBER&vencimento_inicio=2025-11-01
Authorization: Bearer <token>
```

#### Receitas Vencendo
```http
GET /api/v1/financeiro/receitas/vencendo?dias=30
Authorization: Bearer <token>
```

#### Criar Receita
```http
POST /api/v1/financeiro/receitas
Authorization: Bearer <token>
Content-Type: application/json

{
  "pessoa_id": "uuid",
  "descricao": "Venda de Soja",
  "valor": 120000.00,
  "data_vencimento": "2025-12-15",
  "plano_conta_id": "uuid",
  "numero_nf": "12345",
  "origem_id": "uuid",
  "origem_tipo": "ROMANEIO_COLHEITA"
}
```

#### Parcelar Receita
```http
POST /api/v1/financeiro/receitas/{receita_id}/parcelar
Authorization: Bearer <token>
Content-Type: application/json

{
  "total_parcelas": 3,
  "intervalo_dias": 30
}
```

### Despesas

#### Listar Despesas
```http
GET /api/v1/financeiro/despesas?status=A_PAGAR
Authorization: Bearer <token>
```

#### Despesas Vencendo
```http
GET /api/v1/financeiro/despesas/vencendo?dias=30
Authorization: Bearer <token>
```

#### Criar Despesa
```http
POST /api/v1/financeiro/despesas
Authorization: Bearer <token>
Content-Type: application/json

{
  "pessoa_id": "uuid",
  "descricao": "Compra de Fertilizante",
  "valor": 50000.00,
  "data_vencimento": "2025-12-10",
  "plano_conta_id": "uuid",
  "numero_nf": "67890",
  "origem_id": "uuid",
  "origem_tipo": "OPERACAO_AGRICOLA",
  "rateios": [
    {
      "safra_id": "uuid",
      "talhao_id": "uuid",
      "percentual": 60.0
    }
  ]
}
```

### Plano de Contas

#### Listar Plano de Contas
```http
GET /api/v1/financeiro/planos-conta?tipo=DESPESA
Authorization: Bearer <token>
```

#### Criar Conta
```http
POST /api/v1/financeiro/planos-conta
Authorization: Bearer <token>
Content-Type: application/json

{
  "parent_id": "uuid",
  "nome": "Defensivos",
  "codigo": "3.1.02",
  "natureza": "ANALITICA",
  "tipo": "DESPESA",
  "categoria_rfb": "CUSTEIO"
}
```

### Rateios

#### Criar Rateio
```http
POST /api/v1/financeiro/rateios
Authorization: Bearer <token>
Content-Type: application/json

{
  "despesa_id": "uuid",
  "safra_id": "uuid",
  "talhao_id": "uuid",
  "valor_rateado": 30000.00,
  "percentual": 60.0,
  "tipo_centro_custo": "SAFRA"
}
```

### Relatórios

#### Balancete
```http
GET /api/v1/financeiro/relatorios/balancete?mes=11&ano=2025
Authorization: Bearer <token>
```

#### DRE
```http
GET /api/v1/financeiro/relatorios/dre?inicio=2025-01-01&fim=2025-12-31
Authorization: Bearer <token>
```

#### Fluxo de Caixa
```http
GET /api/v1/financeiro/relatorios/fluxo-caixa?mes=11&ano=2025
Authorization: Bearer <token>
```

---

## 7. Módulo Operacional

### Frota

#### Listar Equipamentos
```http
GET /api/v1/operacional/frota?tipo=TRATOR
Authorization: Bearer <token>
```

#### Cadastrar Equipamento
```http
POST /api/v1/operacional/frota
Authorization: Bearer <token>
Content-Type: application/json

{
  "nome": "Trator John Deere 7260",
  "tipo": "TRATOR",
  "marca_id": "uuid",
  "modelo_id": "uuid",
  "ano_fabricacao": 2020,
  "numero_serie": "JD7260123456",
  "horimetro_atual": 1500.5
}
```

#### Planos de Manutenção
```http
POST /api/v1/operacional/frota/planos
Authorization: Bearer <token>
Content-Type: application/json

{
  "equipamento_id": "uuid",
  "nome": "Revisão 500h",
  "tipo": "PREVENTIVA",
  "frequencia_horas": 500,
  "descricao_servico": "Troca de óleo e filtros"
}
```

#### Ordens de Serviço
```http
POST /api/v1/operacional/frota/os
Authorization: Bearer <token>
Content-Type: application/json

{
  "equipamento_id": "uuid",
  "tipo": "CORRETIVA",
  "descricao_problema": "Vazamento de óleo",
  "data_abertura": "2025-11-20"
}
```

#### Adicionar Itens à OS
```http
POST /api/v1/operacional/frota/os/{os_id}/itens
Authorization: Bearer <token>
Content-Type: application/json

{
  "produto_id": "uuid",
  "lote_estoque_id": "uuid",
  "quantidade": 2,
  "custo_unitario": 150.00
}
```

### Estoque

#### Listar Depósitos
```http
GET /api/v1/operacional/estoque/depositos
Authorization: Bearer <token>
```

#### Criar Depósito
```http
POST /api/v1/operacional/estoque/depositos
Authorization: Bearer <token>
Content-Type: application/json

{
  "nome": "Armazém Central",
  "tipo": "GERAL",
  "endereco": "Rodovia BR-123, km 50",
  "responsavel_id": "uuid"
}
```

#### Saldos de Estoque
```http
GET /api/v1/operacional/estoque/saldos?deposito_id=uuid
Authorization: Bearer <token>
```

#### Alertas de Estoque
```http
GET /api/v1/operacional/estoque/alertas
Authorization: Bearer <token>
```

#### Movimentações

**Entrada:**
```http
POST /api/v1/operacional/estoque/movimentacoes/entrada
Authorization: Bearer <token>
Content-Type: application/json

{
  "produto_id": "uuid",
  "lote_id": "uuid",
  "deposito_id": "uuid",
  "quantidade": 1000,
  "unidade": "L",
  "data_movimentacao": "2025-11-20",
  "origem_id": "uuid",
  "origem_tipo": "PEDIDO_COMPRA"
}
```

**Saída:**
```http
POST /api/v1/operacional/estoque/movimentacoes/saida
Authorization: Bearer <token>
```

**Transferência:**
```http
POST /api/v1/operacional/estoque/movimentacoes/transferencia
Authorization: Bearer <token>
```

#### Requisições de Material

**Criar Requisição:**
```http
POST /api/v1/operacional/estoque/requisicoes
Authorization: Bearer <token>
Content-Type: application/json

{
  "deposito_id": "uuid",
  "itens": [
    {
      "produto_id": "uuid",
      "quantidade": 50
    }
  ],
  "observacoes": "Para manutenção"
}
```

**Aprovar Requisição:**
```http
PATCH /api/v1/operacional/estoque/requisicoes/{id}/aprovar
Authorization: Bearer <token>
```

#### Reservas de Estoque

**Criar Reserva:**
```http
POST /api/v1/operacional/estoque/reservas
Authorization: Bearer <token>
Content-Type: application/json

{
  "produto_id": "uuid",
  "deposito_id": "uuid",
  "quantidade": 100,
  "referencia_id": "uuid",
  "referencia_tipo": "ORDEM_SERVICO",
  "data_validade": "2025-12-31"
}
```

### Compras

#### Pedidos de Compra

**Criar Pedido:**
```http
POST /api/v1/operacional/pedidos-compra
Authorization: Bearer <token>
Content-Type: application/json

{
  "fornecedor_id": "uuid",
  "itens": [
    {
      "produto_id": "uuid",
      "quantidade": 500,
      "preco_unitario": 25.00
    }
  ],
  "data_entrega_prevista": "2025-12-15"
}
```

**Adicionar Cotação:**
```http
PATCH /api/v1/operacional/pedidos-compra/{id}/cotacao
Authorization: Bearer <token>
```

**Aprovar Pedido:**
```http
PATCH /api/v1/operacional/pedidos-compra/{id}/aprovar
Authorization: Bearer <token>
```

**Receber Pedido:**
```http
POST /api/v1/operacional/pedidos-compra/{id}/receber
Authorization: Bearer <token>
```

---

## 8. Módulo RH

### Colaboradores

#### Listar Colaboradores
```http
GET /api/v1/rh/colaboradores?ativo=true
Authorization: Bearer <token>
```

#### Cadastrar Colaborador
```http
POST /api/v1/rh/colaboradores
Authorization: Bearer <token>
Content-Type: application/json

{
  "pessoa_id": "uuid",
  "departamento_id": "uuid",
  "cargo": "Tratorista",
  "data_admissao": "2025-01-15",
  "salario_base": 2500.00,
  "tipo_contrato": "FIXO"
}
```

### Diárias

#### Lançar Diárias
```http
POST /api/v1/rh/diarias
Authorization: Bearer <token>
Content-Type: application/json

{
  "colaborador_id": "uuid",
  "data": "2025-11-20",
  "valor_diaria": 150.00,
  "quantidade": 2,
  "motivo": "Viagem para campo"
}
```

### Empreitadas

#### Criar Empreitada
```http
POST /api/v1/rh/empreitadas
Authorization: Bearer <token>
Content-Type: application/json

{
  "colaborador_id": "uuid",
  "descricao": "Limpeza de área 50ha",
  "valor_total": 5000.00,
  "data_inicio": "2025-11-01",
  "data_fim": "2025-11-30"
}
```

---

## 9. Cadastros

### Pessoas

#### Listar Pessoas
```http
GET /api/v1/cadastros/pessoas?categoria=FORNECEDOR
Authorization: Bearer <token>
```

#### Criar Pessoa
```http
POST /api/v1/cadastros/pessoas
Authorization: Bearer <token>
Content-Type: application/json

{
  "nome": "Fornecedor ABC",
  "tipo": "PESSOA_JURIDICA",
  "cpf_cnpj": "12.345.678/0001-90",
  "email": "contato@abc.com",
  "telefone": "(11) 99999-9999",
  "categoria": "FORNECEDOR",
  "enderecos": [...],
  "contatos": [...]
}
```

### Produtos

#### Listar Produtos
```http
GET /api/v1/cadastros/produtos?tipo=DEFENSIVO
Authorization: Bearer <token>
```

#### Criar Produto
```http
POST /api/v1/cadastros/produtos
Authorization: Bearer <token>
Content-Type: application/json

{
  "nome": "Herbicida Roundup",
  "descricao": "Glifosato 480g/L",
  "categoria_id": "uuid",
  "tipo": "DEFENSIVO",
  "unidade": "L",
  "custo_medio": 45.00,
  "estoque_minimo": 100
}
```

### Equipamentos

#### Listar Equipamentos
```http
GET /api/v1/cadastros/equipamentos
Authorization: Bearer <token>
```

### Commodities

#### Listar Commodities
```http
GET /api/v1/cadastros/commodities
Authorization: Bearer <token>
```

---

## 10. Backoffice

### Dashboard Executivo

```http
GET /api/v1/backoffice/dashboard
Authorization: Bearer <token>
X-Admin-Role: super_admin
```

### Business Intelligence

```http
GET /api/v1/backoffice/bi/metrics
Authorization: Bearer <token>
```

### Gestão de Tenants

#### Listar Tenants
```http
GET /api/v1/backoffice/tenants?status=ATIVO&pagina=1
Authorization: Bearer <token>
```

#### Atualizar Tenant
```http
PATCH /api/v1/backoffice/tenants/{tenant_id}
Authorization: Bearer <token>
```

#### Bloquear/Desbloquear Tenant
```http
POST /api/v1/backoffice/tenants/{tenant_id}/toggle-status
Authorization: Bearer <token>
```

### Planos e Assinaturas

#### Listar Planos
```http
GET /api/v1/backoffice/plans
Authorization: Bearer <token>
```

#### Criar Plano
```http
POST /api/v1/backoffice/plans
Authorization: Bearer <token>
Content-Type: application/json

{
  "nome": "Plano Premium",
  "preco_mensal": 999.00,
  "modulos_inclusos": ["A1_PLANEJAMENTO", "F1_TESOURARIA"],
  "tier": "PREMIUM"
}
```

### CRM

#### Listar Leads
```http
GET /api/v1/backoffice/crm/leads?estagio=QUALIFICADO
Authorization: Bearer <token>
```

#### Criar Lead
```http
POST /api/v1/backoffice/crm/leads
Authorization: Bearer <token>
```

#### Criar Oferta
```http
POST /api/v1/backoffice/crm/ofertas
Authorization: Bearer <token>
Content-Type: application/json

{
  "lead_id": "uuid",
  "plano_id": "uuid",
  "modulos_sugeridos": ["A1_PLANEJAMENTO", "O2_ESTOQUE"],
  "valor_total": 1500.00,
  "desconto_pct": 10.0,
  "validade": "2025-12-31"
}
```

### Suporte

#### Listar Chamados
```http
GET /api/v1/backoffice/support/tickets?status=ABERTO
Authorization: Bearer <token>
```

#### Criar Chamado
```http
POST /api/v1/backoffice/support/tickets
Authorization: Bearer <token>
```

### Knowledge Base

#### Listar Artigos
```http
GET /api/v1/backoffice/kb/articles?categoria=AGRICOLA
Authorization: Bearer <token>
```

#### Criar Artigo
```http
POST /api/v1/backoffice/kb/articles
Authorization: Bearer <token>
Content-Type: application/json

{
  "titulo": "Como criar uma safra",
  "conteudo": "# Passo a passo...",
  "categoria": "AGRICOLA",
  "visivel_tenant": true
}
```

### Audit Log

#### Listar Logs de Auditoria
```http
GET /api/v1/backoffice/audit?admin_user_id=uuid&recurso=tenants
Authorization: Bearer <token>
```

---

## Referências Cruzadas

| Documento | Descrição |
|-----------|-----------|
| `docs/qwen/01-arquitetura.md` | Arquitetura geral |
| `docs/qwen/02-modulos.md` | Módulos do sistema |
| `docs/qwen/03-banco-dados.md` | Schema do banco |
| `docs/qwen/06-permissoes.md` | Permissões e RBAC |

---

## Changelog

| Data | Versão | Descrição |
|------|--------|-----------|
| 2026-03-31 | 1.0.0 | Documentação inicial completa |
