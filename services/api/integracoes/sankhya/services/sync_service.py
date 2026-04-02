"""Services para integração com ERP Sankhya."""

import httpx
import base64
from typing import List, Dict, Optional, Any
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session

from integracoes.sankhya.models import (
    SankhyaConfig, SankhyaSyncLog, SankhyaPessoa,
    SankhyaProduto, SankhyaNFe, SankhyaLancamentoFinanceiro,
    SankhyaTabela
)


class SankhyaWSClient:
    """Cliente para Web Services Sankhya BPM."""

    def __init__(self, config: SankhyaConfig):
        self.config = config
        self.base_url = config.ws_url
        self.username = config.username
        self.password = config.password
        self._session: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        self._session = httpx.AsyncClient(timeout=300.0)  # 5 minutos timeout
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.aclose()

    def _get_auth_headers(self) -> Dict[str, str]:
        """Gera headers de autenticação básica."""
        credentials = f"{self.username}:{self.password}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return {
            "Authorization": f"Basic {encoded}",
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": '""'
        }

    async def test_connection(self) -> bool:
        """Testa conexão com o WS Sankhya."""
        try:
            # SOAP envelope para teste
            soap_envelope = """<?xml version="1.0" encoding="UTF-8"?>
            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
                <soapenv:Header/>
                <soapenv:Body/>
            </soapenv:Envelope>"""

            response = await self._session.post(
                self.base_url,
                headers=self._get_auth_headers(),
                content=soap_envelope
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Erro ao testar conexão Sankhya: {e}")
            return False

    async def executar_ws(self, service: str, method: str, 
                         params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa um Web Service Sankhya.
        
        Args:
            service: Nome do serviço (ex: PessoaFisica, PessoaJuridica)
            method: Método do serviço (ex: save, findByKey)
            params: Parâmetros do método
        
        Returns:
            Resultado da chamada
        """
        # Construir SOAP envelope
        soap_envelope = self._build_soap_envelope(service, method, params)
        
        try:
            response = await self._session.post(
                self.base_url,
                headers=self._get_auth_headers(),
                content=soap_envelope
            )
            
            if response.status_code == 200:
                return self._parse_soap_response(response.text)
            else:
                raise Exception(f"Erro WS Sankhya: {response.status_code} - {response.text}")
                
        except Exception as e:
            raise Exception(f"Falha ao executar WS {service}.{method}: {e}")

    def _build_soap_envelope(self, service: str, method: str, 
                            params: Dict[str, Any]) -> str:
        """Constrói envelope SOAP para chamada."""
        # Implementação simplificada - em produção usar biblioteca zeep
        params_xml = ""
        for key, value in params.items():
            params_xml += f"<{key}>{value}</{key}>"
        
        return f"""<?xml version="1.0" encoding="UTF-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                          xmlns:bpm="http://www.sankhya.com.br/bpm">
            <soapenv:Header/>
            <soapenv:Body>
                <bpm:{method}>
                    {params_xml}
                </bpm:{method}>
            </soapenv:Body>
        </soapenv:Envelope>"""

    def _parse_soap_response(self, response_text: str) -> Dict[str, Any]:
        """Parse da resposta SOAP."""
        # Implementação simplificada - em produção usar biblioteca zeep
        # Extrair resultado do XML
        import re
        
        # Procurar por valores no XML
        result = {}
        matches = re.findall(r'<([^>]+)>([^<]+)</\1>', response_text)
        for key, value in matches:
            if key not in ['soapenv', 'bpm']:
                result[key] = value
        
        return result


class SankhyaSyncService:
    """Serviço de sincronização com Sankhya."""

    def __init__(self, db: Session):
        self.db = db

    def get_config(self, tenant_id: str) -> Optional[SankhyaConfig]:
        """Obtém configuração Sankhya do tenant."""
        return self.db.query(SankhyaConfig).filter(
            SankhyaConfig.tenant_id == tenant_id
        ).first()

    def criar_config(self, tenant_id: str, ws_url: str,
                    username: str, password: str,
                    sync_interval: int = 900) -> SankhyaConfig:
        """Cria configuração Sankhya."""
        config = SankhyaConfig(
            tenant_id=tenant_id,
            ws_url=ws_url,
            username=username,
            password=password,
            sync_interval=sync_interval
        )
        self.db.add(config)
        self.db.commit()
        self.db.refresh(config)
        return config

    def testar_conexao(self, tenant_id: str) -> Dict[str, Any]:
        """Testa conexão com Sankhya."""
        config = self.get_config(tenant_id)
        if not config:
            return {"sucesso": False, "erro": "Configuração não encontrada"}

        import asyncio
        
        async def testar():
            async with SankhyaWSClient(config) as client:
                return await client.test_connection()
        
        sucesso = asyncio.run(testar())
        
        # Atualizar status
        config.ultimo_teste = datetime.utcnow()
        config.teste_status = "sucesso" if sucesso else "erro"
        self.db.commit()
        
        return {
            "sucesso": sucesso,
            "mensagem": "Conexão estabelecida" if sucesso else "Falha na conexão"
        }

    def iniciar_sync_log(self, tenant_id: str, tipo: str,
                        operacao: str) -> SankhyaSyncLog:
        """Inicia log de sincronização."""
        log = SankhyaSyncLog(
            tenant_id=tenant_id,
            tipo=tipo,
            operacao=operacao,
            status="processando",
            started_at=datetime.utcnow()
        )
        self.db.add(log)
        self.db.commit()
        return log

    def finalizar_sync_log(self, log_id: int, sucesso: bool,
                          processados: int, erros: int = 0,
                          erro_mensagem: str = None,
                          tempo_ms: float = 0):
        """Finaliza log de sincronização."""
        log = self.db.query(SankhyaSyncLog).filter(
            SankhyaSyncLog.id == log_id
        ).first()
        
        if log:
            log.status = "sucesso" if sucesso else "erro"
            log.registros_processados = processados
            log.registros_erro = erros
            log.tempo_execucao_ms = tempo_ms
            log.completed_at = datetime.utcnow()
            
            if erro_mensagem:
                log.erro_mensagem = erro_mensagem
            
            # Atualizar último sync da config
            config = self.db.query(SankhyaConfig).filter(
                SankhyaConfig.tenant_id == log.tenant_id
            ).first()
            if config:
                config.ultimo_sync = datetime.utcnow()
            
            self.db.commit()


class SankhyaPessoaService:
    """Serviço para sincronização de pessoas."""

    def __init__(self, db: Session):
        self.db = db

    async def importar_pessoas(self, tenant_id: str,
                              log_id: int = None) -> int:
        """Importa pessoas do Sankhya."""
        config = self._get_config(tenant_id)
        if not config:
            return 0
        
        importados = 0
        
        async with SankhyaWSClient(config) as client:
            # Buscar pessoas físicas
            try:
                resultado = await client.executar_ws(
                    "PessoaFisica", "findAll", {}
                )
                
                for pessoa_data in resultado.get("pessoas", []):
                    await self._salvar_pessoa_fisica(tenant_id, pessoa_data)
                    importados += 1
            except Exception as e:
                print(f"Erro ao importar pessoas físicas: {e}")
            
            # Buscar pessoas jurídicas
            try:
                resultado = await client.executar_ws(
                    "PessoaJuridica", "findAll", {}
                )
                
                for pessoa_data in resultado.get("pessoas", []):
                    await self._salvar_pessoa_juridica(tenant_id, pessoa_data)
                    importados += 1
            except Exception as e:
                print(f"Erro ao importar pessoas jurídicas: {e}")
        
        if log_id:
            self._finalizar_log(log_id, True, importados)
        
        return importados

    async def _salvar_pessoa_fisica(self, tenant_id: str,
                                   data: Dict) -> SankhyaPessoa:
        """Salva pessoa física."""
        pessoa = SankhyaPessoa(
            tenant_id=tenant_id,
            sankhya_id=str(data.get("CODPARC", "")),
            tipo="FISICA",
            nome=data.get("NOME", ""),
            cpf=data.get("CGC_CPF", ""),
            email=data.get("EMAIL", ""),
            telefone=data.get("TELEFONE", ""),
            endereco=data.get("ENDERECO", ""),
            bairro=data.get("BAIRRO", ""),
            cidade=data.get("CIDADE", ""),
            uf=data.get("UF", ""),
            cep=data.get("CEP", ""),
            ativo=data.get("ATIVO", "S") == "S",
            sincronizado_em=datetime.utcnow()
        )
        
        # Upsert
        existing = self.db.query(SankhyaPessoa).filter(
            SankhyaPessoa.sankhya_id == pessoa.sankhya_id
        ).first()
        
        if existing:
            for key, value in pessoa.__dict__.items():
                if not key.startswith('_'):
                    setattr(existing, key, value)
            pessoa = existing
        else:
            self.db.add(pessoa)
        
        self.db.commit()
        self.db.refresh(pessoa)
        return pessoa

    async def _salvar_pessoa_juridica(self, tenant_id: str,
                                     data: Dict) -> SankhyaPessoa:
        """Salva pessoa jurídica."""
        pessoa = SankhyaPessoa(
            tenant_id=tenant_id,
            sankhya_id=str(data.get("CODPARC", "")),
            tipo="JURIDICA",
            nome=data.get("NOME", ""),
            nome_fantasia=data.get("NOMEFANTASIA", ""),
            cnpj=data.get("CGC_CPF", ""),
            ie=data.get("INSCRICAO", ""),
            email=data.get("EMAIL", ""),
            telefone=data.get("TELEFONE", ""),
            endereco=data.get("ENDERECO", ""),
            bairro=data.get("BAIRRO", ""),
            cidade=data.get("CIDADE", ""),
            uf=data.get("UF", ""),
            cep=data.get("CEP", ""),
            ativo=data.get("ATIVO", "S") == "S",
            sincronizado_em=datetime.utcnow()
        )
        
        # Upsert
        existing = self.db.query(SankhyaPessoa).filter(
            SankhyaPessoa.sankhya_id == pessoa.sankhya_id
        ).first()
        
        if existing:
            for key, value in pessoa.__dict__.items():
                if not key.startswith('_'):
                    setattr(existing, key, value)
            pessoa = existing
        else:
            self.db.add(pessoa)
        
        self.db.commit()
        self.db.refresh(pessoa)
        return pessoa

    def _get_config(self, tenant_id: str) -> Optional[SankhyaConfig]:
        return self.db.query(SankhyaConfig).filter(
            SankhyaConfig.tenant_id == tenant_id
        ).first()

    def _finalizar_log(self, log_id: int, sucesso: bool,
                      processados: int):
        service = SankhyaSyncService(self.db)
        service.finalizar_sync_log(log_id, sucesso, processados)


class SankhyaProdutoService:
    """Serviço para sincronização de produtos."""

    def __init__(self, db: Session):
        self.db = db

    async def importar_produtos(self, tenant_id: str,
                               log_id: int = None) -> int:
        """Importa produtos do Sankhya."""
        config = self._get_config(tenant_id)
        if not config:
            return 0
        
        importados = 0
        
        async with SankhyaWSClient(config) as client:
            try:
                resultado = await client.executar_ws(
                    "Produto", "findAll", {}
                )
                
                for produto_data in resultado.get("produtos", []):
                    await self._salvar_produto(tenant_id, produto_data)
                    importados += 1
            except Exception as e:
                print(f"Erro ao importar produtos: {e}")
        
        if log_id:
            self._finalizar_log(log_id, True, importados)
        
        return importados

    async def _salvar_produto(self, tenant_id: str,
                             data: Dict) -> SankhyaProduto:
        """Salva produto."""
        produto = SankhyaProduto(
            tenant_id=tenant_id,
            sankhya_id=str(data.get("CODPROD", "")),
            codigo=data.get("CODPROD", ""),
            nome=data.get("DESCRPROD", ""),
            descricao=data.get("COMPLEMENTO", ""),
            ncm=data.get("NCM", ""),
            unidade=data.get("UNIDADE", "UN"),
            preco_custo=float(data.get("VLCUSTO", 0) or 0),
            preco_venda=float(data.get("VLVENDA", 0) or 0),
            ativo=data.get("ATIVO", "S") == "S",
            sincronizado_em=datetime.utcnow()
        )
        
        # Upsert
        existing = self.db.query(SankhyaProduto).filter(
            SankhyaProduto.sankhya_id == produto.sankhya_id
        ).first()
        
        if existing:
            for key, value in produto.__dict__.items():
                if not key.startswith('_'):
                    setattr(existing, key, value)
            produto = existing
        else:
            self.db.add(produto)
        
        self.db.commit()
        self.db.refresh(produto)
        return produto

    def _get_config(self, tenant_id: str) -> Optional[SankhyaConfig]:
        return self.db.query(SankhyaConfig).filter(
            SankhyaConfig.tenant_id == tenant_id
        ).first()

    def _finalizar_log(self, log_id: int, sucesso: bool,
                      processados: int):
        service = SankhyaSyncService(self.db)
        service.finalizar_sync_log(log_id, sucesso, processados)
