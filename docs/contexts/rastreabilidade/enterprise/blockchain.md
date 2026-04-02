---
modulo: Rastreabilidade
submodulo: Blockchain
nivel: enterprise
core: false
dependencias_core:
  - fazendas
dependencias_modulos:
  - ../essencial/lotes-producao.md
  - ../profissional/cadeia-custodia.md
  - ../enterprise/certificacoes.md
complexidade: XL
assinante_alvo:
  - grandes produtores de exportação
  - tradings
  - cooperativas premium
standalone: false
---

# Blockchain

## Descrição Funcional

Registro imutável de eventos de rastreabilidade em blockchain, criando uma camada de confiança verificável por terceiros sem depender do sistema do produtor. Cada evento crítico da cadeia — criação de lote, transferência de custódia, laudo de qualidade, certificação — é hasheado e registrado em uma rede blockchain (pública ou permissionada), gerando prova criptográfica de integridade e timestamp.

Não substitui o banco de dados do sistema. É uma camada complementar de prova imutável, voltada para mercados onde a confiança verificável é um diferencial ou exigência.

## Personas — Quem usa este submódulo

- **Diretor/CEO:** Usa blockchain como argumento comercial para mercados premium e exportação.
- **Comprador internacional:** Verifica a autenticidade da rastreabilidade independentemente do produtor.
- **Auditor:** Valida que os dados não foram alterados após o registro.
- **Equipe de TI:** Configura e monitora a integração com blockchain.

## Dores que resolve

- **"Como confiar no sistema do produtor?":** Comprador questiona se dados não foram alterados. Blockchain prova imutabilidade.
- **Fraude de rastreabilidade:** Concorrentes que falsificam origem ou certificação. Blockchain dificulta fraude.
- **Exigência de mercados premium:** Alguns importadores e redes exigem rastreabilidade com prova de integridade.
- **Disputas comerciais:** Em litígios sobre qualidade ou origem, blockchain serve como prova.

## Regras de Negócio

1. **Eventos selecionáveis:** Nem todo evento vai para blockchain (custo). Produtor configura quais eventos são registrados (criação de lote, fechamento, expedição, laudo, certificação).
2. **Hash, não dados:** Blockchain armazena hash dos dados + metadados mínimos. Dados completos ficam no sistema.
3. **Rede configurável:** Suporte a Polygon (público, baixo custo), Hyperledger (permissionado) ou rede do comprador.
4. **Verificação pública:** Qualquer pessoa pode verificar um hash na blockchain sem acessar o sistema.
5. **Custo por transação:** Cada registro tem custo. Sistema exibe estimativa e permite configurar limite mensal.
6. **Fallback:** Se blockchain estiver indisponível, evento é enfileirado e registrado assim que possível. Dados no sistema não são bloqueados.
7. **Prova de timestamp:** Timestamp da blockchain prova que o dado existia naquele momento.
8. **Multi-tenant:** Cada tenant tem sua própria wallet/identidade na rede.

## Entidades de Dados Principais

- **BlockchainRegistro:** `id`, `tenant_id`, `lote_id`, `evento_tipo`, `dados_hash` (SHA-256), `dados_resumo_json`, `rede` (polygon/hyperledger), `tx_hash`, `bloco_numero`, `timestamp_blockchain`, `status` (pendente/confirmado/falhou), `custo_estimado`, `created_at`
- **BlockchainConfig:** `id`, `tenant_id`, `rede_padrao`, `wallet_address`, `eventos_habilitados[]`, `limite_mensal_transacoes`, `ativo`
- **BlockchainVerificacao:** `id`, `registro_id`, `verificador_info`, `resultado` (valido/invalido/dados_alterados), `data_verificacao`

## Integrações Necessárias

- **Lotes de Produção:** Eventos de criação, fechamento, expedição.
- **Cadeia de Custódia:** Eventos de transferência.
- **Laudos e Análises:** Hash do laudo registrado na blockchain.
- **Certificações:** Registro de certificação emitida.
- **QR Code:** Página pública inclui link para verificação na blockchain.
- **API de blockchain:** Polygon RPC, Hyperledger Fabric SDK ou similar.

## Fluxo de Uso Principal (step-by-step)

1. Admin configura blockchain: rede, wallet, eventos habilitados, limite de custo.
2. Evento habilitado ocorre no sistema (ex: lote fechado).
3. Sistema calcula hash SHA-256 dos dados do evento.
4. Hash + metadados são enviados à rede blockchain como transação.
5. Transação é confirmada → `tx_hash` e `bloco_numero` são salvos.
6. Na página pública do lote (QR code), seção "Verificação Blockchain" mostra link para o explorer da rede.
7. Qualquer pessoa clica no link, vê a transação na blockchain e pode recalcular o hash para comparar.
8. Em caso de disputa, o hash na blockchain prova que os dados existiam naquela data e não foram alterados.

## Casos Extremos e Exceções

- **Blockchain indisponível:** Evento é enfileirado com retry exponencial. Após 24h sem sucesso, alerta ao admin.
- **Custo acima do limite:** Sistema pausa registros e notifica admin. Eventos ficam em fila para quando limite for ampliado.
- **Dados alterados no sistema após registro:** Na verificação, hash não bate → sistema indica "dados alterados após registro blockchain". Isso é proposital e detectável.
- **Migração de rede:** Se produtor trocar de rede, registros antigos permanecem na rede anterior. Novos vão para a nova.
- **Wallet comprometida:** Procedimento de rotação de wallet com registro de transição na blockchain.
- **Volume muito alto:** Batching — agrupar múltiplos eventos em uma única transação (Merkle tree).

## Critérios de Aceite (Definition of Done)

- [ ] Configuração de rede blockchain por tenant
- [ ] Seleção de eventos a registrar
- [ ] Cálculo de hash SHA-256 dos dados do evento
- [ ] Envio de transação para blockchain (Polygon como rede padrão)
- [ ] Armazenamento de tx_hash e bloco_numero
- [ ] Página de verificação pública (recalcular hash e comparar)
- [ ] Fila de retry para blockchain indisponível
- [ ] Controle de custo com limite mensal
- [ ] Integração com QR code (link de verificação)
- [ ] Teste de tenant isolation (wallets separadas)

## Sugestões de Melhoria Futura

- **NFT de lote:** Cada lote pode gerar um NFT com metadados de rastreabilidade — transferível na venda.
- **Smart contracts:** Contratos inteligentes para liberação automática de pagamento após verificação de entrega/qualidade.
- **Rede do setor:** Participar de blockchain setorial do agro (ex: iniciativas da ABAG ou cooperativas).
- **Zero-knowledge proofs:** Provar conformidade sem revelar dados sensíveis (ex: provar que não usou produto proibido sem revelar o que usou).
- **Tokenização de créditos:** Tokenizar créditos de carbono ou certificações para comercialização.
