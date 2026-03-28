"""
Seed das escalas fenológicas padrão do sistema.
Uso: python -m agricola.fenologia.seed_escalas <tenant_id>
"""
import asyncio
import sys
import uuid
from core.database import async_session_maker
from core.models import Tenant  # noqa: F401 — FK resolution

ESCALAS_SOJA = [
    ("VE", "Emergência", "Cotilédones acima da superfície do solo", 1),
    ("VC", "Cotilédone", "Cotilédones completamente abertos", 2),
    ("V1", "1° nó", "1° nó com folha trifoliolada aberta", 3),
    ("V2", "2° nó", "2° nó com folha trifoliolada aberta", 4),
    ("V3", "3° nó", "3° nó com folha trifoliolada aberta", 5),
    ("V4", "4° nó", "4° nó com folha trifoliolada aberta", 6),
    ("V5", "5° nó", "5° nó com folha trifoliolada aberta", 7),
    ("V6", "6° nó", "6° nó com folha trifoliolada aberta", 8),
    ("R1", "Início floração", "Uma flor aberta em qualquer nó", 9),
    ("R2", "Floração plena", "Flor aberta em um dos 2 nós superiores", 10),
    ("R3", "Início vagem", "Vagem de 5 mm em um dos 4 nós superiores", 11),
    ("R4", "Vagem plena", "Vagem de 2 cm em um dos 4 nós superiores", 12),
    ("R5", "Início granação", "Grão detectável em vagem dos 4 nós superiores", 13),
    ("R5.1", "Granação 10%", "Grão com 10% de granação", 14),
    ("R5.3", "Granação 30%", "Grão com 30% de granação", 15),
    ("R5.5", "Granação 50%", "Grão com 50% de granação", 16),
    ("R5.7", "Granação 70%", "Grão com 70% de granação", 17),
    ("R6", "Vagem cheia", "Vagem contendo grão verde que preenche a cavidade", 18),
    ("R7", "Início maturação", "Uma vagem normal com cor de madura", 19),
    ("R8", "Maturação plena", "95% das vagens com cor de matura", 20),
]

ESCALAS_CAFE = [
    # Fase vegetativa
    ("B0",  "Gema dormente",       "Gema axilar em repouso, sem atividade visível", 1),
    ("B1",  "Gema intumescida",    "Gema começa a intumescer, escamas se separam", 2),
    ("B2",  "Gema aberta",         "Gema aberta, tecido verde visível", 3),
    # Indução floral
    ("C1",  "Botão floral fechado","Botões florais formados, pétalas fechadas (roseta)", 4),
    ("C2",  "Botão com pétalas brancas", "Pétalas brancas visíveis, flor prestes a abrir", 5),
    # Floração
    ("60",  "Início floração",     "< 10% das flores abertas (popcorn); início da antese", 6),
    ("65",  "Plena floração",      "≥ 50% das flores abertas; auge da antese", 7),
    ("69",  "Fim da floração",     "Pétalas caindo; < 10% flores abertas", 8),
    # Frutificação
    ("71",  "Chumbinho",           "Frutos recém-formados, diâmetro < 5 mm (chumbinho)", 9),
    ("73",  "Expansão do fruto",   "Frutos em expansão rápida, coloração verde-clara", 10),
    ("75",  "Fruto verde",         "Frutos completamente expandidos, consistência firme, cor verde-escura", 11),
    ("77",  "Fruto verde-cana",    "Início da mudança de coloração, verde amarelado", 12),
    # Maturação
    ("81",  "Cereja inicial",      "< 25% dos frutos no estágio cereja (vermelho ou amarelo)", 13),
    ("85",  "Cereja plena",        "50–75% dos frutos cereja; ponto ideal para colheita seletiva", 14),
    ("87",  "Cereja avançado",     "≥ 75% dos frutos cereja; ponto ótimo para derriça", 15),
    ("89",  "Passa",               "Frutos sobre-maduros, amolecidos, iniciando desidratação", 16),
    ("90",  "Seco no pé",          "Frutos desidratados na planta (café bóia seco)", 17),
]

ESCALAS_MILHO = [
    ("VE", "Emergência", "Coleóptilo visível acima do solo", 1),
    ("V1", "1ª folha", "Colar da 1ª folha visível", 2),
    ("V2", "2ª folha", "Colar da 2ª folha visível", 3),
    ("V3", "3ª folha", "Colar da 3ª folha visível", 4),
    ("V4", "4ª folha", "Colar da 4ª folha visível", 5),
    ("V5", "5ª folha", "Colar da 5ª folha visível", 6),
    ("V6", "6ª folha", "Colar da 6ª folha visível", 7),
    ("V8", "8ª folha", "Colar da 8ª folha visível", 8),
    ("V10", "10ª folha", "Colar da 10ª folha visível", 9),
    ("V12", "12ª folha", "Colar da 12ª folha visível", 10),
    ("VT", "Pendoamento", "Última ramificação do pendão visível", 11),
    ("R1", "Espigamento", "Estigmas visíveis fora das palhas", 12),
    ("R2", "Grão bolha d'água", "Grão com líquido claro", 13),
    ("R3", "Grão leitoso", "Grão com líquido leitoso", 14),
    ("R4", "Grão pastoso", "Grão com consistência pastosa", 15),
    ("R5", "Grão farináceo", "Metade do grão com amido sólido", 16),
    ("R6", "Maturidade fisiológica", "Camada preta formada na base do grão", 17),
]

async def seed(tenant_id: uuid.UUID):
    from agricola.fenologia.models import FenologiaEscala

    async with async_session_maker() as session:
        for codigo, nome, descricao, ordem in ESCALAS_SOJA:
            escala = FenologiaEscala(
                tenant_id=tenant_id,
                cultura="Soja",
                codigo=codigo,
                nome=nome,
                descricao=descricao,
                ordem=ordem,
                is_system=True,
                ativo=True,
            )
            session.add(escala)

        for codigo, nome, descricao, ordem in ESCALAS_MILHO:
            escala = FenologiaEscala(
                tenant_id=tenant_id,
                cultura="Milho",
                codigo=codigo,
                nome=nome,
                descricao=descricao,
                ordem=ordem,
                is_system=True,
                ativo=True,
            )
            session.add(escala)

        for codigo, nome, descricao, ordem in ESCALAS_CAFE:
            escala = FenologiaEscala(
                tenant_id=tenant_id,
                cultura="Café",
                codigo=codigo,
                nome=nome,
                descricao=descricao,
                ordem=ordem,
                is_system=True,
                ativo=True,
            )
            session.add(escala)

        await session.commit()
        print(f"Escalas fenológicas criadas para tenant {tenant_id}")
        print(f"  Soja:  {len(ESCALAS_SOJA)} estágios")
        print(f"  Milho: {len(ESCALAS_MILHO)} estágios")
        print(f"  Café:  {len(ESCALAS_CAFE)} estágios (BBCH adaptado)")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python -m agricola.fenologia.seed_escalas <tenant_id>")
        sys.exit(1)
    asyncio.run(seed(uuid.UUID(sys.argv[1])))
