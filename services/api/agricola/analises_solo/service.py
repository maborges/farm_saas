from uuid import UUID
from decimal import Decimal
from sqlalchemy import select, and_, or_, join
from sqlalchemy.ext.asyncio import AsyncSession
from core.base_service import BaseService
from core.cadastros.produtos.models import ProdutoCultura, SoloParametroCultura
from core.cadastros.propriedades.models import AreaRural
from agricola.analises_solo.models import AnaliseSolo, RegraAgronomica
from agricola.analises_solo.schemas import AnaliseSoloCreate
from agricola.tarefas.service import TarefaService
from agricola.tarefas.schemas import TarefaCreate


class AnaliseSoloService(BaseService[AnaliseSolo]):
    def __init__(self, session: AsyncSession, tenant_id: UUID):
        super().__init__(AnaliseSolo, session, tenant_id)

    # ------------------------------------------------------------------
    # Lookup hierárquico de parâmetros
    # ------------------------------------------------------------------

    async def _get_parametros(self, cultura_id: UUID, regiao: str | None) -> list[SoloParametroCultura]:
        """
        Retorna faixas na hierarquia: tenant+região > tenant > sistema+região > sistema.
        Cada nível é consultado; usa o primeiro que retornar resultados.
        """
        candidatos = [
            and_(SoloParametroCultura.tenant_id == self.tenant_id,
                 SoloParametroCultura.regiao == regiao),
            and_(SoloParametroCultura.tenant_id == self.tenant_id,
                 SoloParametroCultura.regiao.is_(None)),
            and_(SoloParametroCultura.tenant_id.is_(None),
                 SoloParametroCultura.regiao == regiao),
            and_(SoloParametroCultura.tenant_id.is_(None),
                 SoloParametroCultura.regiao.is_(None)),
        ]
        # Filtra candidatos sem região quando regiao=None para evitar duplicatas
        if not regiao:
            candidatos = [candidatos[1], candidatos[3]]

        for filtro in candidatos:
            stmt = select(SoloParametroCultura).where(
                and_(SoloParametroCultura.cultura_id == cultura_id, filtro)
            )
            result = await self.session.execute(stmt)
            rows = result.scalars().all()
            if rows:
                return list(rows)
        return []

    async def _get_cultura(self, cultura_id: UUID | None, cultura_nome: str | None) -> ProdutoCultura | None:
        if cultura_id:
            stmt = select(ProdutoCultura).where(ProdutoCultura.id == cultura_id)
        elif cultura_nome:
            stmt = select(ProdutoCultura).where(
                and_(
                    ProdutoCultura.ativa == True,
                    or_(
                        and_(ProdutoCultura.tenant_id == self.tenant_id,
                             ProdutoCultura.nome.ilike(cultura_nome)),
                        and_(ProdutoCultura.tenant_id.is_(None),
                             ProdutoCultura.nome.ilike(cultura_nome)),
                    )
                )
            ).order_by(ProdutoCultura.tenant_id.desc().nulls_last()).limit(1)
        else:
            return None
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    # ------------------------------------------------------------------
    # Fallbacks hardcoded Embrapa (usados quando não há parâmetros cadastrados)
    # ------------------------------------------------------------------

    def _fallback_nivel_ph(self, ph: float) -> dict:
        if ph < 4.5: return {"nivel": "MUITO_BAIXO", "label": "Muito Ácido",    "cor": "red"}
        if ph < 5.5: return {"nivel": "BAIXO",       "label": "Ácido",          "cor": "orange"}
        if ph < 6.5: return {"nivel": "IDEAL",        "label": "Adequado",       "cor": "green"}
        if ph < 7.5: return {"nivel": "ALTO",         "label": "Alcalino",       "cor": "blue"}
        return               {"nivel": "MUITO_ALTO",  "label": "Muito Alcalino", "cor": "purple"}

    def _fallback_fosforo(self, p: float) -> dict:
        if p < 6:  return {"nivel": "MUITO_BAIXO", "label": "Muito Baixo", "rec_p2o5_kg_ha": 130}
        if p < 12: return {"nivel": "BAIXO",       "label": "Baixo",       "rec_p2o5_kg_ha": 100}
        if p < 25: return {"nivel": "MEDIO",       "label": "Médio",       "rec_p2o5_kg_ha": 65}
        return             {"nivel": "ALTO",        "label": "Alto",        "rec_p2o5_kg_ha": 35}

    def _fallback_potassio(self, k: float) -> dict:
        if k < 70:  return {"nivel": "BAIXO",  "label": "Baixo", "rec_k2o_kg_ha": 130}
        if k < 150: return {"nivel": "MEDIO",  "label": "Médio", "rec_k2o_kg_ha": 75}
        return              {"nivel": "ALTO",   "label": "Alto",  "rec_k2o_kg_ha": 45}

    # ------------------------------------------------------------------
    # Interpretação usando parâmetros cadastrados
    # ------------------------------------------------------------------

    def _interpretar(self, valor: float, parametro: str, rows: list[SoloParametroCultura]) -> dict | None:
        faixas = [r for r in rows if r.parametro == parametro]
        for f in sorted(faixas, key=lambda x: float(x.faixa_min)):
            min_v = float(f.faixa_min)
            max_v = float(f.faixa_max) if f.faixa_max is not None else float("inf")
            if min_v <= valor < max_v:
                return {
                    "nivel": f.classificacao,
                    "label": f.classificacao.replace("_", " ").title(),
                    "rec_dose_kg_ha": float(f.rec_dose_kg_ha) if f.rec_dose_kg_ha else None,
                    "obs": f.obs,
                }
        return None

    # ------------------------------------------------------------------
    # Endpoint principal
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # Ajustes de dose por tipo de irrigação
    # ------------------------------------------------------------------

    def _fator_irrigacao_k(self, tipo_irrigacao: str | None) -> float:
        """Potássio é muito lixiviável em sistemas irrigados — parcela doses."""
        fatores = {
            "GOTEJAMENTO": 0.85,   # fertirrigação permite dose menor por aplicação
            "PIVO_CENTRAL": 0.90,
            "ASPERSAO": 0.92,
            "SULCO": 0.95,
            "SEQUEIRO": 1.0,
        }
        return fatores.get(tipo_irrigacao or "SEQUEIRO", 1.0)

    def _obs_irrigacao_p(self, tipo_irrigacao: str | None) -> str:
        if tipo_irrigacao == "GOTEJAMENTO":
            return " Com gotejamento, preferir fertirrigação parcelada (MAP solúvel)."
        if tipo_irrigacao in ("PIVO_CENTRAL", "ASPERSAO"):
            return " Dividir aplicação em 2× para maior eficiência."
        if tipo_irrigacao == "SULCO":
            return " Atenção à lixiviação; aplicar no sulco antes do fechamento."
        return ""

    def _obs_irrigacao_calagem(self, tipo_irrigacao: str | None) -> str:
        if tipo_irrigacao in ("GOTEJAMENTO", "PIVO_CENTRAL", "ASPERSAO"):
            return " Em sistema irrigado, realizar calagem com maior frequência (a cada 2–3 anos)."
        return ""

    async def gerar_recomendacoes(
        self,
        analise: AnaliseSolo,
        cultura_id: UUID | None = None,
        cultura_nome: str = "SOJA",
        regiao: str | None = None,
        v_meta: float | None = None,
    ) -> dict:
        # Prioriza cultura/irrigação gravadas na própria análise
        cultura_nome_eff = analise.cultura_nome or cultura_nome
        tipo_irrigacao = analise.tipo_irrigacao

        cultura = await self._get_cultura(cultura_id, cultura_nome_eff)
        parametros = await self._get_parametros(cultura.id, regiao) if cultura else []

        v_meta_final = v_meta or (float(cultura.v_meta_pct_padrao) if cultura and cultura.v_meta_pct_padrao else 60.0)

        rec: dict = {
            "cultura": cultura.nome if cultura else cultura_nome_eff,
            "cultura_id": str(cultura.id) if cultura else None,
            "cultura_anterior": analise.cultura_anterior,
            "tipo_irrigacao": tipo_irrigacao,
            "sistema_manejo": analise.sistema_manejo,
            "regiao": regiao,
            "v_meta_pct": v_meta_final,
            "fonte_parametros": "cadastro" if parametros else "fallback_embrapa",
            "vencida": False,
            "calagem": None,
            "fosforo": None,
            "potassio": None,
            "nitrogenio": None,
            "micronutrientes": {},
            "interpretacoes": {},
            "investimento_estimado_total": 0.0,
        }

        # Busca o talhão para saber a área
        stmt_t = select(AreaRural).where(AreaRural.id == analise.talhao_id)
        res_t = await self.session.execute(stmt_t)
        talhao = res_t.scalar_one_or_none()
        area_ha = float(talhao.area_hectares_manual or talhao.area_hectares or 0) if talhao else 0
        rec["area_ha"] = area_ha

        # Custos Estimados de Mercado (Fallback)
        # TODO: Buscar de cadastros_produtos.preco_medio se possível
        PRECOS = {
            "CALCARIO": 185.0,  # R$ / ton
            "P2O5": 5.40,       # R$ / kg
            "K2O": 4.90,        # R$ / kg
            "N": 4.50           # R$ / kg
        }

        # Alerta validade
        from datetime import date as date_
        from dateutil.relativedelta import relativedelta
        meses_val = analise.validade_meses or 12
        rec["vencida"] = date_.today() > analise.data_coleta + relativedelta(months=meses_val)

        # pH
        if analise.ph_agua is not None:
            rec["interpretacoes"]["ph"] = self._fallback_nivel_ph(float(analise.ph_agua))

        # Matéria orgânica
        if analise.materia_organica_pct is not None:
            mo = float(analise.materia_organica_pct)
            rec["interpretacoes"]["materia_organica"] = {
                "nivel": "BAIXO" if mo < 1.5 else ("MEDIO" if mo < 3.5 else "ALTO"),
                "label": "Baixo" if mo < 1.5 else ("Médio" if mo < 3.5 else "Alto"),
            }

        # m% — saturação por alumínio
        if analise.aluminio_al is not None and analise.ctc:
            al = float(analise.aluminio_al)
            ctc_v = float(analise.ctc)
            m_pct = round((al / ctc_v) * 100, 1) if ctc_v > 0 else 0
            rec["interpretacoes"]["aluminio_m_pct"] = {
                "valor": m_pct,
                "nivel": "ALTO" if m_pct > 20 else ("MEDIO" if m_pct > 10 else "BAIXO"),
                "label": "Alto — risco de toxicidade" if m_pct > 20 else (
                    "Médio" if m_pct > 10 else "Baixo"),
                "alerta": m_pct > 20,
            }

        # Calagem — método V% Embrapa
        v_atual = float(analise.v_pct or 0)
        ctc = float(analise.ctc or 0)
        if ctc > 0:
            prnt = 80.0
            nc = max(0.0, round((v_meta_final - v_atual) / 100 * ctc * (100 / prnt) * 2, 2))
            obs_cal = (
                f"Aplicar {nc:.2f} t/ha de calcário dolomítico (PRNT 80%). "
                "Incorporar 60 dias antes do plantio."
                if nc > 0 else "Saturação por bases adequada. Calagem não necessária."
            ) + self._obs_irrigacao_calagem(tipo_irrigacao)
            custo_cal = (nc * area_ha) * PRECOS["CALCARIO"]
            rec["calagem"] = {
                "necessaria": nc > 0,
                "dose_t_ha": nc,
                "v_atual_pct": round(v_atual, 1),
                "v_meta_pct": v_meta_final,
                "observacao": obs_cal,
                "custo_estimado": round(custo_cal, 2),
            }
            rec["investimento_estimado_total"] += custo_cal

        # Fósforo
        if analise.fosforo_p is not None:
            p_val = float(analise.fosforo_p)
            if parametros:
                interp = self._interpretar(p_val, "FOSFORO", parametros)
            else:
                fb = self._fallback_fosforo(p_val)
                interp = {"nivel": fb["nivel"], "label": fb["label"],
                          "rec_dose_kg_ha": fb["rec_p2o5_kg_ha"], "obs": None}
            if interp:
                obs_p = (interp.get("obs") or
                    f"P {interp['label'].lower()} ({analise.fosforo_p} mg/dm³). "
                    f"Recomendar {interp.get('rec_dose_kg_ha')} kg/ha de P₂O₅."
                ) + self._obs_irrigacao_p(tipo_irrigacao)
                custo_p = (interp.get("rec_dose_kg_ha") or 0) * area_ha * PRECOS["P2O5"]
                rec["fosforo"] = {
                    **interp,
                    "valor_mg_dm3": p_val,
                    "rec_p2o5_kg_ha": interp.get("rec_dose_kg_ha"),
                    "observacao": obs_p,
                    "custo_estimado": round(custo_p, 2),
                }
                rec["investimento_estimado_total"] += custo_p
                rec["interpretacoes"]["fosforo"] = interp

        # Potássio
        if analise.potassio_k is not None:
            k_val = float(analise.potassio_k)
            fator_k = self._fator_irrigacao_k(tipo_irrigacao)
            if parametros:
                interp = self._interpretar(k_val, "POTASSIO", parametros)
            else:
                fb = self._fallback_potassio(k_val)
                interp = {"nivel": fb["nivel"], "label": fb["label"],
                          "rec_dose_kg_ha": fb["rec_k2o_kg_ha"], "obs": None}
            if interp:
                dose_k_base = interp.get("rec_dose_kg_ha") or 0
                dose_k_ajust = round(dose_k_base * fator_k, 1)
                obs_k = (interp.get("obs") or
                    f"K {interp['label'].lower()} ({analise.potassio_k} mg/dm³). "
                    f"Recomendar {dose_k_ajust} kg/ha de K₂O"
                    + (f" (ajustado × {fator_k} p/ irrigação {tipo_irrigacao})." if fator_k != 1.0 else ".")
                )
                custo_k = dose_k_ajust * area_ha * PRECOS["K2O"]
                rec["potassio"] = {
                    **interp,
                    "valor_mg_dm3": k_val,
                    "rec_k2o_kg_ha": dose_k_ajust,
                    "rec_k2o_kg_ha_base": dose_k_base,
                    "fator_irrigacao": fator_k,
                    "observacao": obs_k,
                    "custo_estimado": round(custo_k, 2),
                }
                rec["investimento_estimado_total"] += custo_k
                rec["interpretacoes"]["potassio"] = interp

        # Micronutrientes — interpretação por faixas Embrapa
        _micro_faixas = {
            "zinco_zn":    [("BAIXO", 0, 0.5), ("MEDIO", 0.5, 1.5), ("ALTO", 1.5, 999)],
            "boro_b":      [("BAIXO", 0, 0.2), ("MEDIO", 0.2, 0.6), ("ALTO", 0.6, 999)],
            "ferro_fe":    [("BAIXO", 0, 5),   ("MEDIO", 5, 30),    ("ALTO", 30, 999)],
            "manganes_mn": [("BAIXO", 0, 1.5), ("MEDIO", 1.5, 5),   ("ALTO", 5, 999)],
        }
        _micro_labels = {"zinco_zn": "Zn", "boro_b": "B", "ferro_fe": "Fe", "manganes_mn": "Mn"}
        for campo, faixas in _micro_faixas.items():
            val = getattr(analise, campo, None)
            if val is None:
                continue
            val_f = float(val)
            for nivel, fmin, fmax in faixas:
                if fmin <= val_f < fmax:
                    rec["micronutrientes"][campo] = {
                        "valor_mg_dm3": val_f,
                        "simbolo": _micro_labels[campo],
                        "nivel": nivel,
                        "label": nivel.replace("_", " ").title(),
                        "alerta": nivel == "BAIXO",
                    }
                    break

        # Nitrogênio
        if parametros:
            n_rows = [r for r in parametros if r.parametro == "NITROGENIO"]
            if n_rows:
                r = n_rows[0]
                rec["nitrogenio"] = {
                    "rec_n_kg_ha": float(r.rec_dose_kg_ha) if r.rec_dose_kg_ha else None,
                    "observacao": r.obs or "",
                }
        if not rec["nitrogenio"]:
            # fallback genérico
            nome_cult = (cultura.nome if cultura else cultura_nome).upper()
            n_rec = 30 if nome_cult == "SOJA" else 130
            rec["nitrogenio"] = {
                "rec_n_kg_ha": n_rec,
                "observacao": (
                    "Soja: inoculação com Bradyrhizobium spp. + 20–30 kg/ha N foliar se necessário."
                    if nome_cult == "SOJA"
                    else f"Aplicar {n_rec} kg/ha de N (parcelado conforme manejo da cultura)."
                ),
            }
        
        # Atribui custo ao nitrogênio
        if rec["nitrogenio"]:
            custo_n = (rec["nitrogenio"]["rec_n_kg_ha"] or 0) * area_ha * PRECOS["N"]
            rec["nitrogenio"]["custo_estimado"] = round(custo_n, 2)
            rec["investimento_estimado_total"] += custo_n

        return rec

    # ------------------------------------------------------------------
    # Listagem de culturas disponíveis para o tenant
    # ------------------------------------------------------------------

    async def listar_culturas_disponiveis(self) -> list[ProdutoCultura]:
        stmt = (
            select(ProdutoCultura)
            .where(
                and_(
                    ProdutoCultura.ativa == True,
                    or_(
                        ProdutoCultura.tenant_id == self.tenant_id,
                        ProdutoCultura.tenant_id.is_(None),
                    ),
                )
            )
            .order_by(ProdutoCultura.nome)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # ------------------------------------------------------------------
    # Criação com cálculo automático de CTC e V%
    # ------------------------------------------------------------------

    async def criar(self, dados: AnaliseSoloCreate) -> AnaliseSolo:
        dados_dict = dados.model_dump()

        ca = dados_dict.get("calcio_ca") or 0
        mg = dados_dict.get("magnesio_mg") or 0
        k_mg_dm3 = dados_dict.get("potassio_k") or 0
        k_cmol = k_mg_dm3 / 391
        dados_dict["potassio_k"] = k_mg_dm3

        sb = ca + mg + k_cmol
        hal = dados_dict.get("hidrogenio_al_hal") or 0
        ctc_calculada = sb + hal

        if not dados_dict.get("ctc") and ctc_calculada > 0:
            dados_dict["ctc"] = round(ctc_calculada, 2)
        if not dados_dict.get("v_pct") and ctc_calculada > 0:
            dados_dict["v_pct"] = round((sb / ctc_calculada) * 100, 2)

        # m% — saturação por alumínio
        if not dados_dict.get("saturacao_al_m_pct") and ctc_calculada > 0:
            al_val = dados_dict.get("aluminio_al") or 0
            dados_dict["saturacao_al_m_pct"] = round((al_val / ctc_calculada) * 100, 2)

        return await self.create(dados_dict)


    # ------------------------------------------------------------------
    # Motor de Regras Inteligente (Fase 2)
    # ------------------------------------------------------------------

    async def aplicar_regras(self, analise_id: UUID) -> list[dict]:
        """
        Consulta as regras agronômicas cadastradas e as aplica sobre a análise.
        Retorna uma lista de recomendações/ações geradas.
        """
        # Carrega a análise com as relações necessárias
        analise = await self.get_by_id(analise_id)
        if not analise:
            return []

        # Busca todas as regras (sistema e do tenant)
        stmt = select(RegraAgronomica).where(
            and_(
                RegraAgronomica.ativo == True,
                or_(
                    RegraAgronomica.tenant_id == self.tenant_id,
                    RegraAgronomica.tenant_id.is_(None)
                )
            )
        ).order_by(RegraAgronomica.prioridade.desc())
        
        result = await self.session.execute(stmt)
        regras = result.scalars().all()

        recomendacoes = []
        
        # Contexto para avaliação das regras
        # TODO: Buscar dados da cultura/safra se vinculados
        contexto = {
             "v_pct": float(analise.v_pct or 0),
             "fosforo_p": float(analise.fosforo_p or 0),
             "potassio_k": float(analise.potassio_k or 0),
             "ph_agua": float(analise.ph_agua or 0),
             "irrigado": analise.tipo_irrigacao_id is not None,
             # Fallbacks/Metas (podem ser buscados dinamicamente)
             "v_meta_cultura": 60.0, 
             "p_critico": 12.0
        }

        for regra in regras:
            if self._avaliar_condicao(regra.condicao_json, contexto):
                recomendacoes.append({
                    "regra_id": str(regra.id),
                    "nome": regra.nome,
                    "acao": regra.acao_json,
                    "prioridade": regra.prioridade
                })

        return recomendacoes

    def _avaliar_condicao(self, condicao: dict, contexto: dict) -> bool:
        """
        Avalia dinamicamente uma condição JSON contra o contexto.
        Ex: {"campo": "v_pct", "operador": "lt", "referencia": "v_meta_cultura"}
        """
        campo = condicao.get("campo")
        operador = condicao.get("operador")
        referencia = condicao.get("referencia")

        if not campo or not operador or referencia is None:
            return False

        valor_campo = contexto.get(campo)
        # A referência pode ser um valor fixo ou outro campo do contexto
        if isinstance(referencia, str) and referencia in contexto:
            valor_ref = contexto.get(referencia)
        else:
            valor_ref = referencia

        if valor_campo is None or valor_ref is None:
            return False

        if operador == "lt": return valor_campo < valor_ref
        if operador == "le": return valor_campo <= valor_ref
        if operador == "gt": return valor_campo > valor_ref
        if operador == "ge": return valor_campo >= valor_ref
        if operador == "eq": return valor_campo == valor_ref
        return False

    async def list_all(self, limit: int = 100, offset: int = 0, **filters) -> list[AnaliseSolo]:
        """Sobrescreve list_all para incluir o nome do talhão via join."""
        stmt = (
            select(AnaliseSolo, AreaRural.nome.label("talhao_nome"))
            .join(AreaRural, AnaliseSolo.talhao_id == AreaRural.id)
            .where(AnaliseSolo.tenant_id == self.tenant_id)
        )
        
        for field, value in filters.items():
            if hasattr(AnaliseSolo, field):
                stmt = stmt.where(getattr(AnaliseSolo, field) == value)
        
        stmt = stmt.offset(offset).limit(limit).order_by(AnaliseSolo.data_coleta.desc())
        result = await self.session.execute(stmt)
        
        rows = []
        for analise, talhao_nome in result.all():
            analise.talhao_nome = talhao_nome
            rows.append(analise)
        return rows

    async def get_by_id(self, id: UUID) -> AnaliseSolo | None:
        """Sobrescreve get_by_id para incluir talhão."""
        stmt = (
            select(AnaliseSolo, AreaRural.nome.label("talhao_nome"))
            .join(AreaRural, AnaliseSolo.talhao_id == AreaRural.id)
            .where(and_(AnaliseSolo.id == id, AnaliseSolo.tenant_id == self.tenant_id))
        )
        result = await self.session.execute(stmt)
        row = result.first()
        if row:
            analise, talhao_nome = row
            analise.talhao_nome = talhao_nome
            return analise
        return None

    async def vincular_e_gerar_tarefas(self, analise_id: UUID, safra_id: UUID, user_id: UUID | None = None) -> list[UUID]:
        """
        Gera tarefas de correção de solo com base nas recomendações da análise.
        As tarefas são criadas com origem 'SOLO' e status 'PENDENTE_APROVACAO'.
        """
        analise = await self.get_or_fail(analise_id)
        recomendacoes = await self.gerar_recomendacoes(analise)
        
        # Busca o talhão para saber a área
        stmt_t = select(AreaRural).where(AreaRural.id == analise.talhao_id)
        res_t = await self.session.execute(stmt_t)
        talhao = res_t.scalar_one_or_none()
        area_ha = float(talhao.area_hectares_manual or talhao.area_hectares or 0) if talhao else 0
        
        tarefa_svc = TarefaService(self.session, self.tenant_id)
        tarefas_criadas = []

        # Custos Estimados de Mercado (Fallback)
        # TODO: Buscar de cadastros_produtos.preco_medio se possível
        PRECOS = {
            "CALCARIO": 185.0,  # R$ / ton
            "P2O5": 5.40,       # R$ / kg
            "K2O": 4.90,        # R$ / kg
            "N": 4.50           # R$ / kg
        }

        # 1. Calagem
        if recomendacoes.get("calagem") and recomendacoes["calagem"]["necessaria"]:
            cal = recomendacoes["calagem"]
            dose = float(cal["dose_t_ha"])
            qtd_total_kg = dose * area_ha * 1000
            custo = (dose * area_ha) * PRECOS["CALCARIO"]
            
            t = await tarefa_svc.criar(safra_id, TarefaCreate(
                talhao_id=analise.talhao_id,
                analise_solo_id=analise.id,
                origem="SOLO",
                tipo="CALAGEM",
                descricao=f"Calagem via análise de solo — Dose: {dose} t/ha",
                obs=cal["observacao"],
                prioridade="ALTA",
                area_ha=area_ha,
                dose_estimada_kg_ha=dose * 1000,
                quantidade_total_estimada_kg=qtd_total_kg,
                custo_estimado=custo
            ), user_id=user_id)
            tarefas_criadas.append(t.id)

        # 2. Fósforo (P)
        if recomendacoes.get("fosforo") and recomendacoes["fosforo"].get("rec_p2o5_kg_ha"):
            p = recomendacoes["fosforo"]
            dose = float(p["rec_p2o5_kg_ha"])
            qtd_total_kg = dose * area_ha
            custo = qtd_total_kg * PRECOS["P2O5"]

            t = await tarefa_svc.criar(safra_id, TarefaCreate(
                talhao_id=analise.talhao_id,
                analise_solo_id=analise.id,
                origem="SOLO",
                tipo="ADUBACAO_FOSFORO",
                descricao=f"Adubação de Fósforo — Dose: {dose} kg/ha de P2O5",
                obs=p["observacao"],
                prioridade="ALTA",
                area_ha=area_ha,
                dose_estimada_kg_ha=dose,
                quantidade_total_estimada_kg=qtd_total_kg,
                custo_estimado=custo
            ), user_id=user_id)
            tarefas_criadas.append(t.id)

        # 3. Potássio (K)
        if recomendacoes.get("potassio") and recomendacoes["potassio"].get("rec_k2o_kg_ha"):
            k = recomendacoes["potassio"]
            dose = float(k["rec_k2o_kg_ha"])
            qtd_total_kg = dose * area_ha
            custo = qtd_total_kg * PRECOS["POTASSIO"]

            t = await tarefa_svc.criar(safra_id, TarefaCreate(
                talhao_id=analise.talhao_id,
                analise_solo_id=analise.id,
                origem="SOLO",
                tipo="ADUBACAO_POTASSIO",
                descricao=f"Adubação de Potássio — Dose: {dose} kg/ha de K2O",
                obs=k["observacao"],
                prioridade="ALTA",
                area_ha=area_ha,
                dose_estimada_kg_ha=dose,
                quantidade_total_estimada_kg=qtd_total_kg,
                custo_estimado=custo
            ), user_id=user_id)
            tarefas_criadas.append(t.id)

        # 4. Nitrogênio (N)
        if recomendacoes.get("nitrogenio") and recomendacoes["nitrogenio"].get("rec_n_kg_ha"):
            n = recomendacoes["nitrogenio"]
            dose = float(n["rec_n_kg_ha"])
            qtd_total_kg = dose * area_ha
            custo = qtd_total_kg * PRECOS["N"]

            t = await tarefa_svc.criar(safra_id, TarefaCreate(
                talhao_id=analise.talhao_id,
                analise_solo_id=analise.id,
                origem="SOLO",
                tipo="ADUBACAO_NITROGENIO",
                descricao=f"Adubação de Nitrogênio — Dose: {dose} kg/ha de N",
                obs=n["observacao"],
                prioridade="MEDIA",
                area_ha=area_ha,
                dose_estimada_kg_ha=dose,
                quantidade_total_estimada_kg=qtd_total_kg,
                custo_estimado=custo
            ), user_id=user_id)
            tarefas_criadas.append(t.id)

        return tarefas_criadas
