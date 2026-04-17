"""Testes unitários para os schemas Pydantic - C-03."""
import pytest
from pydantic import ValidationError
from datetime import date
import uuid

from core.cadastros.propriedades.propriedade_schemas import (
    PropriedadeCreate,
    PropriedadeUpdate,
    PropriedadeResponse,
    ExploracaoCreate,
    ExploracaoUpdate,
    DocumentoExploracaoCreate,
    DocumentoExploracaoResponse,
)


class TestPropriedadeCreate:
    """Testes para PropriedadeCreate."""

    def test_propriedade_create_valida(self):
        """PropriedadeCreate(nome="Teste") deve validar."""
        p = PropriedadeCreate(nome="Teste")
        assert p.nome == "Teste"
        assert p.ie_isento is False
        assert p.ordem == 0

    def test_propriedade_create_nome_curto_falha(self):
        """PropriedadeCreate(nome="X") deve falhar (min_length=2)."""
        with pytest.raises(ValidationError):
            PropriedadeCreate(nome="X")

    def test_propriedade_create_nome_longo_falha(self):
        """PropriedadeCreate com nome > 200 caracteres deve falhar."""
        with pytest.raises(ValidationError):
            PropriedadeCreate(nome="A" * 201)

    def test_propriedade_create_cpf_cnpj_max_length(self):
        """Deve aceitar cpf_cnpj com até 18 caracteres."""
        p = PropriedadeCreate(nome="Teste", cpf_cnpj="123456789012345678")
        assert p.cpf_cnpj == "123456789012345678"

    def test_propriedade_create_completo(self):
        """Deve aceitar todos os campos."""
        p = PropriedadeCreate(
            nome="Fazenda Teste",
            cpf_cnpj="12.345.678/0001-90",
            inscricao_estadual="ISENTO",
            ie_isento=True,
            email="contato@fazenda.com",
            telefone="(11) 99999-9999",
            nome_fantasia="Fazenda Boa",
            regime_tributario="SIMPLES_NACIONAL",
            cor="#FF0000",
            icone="tractor",
            ordem=1,
            observacoes="Observação teste",
        )
        assert p.nome == "Fazenda Teste"
        assert p.ie_isento is True


class TestPropriedadeUpdate:
    """Testes para PropriedadeUpdate."""

    def test_propriedade_update_parcial(self):
        """Deve aceitar update parcial."""
        p = PropriedadeUpdate(nome="Novo Nome")
        assert p.nome == "Novo Nome"
        assert p.ativo is None

    def test_propriedade_update_ativo(self):
        """Deve aceitar update de ativo."""
        p = PropriedadeUpdate(ativo=False)
        assert p.ativo is False


class TestExploracaoCreate:
    """Testes para ExploracaoCreate."""

    def test_exploracao_create_natureza_valida(self):
        """ExploracaoCreate(natureza="propria", ...) deve validar."""
        unidade_produtiva_id = uuid.uuid4()
        e = ExploracaoCreate(
            unidade_produtiva_id=unidade_produtiva_id,
            natureza="propria",
            data_inicio=date(2024, 1, 1),
        )
        assert e.natureza == "propria"

    def test_exploracao_create_natureza_invalida_falha(self):
        """ExploracaoCreate(natureza="invalida", ...) deve falhar com ValueError."""
        unidade_produtiva_id = uuid.uuid4()
        with pytest.raises(ValidationError) as exc_info:
            ExploracaoCreate(
                unidade_produtiva_id=unidade_produtiva_id,
                natureza="invalida",
                data_inicio=date(2024, 1, 1),
            )
        assert "Natureza inválida" in str(exc_info.value)

    def test_exploracao_create_todas_naturezas_validas(self):
        """Todas as naturezas do enum devem ser aceitas."""
        from core.cadastros.propriedades.propriedade_models import NaturezaVinculo
        unidade_produtiva_id = uuid.uuid4()
        for natureza in NaturezaVinculo:
            e = ExploracaoCreate(
                unidade_produtiva_id=unidade_produtiva_id,
                natureza=natureza.value,
                data_inicio=date(2024, 1, 1),
            )
            assert e.natureza == natureza.value

    def test_exploracao_create_valor_anual_positivo(self):
        """Deve aceitar valor_anual > 0."""
        unidade_produtiva_id = uuid.uuid4()
        e = ExploracaoCreate(
            unidade_produtiva_id=unidade_produtiva_id,
            natureza="propria",
            data_inicio=date(2024, 1, 1),
            valor_anual=10000.0,
        )
        assert e.valor_anual == 10000.0

    def test_exploracao_create_valor_anual_negativo_falha(self):
        """valor_anual deve ser > 0."""
        unidade_produtiva_id = uuid.uuid4()
        with pytest.raises(ValidationError):
            ExploracaoCreate(
                unidade_produtiva_id=unidade_produtiva_id,
                natureza="propria",
                data_inicio=date(2024, 1, 1),
                valor_anual=-100.0,
            )

    def test_exploracao_create_percentual_producao_valido(self):
        """percentual_producao deve ser > 0 e <= 100."""
        unidade_produtiva_id = uuid.uuid4()
        e = ExploracaoCreate(
            unidade_produtiva_id=unidade_produtiva_id,
            natureza="propria",
            data_inicio=date(2024, 1, 1),
            percentual_producao=75.5,
        )
        assert e.percentual_producao == 75.5

    def test_exploracao_create_percentual_producao_acima_100_falha(self):
        """percentual_producao > 100 deve falhar."""
        unidade_produtiva_id = uuid.uuid4()
        with pytest.raises(ValidationError):
            ExploracaoCreate(
                unidade_produtiva_id=unidade_produtiva_id,
                natureza="propria",
                data_inicio=date(2024, 1, 1),
                percentual_producao=150.0,
            )


class TestExploracaoUpdate:
    """Testes para ExploracaoUpdate."""

    def test_exploracao_update_natureza_valida(self):
        """Deve aceitar update com natureza válida."""
        e = ExploracaoUpdate(natureza="arrendamento")
        assert e.natureza == "arrendamento"

    def test_exploracao_update_natureza_invalida_falha(self):
        """Natureza inválida deve falhar."""
        with pytest.raises(ValidationError):
            ExploracaoUpdate(natureza="invalida")

    def test_exploracao_update_natureza_none(self):
        """Deve aceitar natureza None."""
        e = ExploracaoUpdate(natureza=None)
        assert e.natureza is None


class TestDocumentoExploracaoCreate:
    """Testes para DocumentoExploracaoCreate."""

    def test_documento_exploracao_create_tipo_valido(self):
        """DocumentoExploracaoCreate(tipo="contrato_arrendamento", ...) deve validar."""
        d = DocumentoExploracaoCreate(
            tipo="contrato_arrendamento",
            nome_arquivo="contrato.pdf",
            storage_path="/storage/contrato.pdf",
            tamanho_bytes=1024,
        )
        assert d.tipo == "contrato_arrendamento"

    def test_documento_exploracao_create_tipo_invalido_falha(self):
        """Tipo inválido deve falhar com ValueError."""
        with pytest.raises(ValidationError) as exc_info:
            DocumentoExploracaoCreate(
                tipo="invalido",
                nome_arquivo="doc.pdf",
                storage_path="/storage/doc.pdf",
                tamanho_bytes=1024,
            )
        assert "Tipo inválido" in str(exc_info.value)

    def test_documento_exploracao_create_todos_tipos_validos(self):
        """Todos os tipos do enum devem ser aceitos."""
        from core.cadastros.propriedades.propriedade_models import TipoDocumentoExploracao
        for tipo in TipoDocumentoExploracao:
            d = DocumentoExploracaoCreate(
                tipo=tipo.value,
                nome_arquivo="doc.pdf",
                storage_path="/storage/doc.pdf",
                tamanho_bytes=1024,
            )
            assert d.tipo == tipo.value

    def test_documento_exploracao_create_storage_backend_padrao(self):
        """storage_backend deve ser 'local' por padrão."""
        d = DocumentoExploracaoCreate(
            tipo="car",
            nome_arquivo="car.pdf",
            storage_path="/storage/car.pdf",
            tamanho_bytes=2048,
        )
        assert d.storage_backend == "local"


class TestResponseSchemas:
    """Testes para os schemas de Response."""

    def test_propriedade_response_from_attributes(self):
        """PropriedadeResponse deve suportar from_attributes."""
        from core.cadastros.propriedades.propriedade_models import Propriedade
        from datetime import datetime, timezone
        
        now = datetime.now(timezone.utc)
        p = Propriedade(
            id=uuid.uuid4(),
            tenant_id=uuid.uuid4(),
            nome="Fazenda Teste",
            cpf_cnpj="123",
            inscricao_estadual=None,
            ie_isento=False,
            email=None,
            telefone=None,
            nome_fantasia=None,
            regime_tributario=None,
            cor=None,
            icone=None,
            ordem=0,
            ativo=True,
            observacoes=None,
            created_at=now,
            updated_at=now,
        )
        response = PropriedadeResponse.model_validate(p)
        assert response.nome == "Fazenda Teste"

    def test_exploracao_response_from_attributes(self):
        """ExploracaoResponse deve suportar from_attributes."""
        from core.cadastros.propriedades.propriedade_models import ExploracaoRural
        from core.cadastros.propriedades.propriedade_schemas import ExploracaoResponse
        from datetime import datetime, timezone
        
        now = datetime.now(timezone.utc)
        e = ExploracaoRural(
            id=uuid.uuid4(),
            tenant_id=uuid.uuid4(),
            propriedade_id=uuid.uuid4(),
            unidade_produtiva_id=uuid.uuid4(),
            natureza="propria",
            data_inicio=date(2024, 1, 1),
            data_fim=None,
            numero_contrato=None,
            valor_anual=None,
            percentual_producao=None,
            area_explorada_ha=None,
            documento_s3_key=None,
            documento_tipo=None,
            ativo=True,
            observacoes=None,
            created_at=now,
            updated_at=now,
        )
        response = ExploracaoResponse.model_validate(e)
        assert response.natureza == "propria"
