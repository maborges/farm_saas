import uuid
from unittest.mock import AsyncMock, Mock

import pytest

from core.cadastros.pessoas.models import Pessoa
from operacional.models.compras import Fornecedor
from scripts import backfill_fornecedores_pessoa as backfill


pytestmark = pytest.mark.asyncio


class FakeSession:
    def __init__(self, pessoas=None):
        self.added = []
        self.pessoas = pessoas or {}
        self.rollbacks = 0
        self.commits = 0

    def add(self, obj):
        self.added.append(obj)

    async def flush(self):
        for obj in self.added:
            if getattr(obj, "id", None) is None:
                obj.id = uuid.uuid4()

    async def get(self, model, obj_id):
        if model is Pessoa:
            return self.pessoas.get(obj_id)
        return None

    async def commit(self):
        self.commits += 1

    async def rollback(self):
        self.rollbacks += 1


async def test_backfill_vincula_por_documento(monkeypatch):
    tenant_id = uuid.uuid4()
    pessoa = Pessoa(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        tipo="PJ",
        nome_exibicao="Fornecedor Documento",
        base_legal="CONTRATO",
        ativo=True,
    )
    fornecedor = Fornecedor(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        nome_fantasia="Fornecedor Documento",
        cnpj_cpf="12.345.678/0001-90",
    )
    session = FakeSession()
    stats = backfill.BackfillStats()

    monkeypatch.setattr(backfill, "fornecedor_ja_vinculado_corretamente", AsyncMock(return_value=False))
    monkeypatch.setattr(backfill, "_buscar_pessoa_por_documento", AsyncMock(return_value=pessoa))
    monkeypatch.setattr(backfill, "_buscar_pessoa_por_nome_normalizado", AsyncMock(return_value=None))
    monkeypatch.setattr(backfill, "_garantir_papel_fornecedor", AsyncMock())

    acao = await backfill.backfill_fornecedor(session, fornecedor, stats)

    assert acao == "documento"
    assert fornecedor.pessoa_id == pessoa.id
    assert stats.total_processado == 1
    assert stats.vinculados_documento == 1


async def test_backfill_vincula_por_nome_com_baixa_confianca(monkeypatch):
    tenant_id = uuid.uuid4()
    pessoa = Pessoa(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        tipo="PJ",
        nome_exibicao="Fornecedor Nome",
        base_legal="CONTRATO",
        ativo=True,
    )
    fornecedor = Fornecedor(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        nome_fantasia="Fornecedor Nome",
        cnpj_cpf=None,
    )
    session = FakeSession()
    stats = backfill.BackfillStats()
    logger_warning = Mock()

    monkeypatch.setattr(backfill, "fornecedor_ja_vinculado_corretamente", AsyncMock(return_value=False))
    monkeypatch.setattr(backfill, "_buscar_pessoa_por_documento", AsyncMock(return_value=None))
    monkeypatch.setattr(backfill, "_buscar_pessoa_por_nome_normalizado", AsyncMock(return_value=pessoa))
    monkeypatch.setattr(backfill, "_garantir_papel_fornecedor", AsyncMock())
    monkeypatch.setattr(backfill.logger, "warning", logger_warning)

    acao = await backfill.backfill_fornecedor(session, fornecedor, stats)

    assert acao == "nome"
    assert fornecedor.pessoa_id == pessoa.id
    assert stats.vinculados_nome == 1
    logger_warning.assert_called_once()


async def test_backfill_cria_pessoa_quando_nao_encontra_match(monkeypatch):
    tenant_id = uuid.uuid4()
    pessoa_criada = Pessoa(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        tipo="PJ",
        nome_exibicao="Fornecedor Novo",
        base_legal="CONTRATO",
        ativo=True,
    )
    fornecedor = Fornecedor(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        nome_fantasia="Fornecedor Novo",
        cnpj_cpf="12.345.678/0001-90",
    )
    session = FakeSession()
    stats = backfill.BackfillStats()

    resolve_mock = AsyncMock(return_value=pessoa_criada)
    monkeypatch.setattr(backfill, "fornecedor_ja_vinculado_corretamente", AsyncMock(return_value=False))
    monkeypatch.setattr(backfill, "_buscar_pessoa_por_documento", AsyncMock(return_value=None))
    monkeypatch.setattr(backfill, "_buscar_pessoa_por_nome_normalizado", AsyncMock(return_value=None))
    monkeypatch.setattr(backfill, "resolve_fornecedor", resolve_mock)

    acao = await backfill.backfill_fornecedor(session, fornecedor, stats)

    assert acao == "criado"
    assert fornecedor.pessoa_id == pessoa_criada.id
    assert stats.criados_novos == 1
    assert resolve_mock.await_args.args[2:] == ()
    assert resolve_mock.await_args.kwargs["nome_fantasia"] == "Fornecedor Novo"


async def test_backfill_respeita_vinculo_correto_e_garante_papel(monkeypatch):
    tenant_id = uuid.uuid4()
    pessoa_id = uuid.uuid4()
    fornecedor = Fornecedor(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        nome_fantasia="Fornecedor Ja Vinculado",
        cnpj_cpf="12.345.678/0001-90",
        pessoa_id=pessoa_id,
    )
    session = FakeSession()
    stats = backfill.BackfillStats()
    garantir_papel = AsyncMock()

    monkeypatch.setattr(backfill, "fornecedor_ja_vinculado_corretamente", AsyncMock(return_value=True))
    monkeypatch.setattr(backfill, "_garantir_papel_fornecedor", garantir_papel)

    acao = await backfill.backfill_fornecedor(session, fornecedor, stats)

    assert acao == "ja_vinculado"
    assert stats.ja_vinculados == 1
    garantir_papel.assert_awaited_once_with(session, tenant_id, pessoa_id)


async def test_fornecedor_ja_vinculado_corretamente_isola_tenant():
    tenant_correto = uuid.uuid4()
    tenant_errado = uuid.uuid4()
    pessoa = Pessoa(
        id=uuid.uuid4(),
        tenant_id=tenant_errado,
        tipo="PJ",
        nome_exibicao="Pessoa Errada",
        base_legal="CONTRATO",
        ativo=True,
    )
    fornecedor = Fornecedor(
        id=uuid.uuid4(),
        tenant_id=tenant_correto,
        nome_fantasia="Fornecedor",
        pessoa_id=pessoa.id,
    )
    session = FakeSession(pessoas={pessoa.id: pessoa})

    resultado = await backfill.fornecedor_ja_vinculado_corretamente(session, fornecedor)

    assert resultado is False
