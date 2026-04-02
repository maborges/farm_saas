"""
Integração com ERP Sankhya - Sprint 25 (Refatorado)

Módulo responsável pela integração bidirecional com o ERP Sankhya via WS BPM.

Funcionalidades:
- Sincronização de cadastros (Pessoas, Produtos)
- Exportação/Importação de Notas Fiscais
- Integração financeira (Contas a Pagar/Receber)
- Sincronização de tabelas (CFOP, NCM)

Endpoints Sankhya WS:
- https://<servidor>/bpm/ws

Autenticação: Basic Auth (usuário/senha)
"""

__version__ = "1.0.0"
__author__ = "AgroSaaS Team"
