"""
Testes unitários para o parser de OFX e serviço de conciliação
"""

import pytest
from datetime import datetime
from services.api.financeiro.services.ofx_parser import OFXParser, OFXParserFactory, TransacaoOFX
from services.api.financeiro.services.conciliacao_service import (
    ConciliacaoBancariaService,
    ConciliacaoBancariaFactory,
    SugestaoConciliacao,
)


class TestOFXParser:
    """Classe de testes para OFXParser"""
    
    @pytest.fixture
    def ofx_conteudo_exemplo(self):
        """Fixture com conteúdo OFX de exemplo"""
        return """<?xml version="1.0" encoding="UTF-8"?>
<OFX>
    <SIGNONMSGSRSV1>
        <SONRS>
            <STATUS>
                <CODE>0</CODE>
                <SEVERITY>INFO</SEVERITY>
            </STATUS>
        </SONRS>
    </SIGNONMSGSRSV1>
    <BANKMSGSRSV1>
        <STMTTRNRS>
            <TRNUID>123</TRNUID>
            <STATUS>
                <CODE>0</CODE>
                <SEVERITY>INFO</SEVERITY>
            </STATUS>
            <STMTRS>
                <CURDEF>BRL</CURDEF>
                <BANKACCTFROM>
                    <BANKID>341</BANKID>
                    <BRANCHID>1234</BRANCHID>
                    <ACCTID>56789-0</ACCTID>
                    <ACCTTYPE>CHECKING</ACCTTYPE>
                </BANKACCTFROM>
                <BANKTRANLIST>
                    <DTSTART>20260301000000</DTSTART>
                    <DTEND>20260331235959</DTEND>
                    <STMTTRN>
                        <TRNTYPE>CREDIT</TRNTYPE>
                        <DTPOSTED>20260315103000</DTPOSTED>
                        <TRNAMT>1500.00</TRNAMT>
                        <FITID>123456</FITID>
                        <NAME>Pagamento Recebido</NAME>
                        <MEMO>Nota Fiscal 001</MEMO>
                    </STMTTRN>
                    <STMTTRN>
                        <TRNTYPE>DEBIT</TRNTYPE>
                        <DTPOSTED>20260316143000</DTPOSTED>
                        <TRNAMT>-250.50</TRNAMT>
                        <FITID>123457</FITID>
                        <NAME>FORNECEDOR XYZ</NAME>
                        <MEMO>Compra de insumos</MEMO>
                    </STMTTRN>
                </BANKTRANLIST>
                <LEDGERBAL>
                    <BALAMT>10250.75</BALAMT>
                    <DTASOF>20260331235959</DTASOF>
                </LEDGERBAL>
            </STMTRS>
        </STMTTRNRS>
    </BANKMSGSRSV1>
</OFX>"""
    
    def test_parser_criar_instancia(self):
        """Testa criação de instância do parser"""
        parser = OFXParser()
        assert parser is not None
        assert parser.conteudo == ""
    
    def test_parser_factory(self):
        """Testa factory do parser"""
        parser = OFXParserFactory.get_parser()
        assert parser is not None
        assert isinstance(parser, OFXParser)
    
    def test_extrair_conta(self, ofx_conteudo_exemplo):
        """Testa extração de informações da conta"""
        parser = OFXParser()
        extrato = parser.parse_conteudo(ofx_conteudo_exemplo)
        
        assert extrato.banco == "Itaú" or extrato.banco == "Banco 341"
        assert extrato.conta == "56789-0"
        assert extrato.agencia == "1234"
    
    def test_extrair_saldos(self, ofx_conteudo_exemplo):
        """Testa extração de saldos"""
        parser = OFXParser()
        extrato = parser.parse_conteudo(ofx_conteudo_exemplo)
        
        assert extrato.saldo_final == 10250.75
    
    def test_extrair_periodo(self, ofx_conteudo_exemplo):
        """Testa extração do período do extrato"""
        parser = OFXParser()
        extrato = parser.parse_conteudo(ofx_conteudo_exemplo)
        
        assert extrato.data_inicial is not None
        assert extrato.data_final is not None
        assert extrato.data_inicial.month == 3
        assert extrato.data_inicial.year == 2026
    
    def test_extrair_transacoes(self, ofx_conteudo_exemplo):
        """Testa extração de transações"""
        parser = OFXParser()
        extrato = parser.parse_conteudo(ofx_conteudo_exemplo)
        
        assert len(extrato.transacoes) == 2
        
        # Primeira transação (crédito)
        transacao1 = extrato.transacoes[0]
        assert transacao1.valor == 1500.00
        assert transacao1.tipo == 'C'
        assert "Pagamento" in transacao1.descricao
        
        # Segunda transação (débito)
        transacao2 = extrato.transacoes[1]
        assert transacao2.valor == 250.50
        assert transacao2.tipo == 'D'
        assert "FORNECEDOR" in transacao2.descricao
    
    def test_parse_data(self, ofx_conteudo_exemplo):
        """Testa parse de data no formato OFX"""
        parser = OFXParser()
        
        # Testar formato YYYYMMDDHHMMSS
        data = parser._parse_data("20260315103000")
        assert data is not None
        assert data.year == 2026
        assert data.month == 3
        assert data.day == 15
        assert data.hour == 10
        assert data.minute == 30
    
    def test_parse_valor(self, ofx_conteudo_exemplo):
        """Testa parse de valor monetário"""
        parser = OFXParser()
        
        # Testar valor positivo
        valor1 = parser._parse_valor("1500.50")
        assert valor1 == 1500.50
        
        # Testar valor negativo
        valor2 = parser._parse_valor("-250.50")
        assert valor2 == -250.50
        
        # Testar valor com vírgula (formato brasileiro)
        valor3 = parser._parse_valor("100,75")
        assert valor3 == 100.75
    
    def test_mapear_tipo(self, ofx_conteudo_exemplo):
        """Testa mapeamento de tipos OFX"""
        parser = OFXParser()
        
        # Tipos de crédito
        assert parser._mapear_tipo("CREDIT") == 'C'
        assert parser._mapear_tipo("DEP") == 'C'
        assert parser._mapear_tipo("DIV") == 'C'
        
        # Tipos de débito
        assert parser._mapear_tipo("DEBIT") == 'D'
        assert parser._mapear_tipo("FEE") == 'D'
        assert parser._mapear_tipo("ATM") == 'D'
    
    def test_validar_ofx(self, ofx_conteudo_exemplo):
        """Testa validação de arquivo OFX"""
        parser = OFXParser()
        parser.conteudo = ofx_conteudo_exemplo
        
        assert parser.validar_ofx() is True
    
    def test_validar_ofx_invalido(self):
        """Testa validação de arquivo inválido"""
        parser = OFXParser()
        parser.conteudo = "Conteúdo inválido"
        
        assert parser.validar_ofx() is False
    
    def test_transacao_to_dict(self):
        """Testa conversão de transação para dict"""
        transacao = TransacaoOFX(
            data=datetime(2026, 3, 15, 10, 30),
            valor=1500.00,
            tipo='C',
            descricao="Pagamento",
            complemento="Nota 001",
        )
        
        d = transacao.to_dict()
        
        assert d['data'] == "2026-03-15T10:30:00"
        assert d['valor'] == 1500.00
        assert d['tipo'] == 'C'
        assert d['descricao'] == "Pagamento"


class TestConciliacaoBancariaService:
    """Classe de testes para ConciliacaoBancariaService"""
    
    @pytest.fixture
    def transacoes_extrato(self):
        """Fixture com transações de extrato"""
        return [
            {
                "id": "ext_1",
                "data": "2026-03-15",
                "valor": 1500.00,
                "tipo": "C",
                "descricao": "PAGAMENTO RECEBIDO - NOTA 001",
            },
            {
                "id": "ext_2",
                "data": "2026-03-16",
                "valor": 250.50,
                "tipo": "D",
                "descricao": "FORNECEDOR XYZ - INSUMOS",
            },
        ]
    
    @pytest.fixture
    def lancamentos_sistema(self):
        """Fixture com lançamentos do sistema"""
        return [
            {
                "id": "lan_1",
                "data": "2026-03-15",
                "data_vencimento": "2026-03-15",
                "valor": 1500.00,
                "descricao": "Nota Fiscal 001 - Venda",
                "historico": "Venda de produtos",
            },
            {
                "id": "lan_2",
                "data": "2026-03-16",
                "data_vencimento": "2026-03-16",
                "valor": 250.50,
                "descricao": "Fornecedor XYZ",
                "historico": "Compra de insumos agrícolas",
            },
        ]
    
    def test_service_criar_instancia(self):
        """Testa criação de instância do serviço"""
        service = ConciliacaoBancariaService()
        assert service is not None
    
    def test_service_factory(self):
        """Testa factory do serviço"""
        service = ConciliacaoBancariaFactory.get_service()
        assert service is not None
        assert isinstance(service, ConciliacaoBancariaService)
    
    def test_conciliar_valor_igual(self, transacoes_extrato, lancamentos_sistema):
        """Testa conciliação com valores iguais"""
        service = ConciliacaoBancariaFactory.get_service()
        
        sugestoes = service.conciliar(
            transacoes_extrato=transacoes_extrato,
            lancamentos_sistema=lancamentos_sistema,
        )
        
        assert len(sugestoes) >= 1
        assert sugestoes[0].score >= 0.6  # Mínimo 60% confiança
    
    def test_score_valor_identico(self, transacoes_extrato, lancamentos_sistema):
        """Testa score para valores idênticos"""
        service = ConciliacaoBancariaService()
        
        score, motivo, dif = service._score_valor(1500.00, 1500.00)
        
        assert score == 1.0
        assert "idêntico" in motivo.lower()
        assert dif == 0.0
    
    def test_score_valor_proximo(self, transacoes_extrato, lancamentos_sistema):
        """Testa score para valores próximos"""
        service = ConciliacaoBancariaService()
        
        score, motivo, dif = service._score_valor(1500.00, 1505.00)
        
        assert score >= 0.7
        assert dif == 5.0
    
    def test_score_data_identica(self, transacoes_extrato, lancamentos_sistema):
        """Testa score para datas idênticas"""
        service = ConciliacaoBancariaService()
        
        score, motivo, dif = service._score_data("2026-03-15", "2026-03-15")
        
        assert score == 1.0
        assert "idêntica" in motivo.lower()
        assert dif == 0
    
    def test_score_data_proxima(self, transacoes_extrato, lancamentos_sistema):
        """Testa score para datas próximas"""
        service = ConciliacaoBancariaService()
        
        score, motivo, dif = service._score_data("2026-03-15", "2026-03-16")
        
        assert score >= 0.7
        assert dif == 1
    
    def test_score_descricao_identica(self, transacoes_extrato, lancamentos_sistema):
        """Testa score para descrições idênticas"""
        service = ConciliacaoBancariaService()
        
        score, motivo = service._score_descricao(
            "PAGAMENTO RECEBIDO",
            "PAGAMENTO RECEBIDO"
        )
        
        assert score == 1.0
        assert "idêntica" in motivo.lower()
    
    def test_score_descricao_similar(self, transacoes_extrato, lancamentos_sistema):
        """Testa score para descrições similares"""
        service = ConciliacaoBancariaService()
        
        score, motivo = service._score_descricao(
            "FORNECEDOR XYZ - INSUMOS",
            "Fornecedor XYZ - Insumos Agrícolas"
        )
        
        assert score >= 0.5
        assert "similar" in motivo.lower() or "comuns" in motivo.lower()
    
    def test_conciliar_manual(self, transacoes_extrato, lancamentos_sistema):
        """Testa conciliação manual"""
        service = ConciliacaoBancariaFactory.get_service()
        
        sugestao = service.conciliar_manual(
            transacao_extrato_id="ext_1",
            lancamento_sistema_id="lan_2",
        )
        
        assert sugestao.score == 1.0
        assert "manual" in sugestao.motivo.lower()
    
    def test_validar_conciliacao(self, transacoes_extrato, lancamentos_sistema):
        """Testa validação de conciliação"""
        service = ConciliacaoBancariaFactory.get_service()
        
        sugestao = SugestaoConciliacao(
            transacao_extrato_id="ext_1",
            lancamento_sistema_id="lan_1",
            score=0.8,
            motivo="Valor e data idênticos",
        )
        
        assert service.validar_conciliacao(sugestao) is True
    
    def test_validar_conciliacao_score_baixo(self, transacoes_extrato, lancamentos_sistema):
        """Testa validação com score baixo"""
        service = ConciliacaoBancariaFactory.get_service()
        
        sugestao = SugestaoConciliacao(
            transacao_extrato_id="ext_1",
            lancamento_sistema_id="lan_1",
            score=0.3,  # Score muito baixo
            motivo="Descrições diferentes",
        )
        
        assert service.validar_conciliacao(sugestao) is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
