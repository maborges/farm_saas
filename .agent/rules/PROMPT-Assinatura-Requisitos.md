---
trigger: manual
---

# REQUISITOS — Sistema de Assinatura e Gestão de Acesso
> Prompt de requisitos para implementação. A IDE deve ler o contexto técnico
> já definido no projeto e tomar as decisões de implementação adequadas.

---

## Contexto

O AgroSaaS é uma plataforma modular de gestão agropecuária. Este documento
descreve os requisitos do sistema de assinatura, onboarding e controle de
acesso — a camada que governa quem pode acessar o quê antes de qualquer
funcionalidade agrícola ou pecuária.

Toda decisão de arquitetura, stack, padrões de código, segurança e estrutura
de pastas deve seguir o que já está definido no projeto (Dev Rules, stack
tecnológica, padrões de microsserviço).

---

## 1. Identidade Global

Toda pessoa que interage com a plataforma — seja como produtor, gestor,
agrônomo ou operador — possui uma única identidade global identificada pelo
seu endereço de e-mail. Essa identidade existe independentemente de qualquer
conta ou assinatura e persiste mesmo que a pessoa participe de múltiplas
contas ao longo do tempo. Associado ao e-mail, o usuário deve definir seu username. Ao criar ou alterar o username, deve-se verificar se já não existe para outro usuário.


Quando uma pessoa é convidada para uma conta, o sistema deve verificar se
o e-mail já possui identidade cadastrada. Em caso positivo, carrega
automaticamente as informações básicas já existentes (nome, foto de perfil).
Em caso negativo, cria a identidade e notifica a pessoa para completar
o cadastro.

---

## 2. Conta do Produtor

Uma conta (tenant) representa um produtor rural — pessoa física ou jurídica. É a
unidade central de isolamento de dados da plataforma: tudo que pertence a
um produtor (propriedades, safras, animais, financeiro) está vinculado
exclusivamente à sua conta.

Uma conta é criada por uma pessoa que se torna seu proprietário. O proprietário
tem acesso irrevogável e total à conta — não pode ser removido nem ter suas
permissões restringidas por outros membros.

Uma conta possui um ciclo de vida: começa pendente de pagamento, torna-se
ativa após a confirmação financeira, pode ser suspensa por inadimplência
e cancelada definitivamente. Enquanto pendente ou suspensa, os usuários
não devem conseguir acessar as funcionalidades operacionais da plataforma.

---

## 3. Assinatura e Módulos

Cada conta possui uma assinatura que define o plano contratado e os módulos
habilitados. Os módulos disponíveis correspondem aos blocos funcionais
já definidos no projeto (agrícola, pecuário, financeiro, operacional,
ambiental e plugins avançados).

A assinatura tem um ciclo de cobrança (mensal, trimestral ou anual) e uma
data de renovação. O sistema deve controlar o status da assinatura de forma
independente do status da conta — uma assinatura pode estar em renovação
enquanto a conta segue ativa, por exemplo.

A ativação dos módulos contratados só ocorre após a confirmação do pagamento
por um operador do financeiro da plataforma. Enquanto isso não acontece,
a conta existe mas não tem acesso operacional.

O produtor deve poder enviar um comprovante de pagamento. O operador financeiro
deve ter uma área para revisar os comprovantes pendentes, aprovar ou rejeitar
com justificativa. A aprovação deve ativar automaticamente a conta e os módulos.

---

## 4. Perfis de Acesso

Cada conta possui perfis de acesso que determinam o que um usuário pode fazer
dentro dela. A plataforma fornece um conjunto de perfis padrão que cobrem os
papéis mais comuns no contexto agropecuário (proprietário, administrador,
agrônomo, veterinário, operador de campo, financeiro, gerente, somente leitura).

Os perfis padrão não podem ser editados ou removidos pelo assinante — servem
como base confiável e sempre disponível.

Além dos perfis padrão, o assinante pode criar perfis personalizados para
atender necessidades específicas da sua operação. Um perfil personalizado
define quais módulos o usuário pode acessar e o nível de permissão em cada
um (somente leitura, leitura e escrita, aprovação).

---

## 5. Propriedades (Workareas)

Uma conta pode ter uma ou mais propriedades rurais cadastradas. Cada
propriedade representa uma fazenda, sítio ou área de produção geograficamente
identificada. Todo dado operacional da plataforma (talhões, rebanhos, safras,
operações) está associado a uma propriedade específica.

O cadastro de propriedades acontece durante o onboarding e pode ser expandido
a qualquer momento. Uma propriedade pode ser desativada sem perda de histórico.

---

## 6. Usuários e Associações

O assinante pode convidar pessoas para ter acesso à sua conta. Ao convidar,
deve definir:

- Em quais propriedades essa pessoa terá acesso, todas devem ser explicitamente apontadas.
- Qual perfil essa pessoa terá (um dos perfis padrão ou um perfil
  personalizado criado pelo assinante)
- Opcionalmente, uma data de validade para o acesso (útil para prestadores
  de serviço temporários)

Um usuário convidado recebe uma notificação por e-mail da plataforma solicitando que o usuário entre no link do assinante e se logue para confirmar o convite e ter o acesso liberado. Enquanto o convite estiver pendente, o usuário não acessa a conta.

Um mesmo usuário pode participar de múltiplas contas com perfis e permissões
diferentes em cada uma. Por exemplo, um agrônomo pode ser membro da conta
de três produtores diferentes, com níveis de acesso distintos em cada uma.

---

## 7. Gestor Multi-contas

Uma pessoa pode assumir o papel de gestor de múltiplos produtores. Esse
perfil é típico de contadores rurais, consultores agronômicos, cooperativas
e escritórios de gestão que atendem vários clientes.

O gestor pode ser o próprio criador das contas dos produtores que gerencia
ou pode ser convidado para contas que os próprios produtores criaram.
Quando um usuário cria uma conta/assinatura ele automaticamente passa a ser gestor da conta;

O gestor deve ter uma visão centralizada de todas as contas que administra,
com a possibilidade de alternar entre elas de forma fluida — sem necessidade
de novo login a cada troca. Ao alternar de conta, o contexto do sistema
muda completamente para refletir os dados e permissões daquela conta.

---

## 8. Fluxo de Onboarding

Após a confirmação do pagamento, o novo assinante deve ser guiado por um
fluxo de configuração inicial da conta antes de acessar as funcionalidades
operacionais. Esse fluxo deve ser simples, progressivo e permitir que
etapas sejam concluídas depois, sem bloquear totalmente o acesso.

O fluxo deve cobrir, na seguinte ordem:

**Etapa 1 — Propriedades:** o assinante cadastra as propriedades rurais
que serão gerenciadas na plataforma. Deve poder adicionar quantas quiser
e editar depois.

**Etapa 2 — Perfis:** o assinante visualiza os perfis padrão disponíveis
e decide se precisa criar perfis personalizados para sua operação. Pode
pular se os padrões forem suficientes.

**Etapa 3 — Usuários:** o assinante convida as pessoas que terão acesso
à conta, define as propriedades e perfis de cada uma. Pode pular e fazer
depois.

Ao final do fluxo (ou ao pular todas as etapas), o assinante acessa o
dashboard principal da plataforma.

O progresso do onboarding deve ser rastreado para que o sistema saiba
quais etapas foram concluídas e possa exibir lembretes ou retomar o fluxo.

---

## 9. Painel do Financeiro (Interno)

A plataforma deve ter uma área restrita para operadores do financeiro
da AgroSaaS — não confundir com o módulo financeiro dos produtores.

Nessa área, o operador visualiza:

- Assinaturas aguardando confirmação de pagamento, com os dados do
  produtor, plano escolhido e comprovante anexado
- Histórico de assinaturas aprovadas e rejeitadas
- Capacidade de aprovar (ativando a conta imediatamente) ou rejeitar
  com justificativa (notificando o produtor)
- Capacidade de definir e precificar pacotes de produtos (módulos) para que sejam comercializados e apresentados na landingpage

O acesso a essa área é exclusivo de usuários internos da AgroSaaS com
permissão específica — nenhum produtor ou gestor pode visualizá-la.

---

## 10. Regras de Negócio Transversais

**Isolamento de dados:** nenhum dado de uma conta deve ser visível ou
acessível por usuários de outra conta, independentemente do perfil ou
nível de acesso.

**Acesso condicional ao módulo:** qualquer funcionalidade vinculada a um
módulo específico deve verificar se aquele módulo está ativo na assinatura
da conta antes de permitir o acesso. Módulo inativo significa acesso negado,
independentemente do perfil do usuário.

**Hierarquia de acesso por propriedade:** um usuário com acesso restrito
a propriedades específicas não pode ver nem interagir com dados de
propriedades às quais não foi associado.

**Validade de acesso:** acessos com data de validade definida devem ser
revogados automaticamente na data informada, sem necessidade de ação manual.

**Convite por e-mail já cadastrado:** ao convidar um e-mail já existente
na plataforma, o sistema deve pré-preencher as informações disponíveis e
não criar uma nova identidade duplicada.

**Unicidade de vínculo:** um usuário não pode ter dois vínculos ativos
na mesma conta. Se já é membro, o sistema deve informar e oferecer a
opção de editar o vínculo existente.

**Conta suspensa:** usuários gestor de uma conta suspensa não acessam as
funcionalidades operacionais, mas devem conseguir visualizar o motivo
da suspensão e as instruções para regularização.

**Histórico preservado:** cancelamentos, remoções de usuário e desativações
de propriedade não apagam dados históricos — apenas marcam os registros
como inativos.

---

## 11. Notificações

O sistema deve notificar as pessoas nos seguintes eventos:

- Novo convite recebido para uma conta
- Convite expirado sem aceite
- Conta ativada após confirmação do pagamento
- Conta suspensa por inadimplência
- Assinatura rejeitada pelo financeiro (com justificativa)
- Acesso temporário prestes a expirar (aviso com 7 dias de antecedência)
- Acesso temporário expirado

---

## 12. O que NÃO é escopo deste módulo

- Processamento automático de pagamentos ou integração com gateway
- Emissão de nota fiscal para o produtor
- Relatórios financeiros da AgroSaaS (receita, churn, MRR)
- Funcionalidades operacionais agropecuárias (safras, animais, etc.)
