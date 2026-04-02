"""
Atualização do main.py para usar estrutura de arquivos correta.
Este arquivo substitui as importações antigas pelas novas.
"""

# Substituir estas linhas no main.py:

# ANTIGO (não funciona mais):
# from ia_diagnostico.routers import router as router_ia_diagnostico

# NOVO (usar este formato):
from ia_diagnostico.routers.pragas_doencas import router as ia_pragas_doencas_router
from ia_diagnostico.routers.tratamentos import router as ia_tratamentos_router
from ia_diagnostico.routers.diagnosticos import router as ia_diagnosticos_router

# Incluir no app.include_router:
app.include_router(ia_pragas_doencas_router, prefix="/api/v1")
app.include_router(ia_tratamentos_router, prefix="/api/v1")
app.include_router(ia_diagnosticos_router, prefix="/api/v1")

# Repetir para todos os módulos:
# - iot_integracao (john_deere, case_ih, whatsapp, comparador_precos)
# - agricola/amostragem_solo (amostras, mapas_fertilidade, prescricoes_vra)
# - agricola/ndvi_avancado (ndvi, irrigacao, meteorologia)
# - core/api_publica (keys, logs, versions, sdks)
# - enterprise (sap, powerbi, benchmarks, preditivo, pontos)
