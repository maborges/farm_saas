# Brainstorming — Normalização dos Cadastros

**Data:** 2026-03-24
**Status:** Implementado (Ondas 1-4 aplicadas)

---

## Decisões arquiteturais

### 1. Padrão Typed Core + JSONB
- Tabelas tipadas e fortemente modeladas para atributos conhecidos
- `dados_extras JSONB` para extensões por tenant sem migrations
- **Evitado:** EAV puro (antipadrão — queues complexas, sem type safety)

### 2. Animal ≠ Produto (IAS 41 / CPC 29)
- Ativo biológico vivo: ciclo de vida, genealogia, eventos append-only
- `EventoAnimal` é imutável — nunca deletar
- Produto agrícola (leite, grão) é resultado do ativo biológico — vira receita

### 3. Dois tipos de estoque separados
- **Almoxarifado** (`operacional/estoque/`) → insumos, peças, EPIs → gera DESPESA
- **Armazém/Commodity** (`cadastros/commodities/`) → grãos colhidos, leite → gera RECEITA

### 4. AreaRural hierárquica
- Tabela única com `parent_id` e `tipo` ENUM
- Substitui: `talhoes`, `pec_piquetes`, `imoveis_rurais`, `imoveis_benfeitorias`
- Geometria opcional (PostGIS em produção, JSON em dev)

---

## Estrutura final do módulo `cadastros/`

```
core/cadastros/
├── pessoas/
│   ├── Pessoa                    — base (tipo PF/PJ, LGPD)
│   ├── PessoaDocumento           — CPF, CNPJ, RG, IE (tipados, 1:N)
│   ├── PessoaContato             — CELULAR, EMAIL, WHATSAPP (tipados, 1:N)
│   ├── PessoaEndereco            — múltiplos endereços tipados (1:N)
│   ├── PessoaBancario            — múltiplas contas/PIX (1:N, PII alto risco)
│   ├── TipoRelacionamento        — FORNECEDOR, CLIENTE, FUNCIONARIO...
│   ├── PessoaRelacionamento      — pivot pessoa ↔ papel ↔ fazenda
│   ├── PessoaConsentimento       — LGPD append-only
│   └── PessoaAcessoLog           — LGPD audit append-only
│
├── propriedades/
│   ├── AreaRural                 — hierárquica (parent_id), PostGIS opcional
│   │     tipos: PROPRIEDADE, GLEBA, UNIDADE_PRODUTIVA, AREA,
│   │            TALHAO, PIQUETE, PASTAGEM, APP, RESERVA_LEGAL,
│   │            ARMAZEM, SEDE, INFRAESTRUTURA
│   ├── MatriculaImovel           — CAR, NIRF, INCRA, matrícula cartorial
│   └── RegistroAmbiental         — licenças ambientais (APP, RL)
│
├── equipamentos/
│   └── Equipamento               — TRATOR, COLHEDORA, VEICULO, IMPLEMENTO...
│         (substitui frota_maquinarios)
│
├── produtos/
│   ├── Produto                   — catálogo de insumos/almoxarifado (gera DESPESA)
│   ├── ProdutoAgricola           — defensivos, sementes (MAPA, carência, TSI)
│   ├── ProdutoEstoque            — controle físico (NCM, peso, validade)
│   ├── ProdutoEPI                — CA, tipo proteção, vida útil
│   └── ProdutoCultura            — culturas agrícolas (ciclo, espaçamento)
│
└── commodities/
    ├── Commodity                 — produtos de saída/receita (soja, milho, leite...)
    └── CommodityClassificacao    — padrões de qualidade por classe (IN MAPA)
```

## Módulos especializados

```
pecuaria/
├── animal/
│   ├── LoteAnimal                — agrupamento operacional
│   ├── Animal                   — entidade viva individual (ativo biológico)
│   └── EventoAnimal             — linha do tempo append-only
└── producao/
    └── ProducaoLeite            — produção leiteira com qualidade (CCS, CBT, gordura)

rh/
└── ColaboradorRH                — especializa Pessoa para RH (pessoa_id FK obrigatória)
    LancamentoDiaria
    Empreitada
```

## Módulos removidos/absorvidos

| Módulo | Substituído por |
|---|---|
| `pessoas/` | `core/cadastros/pessoas/` |
| `agricola/talhoes/` | `core/cadastros/propriedades/AreaRural` (tipo=TALHAO) |
| `pecuaria/models/piquete.py` | `core/cadastros/propriedades/AreaRural` (tipo=PIQUETE) |
| `imoveis/` | `core/cadastros/propriedades/AreaRural` (tipo=PROPRIEDADE) |
| `frota_maquinarios` | `core/cadastros/equipamentos/Equipamento` |
| `operacional/compras/Fornecedor` | `Pessoa` com papel FORNECEDOR |
| `agricola/cadastros/Cultura` | `core/cadastros/produtos/ProdutoCultura` |

## Migrations aplicadas

| Migration | Descrição |
|---|---|
| `fa37f6f94792` | Onda 1 — pessoas, propriedades, equipamentos |
| `ed0688180f35` | Onda 2 — produtos, commodities |
| `3a5b2924aad1` | Onda 3 — pecuária (Animal, EventoAnimal, ProducaoLeite) |
| `4e0b633ffb18` | Onda 4 — limpeza, RH normalizado, FKs talhoes→areas_rurais |
