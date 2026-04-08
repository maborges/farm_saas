"""
Testes de Integração - Módulo Imóveis Rurais

Testa:
- Validação de NIRF (algoritmo RFB)
- Validação de CAR (formato por estado)
- Consistência de áreas (imóvel vs fazenda)
- Versionamento de documentos
- Criação de contratos de arrendamento
- Geração automática de parcelas
"""
import pytest
import uuid
from decimal import Decimal
from datetime import date, datetime, timezone
from httpx import AsyncClient


# ==================== FIXTURES ====================

@pytest.fixture
async def auth_headers(client: AsyncClient, tenant_auth_token: str) -> dict:
    """Retorna headers de autenticação para requests."""
    return {"Authorization": f"Bearer {tenant_auth_token}"}


@pytest.fixture
async def fazenda(client: AsyncClient, auth_headers: dict) -> dict:
    """Cria uma fazenda de teste."""
    response = await client.post(
        "/api/v1/fazendas/",
        headers=auth_headers,
        json={
            "nome": "Fazenda Teste Imóveis",
            "cpf_cnpj": "00.000.000/0001-00",
            "uf": "MT",
            "municipio": "Sorriso",
            "area_total_ha": 1000.0000,
        },
    )
    assert response.status_code == 201
    return response.json()


# ==================== TESTES DE IMÓVEL RURAL ====================

class TestImovelRural:
    """Testes para CRUD de Imóvel Rural."""

    async def test_criar_imovel_sem_nirf(
        self, client: AsyncClient, auth_headers: dict, fazenda: dict
    ):
        """Deve criar imóvel sem NIRF (opcional)."""
        response = await client.post(
            "/api/v1/imoveis/",
            headers=auth_headers,
            json={
                "nome": "Imóvel Teste 1",
                "fazenda_id": fazenda["id"],
                "municipio": "Sorriso",
                "uf": "MT",
                "area_total_ha": 500.0000,
                "tipo": "rural",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["nome"] == "Imóvel Teste 1"
        assert data["situacao"] == "pendente"  # Sem NIRF/CAR = pendente
        assert data["area_total_ha"] == 500.0000

    async def test_criar_imovel_com_nirf_valido(
        self, client: AsyncClient, auth_headers: dict, fazenda: dict
    ):
        """Deve criar imóvel com NIRF válido."""
        # NIRF fictício válido: 123456789012-3 (DV calculado)
        response = await client.post(
            "/api/v1/imoveis/",
            headers=auth_headers,
            json={
                "nome": "Imóvel com NIRF",
                "fazenda_id": fazenda["id"],
                "municipio": "Sorriso",
                "uf": "MT",
                "area_total_ha": 300.0000,
                "nirf": "1234567890123",
                "car_numero": "MT123456789012",
                "tipo": "rural",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["nirf"] == "1234567890123"
        assert data["car_numero"] == "MT123456789012"
        assert data["situacao"] == "regular"  # Com NIRF e CAR = regular

    async def test_criar_imovel_com_nirf_invalido(
        self, client: AsyncClient, auth_headers: dict, fazenda: dict
    ):
        """Deve rejeitar NIRF com dígito verificador inválido."""
        response = await client.post(
            "/api/v1/imoveis/",
            headers=auth_headers,
            json={
                "nome": "Imóvel NIRF Inválido",
                "fazenda_id": fazenda["id"],
                "municipio": "Sorriso",
                "uf": "MT",
                "area_total_ha": 300.0000,
                "nirf": "1234567890129",  # DV incorreto (deveria ser 3)
            },
        )
        assert response.status_code == 400
        assert "NIRF" in response.json()["detail"]

    async def test_criar_imovel_com_nirf_duplicado(
        self, client: AsyncClient, auth_headers: dict, fazenda: dict
    ):
        """Deve rejeitar NIRF duplicado no tenant."""
        # Cria primeiro imóvel
        await client.post(
            "/api/v1/imoveis/",
            headers=auth_headers,
            json={
                "nome": "Imóvel 1",
                "fazenda_id": fazenda["id"],
                "municipio": "Sorriso",
                "uf": "MT",
                "area_total_ha": 100.0000,
                "nirf": "9876543210987",
            },
        )

        # Tenta criar segundo com mesmo NIRF
        response = await client.post(
            "/api/v1/imoveis/",
            headers=auth_headers,
            json={
                "nome": "Imóvel 2",
                "fazenda_id": fazenda["id"],
                "municipio": "Sorriso",
                "uf": "MT",
                "area_total_ha": 200.0000,
                "nirf": "9876543210987",  # Mesmo NIRF
            },
        )
        assert response.status_code == 400
        assert "NIRF já cadastrado" in response.json()["detail"]

    async def test_criar_imovel_com_car_invalido(
        self, client: AsyncClient, auth_headers: dict, fazenda: dict
    ):
        """Deve rejeitar CAR com formato inválido."""
        response = await client.post(
            "/api/v1/imoveis/",
            headers=auth_headers,
            json={
                "nome": "Imóvel CAR Inválido",
                "fazenda_id": fazenda["id"],
                "municipio": "Sorriso",
                "uf": "MT",
                "area_total_ha": 300.0000,
                "car_numero": "XX123456789012",  # UF inválida
            },
        )
        assert response.status_code == 400
        assert "CAR" in response.json()["detail"]

    async def test_area_excede_fazenda(
        self, client: AsyncClient, auth_headers: dict, fazenda: dict
    ):
        """Deve alertar se área do imóvel excede área da fazenda."""
        response = await client.post(
            "/api/v1/imoveis/",
            headers=auth_headers,
            json={
                "nome": "Imóvel Área Grande",
                "fazenda_id": fazenda["id"],
                "municipio": "Sorriso",
                "uf": "MT",
                "area_total_ha": 1500.0000,  # Fazenda tem 1000 ha
            },
        )
        # Deve criar mas com alerta (tolerância de 10%)
        assert response.status_code == 400
        assert "excede" in response.json()["detail"].lower()

    async def test_listar_imoveis_por_fazenda(
        self, client: AsyncClient, auth_headers: dict, fazenda: dict
    ):
        """Deve listar imóveis filtrando por fazenda."""
        # Cria 3 imóveis
        for i in range(3):
            await client.post(
                "/api/v1/imoveis/",
                headers=auth_headers,
                json={
                    "nome": f"Imóvel {i}",
                    "fazenda_id": fazenda["id"],
                    "municipio": "Sorriso",
                    "uf": "MT",
                    "area_total_ha": 100.0000,
                },
            )

        response = await client.get(
            f"/api/v1/imoveis/?fazenda_id={fazenda['id']}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    async def test_listar_imoveis_por_situacao(
        self, client: AsyncClient, auth_headers: dict, fazenda: dict
    ):
        """Deve listar imóveis filtrando por situação."""
        # Cria imóvel regular
        await client.post(
            "/api/v1/imoveis/",
            headers=auth_headers,
            json={
                "nome": "Imóvel Regular",
                "fazenda_id": fazenda["id"],
                "municipio": "Sorriso",
                "uf": "MT",
                "area_total_ha": 100.0000,
                "nirf": "1111111111111",
                "car_numero": "MT111111111111",
            },
        )

        # Cria imóvel pendente
        await client.post(
            "/api/v1/imoveis/",
            headers=auth_headers,
            json={
                "nome": "Imóvel Pendente",
                "fazenda_id": fazenda["id"],
                "municipio": "Sorriso",
                "uf": "MT",
                "area_total_ha": 200.0000,
            },
        )

        # Filtra por regular
        response = await client.get(
            "/api/v1/imoveis/?situacao=regular",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["nome"] == "Imóvel Regular"


# ==================== TESTES DE DOCUMENTOS LEGAIS ====================

class TestDocumentosLegais:
    """Testes para gestão de documentos legais."""

    async def test_upload_documento_ccir(
        self, client: AsyncClient, auth_headers: dict, fazenda: dict
    ):
        """Deve fazer upload de CCIR com versionamento."""
        # Cria imóvel
        imovel_response = await client.post(
            "/api/v1/imoveis/",
            headers=auth_headers,
            json={
                "nome": "Imóvel para Documentos",
                "fazenda_id": fazenda["id"],
                "municipio": "Sorriso",
                "uf": "MT",
                "area_total_ha": 500.0000,
            },
        )
        imovel = imovel_response.json()

        # Upload CCIR (simulado - na prática seria multipart/form-data)
        # Aqui testamos a estrutura do endpoint
        response = await client.post(
            f"/api/v1/imoveis/{imovel['id']}/documentos/",
            headers=auth_headers,
            json={
                "tipo": "CCIR",
                "numero_documento": "CCIR-2024-001",
                "data_emissao": "2024-01-15",
                "data_vencimento": "2025-01-15",
                "path_storage": "s3://bucket/ccir-2024.pdf",
                "nome_arquivo": "ccir-2024.pdf",
                "tamanho_bytes": 102400,
            },
        )
        # Endpoint pode não existir ainda - teste placeholder
        # assert response.status_code == 201

    async def test_versionamento_documento(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Deve criar nova versão ao substituir documento."""
        # Implementar quando endpoint de documentos estiver pronto
        pass


# ==================== TESTES DE ARRENDAMENTOS ====================

class TestArrendamentos:
    """Testes para contratos de arrendamento."""

    async def test_criar_arrendamento_prazo_valido(
        self, client: AsyncClient, auth_headers: dict, fazenda: dict
    ):
        """Deve criar arrendamento com prazo mínimo de 3 anos."""
        # Cria imóvel
        imovel_response = await client.post(
            "/api/v1/imoveis/",
            headers=auth_headers,
            json={
                "nome": "Imóvel para Arrendamento",
                "fazenda_id": fazenda["id"],
                "municipio": "Sorriso",
                "uf": "MT",
                "area_total_ha": 500.0000,
            },
        )
        imovel = imovel_response.json()

        # Cria arrendamento (3 anos - prazo mínimo)
        response = await client.post(
            "/api/v1/imoveis/arrendamentos/",
            headers=auth_headers,
            json={
                "imovel_id": imovel["id"],
                "fazenda_id": fazenda["id"],
                "tipo": "arrendamento",
                "arrendatario_tipo": "pessoa_fisica",
                "area_arrendada_ha": 200.0000,
                "valor_modalidade": "fixo_brl",
                "valor": 120000.00,  # R$ 120.000/ano
                "periodicidade": "anual",
                "data_inicio": "2024-01-01",
                "data_fim": "2026-12-31",  # 3 anos
                "dia_vencimento": 10,
            },
        )
        # Endpoint pode não existir ainda - teste placeholder
        # assert response.status_code == 201

    async def test_criar_arrendamento_prazo_invalido(
        self, client: AsyncClient, auth_headers: dict, fazenda: dict
    ):
        """Deve alertar para arrendamento com prazo inferior a 3 anos."""
        # Implementar quando endpoint estiver pronto
        pass

    async def test_geracao_parcelas_mensais(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Deve gerar parcelas mensais automaticamente."""
        # Implementar quando endpoint estiver pronto
        pass

    async def test_reajuste_contratual(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Deve aplicar reajuste anual pelo índice configurado."""
        # Implementar quando endpoint estiver pronto
        pass


# ==================== TESTES DE VALIDAÇÃO NIRF ====================

class TestNIRFValidator:
    """Testes unitários para validador de NIRF."""

    def test_calcular_dv_nirf(self):
        """Testa cálculo do dígito verificador do NIRF."""
        from imoveis.services.imovel_service import NIRFValidator

        # NIRF fictício: 123456789012
        corpo = "123456789012"
        dv = NIRFValidator._calcular_dv(corpo)

        # Verifica se DV está correto (deve ser 3)
        assert dv == 3

    def test_validar_nirf_completo(self):
        """Testa validação de NIRF completo."""
        from imoveis.services.imovel_service import NIRFValidator

        # NIRF válido
        valido, msg = NIRFValidator.validar("1234567890123")
        assert valido is True

        # NIRF inválido (DV errado)
        valido, msg = NIRFValidator.validar("1234567890129")
        assert valido is False
        assert "dígito verificador" in msg.lower()

    def test_limpar_nirf(self):
        """Testa limpeza de caracteres não numéricos."""
        from imoveis.services.imovel_service import NIRFValidator

        nirf_formatado = "123.456.789.012-3"
        nirf_limpo = NIRFValidator.limpar_nirf(nirf_formatado)
        assert nirf_limpo == "1234567890123"


# ==================== TESTES DE CAR VALIDATOR ====================

class TestCARValidator:
    """Testes unitários para validador de CAR."""

    def test_validar_car_formato_valido(self):
        """Testa validação de CAR com formato válido."""
        from imoveis.services.imovel_service import CARValidator

        valido, msg = CARValidator.validar("MT123456789012")
        assert valido is True

    def test_validar_car_uf_invalida(self):
        """Testa rejeição de UF inválida."""
        from imoveis.services.imovel_service import CARValidator

        valido, msg = CARValidator.validar("XX123456789012")
        assert valido is False
        assert "UF" in msg

    def test_validar_car_tamanho_invalido(self):
        """Testa rejeição de CAR com tamanho inválido."""
        from imoveis.services.imovel_service import CARValidator

        valido, msg = CARValidator.validar("MT12345678901")  # 11 dígitos
        assert valido is False
        assert "14 caracteres" in msg


# ==================== TESTES DE ARRENDAMENTO SERVICE ====================

class TestArrendamentoService:
    """Testes unitários para ArrendamentoService."""

    def test_calcular_parcelas_mensais(self):
        """Testa cálculo de parcelas mensais."""
        from imoveis.services.arrendamento_service import ArrendamentoService
        from decimal import Decimal
        from datetime import date

        # Mock session
        class MockSession:
            pass

        service = ArrendamentoService(MockSession())

        parcelas = service.calcular_parcelas(
            valor_total=Decimal("120000.00"),  # R$ 120.000/ano
            periodicidade="mensal",
            data_inicio=date(2024, 1, 1),
            data_fim=date(2024, 12, 31),
            dia_vencimento=10,
        )

        assert len(parcelas) == 12
        assert parcelas[0]["valor_centavos"] == 1000000  # R$ 10.000
        assert parcelas[0]["data_vencimento"].day == 10

    def test_validar_prazo_minimo(self):
        """Testa validação de prazo mínimo."""
        from imoveis.services.arrendamento_service import ArrendamentoService
        from datetime import date

        class MockSession:
            pass

        service = ArrendamentoService(MockSession())

        # Prazo válido (3 anos)
        valido, msg = service.validar_prazo_minimo(
            date(2024, 1, 1),
            date(2026, 12, 31),
        )
        assert valido is True

        # Prazo inválido (1 ano)
        valido, msg = service.validar_prazo_minimo(
            date(2024, 1, 1),
            date(2024, 12, 31),
        )
        assert valido is False
        assert "prazo mínimo" in msg.lower()
