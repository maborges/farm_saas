# Análise de Mercado - AgroSaaS vs Concorrentes

**Versão:** 1.0.0
**Data:** 2026-03-31
**Status:** Ativo

---

## 📊 Resumo Executivo

Esta análise compara os módulos do AgroSaaS com os 5 principais softwares de gestão agrícola disponíveis no Brasil:

| # | Software | Empresa | Diferencial Principal |
|---|----------|---------|----------------------|
| 1 | **Aegro** | Orbia/Impulso Bayer | Líder de mercado, app offline robusto |
| 2 | **MyFarm** | Aliare | UX focado em usabilidade |
| 3 | **SSCrop** | Consisa | Usuários ilimitados, fiscal completo |
| 4 | **Agrotools** | Agrotools | IA e supply chain intelligence |
| 5 | **eProdutor** | eProdutor | Pecuária especializada (aves, peixes) |

---

## 🏆 Ranking de Funcionalidades por Categoria

### Gestão Financeira
| Posição | Software | Destaque |
|---------|----------|----------|
| 1 | SSCrop | Conciliação bancária automática, LCDPR integrado |
| 2 | Aegro | Integração contábil múltipla, NF-e/MDF-e grátis |
| 3 | MyFarm | Agendamento de pagamentos |
| 4 | AgroSaaS | ✅ Plano de contas, rateios, conciliação |
| 5 | eProdutor | Multi-atividade |

**Gaps identificados no AgroSaaS:**
- ❌ Emissão de NF-e/MDF-e não implementada
- ❌ Integração com bancos para conciliação automática
- ❌ LCDPR (Livro Caixa Digital) não mencionado

---

### Gestão Agrícola
| Posição | Software | Destaque |
|---------|----------|----------|
| 1 | Aegro | Comparação de preços de insumos regional |
| 2 | MyFarm | Indicadores climáticos integrados |
| 3 | eProdutor | Imagens de satélite, mapa de fertilidade |
| 4 | AgroSaaS | ✅ Fases da safra, NDVI, prescrições |
| 5 | SSCrop | Apontamentos de campo |

**Gaps identificados no AgroSaaS:**
- ⚠️ Comparação de preços de insumos com outros produtores (EXT_IA poderia incluir)
- ⚠️ Alertas climáticos em tempo real
- ✅ NDVI e agricultura de precisão já previstos

---

### Controle de Estoque
| Posição | Software | Destaque |
|---------|----------|----------|
| 1 | SSCrop | Alertas via WhatsApp, localização por ponto |
| 2 | Aegro | Integração campo-financeiro |
| 3 | MyFarm | Recebimento XML de mercadorias |
| 4 | AgroSaaS | ✅ Múltiplos depósitos, reservas, rastreabilidade |
| 5 | eProdutor | Básico |

**Gaps identificados no AgroSaaS:**
- ❌ Alertas de estoque mínimo via WhatsApp
- ❌ Recebimento de XML de notas fiscais
- ⚠️ Localização física dentro do depósito (endereço)

---

### Maquinário e Frota
| Posição | Software | Destaque |
|---------|----------|----------|
| 1 | MyFarm | Alertas de manutenção programada, consumo médio |
| 2 | Aegro | Conexão com máquinas e clima |
| 3 | AgroSaaS | ✅ Planos de manutenção, OS, histórico |
| 4 | SSCrop | Básico |
| 5 | eProdutor | Básico |

**Gaps identificados no AgroSaaS:**
- ⚠️ Alertas automáticas de manutenção preventiva
- ⚠️ Cálculo de consumo médio de combustível por atividade
- ❌ Integração direta com telemetria de máquinas

---

### Pecuária
| Posição | Software | Destaque |
|---------|----------|----------|
| 1 | eProdutor | Sensores IoT, ambiência, consumo em tempo real |
| 2 | AgroSaaS | ✅ Eventos append-only, genealogia, categorias |
| 3 | Aegro | Suporte a múltiplas culturas incluindo pecuária |
| 4 | MyFarm | Básico |
| 5 | SSCrop | Não mencionado |

**Gaps identificados no AgroSaaS:**
- ❌ Sensores IoT para ambiência e consumo
- ❌ Comparação com padrões genéticos de referência
- ❌ Treinamento de funcionários via app
- ⚠️ Módulo de leite básico (falta qualidade detalhada)

---

### Compliance Fiscal
| Posição | Software | Destaque |
|---------|----------|----------|
| 1 | SSCrop | Emissor NFP-e, download automático SEFAZ |
| 2 | Aegro | NF-e/MDF-e grátis ilimitado, integração contábil |
| 3 | MyFarm | NFe, MDF-e, LCDPR |
| 4 | AgroSaaS | 📋 Planejado (F3_FISCAL) |
| 5 | eProdutor | Básico |

**Gaps identificados no AgroSaaS:**
- ❌ Emissor de notas fiscais (NFP-e, NF-e)
- ❌ Download automático de notas da SEFAZ
- ❌ Integração com sistemas contábeis (Domínio, Fortes, Contmatic)
- ❌ LCDPR não implementado

---

### Mobile e Offline
| Posição | Software | Destaque |
|---------|----------|----------|
| 1 | Aegro | App 100% offline, sincronização automática |
| 2 | MyFarm | App com registro de atividades e abastecimento |
| 3 | AgroSaaS | ✅ PWA planejado |
| 4 | SSCrop | Web-based |
| 5 | eProdutor | Web-based |

**Gaps identificados no AgroSaaS:**
- ❌ App nativo offline não implementado
- ❌ Registro de abastecimento e chuva via mobile
- ⚠️ PWA em desenvolvimento (não mencionado no código)

---

### Integrações
| Posição | Software | Destaque |
|---------|----------|----------|
| 1 | Aegro | Bancos, contabilidade, API aberta, pontos Orbia/Bayer |
| 2 | AgroSaaS | ✅ Stripe, APIs internas |
| 3 | MyFarm | Integrações genéricas |
| 4 | SSCrop | SEFAZ, contabilidade |
| 5 | Agrotools | Sistemas corporativos |

**Gaps identificados no AgroSaaS:**
- ❌ Integração com bancos brasileiros (PIX, extrato)
- ❌ Integração com sistemas contábeis
- ❌ Programas de pontos (parcerias)
- ⚠️ API pública para clientes não documentada

---

## 📈 Matriz de Posicionamento

### Por Tamanho de Cliente

| Porte | Melhor Opção | AgroSaaS Posição |
|-------|--------------|------------------|
| Pequeno (<500 ha) | Aegro, SSCrop | ✅ Competitivo (planos acessíveis) |
| Médio (500-5000 ha) | MyFarm, Aegro | ✅ Ideal |
| Grande (>5000 ha) | Agrotools, eProdutor | ⚠️ Precisa de EXT_ERP |
| Pecuária Especializada | eProdutor, GerBov | ⚠️ P2-P4 precisam acelerar |

---

## 🎯 Gaps Críticos do AgroSaaS

### 🔴 Gaps Bloqueantes (Alta Prioridade)

| Gap | Impacto | Esforço | Prioridade |
|-----|---------|---------|------------|
| Emissão NF-e/MDF-e | Fiscal obrigatório | Alto | 🔴 Crítica |
| LCDPR (Livro Caixa Digital) | Contabilidade rural | Médio | 🔴 Crítica |
| App mobile offline | Usabilidade campo | Alto | 🔴 Crítica |
| Conciliação bancária automática | Financeiro | Médio | 🔴 Crítica |

### 🟡 Gaps Competitivos (Média Prioridade)

| Gap | Impacto | Esforço | Prioridade |
|-----|---------|---------|------------|
| Alertas WhatsApp (estoque) | UX | Baixo | 🟡 Alta |
| Integração sistemas contábeis | Enterprise | Alto | 🟡 Alta |
| Comparação preços insumos | Diferencial | Médio | 🟡 Média |
| Recebimento XML NF | Operacional | Médio | 🟡 Média |
| Alertas manutenção preventiva | Frota | Baixo | 🟡 Média |

### 🟢 Gaps de Inovação (Baixa Prioridade)

| Gap | Impacto | Esforço | Prioridade |
|-----|---------|---------|------------|
| Sensores IoT pecuária | Pecuária | Alto | 🟢 Baixa |
| API pública documentada | Devs | Médio | 🟢 Baixa |
| Programa de pontos | Parcerias | Alto | 🟢 Baixa |
| Imagens de satélite avançadas | Precisão | Alto | 🟢 Baixa |

---

## 💰 Análise de Preços

| Software | Preço Base | Modelo |
|----------|------------|--------|
| Aegro | R$ 529/mês | Por fazenda |
| MyFarm | Sob consulta | Personalizado |
| SSCrop | Sob consulta | Por usuários |
| AgroSaaS | R$ 199-1299/mês | Por módulo |
| eProdutor | Sob consulta | Por atividade |

**Posicionamento AgroSaaS:**
- ✅ Mais flexível (módulos avulsos)
- ✅ Mais acessível para pequenos
- ⚠️ Pode parecer fragmentado vs "tudo incluso"

---

## 🎯 Recomendações Estratégicas

### Curto Prazo (1-3 meses)

1. **Implementar F3_FISCAL**
   - Emissão NFP-e/NF-e
   - Download automático SEFAZ
   - LCDPR integrado

2. **Acelerar App Mobile**
   - PWA com offline-first
   - Registro de atividades offline
   - Sincronização automática

3. **Conciliação Bancária**
   - Integração com Open Banking
   - Importação OFX
   - Casamento automático

### Médio Prazo (3-6 meses)

4. **Alertas Inteligentes**
   - WhatsApp para estoque mínimo
   - SMS para manutenções
   - Push notifications

5. **Integrações Contábeis**
   - Domínio Sistemas
   - Fortes
   - Contmatic

6. **Comparador de Preços**
   - Crowdsourcing regional
   - Histórico de compras
   - Sugestões de negociação

### Longo Prazo (6-12 meses)

7. **IoT Pecuária**
   - Sensores de ambiência
   - Balanças inteligentes
   - Cochos automatizados

8. **API Pública**
   - Documentação aberta
   - Sandbox para devs
   - Marketplace de integrações

---

## 📊 Score Competitivo

| Módulo | AgroSaaS | Aegro | MyFarm | SSCrop | eProdutor | Agrotools |
|--------|----------|-------|--------|--------|-----------|-----------|
| Core/Backoffice | ✅ 9/10 | 7/10 | 7/10 | 6/10 | 6/10 | 8/10 |
| Agrícola | ✅ 8/10 | 9/10 | 8/10 | 7/10 | 8/10 | 7/10 |
| Financeiro | 🟡 6/10 | 9/10 | 8/10 | 9/10 | 7/10 | 8/10 |
| Estoque/Compras | ✅ 8/10 | 8/10 | 7/10 | 9/10 | 6/10 | 9/10 |
| Frota | ✅ 7/10 | 8/10 | 9/10 | 6/10 | 6/10 | 7/10 |
| Pecuária | 🟡 6/10 | 7/10 | 6/10 | 5/10 | 9/10 | 6/10 |
| Fiscal/Compliance | ❌ 3/10 | 9/10 | 8/10 | 9/10 | 7/10 | 9/10 |
| Mobile/Offline | ❌ 3/10 | 10/10 | 8/10 | 6/10 | 6/10 | 7/10 |
| Integrações | 🟡 6/10 | 10/10 | 7/10 | 8/10 | 7/10 | 9/10 |
| **Total** | **56/90** | **77/90** | **70/90** | **65/90** | **62/90** | **70/90** |

---

## ✅ Pontos Fortes do AgroSaaS

1. **Arquitetura Multi-tenant Moderna**
   - SaaS nativo vs legacy adaptado
   - Isolamento por tenant
   - Escalabilidade horizontal

2. **Modularidade**
   - Pague pelo que usa
   - Fácil upsell
   - Menor barreira de entrada

3. **Backoffice Completo**
   - CRM integrado
   - Gestão de assinaturas
   - Suporte técnico
   - Base de conhecimento

4. **Agricultura de Precisão**
   - NDVI integrado
   - Prescrição VRA
   - Dados climáticos

5. **Rastreabilidade**
   - Append-only para eventos
   - Histórico completo
   - Compliance

---

## ⚠️ Pontos de Atenção

1. **Fiscal é Obrigatório**
   - Produtores rurais precisam emitir notas
   - Contadores exigem LCDPR
   - Sem isso, não competem com Aegro/SSCrop

2. **Mobile é Crítico**
   - 80% do uso é no campo
   - Internet rural é instável
   - Offline-first não é opcional

3. **Integrações São Esperadas**
   - Bancos (PIX, extrato)
   - Contabilidade
   - Máquinas (John Deere, Case)

4. **Pecuária é Nicho Lucrativo**
   - eProdutor domina aves/peixes
   - GerBov domina bovinos
   - Precisa de diferenciação

---

## 📋 Próximos Passos

1. **Priorizar F3_FISCAL** - Implementar emissão de notas e LCDPR
2. **Acelerar Mobile** - PWA offline-first
3. **Parcerias Bancárias** - Open Banking, conciliação
4. **Integrações Contábeis** - Domínio, Fortes, Contmatic
5. **Alertas WhatsApp** - Baixo esforço, alto impacto

---

**Documentos Individuais por Módulo:**
- `03-01-modulo-core.md`
- `03-02-modulo-agricola.md`
- `03-03-modulo-pecuaria.md`
- `03-04-modulo-financeiro.md`
- `03-05-modulo-operacional.md`
- `03-06-modulo-rh.md`
- `03-07-modulo-ambiental.md`
- `03-08-modulo-extensoes.md`
