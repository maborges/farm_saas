from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from core.exceptions import BusinessRuleError
from core.base_service import BaseService

from agricola.analises_solo.models import AnaliseSolo
from agricola.analises_solo.schemas import AnaliseSoloCreate

class AnaliseSoloService(BaseService[AnaliseSolo]):
    def __init__(self, session: AsyncSession, tenant_id: UUID):
        super().__init__(AnaliseSolo, session, tenant_id)

    def _nivel_ph(self, ph: float) -> dict:
        if ph < 4.5: return {"nivel": "MUITO_BAIXO", "label": "Muito Ácido",    "cor": "red"}
        if ph < 5.5: return {"nivel": "BAIXO",       "label": "Ácido",          "cor": "orange"}
        if ph < 6.5: return {"nivel": "IDEAL",        "label": "Adequado",       "cor": "green"}
        if ph < 7.5: return {"nivel": "ALTO",         "label": "Alcalino",       "cor": "blue"}
        return               {"nivel": "MUITO_ALTO",  "label": "Muito Alcalino", "cor": "purple"}

    def _nivel_fosforo(self, p: float) -> dict:
        if p < 6:  return {"nivel": "MUITO_BAIXO", "label": "Muito Baixo", "rec_p2o5_kg_ha": 130}
        if p < 12: return {"nivel": "BAIXO",       "label": "Baixo",       "rec_p2o5_kg_ha": 100}
        if p < 25: return {"nivel": "MEDIO",       "label": "Médio",       "rec_p2o5_kg_ha": 65}
        return             {"nivel": "ALTO",        "label": "Alto",        "rec_p2o5_kg_ha": 35}

    def _nivel_potassio(self, k: float) -> dict:
        if k < 70:  return {"nivel": "BAIXO",  "label": "Baixo", "rec_k2o_kg_ha": 130}
        if k < 150: return {"nivel": "MEDIO",  "label": "Médio", "rec_k2o_kg_ha": 75}
        return              {"nivel": "ALTO",   "label": "Alto",  "rec_k2o_kg_ha": 45}

    def gerar_recomendacoes(self, analise: AnaliseSolo, cultura: str = "SOJA", v_meta: float = 60.0) -> dict:
        """Recomendações de calagem (método V% Embrapa) e adubação NPK."""
        rec: dict = {
            "cultura": cultura,
            "v_meta_pct": v_meta,
            "calagem": None,
            "fosforo": None,
            "potassio": None,
            "nitrogenio": None,
            "interpretacoes": {},
        }

        if analise.ph_agua is not None:
            rec["interpretacoes"]["ph"] = self._nivel_ph(float(analise.ph_agua))

        if analise.materia_organica_pct is not None:
            mo = float(analise.materia_organica_pct)
            rec["interpretacoes"]["materia_organica"] = {
                "nivel": "BAIXO" if mo < 1.5 else ("MEDIO" if mo < 3.5 else "ALTO"),
                "label": "Baixo" if mo < 1.5 else ("Médio" if mo < 3.5 else "Alto"),
            }

        # Calagem — método saturação por bases (Embrapa)
        v_atual = float(analise.v_pct or 0)
        ctc = float(analise.ctc or 0)
        if ctc > 0:
            prnt = 80.0
            nc = max(0.0, round((v_meta - v_atual) / 100 * ctc * (100 / prnt) * 2, 2))
            rec["calagem"] = {
                "necessaria": nc > 0,
                "dose_t_ha": nc,
                "v_atual_pct": round(v_atual, 1),
                "v_meta_pct": v_meta,
                "observacao": (
                    f"Aplicar {nc:.2f} t/ha de calcário dolomítico (PRNT 80%). "
                    "Incorporar 60 dias antes do plantio." if nc > 0
                    else "Saturação por bases adequada. Calagem não necessária."
                ),
            }

        # Fósforo
        if analise.fosforo_p is not None:
            interp = self._nivel_fosforo(float(analise.fosforo_p))
            rec["fosforo"] = {
                **interp,
                "valor_mg_dm3": float(analise.fosforo_p),
                "observacao": f"P {interp['label'].lower()} ({analise.fosforo_p} mg/dm³). "
                              f"Recomendar {interp['rec_p2o5_kg_ha']} kg/ha de P₂O₅.",
            }
            rec["interpretacoes"]["fosforo"] = interp

        # Potássio
        if analise.potassio_k is not None:
            interp = self._nivel_potassio(float(analise.potassio_k))
            rec["potassio"] = {
                **interp,
                "valor_mg_dm3": float(analise.potassio_k),
                "observacao": f"K {interp['label'].lower()} ({analise.potassio_k} mg/dm³). "
                              f"Recomendar {interp['rec_k2o_kg_ha']} kg/ha de K₂O.",
            }
            rec["interpretacoes"]["potassio"] = interp

        # Nitrogênio
        n_rec = 30 if cultura == "SOJA" else 130
        rec["nitrogenio"] = {
            "rec_n_kg_ha": n_rec,
            "observacao": (
                "Soja: inoculação com Bradyrhizobium spp. + 20–30 kg/ha N foliar se necessário."
                if cultura == "SOJA"
                else f"Milho: 35 kg/ha N na semeadura + {n_rec - 35} kg/ha N em cobertura (V4–V6)."
            ),
        }
        return rec

    async def criar(self, dados: AnaliseSoloCreate) -> AnaliseSolo:
        # Calcular os índices caso o laboratório não os tenha fornecido e existam valores.
        dados_dict = dados.model_dump()
        
        ca = dados_dict.get('calcio_ca') or 0
        mg = dados_dict.get('magnesio_mg') or 0
        k_mg_dm3 = dados_dict.get('potassio_k') or 0
        
        # Converter mg/dm3 de K para cmolc/dm3
        k_cmol = k_mg_dm3 / 391
        dados_dict['potassio_k'] = k_mg_dm3 # mantem o original
        
        sb = ca + mg + k_cmol # Soma de bases
        
        hal = dados_dict.get('hidrogenio_al_hal') or 0

        # CTC = SB + (H+Al)
        ctc_calculada = sb + hal
        if not dados_dict.get('ctc') and ctc_calculada > 0:
            dados_dict['ctc'] = round(ctc_calculada, 2)
            
        # V% = (SB / CTC) * 100
        if not dados_dict.get('v_pct') and ctc_calculada > 0:
            dados_dict['v_pct'] = round((sb / ctc_calculada) * 100, 2)

        return await super().create(dados_dict)
