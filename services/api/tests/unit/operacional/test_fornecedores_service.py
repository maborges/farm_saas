import uuid
from unittest.mock import AsyncMock

import pytest

from core.cadastros.pessoas.models import Pessoa, PessoaContato, PessoaDocumento, PessoaRelacionamento, TipoRelacionamento
from operacional.models.compras import Fornecedor
from operacional.services import fornecedores_service as service


pytestmark = pytest.mark.asyncio


class FakeSession:
    def __init__(self):
        self.added = []

    def add(self, obj):
        self.added.append(obj)

    async def flush(self):
        for obj in self.added:
            if getattr(obj, "id", None) is None:
                obj.id = uuid.uuid4()


async def test_resolve_fornecedor_cria_pessoa_documento_e_papel(monkeypatch):
    session = FakeSession()
    tenant_id = uuid.uuid4()
    tipo_rel = TipoRelacionamento(id=uuid.uuid4(), codigo="FORNECEDOR", nome="Fornecedor", ativo=True)
    garantir_rel = AsyncMock()

    monkeypatch.setattr(service, "_buscar_pessoa_por_documento", AsyncMock(return_value=None))
    monkeypatch.setattr(service, "_buscar_pessoa_fornecedor_por_nome", AsyncMock(return_value=None))
    monkeypatch.setattr(service, "_obter_tipo_fornecedor", AsyncMock(return_value=tipo_rel))
    monkeypatch.setattr(service, "_garantir_relacionamento_fornecedor", garantir_rel)

    pessoa = await service.resolve_fornecedor(
        session,
        tenant_id,
        nome_fantasia="Fornecedor ABC",
        razao_social="Fornecedor ABC Ltda",
        cnpj_cpf="12.345.678/0001-90",
        email="compras@fornecedor.test",
        telefone="11999990000",
    )

    documentos = [obj for obj in session.added if isinstance(obj, PessoaDocumento)]
    contatos = [obj for obj in session.added if isinstance(obj, PessoaContato)]

    assert isinstance(pessoa, Pessoa)
    assert pessoa.id is not None
    assert pessoa.tenant_id == tenant_id
    assert pessoa.tipo == "PJ"
    assert pessoa.nome_exibicao == "Fornecedor ABC"
    assert len(documentos) == 1
    assert documentos[0].tipo == "CNPJ"
    assert documentos[0].numero == "12345678000190"
    assert {contato.tipo for contato in contatos} == {"EMAIL", "TELEFONE"}
    garantir_rel.assert_awaited_once_with(session, pessoa.id, tipo_rel.id)


async def test_resolve_fornecedor_reutiliza_pessoa_existente_por_documento(monkeypatch):
    session = FakeSession()
    tenant_id = uuid.uuid4()
    pessoa_existente = Pessoa(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        tipo="PJ",
        nome_exibicao="Fornecedor ABC",
        base_legal="CONTRATO",
        ativo=True,
    )
    tipo_rel = TipoRelacionamento(id=uuid.uuid4(), codigo="FORNECEDOR", nome="Fornecedor", ativo=True)
    garantir_rel = AsyncMock()

    monkeypatch.setattr(service, "_buscar_pessoa_por_documento", AsyncMock(return_value=pessoa_existente))
    monkeypatch.setattr(service, "_obter_tipo_fornecedor", AsyncMock(return_value=tipo_rel))
    monkeypatch.setattr(service, "_garantir_relacionamento_fornecedor", garantir_rel)

    pessoa = await service.resolve_fornecedor(
        session,
        tenant_id,
        nome_fantasia="Fornecedor ABC Atualizado",
        cnpj_cpf="12345678000190",
    )

    assert pessoa.id == pessoa_existente.id
    assert not any(isinstance(obj, PessoaDocumento) for obj in session.added)
    garantir_rel.assert_awaited_once_with(session, pessoa_existente.id, tipo_rel.id)


async def test_salvar_fornecedor_legado_nao_duplica_mesmo_documento(monkeypatch):
    session = FakeSession()
    tenant_id = uuid.uuid4()
    pessoa = Pessoa(id=uuid.uuid4(), tenant_id=tenant_id, tipo="PJ", nome_exibicao="Fornecedor", base_legal="CONTRATO", ativo=True)

    monkeypatch.setattr(service, "resolve_fornecedor", AsyncMock(return_value=pessoa))

    async def buscar_por_pessoa(_session, _tenant_id, pessoa_id):
        for obj in session.added:
            if isinstance(obj, Fornecedor) and obj.tenant_id == _tenant_id and obj.pessoa_id == pessoa_id:
                return obj
        return None

    monkeypatch.setattr(service, "_buscar_fornecedor_legado_por_pessoa", AsyncMock(side_effect=buscar_por_pessoa))
    monkeypatch.setattr(service, "_buscar_fornecedor_legado_por_documento", AsyncMock(return_value=None))

    fornecedor_a, created_a = await service.salvar_fornecedor_legado(
        session,
        tenant_id,
        nome_fantasia="Fornecedor ABC",
        cnpj_cpf="12.345.678/0001-90",
        email="primeiro@fornecedor.test",
        condicoes_pagamento="15 dias",
    )
    fornecedor_b, created_b = await service.salvar_fornecedor_legado(
        session,
        tenant_id,
        nome_fantasia="Fornecedor ABC Atualizado",
        cnpj_cpf="12345678000190",
        email="segundo@fornecedor.test",
        condicoes_pagamento="28 dias",
        prazo_entrega_dias=4,
        avaliacao=4.5,
    )

    assert created_a is True
    assert created_b is False
    assert fornecedor_b.id == fornecedor_a.id
    assert fornecedor_b.email == "segundo@fornecedor.test"
    assert fornecedor_b.condicoes_pagamento == "28 dias"
    assert fornecedor_b.prazo_entrega_dias == 4
    assert fornecedor_b.avaliacao == 4.5


async def test_salvar_fornecedor_legado_isola_por_tenant(monkeypatch):
    session = FakeSession()
    tenant_a = uuid.uuid4()
    tenant_b = uuid.uuid4()

    pessoa_a = Pessoa(id=uuid.uuid4(), tenant_id=tenant_a, tipo="PJ", nome_exibicao="Fornecedor A", base_legal="CONTRATO", ativo=True)
    pessoa_b = Pessoa(id=uuid.uuid4(), tenant_id=tenant_b, tipo="PJ", nome_exibicao="Fornecedor B", base_legal="CONTRATO", ativo=True)

    async def resolve_side_effect(_session, tenant_id, **_kwargs):
        return pessoa_a if tenant_id == tenant_a else pessoa_b

    monkeypatch.setattr(service, "resolve_fornecedor", AsyncMock(side_effect=resolve_side_effect))
    monkeypatch.setattr(service, "_buscar_fornecedor_legado_por_pessoa", AsyncMock(return_value=None))
    monkeypatch.setattr(service, "_buscar_fornecedor_legado_por_documento", AsyncMock(return_value=None))

    fornecedor_a, created_a = await service.salvar_fornecedor_legado(
        session,
        tenant_a,
        nome_fantasia="Fornecedor Compartilhado",
        cnpj_cpf="12.345.678/0001-90",
    )
    fornecedor_b, created_b = await service.salvar_fornecedor_legado(
        session,
        tenant_b,
        nome_fantasia="Fornecedor Compartilhado",
        cnpj_cpf="12.345.678/0001-90",
    )

    assert created_a is True
    assert created_b is True
    assert fornecedor_a.id != fornecedor_b.id
    assert fornecedor_a.tenant_id == tenant_a
    assert fornecedor_b.tenant_id == tenant_b
    assert fornecedor_a.pessoa_id == pessoa_a.id
    assert fornecedor_b.pessoa_id == pessoa_b.id


async def test_salvar_fornecedor_legado_reutiliza_registro_sem_pessoa_id_e_mantem_campos_comerciais(monkeypatch):
    session = FakeSession()
    tenant_id = uuid.uuid4()
    pessoa = Pessoa(id=uuid.uuid4(), tenant_id=tenant_id, tipo="PJ", nome_exibicao="Fornecedor", base_legal="CONTRATO", ativo=True)
    legado = Fornecedor(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        nome_fantasia="Fornecedor Legado",
        cnpj_cpf="12.345.678/0001-90",
        condicoes_pagamento="7 dias",
        prazo_entrega_dias=2,
        avaliacao=3.0,
    )

    resolve_mock = AsyncMock(return_value=pessoa)
    monkeypatch.setattr(service, "resolve_fornecedor", resolve_mock)
    monkeypatch.setattr(service, "_buscar_fornecedor_legado_por_pessoa", AsyncMock(return_value=None))
    monkeypatch.setattr(service, "_buscar_fornecedor_legado_por_documento", AsyncMock(return_value=legado))

    fornecedor, created = await service.salvar_fornecedor_legado(
        session,
        tenant_id,
        nome_fantasia="Fornecedor Legado Atualizado",
        cnpj_cpf="12345678000190",
        email="financeiro@fornecedor.test",
        telefone="1133334444",
        condicoes_pagamento="21 dias",
        prazo_entrega_dias=5,
        avaliacao=4.8,
    )

    kwargs = resolve_mock.await_args.kwargs

    assert created is False
    assert fornecedor.id == legado.id
    assert fornecedor.pessoa_id == pessoa.id
    assert fornecedor.nome_fantasia == "Fornecedor Legado Atualizado"
    assert fornecedor.email == "financeiro@fornecedor.test"
    assert fornecedor.telefone == "1133334444"
    assert fornecedor.condicoes_pagamento == "21 dias"
    assert fornecedor.prazo_entrega_dias == 5
    assert fornecedor.avaliacao == 4.8
    assert "condicoes_pagamento" not in kwargs
    assert "prazo_entrega_dias" not in kwargs
    assert "avaliacao" not in kwargs
