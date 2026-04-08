# Bounded Contexts --- SaaS Agro

Este documento define a divisão do sistema usando DDD.

------------------------------------------------------------------------

## 1. Organização & Acesso

Responsável por: - Tenant - Usuários - Perfis - Permissões

------------------------------------------------------------------------

## 2. Estrutura Territorial

Gerencia: - Grupo Produtivo - Fazenda - Gleba - Talhão - Subtalhão -
Zona de Manejo - Piquetes

------------------------------------------------------------------------

## 3. Produção Agrícola

Responsável por: - Safras - Culturas - Plantio - Tratos culturais -
Colheita

------------------------------------------------------------------------

## 4. Produção Pecuária

Responsável por: - Rebanho - Lotes - Ciclos produtivos - Manejo de
pastagens

------------------------------------------------------------------------

## 5. Financeiro

Responsável por: - Custos por safra - Receitas - Centro de custos -
Resultado econômico

------------------------------------------------------------------------

## 6. Recursos Operacionais

-   Máquinas
-   Insumos
-   Equipes

------------------------------------------------------------------------

## 7. Comercialização

-   Contratos
-   Vendas
-   Entregas

------------------------------------------------------------------------

## Regra-chave

Contexts comunicam-se por eventos, nunca acesso direto ao banco.
