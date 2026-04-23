import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, desc
from typing import List

from core.cadastros.propriedades.service import AreaRuralService
from core.cadastros.propriedades.models import AreaRural
from agricola.cultivos.models import Cultivo, CultivoArea
from agricola.safras.models import Safra

class AgricolaTalhaoService:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        self.session = session
        self.tenant_id = tenant_id
        self.area_svc = AreaRuralService(session, tenant_id)

    async def listar_talhoes_com_cultivo(self, unidade_produtiva_id: uuid.UUID | None = None) -> List[dict]:
        """
        Lista todos os talhões e anexa informações do cultivo ATIVO (se houver).
        """
        # 1. Buscar talhões base
        areas = await self.area_svc.listar(
            unidade_produtiva_id=unidade_produtiva_id,
            tipo="TALHAO"
        )
        
        talhoes_decorados = []
        
        for area in areas:
            # 2. Buscar cultivo ativo para este talhão
            # Regra: Cultivo cuja área vinculada é este talhão, status não cancelado/encerrado,
            # e preferencialmente da safra vigente.
            stmt = (
                select(Cultivo, Safra.nome.label("safra_nome"))
                .join(CultivoArea, Cultivo.id == CultivoArea.cultivo_id)
                .join(Safra, Cultivo.safra_id == Safra.id)
                .where(
                    CultivoArea.area_id == area.id,
                    Cultivo.tenant_id == self.tenant_id,
                    Cultivo.status.notin_(["CANCELADA", "ENCERRADA"])
                )
                .order_by(desc(Cultivo.created_at))
                .limit(1)
            )
            
            result = await self.session.execute(stmt)
            row = result.first()
            
            # Converter para dict compatível com AreaRuralResponse
            area_dict = {
                "id": area.id,
                "nome": area.nome,
                "tipo": area.tipo,
                "parent_id": area.parent_id,
                "codigo": area.codigo,
                "descricao": area.descricao,
                "area_hectares": area.area_hectares,
                "area_hectares_manual": area.area_hectares_manual,
                "geometria": area.geometria,
                "tipo_solo_id": area.tipo_solo_id,
                "tipo_solo_nome": getattr(area, "tipo_solo_nome", None),
                "irrigado": area.irrigado,
                "tipo_irrigacao_id": area.tipo_irrigacao_id,
                "tipo_irrigacao_nome": getattr(area, "tipo_irrigacao_nome", None),
                "ativo": area.ativo,
                "created_at": area.created_at,
                "updated_at": area.updated_at,
                "cultivo_atual": None
            }
            
            if row:
                cultivo, safra_nome = row
                area_dict["cultivo_atual"] = {
                    "id": cultivo.id,
                    "cultura": cultivo.cultura,
                    "safra_nome": safra_nome,
                    "data_plantio_real": cultivo.data_plantio_real,
                    "status": cultivo.status
                }
            
            talhoes_decorados.append(area_dict)
            
        return talhoes_decorados
