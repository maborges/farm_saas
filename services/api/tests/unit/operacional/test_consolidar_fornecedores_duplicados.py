import uuid

import pytest

from operacional.models.compras import Fornecedor
from scripts import consolidar_fornecedores_duplicados as consolidacao


pytestmark = pytest.mark.asyncio


class FakeResult:
    def __init__(self, rowcount=0):
        self.rowcount = rowcount


class FakeSession:
    def __init__(self):
        self.added = []
        self.deleted = []
        self.executed = []

    def add(self, obj):
        self.added.append(obj)

    async def flush(self):
        return None

    async def execute(self, stmt):
        self.executed.append(stmt)
        return FakeResult(rowcount=2)

    async def delete(self, obj):
        self.deleted.append(obj)


async def test_merge_dados_fornecedor_preenche_apenas_lacunas():
    canonico = Fornecedor(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        nome_fantasia="Fornecedor A",
        cnpj_cpf=None,
        email=None,
        telefone="11999990000",
        condicoes_pagamento=None,
        prazo_entrega_dias=None,
        avaliacao=None,
    )
    duplicado = Fornecedor(
        id=uuid.uuid4(),
        tenant_id=canonico.tenant_id,
        nome_fantasia="Fornecedor B",
        cnpj_cpf="12345678000190",
        email="contato@fornecedor.test",
        telefone="1133334444",
        condicoes_pagamento="30 dias",
        prazo_entrega_dias=7,
        avaliacao=4.8,
    )

    alterou = consolidacao.merge_dados_fornecedor(canonico, duplicado)

    assert alterou is True
    assert canonico.nome_fantasia == "Fornecedor A"
    assert canonico.cnpj_cpf == "12345678000190"
    assert canonico.email == "contato@fornecedor.test"
    assert canonico.telefone == "11999990000"
    assert canonico.condicoes_pagamento == "30 dias"
    assert canonico.prazo_entrega_dias == 7
    assert canonico.avaliacao == 4.8


async def test_escolher_canonico_prioriza_referencias_e_depois_dados(monkeypatch):
    tenant_id = uuid.uuid4()
    pessoa_id = uuid.uuid4()
    fornecedor_a = Fornecedor(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        pessoa_id=pessoa_id,
        nome_fantasia="Fornecedor A",
        email="a@test",
    )
    fornecedor_b = Fornecedor(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        pessoa_id=pessoa_id,
        nome_fantasia="Fornecedor B",
        email="b@test",
        telefone="1199999",
        condicoes_pagamento="28 dias",
    )

    async def contar_refs(_session, fornecedor_id):
        return 5 if fornecedor_id == fornecedor_a.id else 1

    monkeypatch.setattr(consolidacao, "contar_referencias", contar_refs)

    canonico = await consolidacao.escolher_canonico(None, [fornecedor_a, fornecedor_b])

    assert canonico.id == fornecedor_a.id


async def test_consolidar_grupo_reaponta_referencias_remove_duplicado_e_e_idempotente(monkeypatch):
    tenant_id = uuid.uuid4()
    pessoa_id = uuid.uuid4()
    canonico = Fornecedor(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        pessoa_id=pessoa_id,
        nome_fantasia="Fornecedor Canonico",
        cnpj_cpf="12345678000190",
        email="contato@fornecedor.test",
    )
    duplicado = Fornecedor(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        pessoa_id=pessoa_id,
        nome_fantasia="Fornecedor Duplicado",
        cnpj_cpf=None,
        telefone="11988887777",
        condicoes_pagamento="30 dias",
    )
    session = FakeSession()
    stats = consolidacao.ConsolidacaoStats()
    estado = {"primeira": True}

    async def carregar(_session, _tenant_id, _pessoa_id):
        if estado["primeira"]:
            return [canonico, duplicado]
        return [canonico]

    async def escolher(_session, fornecedores):
        return fornecedores[0]

    monkeypatch.setattr(consolidacao, "carregar_fornecedores_grupo", carregar)
    monkeypatch.setattr(consolidacao, "escolher_canonico", escolher)

    resultado_1 = await consolidacao.consolidar_grupo(session, tenant_id, pessoa_id, stats)
    estado["primeira"] = False
    resultado_2 = await consolidacao.consolidar_grupo(session, tenant_id, pessoa_id, stats)

    assert resultado_1["status"] == "consolidado"
    assert resultado_1["canonico_id"] == canonico.id
    assert resultado_1["duplicados_removidos"] == [duplicado.id]
    assert resultado_1["referencias_reapontadas"] == 4
    assert canonico.telefone == "11988887777"
    assert canonico.condicoes_pagamento == "30 dias"
    assert duplicado in session.deleted
    assert stats.grupos_processados == 1
    assert stats.fornecedores_removidos == 1
    assert stats.referencias_reapontadas == 4

    assert resultado_2["status"] == "sem_duplicidade"
    assert stats.grupos_processados == 1


async def test_reapontar_referencias_soma_rowcounts():
    session = FakeSession()

    total = await consolidacao.reapontar_referencias(session, uuid.uuid4(), uuid.uuid4())

    assert total == 4
    assert len(session.executed) == len(consolidacao.REFERENCIAS_FORNECEDOR)
