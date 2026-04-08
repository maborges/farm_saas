"""
Documentos Legais - Service Layer

Implementa regras de negócio para gestão documental de imóveis rurais:
- Versionamento automático de documentos
- Validação de vencimentos (CCIR, ITR)
- Alertas de documentos próximos do vencimento
- Controle de acesso a documentos restritos
- Hash de integridade de arquivos
"""
import hashlib
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
import uuid

from imoveis.models.imovel import (
    DocumentoLegal, HistoricoDocumento, ImovelRural,
    TipoDocumento, StatusDocumento
)
from core.models.auth import Usuario


class DocumentoLegalService:
    """
    Service para gestão de Documentos Legais de Imóveis Rurais.
    
    Responsabilidades:
    - Upload com versionamento automático
    - Validação de documentos obrigatórios (CCIR, ITR, CAR)
    - Alertas de vencimento (T-60, T-30, T-7, T-1)
    - Controle de acesso a documentos restritos
    - Hash SHA-256 para integridade de arquivos
    - Histórico completo de ações
    """
    
    # Documentos que exigem vencimento
    DOCUMENTOS_COM_VENCIMENTO = [TipoDocumento.CCIR, TipoDocumento.ITR_DITR]
    
    # Dias para alertas de vencimento
    ALERTAS_VENCIMENTO = [60, 30, 7, 1]
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    def calcular_hash(self, conteudo: bytes) -> str:
        """Calcula hash SHA-256 do conteúdo do arquivo."""
        return hashlib.sha256(conteudo).hexdigest()
    
    async def get_documento_by_id(
        self,
        documento_id: uuid.UUID,
        tenant_id: uuid.UUID
    ) -> Optional[DocumentoLegal]:
        """Busca documento por ID com tenant isolation."""
        result = await self.session.execute(
            select(DocumentoLegal)
            .where(
                and_(
                    DocumentoLegal.id == documento_id,
                    DocumentoLegal.tenant_id == tenant_id,
                    DocumentoLegal.deleted_at.is_(None)
                )
            )
            .options(
                selectinload(DocumentoLegal.imovel),
                selectinload(DocumentoLegal.versao_anterior)
            )
        )
        return result.scalar_one_or_none()
    
    async def get_documentos_by_imovel(
        self,
        imovel_id: uuid.UUID,
        tenant_id: uuid.UUID,
        tipo: Optional[TipoDocumento] = None,
        apenas_ativos: bool = True
    ) -> List[DocumentoLegal]:
        """
        Busca documentos de um imóvel.
        
        Args:
            imovel_id: ID do imóvel
            tenant_id: ID do tenant
            tipo: Filtrar por tipo específico (CCIR, ITR, etc.)
            apenas_ativos: Se True, retorna apenas documentos ativos
        """
        conditions = [
            DocumentoLegal.imovel_id == imovel_id,
            DocumentoLegal.tenant_id == tenant_id,
            DocumentoLegal.deleted_at.is_(None)
        ]
        
        if tipo:
            conditions.append(DocumentoLegal.tipo == tipo)
        
        if apenas_ativos:
            conditions.append(DocumentoLegal.status == StatusDocumento.ATIVO)
        
        result = await self.session.execute(
            select(DocumentoLegal)
            .where(and_(*conditions))
            .order_by(DocumentoLegal.tipo, DocumentoLegal.versao.desc())
        )
        return list(result.scalars().all())
    
    async def get_documento_ativo(
        self,
        imovel_id: uuid.UUID,
        tipo: TipoDocumento,
        tenant_id: uuid.UUID
    ) -> Optional[DocumentoLegal]:
        """Busca documento ativo mais recente por tipo e imóvel."""
        result = await self.session.execute(
            select(DocumentoLegal)
            .where(
                and_(
                    DocumentoLegal.imovel_id == imovel_id,
                    DocumentoLegal.tipo == tipo,
                    DocumentoLegal.status == StatusDocumento.ATIVO,
                    DocumentoLegal.tenant_id == tenant_id,
                    DocumentoLegal.deleted_at.is_(None)
                )
            )
            .order_by(DocumentoLegal.versao.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    async def validar_documento_obrigatorio(
        self,
        imovel_id: uuid.UUID,
        tipo: TipoDocumento,
        tenant_id: uuid.UUID
    ) -> Tuple[bool, str, Optional[DocumentoLegal]]:
        """
        Valida se imóvel possui documento obrigatório ativo.
        
        Returns:
            tuple[bool, str, DocumentoLegal]: (valido, mensagem, documento)
        """
        documento = await self.get_documento_ativo(imovel_id, tipo, tenant_id)
        
        if not documento:
            return False, f"Imóvel não possui {tipo.value} cadastrado", None
        
        if documento.data_vencimento and documento.data_vencimento < date.today():
            dias_vencido = (date.today() - documento.data_vencimento).days
            return (
                False,
                f"{tipo.value} vencido há {dias_vencido} dias em {documento.data_vencimento}",
                documento
            )
        
        return True, f"{tipo.value} válido", documento
    
    async def criar_documento(
        self,
        tenant_id: uuid.UUID,
        imovel_id: uuid.UUID,
        tipo: TipoDocumento,
        path_storage: str,
        nome_arquivo: str,
        tamanho_bytes: int,
        conteudo_bytes: Optional[bytes] = None,
        descricao: Optional[str] = None,
        numero_documento: Optional[str] = None,
        data_emissao: Optional[date] = None,
        data_vencimento: Optional[date] = None,
        restrito: bool = False,
        created_by: Optional[uuid.UUID] = None
    ) -> Tuple[DocumentoLegal, List[str]]:
        """
        Cria novo documento com versionamento automático.
        
        Se já existe documento ativo do mesmo tipo:
        1. Marca versão anterior como SUBSTITUIDO
        2. Cria nova versão com número incrementado
        3. Registra no histórico
        
        Args:
            tenant_id: ID do tenant
            imovel_id: ID do imóvel
            tipo: Tipo de documento
            path_storage: Caminho no storage (S3/local)
            nome_arquivo: Nome original do arquivo
            tamanho_bytes: Tamanho em bytes
            conteudo_bytes: Conteúdo do arquivo para hash
            descricao: Descrição opcional
            numero_documento: Número do documento (ex: número CCIR)
            data_emissao: Data de emissão
            data_vencimento: Data de vencimento (obrigatória para CCIR/ITR)
            restrito: Se True, apenas admin/owner podem acessar
            created_by: ID do usuário criador
        
        Returns:
            tuple[DocumentoLegal, List[str]]: (documento, alertas)
        """
        alertas = []
        
        # Validações
        if tipo in self.DOCUMENTOS_COM_VENCIMENTO and not data_vencimento:
            raise ValueError(f"{tipo.value} exige data de vencimento")
        
        # Verifica se CCIR do imóvel está ativo (para outros documentos)
        imovel = await self.session.get(ImovelRural, imovel_id)
        if not imovel:
            raise ValueError("Imóvel não encontrado")
        
        # Busca documento ativo do mesmo tipo para versionamento
        documento_ativo = await self.get_documento_ativo(imovel_id, tipo, tenant_id)
        
        # Determina número da versão
        versao = 1
        substituido_por = None
        
        if documento_ativo:
            # Marca versão anterior como substituída
            documento_ativo.status = StatusDocumento.SUBSTITUIDO
            documento_ativo.substituido_por = None  # Será atualizado após criar novo
            
            versao = documento_ativo.versao + 1
            alertas.append(f"Documento versão {documento_ativo.versao} será marcado como substituído")
        
        # Calcula hash do conteúdo
        hash_conteudo = None
        if conteudo_bytes:
            hash_conteudo = self.calcular_hash(conteudo_bytes)
        
        # Cria novo documento
        documento = DocumentoLegal(
            tenant_id=tenant_id,
            imovel_id=imovel_id,
            tipo=tipo,
            descricao=descricao,
            numero_documento=numero_documento,
            data_emissao=data_emissao,
            data_vencimento=data_vencimento,
            status=StatusDocumento.ATIVO,
            versao=versao,
            path_storage=path_storage,
            nome_arquivo=nome_arquivo,
            tamanho_bytes=tamanho_bytes,
            hash_conteudo=hash_conteudo,
            restrito=restrito,
            created_by=created_by
        )
        
        self.session.add(documento)
        await self.session.flush()  # Para gerar ID
        
        # Atualiza referência do documento anterior
        if documento_ativo:
            documento_ativo.substituido_por = documento.id
        
        # Registra no histórico
        historico = HistoricoDocumento(
            documento_id=documento.id,
            usuario_id=created_by or uuid.UUID(int=0),  # System user if None
            acao="UPLOAD",
            dados_acao={
                "versao": versao,
                "nome_arquivo": nome_arquivo,
                "tamanho_bytes": tamanho_bytes
            }
        )
        self.session.add(historico)
        
        # Verifica se está próximo do vencimento
        if data_vencimento:
            dias_para_vencimento = (data_vencimento - date.today()).days
            if dias_para_vencimento <= 30:
                alertas.append(f"ALERTA: Documento vence em {dias_para_vencimento} dias")
        
        return documento, alertas
    
    async def substituir_documento(
        self,
        documento_id: uuid.UUID,
        tenant_id: uuid.UUID,
        path_storage: str,
        nome_arquivo: str,
        tamanho_bytes: int,
        conteudo_bytes: Optional[bytes] = None,
        usuario_id: Optional[uuid.UUID] = None
    ) -> Tuple[DocumentoLegal, List[str]]:
        """
        Substitui documento existente por nova versão.
        
        Atalho para criar_documento que busca o documento existente.
        """
        documento_atual = await self.get_documento_by_id(documento_id, tenant_id)
        
        if not documento_atual:
            raise ValueError("Documento não encontrado")
        
        # Cria nova versão mantendo dados do documento atual
        return await self.criar_documento(
            tenant_id=tenant_id,
            imovel_id=documento_atual.imovel_id,
            tipo=documento_atual.tipo,
            path_storage=path_storage,
            nome_arquivo=nome_arquivo,
            tamanho_bytes=tamanho_bytes,
            conteudo_bytes=conteudo_bytes,
            descricao=documento_atual.descricao,
            numero_documento=documento_atual.numero_documento,
            data_emissao=documento_atual.data_emissao,
            data_vencimento=documento_atual.data_vencimento,
            restrito=documento_atual.restrito,
            created_by=usuario_id
        )
    
    async def cancelar_documento(
        self,
        documento_id: uuid.UUID,
        tenant_id: uuid.UUID,
        motivo: str,
        usuario_id: uuid.UUID
    ) -> bool:
        """
        Cancela documento (ex: documento errado, fraudulento).
        
        Diferente de substituir, não cria nova versão.
        """
        documento = await self.get_documento_by_id(documento_id, tenant_id)
        
        if not documento:
            raise ValueError("Documento não encontrado")
        
        documento.status = StatusDocumento.CANCELADO
        
        # Registra no histórico
        historico = HistoricoDocumento(
            documento_id=documento_id,
            usuario_id=usuario_id,
            acao="CANCELAMENTO",
            dados_acao={"motivo": motivo}
        )
        self.session.add(historico)
        
        return True
    
    async def registrar_visualizacao(
        self,
        documento_id: uuid.UUID,
        usuario_id: uuid.UUID
    ) -> None:
        """Registra visualização de documento no histórico."""
        historico = HistoricoDocumento(
            documento_id=documento_id,
            usuario_id=usuario_id,
            acao="VISUALIZACAO",
            dados_acao={}
        )
        self.session.add(historico)
    
    async def registrar_download(
        self,
        documento_id: uuid.UUID,
        usuario_id: uuid.UUID,
        ip_address: Optional[str] = None
    ) -> None:
        """Registra download de documento no histórico."""
        historico = HistoricoDocumento(
            documento_id=documento_id,
            usuario_id=usuario_id,
            acao="DOWNLOAD",
            dados_acao={"ip_address": ip_address}
        )
        self.session.add(historico)
    
    async def get_documentos_vencendo(
        self,
        tenant_id: uuid.UUID,
        dias_limite: int = 60,
        imovel_id: Optional[uuid.UUID] = None
    ) -> List[DocumentoLegal]:
        """
        Busca documentos vencendo nos próximos X dias.
        
        Usado para gerar alertas e notificações.
        """
        hoje = date.today()
        limite = hoje + timedelta(days=dias_limite)
        
        conditions = [
            DocumentoLegal.tenant_id == tenant_id,
            DocumentoLegal.status == StatusDocumento.ATIVO,
            DocumentoLegal.deleted_at.is_(None),
            DocumentoLegal.data_vencimento.is_not(None),
            DocumentoLegal.data_vencimento <= limite,
            DocumentoLegal.data_vencimento >= hoje
        ]
        
        if imovel_id:
            conditions.append(DocumentoLegal.imovel_id == imovel_id)
        
        result = await self.session.execute(
            select(DocumentoLegal)
            .where(and_(*conditions))
            .order_by(DocumentoLegal.data_vencimento.asc())
        )
        return list(result.scalars().all())
    
    async def get_documentos_vencidos(
        self,
        tenant_id: uuid.UUID,
        imovel_id: Optional[uuid.UUID] = None
    ) -> List[DocumentoLegal]:
        """Busca documentos já vencidos."""
        hoje = date.today()
        
        conditions = [
            DocumentoLegal.tenant_id == tenant_id,
            DocumentoLegal.status == StatusDocumento.ATIVO,
            DocumentoLegal.deleted_at.is_(None),
            DocumentoLegal.data_vencimento.is_not(None),
            DocumentoLegal.data_vencimento < hoje
        ]
        
        if imovel_id:
            conditions.append(DocumentoLegal.imovel_id == imovel_id)
        
        result = await self.session.execute(
            select(DocumentoLegal)
            .where(and_(*conditions))
            .order_by(DocumentoLegal.data_vencimento.asc())
        )
        return list(result.scalars().all())
    
    async def verificar_situacao_documental(
        self,
        imovel_id: uuid.UUID,
        tenant_id: uuid.UUID
    ) -> dict:
        """
        Verifica situação documental completa do imóvel.
        
        Returns:
            dict: {
                "regular": bool,
                "documentos_obrigatorios": dict,
                "pendentes": list,
                "vencidos": list,
                "alertas": list
            }
        """
        documentos_obrigatorios = {
            TipoDocumento.CCIR: None,
            TipoDocumento.ITR_DITR: None,
            TipoDocumento.CAR: None
        }
        
        pendentes = []
        vencidos = []
        alertas = []
        
        # Busca documentos ativos
        for tipo in documentos_obrigatorios.keys():
            valido, msg, doc = await self.validar_documento_obrigatorio(
                imovel_id, tipo, tenant_id
            )
            
            if doc:
                documentos_obrigatorios[tipo] = doc
                
                # Verifica se está vencendo em breve
                if doc.data_vencimento:
                    dias_para_vencimento = (doc.data_vencimento - date.today()).days
                    if dias_para_vencimento <= 30 and dias_para_vencimento > 0:
                        alertas.append(f"{tipo.value} vence em {dias_para_vencimento} dias")
                    elif dias_para_vencimento <= 0:
                        vencidos.append({
                            "tipo": tipo.value,
                            "vencimento": doc.data_vencimento,
                            "dias_vencido": abs(dias_para_vencimento)
                        })
            else:
                pendentes.append(tipo.value)
                alertas.append(msg)
        
        regular = len(pendentes) == 0 and len(vencidos) == 0
        
        return {
            "regular": regular,
            "documentos_obrigatorios": {
                k.value: v.numero_documento if v else None
                for k, v in documentos_obrigatorios.items()
            },
            "pendentes": pendentes,
            "vencidos": vencidos,
            "alertas": alertas
        }
    
    async def get_historico_documento(
        self,
        documento_id: uuid.UUID
    ) -> List[HistoricoDocumento]:
        """Busca histórico completo de ações de um documento."""
        result = await self.session.execute(
            select(HistoricoDocumento)
            .where(HistoricoDocumento.documento_id == documento_id)
            .order_by(HistoricoDocumento.created_at.desc())
        )
        return list(result.scalars().all())
