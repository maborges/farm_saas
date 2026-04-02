# ⚠️ PENDÊNCIA - Setup de Performance (DBA)

**Data de Criação:** 2026-03-31
**Prioridade:** 🔴 **ALTA**
**Status:** ⏳ **Aguardando DBA**

---

## 📋 DESCRIÇÃO

Para iniciar a Sprint 35 - Performance, é necessário habilitar recursos de monitoring no banco de dados PostgreSQL. Estas configurações requerem privilégios de **superuser** que o usuário atual não possui.

---

## 🔧 AÇÕES NECESSÁRIAS

### 1. Habilitar pg_stat_statements

**O que é:** Extensão PostgreSQL que monitora todas as queries executadas, permitindo identificar queries lentas e gargalos de performance.

**Comando:**
```sql
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
```

**Por que precisamos:**
- Identificar top 20 queries mais lentas
- Coletar métricas de tempo médio, máximo e total
- Priorizar otimizações baseadas em dados reais

---

### 2. Habilitar Query Logging

**O que é:** Configuração que loga automaticamente todas as queries que excedem um tempo limite (500ms).

**Comando:**
```sql
ALTER SYSTEM SET log_min_duration_statement = 500;
SELECT pg_reload_conf();
```

**Por que precisamos:**
- Capturar queries lentas em tempo real
- Identificar problemas de performance em produção
- Criar alertas proativos

---

### 3. Verificação

**Comandos para verificar se foi aplicado:**
```sql
-- Verificar pg_stat_statements
SELECT COUNT(*) FROM pg_stat_statements;
-- Deve retornar um número > 0

-- Verificar query logging
SHOW log_min_duration_statement;
-- Deve retornar: 500
```

---

## 📁 SCRIPT PRONTO PARA DBA

**Localização:** `services/api/scripts/sprint35_dba_setup.sql`

**Como executar:**
```bash
# Opção 1: Via linha de comando
psql -h 192.168.0.2 -U postgres -d farms -f scripts/sprint35_dba_setup.sql

# Opção 2: Via pgAdmin ou outro GUI
# Copiar conteúdo do arquivo e executar no SQL Editor
```

---

## 📊 IMPACTO DA PENDÊNCIA

### Com pg_stat_statements
- ✅ Métricas completas de performance
- ✅ Identificação precisa de queries lentas
- ✅ Baseline real para comparação

### Sem pg_stat_statements (Atual)
- ⚠️ Métricas limitadas a estatísticas de tabelas
- ⚠️ Não é possível rankear queries por tempo
- ⚠️ Otimizações baseadas em estimativas

---

## 🎯 PLANO DE CONTINGÊNCIA

Enquanto aguardamos o DBA, a Sprint 35 pode prosseguir com:

1. **Otimizações baseadas em estatísticas**
   - Identificar tabelas com muitas seq scans
   - Criar índices baseados em padrões de uso

2. **Índices já mapeados**
   - Migration `035_sprint35_performance_indexes.py` está pronta
   - 23 índices baseados em análise de baseline

3. **Cache Redis**
   - Implementação não depende do pg_stat_statements
   - Pode prosseguir normalmente

---

## 📞 CONTATOS DO DBA

| Nome | Email | Telefone |
|------|-------|----------|
| DBA Responsável | _________ | _________ |

---

## 📅 TIMELINE

| Data | Evento | Status |
|------|--------|--------|
| 2026-03-31 | Pendência criada | ✅ |
| TBD | DBA executa script | ⏳ |
| TBD | Verificação da equipe | ⏳ |
| 2026-07-01 | Início da Sprint 35 | ⏳ |

---

## ✅ CHECKLIST DE RESOLUÇÃO

- [ ] DBA executou `sprint35_dba_setup.sql`
- [ ] Equipe técnica verificou pg_stat_statements
- [ ] Equipe técnica verificou query logging
- [ ] Baseline completa coletada
- [ ] Sprint 35 pode iniciar com métricas completas

---

## 🔗 LINKS RELACIONADOS

- [Script SQL para DBA](../services/api/scripts/sprint35_dba_setup.sql)
- [Relatório de Execução](docs/qwen/27-relatorio-execucao-setup.md)
- [Sprint 35 Kickoff](docs/qwen/21-sprint-35-kickoff.md)
- [Guia de Performance](docs/qwen/22-guia-performance-profiling.md)

---

**Responsável pelo Acompanhamento:** Tech Lead  
**Data de Criação:** 2026-03-31  
**Última Atualização:** 2026-03-31

---

## 📝 NOTAS

> **Importante:** Esta pendência não bloqueia completamente a Sprint 35, mas limita a capacidade de identificar queries lentas com precisão. As otimizações de índices podem prosseguir normalmente.

---

**Status:** ⏳ Aguardando ação do DBA
