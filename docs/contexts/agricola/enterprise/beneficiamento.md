---
modulo: "Agr\xEDcola"
submodulo: Beneficiamento
nivel: enterprise
core: false
dependencias_core:
  - core/auth
  - core/cadastros/fazendas
  - core/cadastros/produtos
  - core/tenant
dependencias_modulos:
  - ../essencial/safras.md
  - ../essencial/operacoes-campo.md
  - ../enterprise/rastreabilidade-campo.md
  - ../../operacional/estoque.md
standalone: false
complexidade: L
assinante_alvo:
  - grande-produtor
  - cooperativa
  - agroindústria
  - cafeicultor
  - produtor-de-graos
---

# Beneficiamento

## Descricao Funcional

O submodulo de Beneficiamento cobre todas as etapas de pos-colheita que transformam o produto bruto colhido no campo em produto pronto para comercializacao. Isso inclui secagem, limpeza, classificacao, armazenamento e, no caso do cafe, despolpamento e torrefacao.

O beneficiamento e critico porque afeta diretamente a qualidade e o valor do produto. Uma secagem mal feita pode desvalorizar toda a safra. O sistema rastreia cada lote desde a entrada no beneficiamento ate a saida, mantendo a rastreabilidade de campo intacta.

Funcionalidades principais:
- Registro de entrada de lotes no beneficiamento (vinculados a romaneios de colheita)
- Controle de secagem: umidade inicial, umidade final, tempo de secagem, metodo (terreiro, secador)
- Classificacao e tipagem do produto (defeitos, peneira, tipo, bebida para cafe)
- Rendimento do beneficiamento (peso bruto → peso beneficiado, perdas)
- Rastreabilidade preservada: lote beneficiado aponta para lotes de origem
- Controle de armazenamento pos-beneficiamento (silo, armazem, tulha)
- Romaneios de saida para venda com vinculo ao lote beneficiado

## Personas — Quem usa este submodulo

- **Gerente de Beneficiamento:** controla entrada, processo e saida de lotes
- **Operador de Secador/Terreiro:** registra umidade e tempos de secagem
- **Classificador:** registra analise de qualidade (defeitos, peneira, tipo)
- **Gerente Comercial:** consulta lotes disponiveis para venda com classificacao e rastreabilidade
- **Produtor:** acompanha rendimento e qualidade da safra apos beneficiamento

## Dores que resolve

1. **Perda de qualidade:** sem controle de secagem, graos sao secos demais (quebra) ou de menos (mofo)
2. **Rendimento desconhecido:** produtor nao sabe quanto perde no beneficiamento (impurezas, umidade, defeitos)
3. **Rastreabilidade quebrada:** a rastreabilidade se perde ao misturar lotes no beneficiamento
4. **Valorizacao errada:** sem classificacao, produtor vende cafe fino pelo preco de rio/riado
5. **Controle de estoque:** produto beneficiado em silos sem registro preciso de quantidade e qualidade

## Regras de Negocio

1. Todo lote que entra no beneficiamento deve ter vinculo com romaneio de colheita (rastreabilidade obrigatoria)
2. A umidade de entrada e obrigatoria; a umidade alvo depende do produto (ex: 11-12% para cafe, 13-14% para soja)
3. O rendimento e calculado: `peso_beneficiado / peso_bruto * 100`
4. Quando lotes de origens diferentes sao misturados (blending), o lote resultante herda rastreabilidade de todos os lotes de origem
5. A classificacao segue normas oficiais: cafe (IN 08/2003 MAPA), soja (IN 11/2007), milho (Portaria 845)
6. Lotes reprovados na classificacao devem ser segregados com status `reprovado` e motivo
7. O controle de secagem registra leituras periodicas de umidade (a cada X horas, configuravel)
8. A saida do beneficiamento gera novo registro de estoque com produto beneficiado
9. Nao e permitido dar saida em lote sem classificacao concluida (configuravel por tenant)
10. Permissoes: `agricola:beneficiamento:create/read/update`, `agricola:beneficiamento:classificar`

## Entidades de Dados Principais

| Entidade | Campos Chave | Relacionamentos |
|----------|-------------|-----------------|
| `LoteBeneficiamento` | id, tenant_id, lote_producao_ids (array), data_entrada, peso_bruto_kg, umidade_entrada_pct, status | vinculado a LoteProducao |
| `SecagemRegistro` | id, lote_beneficiamento_id, metodo (terreiro/secador), umidade_atual_pct, temperatura_c, data_hora_leitura | leituras de secagem |
| `Classificacao` | id, lote_beneficiamento_id, tipo_produto, peneira, defeitos_pct, bebida (cafe), cor, observacoes, classificador_id | qualidade |
| `LoteBeneficiado` | id, lote_beneficiamento_id, peso_liquido_kg, umidade_final_pct, rendimento_pct, classificacao_id, local_armazenamento | produto final |
| `SaidaBeneficiamento` | id, lote_beneficiado_id, destino, peso_kg, data_saida, nota_fiscal, comprador | romaneio de saida |

## Integracoes Necessarias

| Sistema/Modulo | Tipo | Descricao |
|----------------|------|-----------|
| `agricola/romaneios` | Leitura | Lotes de producao que entram no beneficiamento |
| `agricola/rastreabilidade` | Bidirecional | Propaga rastreabilidade do campo ao lote beneficiado |
| `operacional/estoque` | Escrita | Registra produto beneficiado no estoque |
| `agricola/custos` | Escrita | Custo do beneficiamento (energia, mao de obra, perda) |
| `financeiro/receitas` | Leitura | Receita de venda vinculada ao lote beneficiado |
| `core/cadastros/produtos` | Leitura | Catalogo de produtos e classificacoes |

## Fluxo de Uso Principal (step-by-step)

1. Caminhao chega da colheita — operador registra entrada no beneficiamento com peso bruto e umidade
2. Sistema vincula automaticamente ao romaneio de colheita (lote de producao)
3. Lote e encaminhado para secagem — operador seleciona metodo (terreiro ou secador mecanico)
4. Durante secagem, operador registra leituras periodicas de umidade e temperatura
5. Quando umidade atinge nivel alvo, secagem e encerrada
6. Lote segue para limpeza e classificacao — classificador registra peneira, defeitos, tipo, bebida
7. Sistema calcula rendimento: `peso_beneficiado / peso_bruto`
8. Lote beneficiado e armazenado — sistema registra local (silo, tulha, armazem) e quantidade
9. Estoque de produto beneficiado e atualizado automaticamente
10. Quando comercializado, registra saida com destino, comprador e nota fiscal
11. Rastreabilidade completa: comprador pode rastrear do lote beneficiado ate os insumos do campo

## Casos Extremos e Excecoes

- **Lote com umidade critica:** umidade acima de 25% — priorizar secagem e alertar risco de fermentacao
- **Secador quebrado:** transferencia para terreiro mid-processo — registrar mudanca de metodo com justificativa
- **Blending de lotes:** mistura de cafes de talhoes diferentes para criar blend comercial — rastreabilidade deve listar todas as origens com percentuais
- **Reclassificacao:** lote classificado como tipo 6 na prova de xicara sobe para tipo 4 — permitir nova classificacao mantendo historico
- **Perda anormal:** rendimento abaixo de 50% — alertar e exigir justificativa (possivel erro de pesagem ou perda por praga)
- **Produto sem classificacao padrao:** cultura sem norma oficial (ex: macadamia) — permitir classificacao customizada por tenant
- **Armazenamento lotado:** silo cheio — alertar e sugerir destinos alternativos

## Criterios de Aceite (Definition of Done)

- [ ] Registro de entrada com peso bruto, umidade e vinculo ao romaneio
- [ ] Controle de secagem com leituras periodicas de umidade e temperatura
- [ ] Alerta quando umidade atinge nivel alvo
- [ ] Classificacao com campos especificos por tipo de produto (cafe, soja, milho)
- [ ] Calculo automatico de rendimento (peso beneficiado / peso bruto)
- [ ] Propagacao de rastreabilidade: lote beneficiado → lotes de producao → insumos
- [ ] Blending com rastreabilidade multi-origem
- [ ] Registro de saida com destino e nota fiscal
- [ ] Atualizacao automatica de estoque de produto beneficiado
- [ ] Tenant isolation e RBAC testados
- [ ] Componente frontend `beneficiamento-cafe.tsx` integrado

## Sugestoes de Melhoria Futura

1. **IoT para secagem:** sensores de umidade e temperatura com leitura automatica em tempo real
2. **Classificacao por visao computacional:** camera analisa graos e classifica defeitos automaticamente
3. **Prova de xicara digital:** registro completo de cupping com formulario SCA (Specialty Coffee Association)
4. **Integracao com balanca:** leitura automatica de peso na entrada e saida do beneficiamento
5. **Controle de energia:** monitorar consumo energetico do secador por lote para custeio preciso
6. **Marketplace de lotes:** publicar lotes classificados em marketplace B2B para compradores
7. **Certificacao de origem:** gerar selo de origem digital com QR Code vinculado a rastreabilidade completa
