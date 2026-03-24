# AgroSaaS Expert Skills

This directory contains specialized expert skills for each module of the AgroSaaS platform. Each skill provides deep domain knowledge, best practices, and implementation patterns for its respective area.

## Available Skills

### 1. [Core Module Expert](CORE_MODULE_EXPERT.md)
**Expertise:** Authentication, Authorization, Multi-tenancy, Billing, Platform Administration

**When to use:**
- Implementing authentication/authorization features
- Setting up RBAC (Role-Based Access Control)
- Managing subscriptions and billing
- Handling multi-tenancy concerns
- Implementing onboarding flows
- Working with team management
- Setting up farm groups (grupos de fazendas)

**Key Topics:**
- JWT token structure and validation
- Two-level RBAC (Backoffice + Tenant)
- Multi-subscription support
- BaseService pattern for tenant isolation
- Module access control
- Impersonation system

---

### 2. [Agricola Module Expert](AGRICOLA_MODULE_EXPERT.md)
**Expertise:** Crop Management, Field Operations, Precision Agriculture, Harvest

**When to use:**
- Working with crop planning (safras)
- Managing fields/plots (talhões) with geospatial data
- Implementing field operations (work orders)
- Building precision agriculture features (NDVI, prescriptions)
- Handling harvest/grain tickets (romaneios)
- Managing agronomist prescriptions
- Implementing soil analysis features

**Key Topics:**
- Geospatial operations (PostGIS, GeoJSON)
- Safra lifecycle management
- Chemical application regulations
- Cost allocation to crops
- NDVI processing
- Traceability chains

---

### 3. [Pecuaria Module Expert](PECUARIA_MODULE_EXPERT.md)
**Expertise:** Livestock Management, Reproduction, Feeding, Animal Health

**When to use:**
- Managing cattle lots (lotes)
- Implementing pasture management (piquetes)
- Building livestock handling workflows (manejos)
- Working with reproduction protocols (IATF)
- Implementing feedlot operations
- Managing dairy operations
- Animal health tracking

**Key Topics:**
- Lot management and stocking calculations
- Rotational grazing strategies
- Vaccination protocols and compliance
- IATF (timed artificial insemination)
- Feed efficiency calculations
- Milk quality tracking (CCS, CBT)

---

### 4. [Financeiro Module Expert](FINANCEIRO_MODULE_EXPERT.md)
**Expertise:** Financial Management, Cost Accounting, Cash Flow, Tax Compliance

**When to use:**
- Implementing chart of accounts (plano de contas)
- Managing accounts payable/receivable
- Building cost allocation (rateio) systems
- Generating financial reports (DRE, cash flow)
- Implementing profitability analysis
- Working with agricultural loans
- Handling barter operations
- Commodity hedging features

**Key Topics:**
- Agricultural cost structure (variable/fixed)
- Safra profitability calculations
- ABC costing and allocation
- Brazilian tax compliance (FUNRURAL, ICMS)
- Biological asset accounting (IAS 41)
- Break-even analysis

---

### 5. [Operacional Module Expert](OPERACIONAL_MODULE_EXPERT.md)
**Expertise:** Fleet Management, Inventory Control, Maintenance, Procurement

**When to use:**
- Managing machinery and equipment (frota)
- Implementing maintenance schedules
- Building work order systems
- Handling inventory management (estoque)
- Implementing procurement workflows
- Managing suppliers and quotations
- Working with spare parts tracking

**Key Topics:**
- Preventive maintenance plans
- Hourmeter-based maintenance triggers
- Inventory valuation methods (FIFO, average cost)
- Multi-warehouse operations
- Purchase order workflows
- Equipment availability calculations

---

### 6. [Backoffice/Admin Expert](BACKOFFICE_ADMIN_EXPERT.md)
**Expertise:** SaaS Administration, Tenant Management, Support Operations, Analytics

**When to use:**
- Building backoffice/admin interfaces
- Implementing tenant management features
- Working with subscription operations
- Building support ticket systems
- Implementing impersonation (admin → tenant)
- Creating analytics dashboards
- Managing platform-wide settings

**Key Topics:**
- Backoffice roles and permissions
- Tenant lifecycle management
- Billing cycle processing
- Coupon/promotion systems
- Support SLA tracking
- MRR/ARR calculations
- Audit logging

---

## How to Use These Skills

### For Development
When working on a feature, consult the relevant expert skill to understand:
- Domain-specific business rules
- Data models and relationships
- Common workflows and patterns
- Integration points with other modules
- Performance considerations
- Testing strategies

### For Code Review
Use these skills to verify:
- Business logic correctness
- Compliance with module patterns
- Proper integration with other modules
- Security best practices (especially tenant isolation)

### For Onboarding
New team members should read:
1. [CORE_MODULE_EXPERT.md](CORE_MODULE_EXPERT.md) - Understanding authentication and multi-tenancy
2. The skill(s) for their assigned module(s)
3. [CLAUDE.md](../../CLAUDE.md) - Overall architecture

### For Troubleshooting
Each skill includes a **Troubleshooting** section with common issues and solutions specific to that module.

## Skill Organization

Each skill follows this structure:

1. **Module Overview** - Purpose and scope
2. **Submodules Structure** - Organization and key models
3. **Key Features** - Detailed explanations of major capabilities
4. **Business Rules** - Domain-specific rules and constraints
5. **Integration Points** - How this module connects with others
6. **Common Workflows** - Step-by-step process examples
7. **Performance Considerations** - Optimization tips
8. **Testing Guidelines** - Module-specific test patterns
9. **Troubleshooting** - Common issues and solutions
10. **References** - Links to code and external resources

## Cross-Module Dependencies

```
Core Module (Base)
    ├── Authentication/Authorization (used by all)
    ├── Multi-tenancy (enforced by all)
    └── Billing (determines module access)
        ├── Agricola Module
        │   ├── Uses: Operacional (equipment, inventory)
        │   └── Feeds: Financeiro (costs, revenue)
        ├── Pecuaria Module
        │   ├── Uses: Operacional (feed inventory)
        │   ├── Shares: Agricola (pasture talhões)
        │   └── Feeds: Financeiro (animal costs, milk revenue)
        ├── Financeiro Module
        │   ├── Consumes: Agricola (safra costs/revenue)
        │   ├── Consumes: Pecuaria (animal costs/revenue)
        │   └── Consumes: Operacional (maintenance costs)
        └── Operacional Module
            ├── Serves: Agricola (equipment, inputs)
            ├── Serves: Pecuaria (feed, medications)
            └── Feeds: Financeiro (purchase costs)

Backoffice Module (Platform Admin)
    └── Manages: All tenant modules
```

## Best Practices

### 1. Always Check Tenant Isolation
Every module must enforce tenant isolation. See [CORE_MODULE_EXPERT.md](CORE_MODULE_EXPERT.md) for the BaseService pattern.

### 2. Respect Module Boundaries
Don't bypass module APIs. Use proper service layer integration.

### 3. Follow Domain Patterns
Each module has established patterns (e.g., Safra lifecycle, Lot management). Follow these patterns for consistency.

### 4. Consider Performance
Agricultural data can be large (thousands of animals, hundreds of fields). Use pagination, indexing, and caching appropriately.

### 5. Understand Business Rules
Many rules are driven by regulations (Brazilian agricultural law, tax compliance, export requirements). Don't change these without domain expert consultation.

## Contributing

When adding new features to a module:

1. Consult the relevant expert skill
2. Follow established patterns
3. Update the expert skill if adding new patterns
4. Add integration points if connecting modules
5. Update this README if adding new cross-module dependencies

## Questions?

For questions about:
- **Architecture & Core:** See [CLAUDE.md](../../CLAUDE.md) and [CORE_MODULE_EXPERT.md](CORE_MODULE_EXPERT.md)
- **Specific Module:** See that module's expert skill
- **RBAC & Multi-tenancy:** See [IMPLEMENTACAO_RBAC_MULTI_SUB.md](../../IMPLEMENTACAO_RBAC_MULTI_SUB.md)
