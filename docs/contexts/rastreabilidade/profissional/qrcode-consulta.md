---
modulo: Rastreabilidade
submodulo: QR Code de Consulta
nivel: profissional
core: false
dependencias_core:
  - fazendas
dependencias_modulos:
  - ../essencial/lotes-producao.md
  - ../essencial/origem-destino.md
  - ../essencial/historico-aplicacoes.md
  - ../profissional/cadeia-custodia.md
complexidade: S
assinante_alvo:
  - produtor com venda direta
  - cooperativas
  - agroindústrias com marca própria
standalone: false
---

# QR Code de Consulta

## Descrição Funcional

Gera QR codes únicos para cada lote de produção, permitindo que qualquer pessoa — comprador, consumidor final, fiscal — escaneie o código e acesse uma página pública com informações de rastreabilidade do produto. A página mostra origem, data de colheita, histórico de aplicações resumido, certificações e caminho percorrido.

O QR code é a ponte entre o mundo físico (embalagem, caixa, pallet) e o mundo digital (dados completos de rastreabilidade no sistema). Agrega valor ao produto e diferencia o produtor no mercado.

## Personas — Quem usa este submódulo

- **Consumidor final:** Escaneia o QR no produto e vê de onde veio, como foi produzido.
- **Comprador B2B:** Valida rapidamente a rastreabilidade do lote recebido.
- **Setor de marketing do produtor:** Usa o QR como diferencial de venda e transparência.
- **Fiscal:** Acessa dados básicos do lote sem precisar acessar o sistema.

## Dores que resolve

- **Falta de transparência:** Consumidor não sabe de onde vem o alimento. QR code resolve isso instantaneamente.
- **Diferencial competitivo zero:** Produtos rastreáveis com QR vendem melhor e com preço premium.
- **Consulta manual por telefone/e-mail:** Compradores pedem informações de rastreabilidade por telefone. QR elimina essa demanda.
- **Fiscalização lenta:** Fiscal precisa solicitar documentos ao produtor. Com QR, acessa na hora.

## Regras de Negócio

1. **Um QR por lote:** Cada lote tem exatamente um QR code. Sublotes de fracionamento recebem seus próprios QR codes.
2. **URL pública e segura:** QR aponta para URL pública (sem login) com token único não sequencial (UUID ou hash).
3. **Informações configuráveis:** Produtor define quais informações aparecem na página pública (origem, aplicações, certificações, etc.).
4. **Dados sensíveis ocultos:** Informações financeiras, nome de funcionários e dados internos nunca aparecem na página pública.
5. **QR ativo/inativo:** Produtor pode desativar QR de um lote (ex: recall). Página mostra mensagem de indisponibilidade.
6. **Geração em lote:** Possível gerar QR codes para múltiplos lotes de uma vez, com download em PDF para impressão.
7. **Personalização visual:** QR pode incluir logo da fazenda/marca no centro (QR com logo).
8. **Contagem de acessos:** Sistema registra cada escaneamento (data, localização aproximada, dispositivo) para analytics.

## Entidades de Dados Principais

- **QRCodeLote:** `id`, `tenant_id`, `lote_id`, `token_publico` (UUID), `url_publica`, `configuracao_json` (campos visíveis), `logo_url`, `ativo`, `created_at`
- **QRCodeAcesso:** `id`, `qrcode_id`, `data_hora`, `ip_hash`, `user_agent`, `localizacao_aproximada`, `referrer`
- **PaginaPublicaConfig:** `id`, `tenant_id`, `template` (basico/detalhado/premium), `cores_json`, `logo_url`, `texto_institucional`, `links_redes_sociais`

## Integrações Necessárias

- **Lotes de Produção:** Dados do lote para exibição.
- **Origem-Destino:** Informações de origem para a página pública.
- **Histórico de Aplicações:** Resumo de insumos aplicados (sem detalhes técnicos sensíveis).
- **Cadeia de Custódia:** Timeline simplificada do caminho do produto.
- **Certificações (enterprise):** Selos e certificados válidos para exibição.
- **Serviço de geração de QR:** Biblioteca interna ou API para gerar imagens QR.

## Fluxo de Uso Principal (step-by-step)

1. Lote é fechado → sistema gera automaticamente `QRCodeLote` com token único.
2. Produtor acessa configuração e define quais informações aparecem na página pública.
3. Produtor personaliza visual (logo, cores, texto institucional) — configuração vale para todos os QRs do tenant.
4. Produtor baixa QR code em PDF (individual ou em lote) para impressão em etiquetas/embalagens.
5. QR é impresso e afixado no produto/embalagem/caixa.
6. Consumidor/comprador escaneia QR com celular.
7. Navegador abre página pública com dados do lote: origem, data, cultura, certificações, timeline.
8. Sistema registra o acesso para analytics.

## Casos Extremos e Exceções

- **QR de lote cancelado:** Página exibe mensagem "Este lote foi recolhido/cancelado" com informações de contato do produtor.
- **QR de lote sem dados completos:** Página exibe apenas dados disponíveis com nota "informações em atualização".
- **Alto volume de acessos (viral):** Página pública deve ser cacheada (CDN) para suportar picos.
- **Tentativa de acesso a dados internos via URL:** Token público não permite acesso a dados além do configurado. Rotas internas exigem autenticação.
- **QR falsificado:** Cada QR tem hash de verificação. Página exibe selo "verificado" apenas para QR legítimos.
- **Impressão em baixa resolução:** QR gerado em SVG/vetor para manter legibilidade em qualquer tamanho.

## Critérios de Aceite (Definition of Done)

- [ ] Geração automática de QR code ao fechar lote
- [ ] Página pública acessível sem login com dados configuráveis
- [ ] Configuração de campos visíveis na página pública por tenant
- [ ] Personalização visual (logo, cores, texto)
- [ ] Download de QR em PDF (individual e em lote)
- [ ] Registro de acessos (analytics)
- [ ] Ativação/desativação de QR
- [ ] Página responsiva (mobile-first)
- [ ] Cache/CDN para página pública
- [ ] Teste que dados sensíveis não vazam na página pública

## Sugestões de Melhoria Futura

- **QR dinâmico:** Atualizar informações da página sem trocar o QR impresso.
- **Multilíngue:** Página pública em português, inglês e espanhol para exportação.
- **Vídeo do campo:** Permitir vincular vídeo curto da fazenda/colheita à página.
- **Feedback do consumidor:** Botão na página para consumidor avaliar o produto.
- **Integração com e-commerce:** QR linka para compra direta do produtor.
- **Dashboard de analytics:** Mapa de calor de escaneamentos, dispositivos, horários mais acessados.
