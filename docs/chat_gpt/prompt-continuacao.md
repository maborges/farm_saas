

## STATUS ATUAL

- Step 20: iniciar, os demais anteriores foram concluídos

CONTEXTO:

Estou desenvolvendo um sistema SaaS de gestão de safras agrícolas com arquitetura incremental.

Anexo/fornecido:
- contexto_sistema_agro_safra.md (documento mestre com arquitetura e decisões)
- schema-diff-production-unit.md (definição técnica dos steps)

Princípios obrigatórios:
- evolução incremental (não recriar sistema)
- não quebrar compatibilidade
- schema diff (não redesign)
- append-only para eventos críticos
- separar estrutura, execução e análise
- PostgreSQL como banco principal

---

ESTADO ATUAL:

- falta do Step 20 em diante se houver


Controle de concorrência:
- advisory lock (PostgreSQL)
- constraint trigger DEFERRABLE (validação no COMMIT)
- job noturno apenas para detecção

status_consorcio_area:
- read model derivado (não é fonte de verdade)
- usado para validação e bloqueio seletivo
- bloqueia inconsistências e encerramento de safra

---

TAREFA:

Contunuar a partir do step 20.

Entregar:

1. migration completa:
   - upgrade()
   - downgrade (seguindo política do projeto)

2. criação das tabelas:
   - production_units
   - status_consorcio_area

3. constraints:
   - partial unique de production_units
   - CHECKs
   - FK rules

4. triggers:
   - constraint trigger DEFERRABLE para soma das participações
   - trigger de refresh do status_consorcio_area

5. backfill:
   - idempotente a partir de cultivo_areas
   - com triggers desabilitadas durante execução

6. plano completo:
   - justificativas
   - riscos
   - estratégia de testes
   - rollout
   - rollback

IMPORTANTE:
- não alterar steps anteriores
- não inventar novas entidades fora do schema-diff
- respeitar nomenclatura definida (pt-BR + production_units em inglês)

Responder com código + explicação.