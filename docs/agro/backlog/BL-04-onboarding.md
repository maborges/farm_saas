# BL-04 — Onboarding

**Módulo:** core/onboarding  
**Frente:** Frontend + Backend  
**Dependências:** BL-01, BL-02, BL-06 (CEP/CNPJ)  
**Estimativa:** 2 dias

---

## Contexto

Wizard de primeiro acesso para guiar o usuário desde o cadastro até ter
uma Propriedade configurada e pronta para uso.
Fluxo deve ser fluente e sem atrito — produtor rural não é usuário técnico.

---

## User Stories

### US-04.1 — Wizard de Primeiro Acesso
**Como** novo usuário,  
**quero** ser guiado em um fluxo simples de configuração inicial,  
**para** ter minha propriedade cadastrada rapidamente.

**Critérios de aceite:**
- [ ] Dispara automaticamente na primeira sessão (sem assinatura ativa)
- [ ] Wizard em 3 passos com barra de progresso
- [ ] Salva progresso (pode retomar se fechar)
- [ ] Skip disponível no passo 3 (convite de equipe)

**Passo 1 — Dados do Produtor:**
- [ ] Campo CPF/CNPJ com máscara
- [ ] Busca automática na Receita Federal ao sair do campo
- [ ] Nome/razão social preenchido automaticamente (editável)
- [ ] CEP → preenche endereço automaticamente

**Passo 2 — Primeira Propriedade:**
- [ ] Nome da propriedade
- [ ] Tipo: fazenda/sítio/chácara/arrendamento/parceria
- [ ] Área total (ha)
- [ ] CEP → município/UF automático
- [ ] CAR (opcional) — busca SICAR se informado

**Passo 3 — Convidar Equipe (opcional):**
- [ ] Campo de email + seleção de perfil
- [ ] Adicionar múltiplos convites
- [ ] Botão "Fazer isso depois"

---

### US-04.2 — Guard de Onboarding
**Como** sistema,  
**quero** redirecionar usuários sem configuração completa para o wizard,  
**para** garantir que a estrutura mínima seja criada antes de usar os módulos.

**Critérios de aceite:**
- [ ] `OnboardingGuard` verifica se assinatura tem ao menos 1 propriedade
- [ ] Redireciona para `/onboarding` se incompleto
- [ ] Não bloqueia rotas de `/settings/billing` e `/auth/*`

---

## Tarefas Técnicas

### Backend
- [ ] Endpoint `GET /onboarding/status` — retorna etapas completas/pendentes
- [ ] Endpoint `POST /onboarding/produtor` — cria Assinatura + dados do produtor
- [ ] Endpoint `POST /onboarding/propriedade` — cria primeira Propriedade
- [ ] Reutiliza endpoints de BL-01 e BL-02

### Frontend
- [ ] Página `/onboarding` com wizard multi-step
- [ ] Componente `StepIndicator` — barra de progresso
- [ ] Formulário Passo 1: `ProdutorForm` com lookup CPF/CNPJ
- [ ] Formulário Passo 2: `PropriedadeForm` com lookup CEP + CAR
- [ ] Formulário Passo 3: `ConviteEquipeForm` (reutilizável)
- [ ] `OnboardingGuard` component — já existe, adaptar para novo modelo
- [ ] Redirect pós-onboarding → dashboard principal
