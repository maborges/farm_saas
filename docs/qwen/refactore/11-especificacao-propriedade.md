# Especificação Técnica — Propriedade + Exploração Rural (Frente C)

**Data:** 2026-04-06
**Base conceitual:** `docs/architecture/conceituacao-propriedade.md`

---

## 1. Visão Geral

A Frente C redefine a relação entre **quem produz** (Propriedade) e **onde produz** (Fazenda), introduzindo um vínculo temporal e contratual (`ExploracaoRural`).

```
ANTES (modelo atual):
  Tenant → GrupoFazendas → Fazenda

DEPOIS (modelo novo):
  Tenant → Propriedade → ExploracaoRural → Fazenda
```

### O que muda

| Aspecto | Antes | Depois |
|---------|-------|--------|
| Unidade econômica | `GrupoFazendas` (só nome + visual) | `Propriedade` (CNPJ, IE, regime tributário, email, telefone) |
| Vínculo com Fazenda | Direto (`Fazenda.grupo_id`) | Via `ExploracaoRural` (natureza, vigência, documentos) |
| Temporalidade | Sem controle de tempo | `data_inicio` / `data_fim` no vínculo |
| Natureza jurídica | Não existia | `propria`, `arrendamento`, `parceria`, `comodato`, `posse` |
| Documentos | Fora do escopo | `DocumentoExploracao` com validade e storage |

---

## 2. Modelos

### 2.1 `Propriedade` (substitui `GrupoFazendas`)

**Arquivo novo:** `core/cadastros/propriedades/propriedade_models.py`
**Tabela:** `cadastros_propriedades`

| Coluna | Tipo | Obrigatório | Descrição |
|--------|------|:-----------:|-----------|
| `id` | UUID | ✅ | PK |
| `tenant_id` | UUID | ✅ | FK → tenants |
| `nome` | String(200) | ✅ | Nome fantasia / razão social do explorador |
| `cpf_cnpj` | String(18) | ❌ | CPF ou CNPJ do proprietário/explorador |
| `inscricao_estadual` | String(50) | ❌ | IE |
| `ie_isento` | Boolean | ✅ | Default: False |
| `email` | String(200) | ❌ | |
| `telefone` | String(30) | ❌ | |
| `nome_fantasia` | String(200) | ❌ | |
| `regime_tributario` | String(30) | ❌ | SIMPLES, PRESUMIDO, REAL, ISENTO |
| `cor` | String(7) | ❌ | Cor HEX para UI |
| `icone` | String(50) | ❌ | Ícone para UI |
| `ordem` | Integer | ✅ | Default: 0 |
| `ativo` | Boolean | ✅ | Default: True |
| `observacoes` | Text | ❌ | |
| `created_at` | DateTime | ✅ | |
| `updated_at` | DateTime | ✅ | |

### 2.2 `ExploracaoRural` (nova — vínculo intermediário)

**Arquivo novo:** `core/cadastros/propriedades/propriedade_models.py`
**Tabela:** `cadastros_exploracoes_rurais`

| Coluna | Tipo | Obrigatório | Descrição |
|--------|------|:-----------:|-----------|
| `id` | UUID | ✅ | PK |
| `tenant_id` | UUID | ✅ | FK → tenants |
| `propriedade_id` | UUID | ✅ | FK → cadastros_propriedades |
| `fazenda_id` | UUID | ✅ | FK → fazendas |
| `natureza` | String(30) | ✅ | Enum: propria, arrendamento, parceria, comodato, posse |
| `data_inicio` | Date | ✅ | Início do direito de exploração |
| `data_fim` | Date | ❌ | NULL = vigente |
| `numero_contrato` | String(100) | ❌ | |
| `valor_anual` | Float | ❌ | R$ — valor do arrendamento/parceria |
| `percentual_producao` | Float | ❌ | % para o proprietário (parceria) |
| `area_explorada_ha` | Float | ❌ | Pode ser < área total da fazenda |
| `documento_s3_key` | String(512) | ❌ | Contrato digitalizado |
| `documento_tipo` | String(20) | ❌ | pdf, jpg, docx |
| `ativo` | Boolean | ✅ | Default: True |
| `observacoes` | Text | ❌ | |
| `created_at` | DateTime | ✅ | |
| `updated_at` | DateTime | ✅ | |

### 2.3 `DocumentoExploracao` (nova — controle documental)

**Arquivo novo:** `core/cadastros/propriedades/propriedade_models.py`
**Tabela:** `cadastros_documentos_exploracao`

| Coluna | Tipo | Obrigatório | Descrição |
|--------|------|:-----------:|-----------|
| `id` | UUID | ✅ | PK |
| `tenant_id` | UUID | ✅ | FK → tenants |
| `exploracao_id` | UUID | ✅ | FK → cadastros_exploracoes_rurais |
| `tipo` | String(50) | ✅ | Enum: contrato_arrendamento, contrato_parceria, escritura, matricula, ccir, itr, car, outro |
| `nome_arquivo` | String(255) | ✅ | |
| `storage_path` | String(512) | ✅ | S3 key ou caminho local |
| `storage_backend` | String(10) | ✅ | Default: "local" |
| `tamanho_bytes` | Integer | ✅ | |
| `mime_type` | String(100) | ❌ | |
| `data_emissao` | Date | ❌ | |
| `data_validade` | Date | ❌ | NULL = sem vencimento |
| `numero_documento` | String(100) | ❌ | |
| `orgao_expedidor` | String(100) | ❌ | |
| `observacoes` | Text | ❌ | |
| `ativo` | Boolean | ✅ | Default: True |
| `created_at` | DateTime | ✅ | |

---

## 3. Migração de `GrupoFazendas` → `Propriedade`

### 3.1. Estratégia

**Não deletar** `GrupoFazendas` imediatamente. Criar `Propriedade` em paralelo e fazer **migração gradual**:

```sql
-- Migration 1: Criar tabelas novas (sem alterar existentes)
-- Migration 2: Popular Propriedade a partir de GrupoFazendas
INSERT INTO cadastros_propriedades (id, tenant_id, nome, descricao, cor, icone, ordem, ativo, created_at, updated_at)
SELECT id, tenant_id, nome, descricao, cor, icone, ordem, ativo, created_at, updated_at
FROM grupos_fazendas;

-- Migration 3: Criar ExploracaoRural para cada Fazenda vinculada a Grupo
INSERT INTO cadastros_exploracoes_rurais (id, tenant_id, propriedade_id, fazenda_id, natureza, data_inicio, ativo)
SELECT gen_random_uuid(), gf.tenant_id, gf.id, gfr.fazenda_id, 'propria', CURRENT_DATE, true
FROM grupos_fazendas gf
JOIN grupo_fazendas_rel gfr ON gfr.grupo_id = gf.id;

-- Migration 4: (posterior) Remover GrupoFazendas após transição
```

### 3.2. Impacto em FK existente

| Tabela FK → GrupoFazendas | Ação |
|---------------------------|------|
| `Fazenda.grupo_id` | Manter como FK nullable; novo campo: `exploracao_id` opcional |
| `GrupoUsuario.grupo_id` | Criar `PropriedadeUsuario` paralelo; migrar gradualmente |
| `Safra` (sem vínculo direto com grupo) | Sem impacto |

---

## 4. Schemas Pydantic

**Arquivo novo:** `core/cadastros/propriedades/propriedade_schemas.py`

```python
class PropriedadeCreate(BaseModel):
    nome: str = Field(..., min_length=2, max_length=200)
    cpf_cnpj: Optional[str] = Field(None, max_length=18)
    inscricao_estadual: Optional[str] = Field(None, max_length=50)
    ie_isento: bool = False
    email: Optional[str] = Field(None, max_length=200)
    telefone: Optional[str] = Field(None, max_length=30)
    nome_fantasia: Optional[str] = Field(None, max_length=200)
    regime_tributario: Optional[str] = Field(None, max_length=30)
    cor: Optional[str] = Field(None, max_length=7)
    icone: Optional[str] = Field(None, max_length=50)
    ordem: int = 0
    observacoes: Optional[str] = None

class ExploracaoCreate(BaseModel):
    fazenda_id: uuid.UUID
    natureza: str  # valida contra NaturezaVinculo
    data_inicio: date
    data_fim: Optional[date] = None
    numero_contrato: Optional[str] = Field(None, max_length=100)
    valor_anual: Optional[float] = Field(None, gt=0)
    percentual_producao: Optional[float] = Field(None, gt=0, le=100)
    area_explorada_ha: Optional[float] = Field(None, gt=0)
    observacoes: Optional[str] = None

class DocumentoExploracaoCreate(BaseModel):
    tipo: str  # valida contra TipoDocumentoExploracao
    nome_arquivo: str
    storage_path: str
    storage_backend: str = "local"
    tamanho_bytes: int
    mime_type: Optional[str] = None
    data_emissao: Optional[date] = None
    data_validade: Optional[date] = None
    numero_documento: Optional[str] = None
    orgao_expedidor: Optional[str] = None
    observacoes: Optional[str] = None
```

---

## 5. Service — Regras de Negócio

```python
class ExploracaoRuralService:
    async def criar(self, data: ExploracaoCreate, propriedade_id: UUID) -> ExploracaoRural:
        # Regra: não permitir sobreposição de vigência
        # mesma fazenda + mesma propriedade + período sobreposto → erro
        await self._validar_sobreposicao(
            fazenda_id=data.fazenda_id,
            propriedade_id=propriedade_id,
            data_inicio=data.data_inicio,
            data_fim=data.data_fim,
        )

        # Regra: data_fim > data_inicio
        if data.data_fim and data.data_fim <= data.data_inicio:
            raise BusinessRuleError("data_fim deve ser posterior a data_inicio")

        # Regra: área explorada <= área total da fazenda
        fazenda = await self._get_fazenda(data.fazenda_id)
        if data.area_explorada_ha and fazenda.area_total_ha:
            if data.area_explorada_ha > float(fazenda.area_total_ha) * 1.05:
                raise BusinessRuleError(
                    f"Área explorada ({data.area_explorada_ha} ha) excede "
                    f"área total da fazenda ({fazenda.area_total_ha} ha)"
                )

        return await self._save(data, propriedade_id)

    async def verificar_vigentes(self, fazenda_id: UUID) -> list[ExploracaoRural]:
        """Retorna explorações vigentes de uma fazenda (data_fim NULL ou >= hoje)."""
        ...

    async def historico_fazenda(self, fazenda_id: UUID) -> list[dict]:
        """Retorna histórico completo de exploradores de uma fazenda."""
        ...
```

---

## 6. Router — Endpoints

```python
router = APIRouter(prefix="/cadastros/propriedades", tags=["Propriedades (Unidade Econômica)"])

# CRUD Propriedade
POST   /cadastros/propriedades/              → Criar propriedade
GET    /cadastros/propriedades/              → Listar propriedades do tenant
GET    /cadastros/propriedades/{id}          → Detalhes
PATCH  /cadastros/propriedades/{id}          → Atualizar
DELETE /cadastros/propriedades/{id}          → Soft delete (só se sem explorações ativas)

# Explorações de uma propriedade
GET    /cadastros/propriedades/{id}/exploracoes       → Listar vínculos
POST   /cadastros/propriedades/{id}/exploracoes       → Criar vínculo

# Explorações de uma fazenda
GET    /fazendas/{fazenda_id}/exploracoes             → Histórico de exploradores
GET    /fazendas/{fazenda_id}/exploracoes/vigentes    → Explorações ativas agora

# Documentos
POST   /cadastros/exploracoes/{id}/documentos/upload  → Upload de documento
GET    /cadastros/exploracoes/{id}/documentos         → Listar documentos
GET    /cadastros/exploracoes/{id}/documentos/{doc_id}→ Download
DELETE /cadastros/exploracoes/{id}/documentos/{doc_id}→ Remover
```

---

## 7. Impacto no Frontend

### 7.1. Páginas novas

| Página | Rota | O que faz |
|--------|------|-----------|
| Lista de Propriedades | `/cadastros/propriedades-econ` | Lista propriedades com CNPJ, nº fazendas, status |
| Detalhe da Propriedade | `/cadastros/propriedades-econ/{id}` | Dados + abas: Fazendas Vinculadas, Documentos, Histórico |
| Upload de Documento | Dialog | Upload de contrato, CCIR, ITR com validação de validade |

### 7.2. Páginas existentes modificadas

| Página | Mudança |
|--------|---------|
| `/cadastros/propriedades` (Fazendas) | Seleção de Propriedade ao criar fazenda; exibir vínculo atual |
| `/cadastros/propriedades/[id]` (Detalhe Fazenda) | Aba nova: "Vínculo de Exploração" (natureza, vigência, documentos) |
| Safras | Safra vinculada a Propriedade (não mais a Fazenda diretamente) |

### 7.3. Zod schemas novos

```typescript
// packages/zod-schemas/src/propriedade-schemas.ts
export const createPropriedadeSchema = z.object({
  nome: z.string().min(2).max(200),
  cpf_cnpj: z.string().max(18).optional().or(z.literal("")),
  inscricao_estadual: z.string().max(50).optional(),
  ie_isento: z.boolean().default(false),
  email: z.string().email().max(200).optional(),
  telefone: z.string().max(30).optional(),
  nome_fantasia: z.string().max(200).optional(),
  regime_tributario: z.enum(["SIMPLES", "PRESUMIDO", "REAL", "ISENTO"]).optional(),
});

export const createExploracaoSchema = z.object({
  fazenda_id: z.string().uuid(),
  natureza: z.enum(["propria", "arrendamento", "parceria", "comodato", "posse"]),
  data_inicio: z.coerce.date(),
  data_fim: z.coerce.date().optional().nullable(),
  numero_contrato: z.string().max(100).optional(),
  valor_anual: z.coerce.number().gt(0).optional(),
  percentual_producao: z.coerce.number().gt(0).lte(100).optional(),
  area_explorada_ha: z.coerce.number().gt(0).optional(),
});
```

---

## 8. Migration — Script Alembic

```python
"""add_propriedade_exploracao_rural

Revision ID: add_propriedade_exploracao
Revises: previous
Create Date: 2026-04-06

Changes:
1. Criar tabela cadastros_propriedades
2. Criar tabela cadastros_exploracoes_rurais
3. Criar tabela cadastros_documentos_exploracao
4. Popular Propriedade a partir de grupos_fazendas (migração de dados)
5. Criar ExploracaoRural para cada fazenda vinculada a grupo
6. Adicionar coluna exploracao_id em fazendas (nullable)
"""

def upgrade():
    # 1. Propriedade
    op.create_table(
        "cadastros_propriedades",
        sa.Column("id", Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("tenant_id", Uuid(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("nome", String(200), nullable=False),
        sa.Column("cpf_cnpj", String(18), nullable=True),
        sa.Column("inscricao_estadual", String(50), nullable=True),
        sa.Column("ie_isento", Boolean, default=False),
        sa.Column("email", String(200), nullable=True),
        sa.Column("telefone", String(30), nullable=True),
        sa.Column("nome_fantasia", String(200), nullable=True),
        sa.Column("regime_tributario", String(30), nullable=True),
        sa.Column("cor", String(7), nullable=True),
        sa.Column("icone", String(50), nullable=True),
        sa.Column("ordem", Integer, default=0),
        sa.Column("ativo", Boolean, default=True),
        sa.Column("observacoes", Text, nullable=True),
        sa.Column("created_at", DateTime(timezone=True), default=...),
        sa.Column("updated_at", DateTime(timezone=True), default=..., onupdate=...),
    )
    op.create_index("ix_propriedades_tenant", "cadastros_propriedades", ["tenant_id"])

    # 2. ExploracaoRural
    op.create_table(
        "cadastros_exploracoes_rurais",
        sa.Column("id", Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("tenant_id", Uuid(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("propriedade_id", Uuid(as_uuid=True), ForeignKey("cadastros_propriedades.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("fazenda_id", Uuid(as_uuid=True), ForeignKey("fazendas.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("natureza", String(30), nullable=False, default="propria"),
        sa.Column("data_inicio", Date, nullable=False),
        sa.Column("data_fim", Date, nullable=True),
        sa.Column("numero_contrato", String(100), nullable=True),
        sa.Column("valor_anual", Float, nullable=True),
        sa.Column("percentual_producao", Float, nullable=True),
        sa.Column("area_explorada_ha", Float, nullable=True),
        sa.Column("documento_s3_key", String(512), nullable=True),
        sa.Column("documento_tipo", String(20), nullable=True),
        sa.Column("ativo", Boolean, default=True),
        sa.Column("observacoes", Text, nullable=True),
        sa.Column("created_at", DateTime(timezone=True), default=...),
        sa.Column("updated_at", DateTime(timezone=True), default=..., onupdate=...),
    )
    op.create_index("ix_exploracoes_vigencia", "cadastros_exploracoes_rurais", ["data_inicio", "data_fim"])

    # 3. DocumentoExploracao
    op.create_table(
        "cadastros_documentos_exploracao",
        sa.Column("id", Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("tenant_id", Uuid(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("exploracao_id", Uuid(as_uuid=True), ForeignKey("cadastros_exploracoes_rurais.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("tipo", String(50), nullable=False),
        sa.Column("nome_arquivo", String(255), nullable=False),
        sa.Column("storage_path", String(512), nullable=False),
        sa.Column("storage_backend", String(10), nullable=False, default="local"),
        sa.Column("tamanho_bytes", Integer, nullable=False),
        sa.Column("mime_type", String(100), nullable=True),
        sa.Column("data_emissao", Date, nullable=True),
        sa.Column("data_validade", Date, nullable=True),
        sa.Column("numero_documento", String(100), nullable=True),
        sa.Column("orgao_expedidor", String(100), nullable=True),
        sa.Column("observacoes", Text, nullable=True),
        sa.Column("ativo", Boolean, default=True),
        sa.Column("created_at", DateTime(timezone=True), default=...),
    )

    # 4. Migração de dados: GrupoFazendas → Propriedade
    op.execute("""
        INSERT INTO cadastros_propriedades (id, tenant_id, nome, descricao, cor, icone, ordem, ativo, created_at, updated_at)
        SELECT id, tenant_id, nome, descricao, cor, icone, ordem, ativo, created_at, updated_at
        FROM grupos_fazendas
    """)

    # 5. Migração de dados: grupo_fazendas_rel → ExploracaoRural
    op.execute("""
        INSERT INTO cadastros_exploracoes_rurais (id, tenant_id, propriedade_id, fazenda_id, natureza, data_inicio, ativo)
        SELECT gen_random_uuid(), gf.tenant_id, gf.id, gfr.fazenda_id, 'propria', CURRENT_DATE, true
        FROM grupos_fazendas gf
        JOIN grupo_fazendas_rel gfr ON gfr.grupo_id = gf.id
    """)

    # 6. Adicionar exploracao_id em fazendas (nullable, para transição)
    op.add_column("fazendas", sa.Column("exploracao_id", Uuid(as_uuid=True), nullable=True))
    op.create_foreign_key("fk_fazendas_exploracao", "fazendas", "cadastros_exploracoes_rurais",
                          ["exploracao_id"], ["id"], ondelete="SET NULL")
```

---

## 9. Checklist da Frente C

- [ ] Modelos `Propriedade`, `ExploracaoRural`, `DocumentoExploracao` criados
- [ ] Enums `NaturezaVinculo`, `TipoDocumentoExploracao` criados
- [ ] Migration criada e testada (up + down)
- [ ] Migração de dados (GrupoFazendas → Propriedade) funcionando
- [ ] Service com validação de sobreposição de vigência
- [ ] Service com validação área explorada ≤ área total
- [ ] Router com CRUD Propriedade completo
- [ ] Router com CRUD ExploracaoRural completo
- [ ] Router com upload/download de documentos
- [ ] Schemas Pydantic criados
- [ ] Schemas Zod criados (frontend)
- [ ] UI: Lista de Propriedades
- [ ] UI: Detalhe da Propriedade (abas Fazendas, Documentos, Histórico)
- [ ] UI: Dialog de criação de Exploração (natureza, vigência, contrato)
- [ ] UI: Upload de documentos de exploração
- [ ] UI: Página de Fazenda exibe vínculo de exploração atual
- [ ] Testes unitários: sobreposição de vigência
- [ ] Testes unitários: área explorada > área total
- [ ] Testes de integração: CRUD completo
- [ ] Documentação API (Swagger) atualizada
- [ ] Zero regressões em GrupoFazendas (funciona em paralelo)
