"""
Serviço de Configurações Globais do Tenant.

Responsabilidades:
- Gerenciar configurações gerais do tenant (ano agrícola, unidades, moeda, fuso)
- Conversão de unidades de área (hectare ↔ alqueire)
- Gerenciar categorias customizáveis via CategoriaCustom
- Registrar histórico de alterações
- Override de configurações por fazenda
"""
from uuid import UUID
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, update
from loguru import logger
import re
import uuid as uuid_module

from core.models.tenant_config import ConfiguracaoTenant
from core.models.categoria_custom import CategoriaCustom, TipoCategoria
from core.models.configuracao_fazenda import ConfiguracaoFazenda
from core.models.historico_configuracao import HistoricoConfiguracao
from core.models.tenant import Tenant


# =============================================================================
# CONVERSÃO DE UNIDADES DE ÁREA
# =============================================================================

class UnidadeAreaConverter:
    """
    Conversor de unidades de área agrícolas.

    Fatores de conversão baseados em INCRA:
    - 1 hectare = 10.000 m²
    - 1 alqueire paulista = 24.200 m² = 2,42 ha
    - 1 alqueire mineiro = 48.400 m² = 4,84 ha
    - 1 alqueire do norte = 27.225 m² = 2,7225 ha
    - 1 acre = 4.047 m² = 0,4047 ha
    """

    PARA_HECTARE: Dict[str, float] = {
        "HA": 1.0,
        "ALQUEIRE_PAULISTA": 2.42,
        "ALQUEIRE_MINEIRO": 4.84,
        "ALQUEIRE_NORTE": 2.7225,
        "ACRE": 0.4047,
    }

    NOMES: Dict[str, str] = {
        "HA": "Hectare",
        "ALQUEIRE_PAULISTA": "Alqueire Paulista",
        "ALQUEIRE_MINEIRO": "Alqueire Mineiro",
        "ALQUEIRE_NORTE": "Alqueire do Norte",
        "ACRE": "Acre",
    }

    FUSOS_PERMITIDOS = [
        "America/Sao_Paulo",
        "America/Cuiaba",
        "America/Manaus",
        "America/Boa_Vista",
        "America/Porto_Velho",
        "America/Recife",
        "America/Fortaleza",
        "America/Belem",
        "America/Noronha",
    ]

    @classmethod
    def converter(cls, valor: float, de: str, para: str) -> float:
        de = de.upper()
        para = para.upper()
        if de not in cls.PARA_HECTARE:
            raise ValueError(f"Unidade de origem inválida: {de}")
        if para not in cls.PARA_HECTARE:
            raise ValueError(f"Unidade de destino inválida: {para}")
        valor_em_hectares = valor * cls.PARA_HECTARE[de]
        return round(valor_em_hectares / cls.PARA_HECTARE[para], 4)

    @classmethod
    def get_unidades_disponiveis(cls) -> List[Dict[str, str]]:
        return [{"codigo": c, "nome": n} for c, n in cls.NOMES.items()]


def _slugify(nome: str) -> str:
    slug = nome.lower().strip()
    slug = re.sub(r'[àáâãäå]', 'a', slug)
    slug = re.sub(r'[èéêë]', 'e', slug)
    slug = re.sub(r'[ìíîï]', 'i', slug)
    slug = re.sub(r'[òóôõö]', 'o', slug)
    slug = re.sub(r'[ùúûü]', 'u', slug)
    slug = re.sub(r'[ç]', 'c', slug)
    slug = re.sub(r'[ñ]', 'n', slug)
    slug = re.sub(r'[^a-z0-9_]', '_', slug)
    slug = re.sub(r'_+', '_', slug).strip('_')
    return slug


# =============================================================================
# SERVICE DE CONFIGURAÇÕES
# =============================================================================

class ConfiguracoesService:
    def __init__(self, session: AsyncSession, tenant_id: UUID):
        self.session = session
        self.tenant_id = tenant_id

    # --------------------------------------------------------------------------
    # CONFIGURAÇÕES GERAIS (key-value via ConfiguracaoTenant)
    # --------------------------------------------------------------------------

    async def get_configuracao(self, categoria: str, chave: str) -> Optional[ConfiguracaoTenant]:
        stmt = select(ConfiguracaoTenant).where(
            and_(
                ConfiguracaoTenant.tenant_id == self.tenant_id,
                ConfiguracaoTenant.categoria == categoria,
                ConfiguracaoTenant.chave == chave,
                ConfiguracaoTenant.ativo == True,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def set_configuracao(
        self,
        categoria: str,
        chave: str,
        valor: Any,
        descricao: Optional[str] = None,
        usuario_id: Optional[UUID] = None,
    ) -> ConfiguracaoTenant:
        config = await self.get_configuracao(categoria, chave)
        valor_anterior = config.valor if config else None

        if not config:
            config = ConfiguracaoTenant(
                tenant_id=self.tenant_id,
                categoria=categoria,
                chave=chave,
                valor=valor,
                descricao=descricao,
            )
            self.session.add(config)
        else:
            config.valor = valor
            if descricao:
                config.descricao = descricao

        await self.session.flush()

        # Registrar histórico apenas se houve mudança
        if valor_anterior != valor:
            historico = HistoricoConfiguracao(
                tenant_id=self.tenant_id,
                campo_alterado=f"{categoria}.{chave}",
                valor_anterior={"valor": valor_anterior} if valor_anterior is not None else None,
                valor_novo={"valor": valor},
                alterado_por=usuario_id,
            )
            self.session.add(historico)

        await self.session.commit()
        await self.session.refresh(config)
        return config

    async def get_configuracoes_por_categoria(self, categoria: str) -> List[ConfiguracaoTenant]:
        stmt = select(ConfiguracaoTenant).where(
            and_(
                ConfiguracaoTenant.tenant_id == self.tenant_id,
                ConfiguracaoTenant.categoria == categoria,
                ConfiguracaoTenant.ativo == True,
            )
        ).order_by(ConfiguracaoTenant.chave)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # --------------------------------------------------------------------------
    # UNIDADES DE ÁREA
    # --------------------------------------------------------------------------

    async def get_unidade_area_padrao(self) -> str:
        config = await self.get_configuracao("unidades", "area_padrao")
        return config.valor if config else "HA"

    async def set_unidade_area_padrao(self, unidade: str, usuario_id: Optional[UUID] = None) -> ConfiguracaoTenant:
        if unidade.upper() not in UnidadeAreaConverter.PARA_HECTARE:
            raise ValueError(f"Unidade inválida: {unidade}")
        return await self.set_configuracao(
            categoria="unidades",
            chave="area_padrao",
            valor=unidade.upper(),
            descricao="Unidade de área padrão para exibição",
            usuario_id=usuario_id,
        )

    async def converter_area(self, valor: float, de: str, para: Optional[str] = None) -> float:
        if para is None:
            para = await self.get_unidade_area_padrao()
        return UnidadeAreaConverter.converter(valor, de, para)

    # --------------------------------------------------------------------------
    # ANO AGRÍCOLA
    # --------------------------------------------------------------------------

    async def get_ano_agricola(self) -> Dict[str, int]:
        config_inicio = await self.get_configuracao("ano_agricola", "mes_inicio")
        config_fim = await self.get_configuracao("ano_agricola", "mes_fim")
        return {
            "mes_inicio": config_inicio.valor if config_inicio else 7,
            "mes_fim": config_fim.valor if config_fim else 6,
        }

    async def set_ano_agricola(
        self, mes_inicio: int, mes_fim: int, usuario_id: Optional[UUID] = None
    ) -> List[ConfiguracaoTenant]:
        if not (1 <= mes_inicio <= 12 and 1 <= mes_fim <= 12):
            raise ValueError("Meses devem estar entre 1 e 12")
        configs = []
        configs.append(await self.set_configuracao("ano_agricola", "mes_inicio", mes_inicio, "Mês de início do ano agrícola (1-12)", usuario_id))
        configs.append(await self.set_configuracao("ano_agricola", "mes_fim", mes_fim, "Mês de fim do ano agrícola (1-12)", usuario_id))
        return configs

    # --------------------------------------------------------------------------
    # MOEDA / FUSO / IDIOMA
    # --------------------------------------------------------------------------

    async def get_moeda_padrao(self) -> str:
        config = await self.get_configuracao("geral", "moeda")
        return config.valor if config else "BRL"

    async def set_moeda_padrao(self, moeda: str, usuario_id: Optional[UUID] = None) -> ConfiguracaoTenant:
        return await self.set_configuracao("geral", "moeda", moeda.upper(), "Moeda padrão", usuario_id)

    async def set_fuso_horario(self, fuso: str, usuario_id: Optional[UUID] = None) -> ConfiguracaoTenant:
        if fuso not in UnidadeAreaConverter.FUSOS_PERMITIDOS:
            raise ValueError(f"Fuso inválido: {fuso}. Permitidos: {UnidadeAreaConverter.FUSOS_PERMITIDOS}")
        return await self.set_configuracao("geral", "fuso_horario", fuso, "Fuso horário padrão", usuario_id)

    # --------------------------------------------------------------------------
    # SEGURANÇA (rate limiting)
    # --------------------------------------------------------------------------

    async def get_seguranca_config(self) -> dict:
        config_ativa = await self.get_configuracao("seguranca", "rate_limiting_ativo")
        config_max = await self.get_configuracao("seguranca", "max_tentativas")
        config_tempo = await self.get_configuracao("seguranca", "tempo_bloqueio_minutos")
        return {
            "rate_limiting_ativo": config_ativa.valor if config_ativa else True,
            "max_tentativas": config_max.valor if config_max else 5,
            "tempo_bloqueio_minutos": config_tempo.valor if config_tempo else 15,
        }

    async def set_seguranca_config(
        self,
        rate_limiting_ativo: bool = True,
        max_tentativas: int = 5,
        tempo_bloqueio_minutos: int = 15,
    ) -> dict:
        await self.set_configuracao("seguranca", "rate_limiting_ativo", rate_limiting_ativo)
        await self.set_configuracao("seguranca", "max_tentativas", max_tentativas)
        await self.set_configuracao("seguranca", "tempo_bloqueio_minutos", tempo_bloqueio_minutos)
        return {
            "rate_limiting_ativo": rate_limiting_ativo,
            "max_tentativas": max_tentativas,
            "tempo_bloqueio_minutos": tempo_bloqueio_minutos,
        }

    # --------------------------------------------------------------------------
    # CATEGORIAS CUSTOMIZÁVEIS (via tabela CategoriaCustom)
    # --------------------------------------------------------------------------

    async def get_categorias(
        self,
        tipo: TipoCategoria | str,
        apenas_ativas: bool = True,
        parent_id: Optional[UUID] = None,
    ) -> List[CategoriaCustom]:
        stmt = select(CategoriaCustom).where(
            and_(
                CategoriaCustom.tenant_id == self.tenant_id,
                CategoriaCustom.tipo == tipo,
            )
        )
        if apenas_ativas:
            stmt = stmt.where(CategoriaCustom.is_active == True)
        if parent_id is not None:
            stmt = stmt.where(CategoriaCustom.parent_id == parent_id)
        stmt = stmt.order_by(CategoriaCustom.ordem, CategoriaCustom.nome)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def criar_categoria(
        self,
        tipo: TipoCategoria | str,
        nome: str,
        parent_id: Optional[UUID] = None,
        cor_hex: Optional[str] = None,
        icone: Optional[str] = None,
        is_system: bool = False,
        ordem: int = 0,
    ) -> CategoriaCustom:
        # Validar nível hierárquico (máximo 2 níveis)
        if parent_id:
            pai = await self.session.get(CategoriaCustom, parent_id)
            if pai and pai.parent_id:
                raise ValueError("Máximo 2 níveis hierárquicos permitidos")

        # Slug único por tenant + tipo
        slug_base = _slugify(nome)
        slug = slug_base
        contador = 1
        while True:
            existe = await self.session.execute(
                select(CategoriaCustom).where(
                    and_(
                        CategoriaCustom.tenant_id == self.tenant_id,
                        CategoriaCustom.tipo == tipo,
                        CategoriaCustom.slug == slug,
                    )
                )
            )
            if not existe.scalar_one_or_none():
                break
            slug = f"{slug_base}_{contador}"
            contador += 1

        categoria = CategoriaCustom(
            tenant_id=self.tenant_id,
            tipo=tipo,
            nome=nome,
            slug=slug,
            parent_id=parent_id,
            cor_hex=cor_hex,
            icone=icone,
            is_system=is_system,
            ordem=ordem,
        )
        self.session.add(categoria)
        await self.session.commit()
        await self.session.refresh(categoria)
        logger.info(f"Categoria '{nome}' ({tipo}) criada para tenant {self.tenant_id}")
        return categoria

    async def atualizar_categoria(
        self,
        categoria_id: UUID,
        nome: Optional[str] = None,
        cor_hex: Optional[str] = None,
        icone: Optional[str] = None,
        ordem: Optional[int] = None,
    ) -> CategoriaCustom:
        categoria = await self.session.get(CategoriaCustom, categoria_id)
        if not categoria or categoria.tenant_id != self.tenant_id:
            raise ValueError("Categoria não encontrada")
        if categoria.is_system:
            raise ValueError("Categorias do sistema não podem ser editadas")

        if nome:
            categoria.nome = nome
        if cor_hex is not None:
            categoria.cor_hex = cor_hex
        if icone is not None:
            categoria.icone = icone
        if ordem is not None:
            categoria.ordem = ordem

        await self.session.commit()
        await self.session.refresh(categoria)
        return categoria

    async def inativar_categoria(self, categoria_id: UUID) -> bool:
        categoria = await self.session.get(CategoriaCustom, categoria_id)
        if not categoria or categoria.tenant_id != self.tenant_id:
            return False
        if categoria.is_system:
            raise ValueError("Categorias do sistema não podem ser removidas")
        categoria.is_active = False
        await self.session.commit()
        logger.info(f"Categoria {categoria_id} inativada")
        return True

    # --------------------------------------------------------------------------
    # OVERRIDE POR FAZENDA
    # --------------------------------------------------------------------------

    async def get_configuracao_fazenda(self, fazenda_id: UUID) -> Optional[ConfiguracaoFazenda]:
        stmt = select(ConfiguracaoFazenda).where(
            and_(
                ConfiguracaoFazenda.fazenda_id == fazenda_id,
                ConfiguracaoFazenda.tenant_id == self.tenant_id,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def set_override_fazenda(self, fazenda_id: UUID, overrides: dict) -> ConfiguracaoFazenda:
        cfg = await self.get_configuracao_fazenda(fazenda_id)
        if not cfg:
            cfg = ConfiguracaoFazenda(
                fazenda_id=fazenda_id,
                tenant_id=self.tenant_id,
                overrides=overrides,
            )
            self.session.add(cfg)
        else:
            cfg.overrides = overrides
        await self.session.commit()
        await self.session.refresh(cfg)
        return cfg

    # --------------------------------------------------------------------------
    # HISTÓRICO
    # --------------------------------------------------------------------------

    async def get_historico(self, limit: int = 50) -> List[HistoricoConfiguracao]:
        stmt = (
            select(HistoricoConfiguracao)
            .where(HistoricoConfiguracao.tenant_id == self.tenant_id)
            .order_by(HistoricoConfiguracao.alterado_em.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


# =============================================================================
# SEEDING: CATEGORIAS PADRÃO DO SISTEMA
# =============================================================================

CATEGORIAS_PADRAO_SEED = [
    # despesa
    {"tipo": "despesa", "nome": "Despesas Operacionais", "slug": "sys_despesas_operacionais", "parent_slug": None, "is_system": True, "ordem": 1},
    {"tipo": "despesa", "nome": "Insumos", "slug": "sys_insumos", "parent_slug": "sys_despesas_operacionais", "is_system": True, "ordem": 2},
    {"tipo": "despesa", "nome": "Mão de Obra", "slug": "sys_mao_de_obra", "parent_slug": "sys_despesas_operacionais", "is_system": True, "ordem": 3},
    {"tipo": "despesa", "nome": "Manutenção", "slug": "sys_manutencao", "parent_slug": "sys_despesas_operacionais", "is_system": True, "ordem": 4},
    # receita
    {"tipo": "receita", "nome": "Vendas de Produção", "slug": "sys_vendas_producao", "parent_slug": None, "is_system": True, "ordem": 1},
    {"tipo": "receita", "nome": "Vendas de Grãos", "slug": "sys_vendas_graos", "parent_slug": "sys_vendas_producao", "is_system": True, "ordem": 2},
    {"tipo": "receita", "nome": "Vendas de Animais", "slug": "sys_vendas_animais", "parent_slug": "sys_vendas_producao", "is_system": True, "ordem": 3},
    # operacao
    {"tipo": "operacao", "nome": "Preparo do Solo", "slug": "sys_preparo_solo", "parent_slug": None, "is_system": True, "ordem": 1},
    {"tipo": "operacao", "nome": "Plantio", "slug": "sys_plantio", "parent_slug": None, "is_system": True, "ordem": 2},
    {"tipo": "operacao", "nome": "Tratos Culturais", "slug": "sys_tratos_culturais", "parent_slug": None, "is_system": True, "ordem": 3},
    {"tipo": "operacao", "nome": "Colheita", "slug": "sys_colheita", "parent_slug": None, "is_system": True, "ordem": 4},
    # produto
    {"tipo": "produto", "nome": "Insumos Agrícolas", "slug": "sys_insumos_agricolas", "parent_slug": None, "is_system": True, "ordem": 1},
    {"tipo": "produto", "nome": "Sementes", "slug": "sys_sementes", "parent_slug": "sys_insumos_agricolas", "is_system": True, "ordem": 2},
    {"tipo": "produto", "nome": "Fertilizantes", "slug": "sys_fertilizantes", "parent_slug": "sys_insumos_agricolas", "is_system": True, "ordem": 3},
    {"tipo": "produto", "nome": "Defensivos", "slug": "sys_defensivos", "parent_slug": "sys_insumos_agricolas", "is_system": True, "ordem": 4},
]


async def seed_categorias_padrao(session: AsyncSession, tenant_id: UUID) -> None:
    """Insere categorias padrão (sys_*) para um tenant no onboarding."""
    # Verificar se já existem
    existe = await session.execute(
        select(CategoriaCustom).where(
            and_(CategoriaCustom.tenant_id == tenant_id, CategoriaCustom.is_system == True)
        ).limit(1)
    )
    if existe.scalar_one_or_none():
        return  # Já seed feito

    # Primeira passagem: criar categorias raiz
    slug_to_id: Dict[str, UUID] = {}
    for item in CATEGORIAS_PADRAO_SEED:
        if item["parent_slug"] is None:
            cat = CategoriaCustom(
                tenant_id=tenant_id,
                tipo=item["tipo"],
                nome=item["nome"],
                slug=item["slug"],
                is_system=True,
                is_active=True,
                ordem=item["ordem"],
            )
            session.add(cat)
            await session.flush()
            slug_to_id[item["slug"]] = cat.id

    # Segunda passagem: criar subcategorias
    for item in CATEGORIAS_PADRAO_SEED:
        if item["parent_slug"] is not None:
            parent_id = slug_to_id.get(item["parent_slug"])
            cat = CategoriaCustom(
                tenant_id=tenant_id,
                tipo=item["tipo"],
                nome=item["nome"],
                slug=item["slug"],
                parent_id=parent_id,
                is_system=True,
                is_active=True,
                ordem=item["ordem"],
            )
            session.add(cat)

    await session.commit()
    logger.info(f"Categorias padrão criadas para tenant {tenant_id}")


# Manter compatibilidade com código legado que importa CATEGORIAS_PADRAO
CATEGORIAS_PADRAO = {
    "despesa": [{"id": s["slug"], "nome": s["nome"], "parent_id": s["parent_slug"], "ativa": True, "metadata": {}} for s in CATEGORIAS_PADRAO_SEED if s["tipo"] == "despesa"],
    "receita": [{"id": s["slug"], "nome": s["nome"], "parent_id": s["parent_slug"], "ativa": True, "metadata": {}} for s in CATEGORIAS_PADRAO_SEED if s["tipo"] == "receita"],
    "operacao": [{"id": s["slug"], "nome": s["nome"], "parent_id": s["parent_slug"], "ativa": True, "metadata": {}} for s in CATEGORIAS_PADRAO_SEED if s["tipo"] == "operacao"],
    "produto": [{"id": s["slug"], "nome": s["nome"], "parent_id": s["parent_slug"], "ativa": True, "metadata": {}} for s in CATEGORIAS_PADRAO_SEED if s["tipo"] == "produto"],
}
