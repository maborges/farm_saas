---
modulo: "Agrícola"
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

## Descrição Funcional

O submódulo de Beneficiamento cobre todas as etapas de pós-colheita que transformam o produto bruto colhido no campo em produto pronto para comercialização. Isso inclui secagem, limpeza, classificação, armazenamento e, no caso do café, despolpamento e torrefação.

O beneficiamento é crítico porque afeta diretamente a qualidade e o valor do produto. Uma secagem mal feita pode desvalorizar toda a safra. O sistema rastreia cada lote desde a entrada no beneficiamento até a saída, mantendo a rastreabilidade de campo intacta.

### Contexto Brasileiro

#### Beneficiamento por Cultura

**Soja e Milho (MT/GO/PR/RS)**:
- **Secagem**: Grãos colhidos com 18-25% de umidade devem ser secos para 13-14% (padrão MAPA para armazenamento)
- **Limpeza**: Remoção de impurezas (palha, pedras, grãos avariados)
- **Classificação**: Separação por tamanho (peneira) e qualidade
- **Armazenamento**: Silos com controle de temperatura e umidade
- **Perdas típicas**: 2-4% na secagem + 1-2% na limpeza = 3-6% total

**Café (MG/SP/ES/RO)**:
- **Café Cereja (CC)**: Passa por despolpador, fermentação, lavagem
- **Café Descascado (CD)**: Retira casca mas mantém mucilagem
- **Café Boia/VC (Vinho em Cana)**: Secado no terreiro sem despolpar
- **Secagem**: Terreiro (15-20 dias) ou secador mecânico (24-48 horas)
- **Classificação**: Peneira (15-16-17-18), defeitos (preto, verde, ardido), bebida (doce, dura, rio, riado)
- **Benefício**: Café em coco → café beneficiado (perde 20% do peso em casca)
- **Valorização**: Café tipo 4/5/6 vale R$ 800-1200/sc; Café especial (84+ pontos) vale R$ 2000-5000/sc

**Algodão (MT/BA/GO)**:
- **Descaroçamento**: Separação de pluma (60%) e caroço (40%)
- **Prensagem**: Pluma prensada em fardos de 220kg
- **Classificação**: Micronaire (finura), comprimento, cor, resistência
- **Rastreabilidade**: Pluma de cada talhão deve ser identificada separadamente

**Arroz (RS/SC)**:
- **Descascamento**: Retirada da casca (20% do peso)
- **Polimento**: Retirada do farelo (8-10% do peso)
- **Classificação**: Grãos inteiros vs quebrados (tipos 1, 2, 3)
- **Rendimento típico**: 68-72% de grãos inteiros

**Cana-de-açúcar (SP/MG/GO)**:
- **Moagem**: Cana → caldo + bagaço
- **Processamento**: Caldo → açúcar cristal/refinado ou fermentação → etanol
- **Rendimento**: 85-95 litros de etanol por tonelada de cana

#### Padrões de Qualidade MAPA

O Ministério da Agricultura define padrões oficiais:

| Produto | Norma | Umidade Máxima | Classificação |
|---------|-------|----------------|---------------|
| Soja | IN 11/2007 | 14% | Tipo 1, 2, 3 (defeitos) |
| Milho | Portaria 845/1986 | 13% | Tipo 1, 2, 3 (defeitos) |
| Café | IN 08/2003 | 11-12% | Tipo 1-8, bebida, peneira |
| Arroz | IN 06/2010 | 13% | Tipo 1, 2, 3 (grãos inteiros) |
| Algodão | IN 04/2004 | 12% | Micronaire, cor, comprimento |

#### Perdas no Beneficiamento

As perdas são inevitáveis mas devem ser controladas:

- **Soja/Milho**: 3-6% (umidade + impurezas)
- **Café**: 20% (casca) + 2-3% (defeitos)
- **Arroz**: 28-32% (casca + farelo)
- **Algodão**: 40% (caroço, que é coproduto vendável)

**Exemplo econômico (café)**:
- Produtor colhe 1000 sc de café em coco (60kg cada) = 60.000kg
- Após beneficiamento: 800 sc de café beneficiado (perda de 20% = casca)
- Se vender café em coco: R$ 400/sc × 1000 = R$ 400.000
- Se vender beneficiado classificado como Tipo 5: R$ 600/sc × 800 = R$ 480.000
- Valor agregado: R$ 80.000 (menos custo de beneficiamento)

Funcionalidades principais:
- Registro de entrada de lotes no beneficiamento (vinculados a romaneios de colheita)
- Controle de secagem: umidade inicial, umidade final, tempo de secagem, método (terreiro, secador)
- Classificação e tipagem do produto (defeitos, peneira, tipo, bebida para café)
- Rendimento do beneficiamento (peso bruto → peso beneficiado, perdas)
- Rastreabilidade preservada: lote beneficiado aponta para lotes de origem
- Controle de armazenamento pós-beneficiamento (silo, armazém, tulha)
- Romaneios de saída para venda com vínculo ao lote beneficiado
- Cálculo de custo de beneficiamento (energia, mão de obra, perda)
- Integração com classificação oficial (MAPA)

## Personas — Quem usa este submódulo

- **Gerente de Beneficiamento (Cooperativa/Usina)**: Controla entrada, processo e saída de lotes. Garante que padrões de qualidade sejam atingidos.

- **Operador de Secador/Terreiro**: Registra umidade e tempos de secagem. Ajusta temperatura e vazão de ar para evitar supersecagem (quebra de grãos) ou subsecagem (mofo).

- **Classificador (Café/Grãos)**: Registra análise de qualidade (defeitos, peneira, tipo, bebida). Profissional certificado pelo MAPA para café.

- **Gerente Comercial**: Consulta lotes disponíveis para venda com classificação e rastreabilidade. Negocia com trading ou indústria.

- **Produtor de Café Especial**: Acompanha rendimento e qualidade da safra após beneficiamento. Café com 84+ pontos (SCA) vale 3-5x mais que café commodity.

- **Armazenista**: Controla estoque de produto beneficiado em silos e armazéns. Monitora temperatura e umidade para evitar deterioração.

## Dores que resolve

1. **Perda de qualidade**: Sem controle de secagem, grãos são secos demais (quebra) ou de menos (mofo). Soja com umidade >14% mofa no armazenamento.

2. **Rendimento desconhecido**: Produtor não sabe quanto perde no beneficiamento (impurezas, umidade, defeitos). Não consegue calcular custo real do produto beneficiado.

3. **Rastreabilidade quebrada**: A rastreabilidade se perde ao misturar lotes no beneficiamento. Exportador não consegue comprovar origem para EUDR.

4. **Valorização errada**: Sem classificação, produtor vende café fino pelo preço de rio/riado. Café tipo 4 vendido como tipo 6 perde R$ 200-300/sc.

5. **Controle de estoque**: Produto beneficiado em silos sem registro preciso de quantidade e qualidade. Dificulta venda e planejamento logístico.

6. **Custo de beneficiamento**: Produtor não sabe quanto gasta de energia, gás ou lenha na secagem. Não consegue precificar corretamente.

7. **Blending sem controle**: Mistura de lotes de origens diferentes para criar blend — sem registro, perde-se rastreabilidade.

## Regras de Negócio

1. Todo lote que entra no beneficiamento deve ter vínculo com romaneio de colheita (rastreabilidade obrigatória)
2. A umidade de entrada é obrigatória; a umidade alvo depende do produto (ex: 11-12% para café, 13-14% para soja)
3. O rendimento é calculado: `peso_beneficiado / peso_bruto * 100`
4. Quando lotes de origens diferentes são misturados (blending), o lote resultante herda rastreabilidade de todos os lotes de origem
5. A classificação segue normas oficiais: café (IN 08/2003 MAPA), soja (IN 11/2007), milho (Portaria 845)
6. Lotes reprovados na classificação devem ser segregados com status `reprovado` e motivo
7. O controle de secagem registra leituras periódicas de umidade (a cada X horas, configurável)
8. A saída do beneficiamento gera novo registro de estoque com produto beneficiado
9. Não é permitido dar saída em lote sem classificação concluída (configurável por tenant)
10. **Blending com percentuais**: Ao misturar lotes, registrar percentual de cada origem no blend final
11. **Custo de beneficiamento**: Ratear custos de energia, mão de obra e perdas por lote processado
12. Permissões: `agricola:beneficiamento:create/read/update`, `agricola:beneficiamento:classificar`

## Entidades de Dados Principais

| Entidade | Campos Chave | Relacionamentos |
|----------|-------------|-----------------|
| `LoteBeneficiamento` | id, tenant_id, lote_producao_ids (array), data_entrada, peso_bruto_kg, umidade_entrada_pct, status | vinculado a LoteProducao |
| `SecagemRegistro` | id, lote_beneficiamento_id, metodo (terreiro/secador), umidade_atual_pct, temperatura_c, data_hora_leitura | leituras de secagem |
| `Classificacao` | id, lote_beneficiamento_id, tipo_produto, peneira, defeitos_pct, bebida (cafe), cor, observacoes, classificador_id | qualidade |
| `LoteBeneficiado` | id, lote_beneficiamento_id, peso_liquido_kg, umidade_final_pct, rendimento_pct, classificacao_id, local_armazenamento | produto final |
| `SaidaBeneficiamento` | id, lote_beneficiado_id, destino, peso_kg, data_saida, nota_fiscal, comprador | romaneio de saída |
| `BlendComposicao` | id, lote_blend_id, lote_origem_id, percentual, peso_kg | composição do blend |
| `CustoBeneficiamento` | id, lote_beneficiamento_id, tipo_custo (energia/mo/perda), valor, unidade | custo do processo |

## Integrações Necessárias

| Sistema/Modulo | Tipo | Descrição |
|----------------|------|-----------|
| `agricola/romaneios` | Leitura | Lotes de produção que entram no beneficiamento |
| `agricola/rastreabilidade` | Bidirecional | Propaga rastreabilidade do campo ao lote beneficiado |
| `operacional/estoque` | Escrita | Registra produto beneficiado no estoque |
| `agricola/custos` | Escrita | Custo do beneficiamento (energia, mão de obra, perda) |
| `financeiro/receitas` | Leitura | Receita de venda vinculada ao lote beneficiado |
| `core/cadastros/produtos` | Leitura | Catálogo de produtos e classificações |
| `api/mapa-classificacao` | Leitura | Tabelas oficiais de classificação de produtos |

## Fluxo de Uso Principal (step-by-step)

1. Caminhão chega da colheita — operador registra entrada no beneficiamento com peso bruto e umidade
2. Sistema vincula automaticamente ao romaneio de colheita (lote de produção)
3. **Amostragem**: Coleta de amostra para análise de umidade e qualidade inicial
4. Lote é encaminhado para secagem — operador seleciona método (terreiro ou secador mecânico)
5. Durante secagem, operador registra leituras periódicas de umidade e temperatura
6. **Alerta de umidade alvo**: Sistema notifica quando umidade atinge nível ideal (ex: 13% para soja)
7. Quando umidade atinge nível alvo, secagem é encerrada
8. Lote segue para limpeza e classificação — classificador registra peneira, defeitos, tipo, bebida
9. **Café**: Prova de xícara (cupping) para avaliar bebida (doce, dura, rio, riado, xícara)
10. Sistema calcula rendimento: `peso_beneficiado / peso_bruto`
11. **Perdas**: Sistema registra perdas por umidade, impurezas e defeitos
12. Lote beneficiado é armazenado — sistema registra local (silo, tulha, armazém) e quantidade
13. Estoque de produto beneficiado é atualizado automaticamente
14. **Blending (opcional)**: Misturar lotes de origens diferentes para criar blend com características específicas
15. Quando comercializado, registra saída com destino, comprador e nota fiscal
16. Rastreabilidade completa: comprador pode rastrear do lote beneficiado até os insumos do campo

## Casos Extremos e Exceções

- **Lote com umidade crítica**: Umidade acima de 25% — priorizar secagem e alertar risco de fermentação

- **Secador quebrado**: Transferência para terreiro mid-processo — registrar mudança de método com justificativa

- **Blending de lotes**: Mistura de cafés de talhões diferentes para criar blend comercial — rastreabilidade deve listar todas as origens com percentuais

- **Reclassificação**: Lote classificado como tipo 6 na prova de xícara sobe para tipo 4 — permitir nova classificação mantendo histórico

- **Perda anormal**: Rendimento abaixo de 50% — alertar e exigir justificativa (possível erro de pesagem ou perda por praga)

- **Produto sem classificação padrão**: Cultura sem norma oficial (ex: macadâmia) — permitir classificação customizada por tenant

- **Armazenamento lotado**: Silo cheio — alertar e sugerir destinos alternativos

- **Contaminação cruzada**: Lote orgânico não pode ser misturado com convencional — sistema deve bloquear blending

- **Recall de lote beneficiado**: Se lote de origem tem problema (resíduo de defensivo), sistema deve identificar todos os lotes beneficiados derivados

- **Umidade não atinge alvo**: Secador com problema não consegue baixar umidade — alertar para manutenção

## Critérios de Aceite (Definition of Done)

- [ ] Registro de entrada com peso bruto, umidade e vínculo ao romaneio
- [ ] Controle de secagem com leituras periódicas de umidade e temperatura
- [ ] Alerta quando umidade atinge nível alvo
- [ ] Classificação com campos específicos por tipo de produto (café, soja, milho)
- [ ] Cálculo automático de rendimento (peso beneficiado / peso bruto)
- [ ] Propagação de rastreabilidade: lote beneficiado → lotes de produção → insumos
- [ ] Blending com rastreabilidade multi-origem e percentuais
- [ ] Registro de saída com destino e nota fiscal
- [ ] Atualização automática de estoque de produto beneficiado
- [ ] Tenant isolation e RBAC testados
- [ ] Componente frontend `beneficiamento-cafe.tsx` integrado
- [ ] Tabelas de classificação MAPA integradas (café, soja, milho)
- [ ] Custo de beneficiamento rateado por lote

## Sugestões de Melhoria Futura

1. **IoT para secagem**: Sensores de umidade e temperatura com leitura automática em tempo real

2. **Classificação por visão computacional**: Câmera analisa grãos e classifica defeitos automaticamente

3. **Prova de xícara digital**: Registro completo de cupping com formulário SCA (Specialty Coffee Association)

4. **Integração com balança**: Leitura automática de peso na entrada e saída do beneficiamento

5. **Controle de energia**: Monitorar consumo energético do secador por lote para custeio preciso

6. **Marketplace de lotes**: Publicar lotes classificados em marketplace B2B para compradores

7. **Certificação de origem**: Gerar selo de origem digital com QR Code vinculado à rastreabilidade completa

8. **Predição de qualidade**: IA que prevê classificação final baseada em dados de secagem e origem

9. **Integração com indústria**: Enviar dados de qualidade automaticamente para comprador (usina, trading)

10. **Controle de pragas de armazenamento**: Monitorar temperatura do silo para detectar infestação de gorgulho

11. **Rastreabilidade de embalagens**: Vincular lote beneficiado a embalagens (sacos, big bags) para venda

12. **Integração comweighbridge**: Balança rodoviária integrada para pesagem automática de caminhões
