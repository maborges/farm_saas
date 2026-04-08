# Configurações Globais — Guia de Implementação

## Visão Geral

O módulo de **Configurações Globais** centraliza todas as configurações transversais do tenant, garantindo consistência em todos os módulos da plataforma.

---

## 🎯 Funcionalidades Implementadas

### 1. **Conversão de Unidades de Área**

Converte automaticamente entre:
- Hectare (HA)
- Alqueire Paulista (2,42 ha)
- Alqueire Mineiro (4,84 ha)
- Alqueire do Norte (2,7225 ha)
- Acre (0,4047 ha)

### 2. **Ano Agrícola**

Define o período do ano agrícola (ex: julho a junho) para todas as safras.

### 3. **Moeda e Fuso Horário**

Configura moeda padrão (BRL) e fuso horário do tenant.

### 4. **Categorias Customizáveis**

Permite criar, editar e remover categorias para:
- Despesas
- Receitas
- Operações agrícolas
- Produtos/insumos

### 5. **Wizard de Onboarding**

API para configuração inicial durante o onboarding do tenant.

---

## 📡 Endpoints

### 1. Obter Configurações Gerais

```http
GET /api/v1/config/geral
Authorization: Bearer <token>
```

**Retorno:**
```json
{
  "ano_agricola": {
    "mes_inicio": 7,
    "mes_fim": 6
  },
  "unidade_area": "HA",
  "moeda": "BRL",
  "fuso_horario": "America/Sao_Paulo",
  "idioma": "pt-BR"
}
```

---

### 2. Atualizar Configurações Gerais

```http
PATCH /api/v1/config/geral
Authorization: Bearer <token>
Content-Type: application/json

{
  "ano_agricola_inicio": 7,
  "ano_agricola_fim": 6,
  "unidade_area": "ALQUEIRE_PAULISTA",
  "moeda": "BRL",
  "fuso_horario": "America/Sao_Paulo"
}
```

---

### 3. Listar Unidades de Área

```http
GET /api/v1/config/unidades-area
Authorization: Bearer <token>
```

**Retorno:**
```json
[
  {"codigo": "HA", "nome": "Hectare"},
  {"codigo": "ALQUEIRE_PAULISTA", "nome": "Alqueire Paulista"},
  {"codigo": "ALQUEIRE_MINEIRO", "nome": "Alqueire Mineiro"},
  {"codigo": "ALQUEIRE_NORTE", "nome": "Alqueire do Norte"},
  {"codigo": "ACRE", "nome": "Acre"}
]
```

---

### 4. Converter Área

```http
POST /api/v1/config/converter-area
Authorization: Bearer <token>
Content-Type: application/json

{
  "valor": 100,
  "unidade_origem": "ALQUEIRE_PAULISTA",
  "unidade_destino": "HA"
}
```

**Retorno:**
```json
{
  "valor_original": 100,
  "unidade_origem": "ALQUEIRE_PAULISTA",
  "valor_convertido": 242.0,
  "unidade_destino": "HA"
}
```

---

### 5. Listar Categorias

```http
GET /api/v1/config/categorias/{tipo}
Authorization: Bearer <token>
```

**Parâmetros:**
- `tipo`: `despesa`, `receita`, `operacao`, `produto`

**Retorno:**
```json
{
  "tipo": "despesa",
  "categorias": [
    {
      "id": "uuid",
      "nome": "Insumos",
      "parent_id": "uuid-pai",
      "ativa": true,
      "metadata": {}
    }
  ],
  "total": 5
}
```

---

### 6. Criar Categoria

```http
POST /api/v1/config/categorias
Authorization: Bearer <token>
Content-Type: application/json

{
  "tipo": "despesa",
  "nome": "Combustível",
  "parent_id": "uuid-da-categoria-pai",
  "metadata": {"icone": "fuel"}
}
```

---

### 7. Atualizar Categoria

```http
PATCH /api/v1/config/categorias/{categoria_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "nome": "Novo Nome",
  "metadata": {"icone": "new-icon"}
}
```

---

### 8. Remover Categoria

```http
DELETE /api/v1/config/categorias/{categoria_id}
Authorization: Bearer <token>
```

**Nota:** Categorias do sistema (prefixo `sys_`) não podem ser removidas.

---

### 9. Wizard de Onboarding

```http
POST /api/v1/config/onboarding/configurar
Authorization: Bearer <token>
Content-Type: application/json

{
  "ano_agricola_inicio": 7,
  "ano_agricola_fim": 6,
  "unidade_area": "HA",
  "moeda": "BRL",
  "fuso_horario": "America/Sao_Paulo",
  "aceitar_categorias_padrao": true
}
```

**Retorno:**
```json
{
  "message": "Configuração inicial concluída com sucesso",
  "proximo_passo": "/dashboard"
}
```

---

## 🧪 Testes Manuais

### Testar Conversão de Unidades

```bash
# Converter 100 alqueires paulistas para hectares
curl -X POST http://localhost:8000/api/v1/config/converter-area \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "valor": 100,
    "unidade_origem": "ALQUEIRE_PAULISTA",
    "unidade_destino": "HA"
  }'
```

### Testar Categorias

```bash
# Listar categorias de despesa
curl -X GET http://localhost:8000/api/v1/config/categorias/despesa \
  -H "Authorization: Bearer SEU_TOKEN"

# Criar nova categoria
curl -X POST http://localhost:8000/api/v1/config/categorias \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tipo": "despesa",
    "nome": "Energia Elétrica",
    "parent_id": null,
    "metadata": {"icone": "energy"}
  }'
```

### Testar Onboarding

```bash
curl -X POST http://localhost:8000/api/v1/config/onboarding/configurar \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ano_agricola_inicio": 7,
    "ano_agricola_fim": 6,
    "unidade_area": "HA",
    "moeda": "BRL",
    "fuso_horario": "America/Sao_Paulo",
    "aceitar_categorias_padrao": true
  }'
```

---

## 📊 Estrutura de Dados

### Armazenamento

As configurações são armazenadas em `configuracoes_tenant`:

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | Identificador único |
| `tenant_id` | UUID | Isolamento multi-tenant |
| `categoria` | String(30) | Categoria (ex: `unidades`, `ano_agricola`) |
| `chave` | String(50) | Chave da configuração (ex: `area_padrao`) |
| `valor` | JSON | Valor flexível (string, número, objeto, array) |
| `descricao` | String(255) | Descrição opcional |
| `ativo` | Boolean | Status da configuração |

### Categorias Padrão

O sistema inclui categorias padrão (prefixo `sys_`):

```python
CATEGORIAS_PADRAO = {
    "despesa": [
        {"id": "sys_despesas_operacionais", "nome": "Despesas Operacionais"},
        {"id": "sys_insumos", "nome": "Insumos"},
        {"id": "sys_mao_de_obra", "nome": "Mão de Obra"},
    ],
    "receita": [...],
    "operacao": [...],
    "produto": [...],
}
```

---

## 🔒 Segurança

### Isolamento Multi-Tenant

- ✅ Todas as queries filtram por `tenant_id`
- ✅ Categorias de um tenant não vazam para outro
- ✅ Configurações são específicas por tenant

### Permissões

| Endpoint | Permissão |
|----------|-----------|
| `GET /config/geral` | Tenant usuário |
| `PATCH /config/geral` | Tenant admin |
| `GET /config/categorias/*` | Tenant usuário |
| `POST /config/categorias` | Tenant admin |
| `DELETE /config/categorias/*` | Tenant admin |
| `POST /config/onboarding/*` | Tenant admin |

---

## 🎯 Casos de Uso

### Caso 1: Exibir Área em Unidade do Tenant

```python
# Backend
from core.services.configuracoes_service import ConfiguracoesService

async def get_fazenda_area(fazenda_id: UUID, tenant_id: UUID, session):
    svc = ConfiguracoesService(session, tenant_id)
    
    # Área sempre armazenada em hectares no banco
    fazenda = await get_fazenda(fazenda_id)
    area_ha = fazenda.area_total_ha
    
    # Converter para unidade do tenant
    unidade = await svc.get_unidade_area_padrao()
    area_convertida = await svc.converter_area(area_ha, "HA", unidade)
    
    return {
        "valor": area_convertida,
        "unidade": unidade,
    }
```

### Caso 2: Filtrar Despesas por Categoria

```typescript
// Frontend
const { data: categorias } = useQuery({
  queryKey: ['categorias', 'despesa'],
  queryFn: async () => {
    const res = await fetch('/api/v1/config/categorias/despesa')
    return res.json()
  }
})

// Usar no filtro de despesas
const despesasFiltradas = despesas.filter(d => 
  categorias.categorias.some(c => c.id === d.categoria_id)
)
```

---

## 📝 Próximos Passos

### Melhorias Futuras:
1. [ ] Adicionar mais unidades (alqueire baiano, tarefa, etc.)
2. [ ] Categorias com ícones customizados
3. [ ] Exportar/importar configurações entre tenants
4. [ ] Histórico de alterações de configurações
5. [ ] Validação de categorias em uso antes de remover

---

## 🔗 Links Relacionados

- [Especificação Funcional](docs/contexts/core/configuracoes-globais.md)
- [Service Implementation](services/api/core/services/configuracoes_service.py)
- [Router Implementation](services/api/core/routers/configuration.py)
- [Schemas](services/api/core/schemas/config_schemas.py)

---

**Documento gerado em:** 2026-04-01  
**Responsável:** Tech Lead  
**Status:** ✅ Implementado e funcional
