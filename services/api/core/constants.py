"""
Constantes globais do AgroSaaS - Identificadores de Módulos Vendáveis
Cada constante representa um módulo que pode ser contratado individualmente.
"""
from enum import Enum


class PlanTier(str, Enum):
    """
    Tier do plano de assinatura. Governa a profundidade de funcionalidades
    financeiras em TODOS os módulos contratados.

    Ordem crescente: BASICO < PROFISSIONAL < ENTERPRISE

    ``PREMIUM`` permanece como alias legado para compatibilidade com dados
    antigos e integrações já publicadas.

    Uso em router:
        @router.post("/rateio", dependencies=[Depends(require_tier(PlanTier.PROFISSIONAL))])

    Uso em código:
        if tenant_tier >= PlanTier.PROFISSIONAL:
            # habilitar rateio automático
    """
    BASICO = "BASICO"
    PROFISSIONAL = "PROFISSIONAL"
    ENTERPRISE = "ENTERPRISE"
    PREMIUM = "ENTERPRISE"

    @classmethod
    def _missing_(cls, value):
        if value == "PREMIUM":
            return cls.ENTERPRISE
        return None

    @property
    def level(self) -> int:
        return {"BASICO": 1, "PROFISSIONAL": 2, "ENTERPRISE": 3}[self.value]

    def __ge__(self, other: "PlanTier") -> bool:  # type: ignore[override]
        return self.level >= other.level

    def __gt__(self, other: "PlanTier") -> bool:  # type: ignore[override]
        return self.level > other.level

    def __le__(self, other: "PlanTier") -> bool:  # type: ignore[override]
        return self.level <= other.level

    def __lt__(self, other: "PlanTier") -> bool:  # type: ignore[override]
        return self.level < other.level


class Modulos:
    """
    Identificadores únicos de módulos comercializáveis.
    Usado em:
    - PlanoAssinatura.modulos_inclusos (lista de módulos do plano)
    - Feature gates (require_module dependency)
    - Telemetria de uso
    - Precificação
    """

    # ==================== NÚCLEO (Obrigatório) ====================
    CORE = "CORE"

    # ==================== BLOCO IMÓVEIS RURAIS ====================
    IMOVEIS_CADASTRO = "IMOVEIS_CADASTRO"        # Cadastro de Imóveis Rurais + Documentos Legais
    IMOVEIS_ARRENDAMENTOS = "IMOVEIS_ARRENDAMENTOS"  # Arrendamentos e Parcerias Rurais
    IMOVEIS_AVALIACAO = "IMOVEIS_AVALIACAO"      # Avaliação Patrimonial (Enterprise)

    # ==================== BLOCO AGRÍCOLA ====================
    AGRICOLA_PLANEJAMENTO = "A1_PLANEJAMENTO"      # Planejamento de Safra e Orçamento
    AGRICOLA_CAMPO = "A2_CAMPO"                    # Caderno de Campo (OS, Apontamentos)
    AGRICOLA_DEFENSIVOS = "A3_DEFENSIVOS"          # Defensivos e Receituário
    AGRICOLA_PRECISAO = "A4_PRECISAO"              # Agricultura de Precisão (NDVI, IoT)
    AGRICOLA_COLHEITA = "A5_COLHEITA"              # Colheita e Romaneio

    # ==================== BLOCO PECUÁRIA ====================
    PECUARIA_REBANHO = "P1_REBANHO"                # Rastreio do Rebanho Básico
    PECUARIA_GENETICA = "P2_GENETICA"              # Genética Reprodutiva
    PECUARIA_CONFINAMENTO = "P3_CONFINAMENTO"      # Feedlot Control
    PECUARIA_LEITE = "P4_LEITE"                    # Pecuária Leiteira

    # ==================== BLOCO FINANCEIRO ====================
    FINANCEIRO_TESOURARIA = "F1_TESOURARIA"        # Tesouraria Básica
    FINANCEIRO_CUSTOS_ABC = "F2_CUSTOS_ABC"        # Custos ABC / Rateio
    FINANCEIRO_FISCAL = "F3_FISCAL"                # SPED, NF-e, Conformidade
    FINANCEIRO_HEDGING = "F4_HEDGING"              # Hedging, Futuros, Barter

    # ==================== BLOCO OPERACIONAL ====================
    OPERACIONAL_FROTA = "O1_FROTA"                 # Controle de Maquinários
    OPERACIONAL_ESTOQUE = "O2_ESTOQUE"             # Estoque Multi-armazéns
    OPERACIONAL_COMPRAS = "O3_COMPRAS"             # Supply e Compras

    # ==================== BLOCO RH ====================
    RH_REMUNERACAO = "RH1_REMUNERACAO"             # Remuneração Temporários
    RH_SEGURANCA = "RH2_SEGURANCA"                 # EPC, EPIs, SESMT

    # ==================== BLOCO MEIO AMBIENTE ====================
    AMBIENTAL_COMPLIANCE = "AM1_COMPLIANCE"        # CAR, Outorgas
    AMBIENTAL_CARBONO = "AM2_CARBONO"              # Pegada de Carbono, MRV

    # ==================== EXTENSÕES ENTERPRISE ====================
    EXTENSAO_IA_COPILOT = "EXT_IA"                 # IA Agrônoma / ML
    EXTENSAO_IOT_SENSORES = "EXT_IOT"              # Sensórica Direta
    EXTENSAO_ERP_BRIDGE = "EXT_ERP"                # Bridge SAP/Datasul


# ── Dependências de Cadastro ───────────────────────────────────────────────────
# Mapeia tipo de produto do catálogo → módulos que o requerem.
# Usado para filtrar o catálogo exibido ao usuário com base nos módulos contratados.
# Ex: cliente com apenas PECUARIA_REBANHO vê só RACAO_ANIMAL e MEDICAMENTO_ANIMAL.
CADASTRO_REQUERIDO_POR: dict[str, list[str]] = {
    "INSUMO_AGRICOLA": [Modulos.AGRICOLA_PLANEJAMENTO, Modulos.AGRICOLA_CAMPO],
    "SEMENTE":         [Modulos.AGRICOLA_PLANEJAMENTO, Modulos.AGRICOLA_CAMPO],
    "DEFENSIVO":       [Modulos.AGRICOLA_DEFENSIVOS],
    "FERTILIZANTE":    [Modulos.AGRICOLA_PLANEJAMENTO, Modulos.AGRICOLA_CAMPO],
    "COMBUSTIVEL":     [Modulos.OPERACIONAL_FROTA, Modulos.OPERACIONAL_ESTOQUE],
    "PECA_MAQUINARIO": [Modulos.OPERACIONAL_FROTA, Modulos.OPERACIONAL_ESTOQUE],
    "MATERIAL_GERAL":  [Modulos.OPERACIONAL_ESTOQUE, Modulos.OPERACIONAL_COMPRAS],
    "RACAO_ANIMAL":    [Modulos.PECUARIA_REBANHO],
    "MEDICAMENTO_ANIMAL": [Modulos.PECUARIA_REBANHO],
    "SERVICO":         [Modulos.CORE],
    "OUTROS":          [Modulos.CORE],
}


class ModuloMetadata:
    """
    Metadados descritivos de cada módulo.
    Usado em: Admin backoffice, catálogo de produtos, onboarding.
    """

    CATALOGO = {
        # CORE
        Modulos.CORE: {
            "nome": "Núcleo AgroSaaS",
            "descricao": "Multi-tenancy, GIS, RBAC, Offline-first",
            "categoria": "CORE",
            "obrigatorio": True,
            "preco_base_mensal": 0.0,  # Incluído em todos os planos
        },

        # IMÓVEIS RURAIS
        Modulos.IMOVEIS_CADASTRO: {
            "nome": "Cadastro de Imóveis Rurais",
            "descricao": "Gestão de NIRF, CAR, CCIR, documentos legais, certidões",
            "categoria": "IMOVEIS",
            "dependencias": [Modulos.CORE],
            "preco_base_mensal": 99.0,
        },
        Modulos.IMOVEIS_ARRENDAMENTOS: {
            "nome": "Arrendamentos e Parcerias",
            "descricao": "Contratos de arrendamento, parcerias rurais, integração financeira",
            "categoria": "IMOVEIS",
            "dependencias": [Modulos.CORE, Modulos.IMOVEIS_CADASTRO],
            "preco_base_mensal": 149.0,
        },
        Modulos.IMOVEIS_AVALIACAO: {
            "nome": "Avaliação Patrimonial",
            "descricao": "Laudo de avaliação, valor de mercado, histórico de valorização",
            "categoria": "IMOVEIS",
            "dependencias": [Modulos.CORE, Modulos.IMOVEIS_CADASTRO],
            "preco_base_mensal": 199.0,
        },

        # AGRÍCOLA
        Modulos.AGRICOLA_PLANEJAMENTO: {
            "nome": "Planejamento de Safra",
            "descricao": "Gestão de ciclos, orçado vs realizado, rotação de culturas",
            "categoria": "AGRICOLA",
            "dependencias": [Modulos.CORE],
            "preco_base_mensal": 199.0,
        },
        Modulos.AGRICOLA_CAMPO: {
            "nome": "Caderno de Campo",
            "descricao": "Ordens de Serviço, apontamentos, scouting georreferenciado",
            "categoria": "AGRICOLA",
            "dependencias": [Modulos.CORE],
            "preco_base_mensal": 299.0,
        },
        Modulos.AGRICOLA_DEFENSIVOS: {
            "nome": "Defensivos e Receituário",
            "descricao": "Controle fitossanitário, período de carência, receituário CREA",
            "categoria": "AGRICOLA",
            "dependencias": [Modulos.CORE, Modulos.AGRICOLA_CAMPO],
            "preco_base_mensal": 149.0,
        },
        Modulos.AGRICOLA_PRECISAO: {
            "nome": "Agricultura de Precisão",
            "descricao": "NDVI, NDRE, prescrições variable rate, IoT",
            "categoria": "AGRICOLA",
            "dependencias": [Modulos.CORE],
            "preco_base_mensal": 499.0,
        },
        Modulos.AGRICOLA_COLHEITA: {
            "nome": "Colheita e Romaneio",
            "descricao": "Romaneio dinâmico, balanças, despacho MDFe",
            "categoria": "AGRICOLA",
            "dependencias": [Modulos.CORE, Modulos.AGRICOLA_PLANEJAMENTO],
            "preco_base_mensal": 249.0,
        },

        # PECUÁRIA
        Modulos.PECUARIA_REBANHO: {
            "nome": "Controle de Rebanho",
            "descricao": "Rastreio individual, GMD, pesagens, sanidade básica",
            "categoria": "PECUARIA",
            "dependencias": [Modulos.CORE],
            "preco_base_mensal": 249.0,
        },
        Modulos.PECUARIA_GENETICA: {
            "nome": "Genética Reprodutiva",
            "descricao": "IATF, diagnóstico prenhez, genealogia",
            "categoria": "PECUARIA",
            "dependencias": [Modulos.CORE, Modulos.PECUARIA_REBANHO],
            "preco_base_mensal": 349.0,
        },
        Modulos.PECUARIA_CONFINAMENTO: {
            "nome": "Feedlot Control",
            "descricao": "Fábrica de ração, TMR, controle de cochos",
            "categoria": "PECUARIA",
            "dependencias": [Modulos.CORE, Modulos.PECUARIA_REBANHO],
            "preco_base_mensal": 399.0,
        },
        Modulos.PECUARIA_LEITE: {
            "nome": "Pecuária Leiteira",
            "descricao": "Controle leiteiro, CCS, CBT, curvas de lactação",
            "categoria": "PECUARIA",
            "dependencias": [Modulos.CORE, Modulos.PECUARIA_REBANHO],
            "preco_base_mensal": 299.0,
        },

        # FINANCEIRO
        Modulos.FINANCEIRO_TESOURARIA: {
            "nome": "Tesouraria",
            "descricao": "DFC, contas a pagar/receber, conciliação bancária",
            "categoria": "FINANCEIRO",
            "dependencias": [Modulos.CORE],
            "preco_base_mensal": 199.0,
        },
        Modulos.FINANCEIRO_CUSTOS_ABC: {
            "nome": "Custos ABC",
            "descricao": "Rateio de custos, centro de custos rurais, margem por talhão",
            "categoria": "FINANCEIRO",
            "dependencias": [Modulos.CORE, Modulos.FINANCEIRO_TESOURARIA],
            "preco_base_mensal": 299.0,
        },
        Modulos.FINANCEIRO_FISCAL: {
            "nome": "Fiscal e Compliance",
            "descricao": "LCDPR, NF-e, MDFe, SPED, GPS/DARF",
            "categoria": "FINANCEIRO",
            "dependencias": [Modulos.CORE, Modulos.FINANCEIRO_TESOURARIA],
            "preco_base_mensal": 449.0,
        },
        Modulos.FINANCEIRO_HEDGING: {
            "nome": "Hedging e Futuros",
            "descricao": "Proteção B3, barter, contratos futuros",
            "categoria": "FINANCEIRO",
            "dependencias": [Modulos.CORE, Modulos.FINANCEIRO_TESOURARIA],
            "preco_base_mensal": 599.0,
        },

        # OPERACIONAL
        Modulos.OPERACIONAL_FROTA: {
            "nome": "Controle de Frota",
            "descricao": "Manutenções preventivas, horímetro, combustível",
            "categoria": "OPERACIONAL",
            "dependencias": [Modulos.CORE],
            "preco_base_mensal": 179.0,
        },
        Modulos.OPERACIONAL_ESTOQUE: {
            "nome": "Estoque Multi-armazéns",
            "descricao": "Movimentações, validade, inventário, auditoria",
            "categoria": "OPERACIONAL",
            "dependencias": [Modulos.CORE],
            "preco_base_mensal": 199.0,
        },
        Modulos.OPERACIONAL_COMPRAS: {
            "nome": "Supply e Compras",
            "descricao": "Solicitações, cotações, PO, recebimento",
            "categoria": "OPERACIONAL",
            "dependencias": [Modulos.CORE, Modulos.OPERACIONAL_ESTOQUE],
            "preco_base_mensal": 249.0,
        },

        # RH
        Modulos.RH_REMUNERACAO: {
            "nome": "Remuneração Rural",
            "descricao": "Diárias, empreitadas, pagamento por produção",
            "categoria": "RH",
            "dependencias": [Modulos.CORE],
            "preco_base_mensal": 199.0,
        },
        Modulos.RH_SEGURANCA: {
            "nome": "Segurança do Trabalho",
            "descricao": "EPC, EPIs, PPP, PCMSO, NR-31",
            "categoria": "RH",
            "dependencias": [Modulos.CORE],
            "preco_base_mensal": 149.0,
        },

        # AMBIENTAL
        Modulos.AMBIENTAL_COMPLIANCE: {
            "nome": "Compliance Ambiental",
            "descricao": "CAR, CCIR, outorgas hídricas, APP/RL",
            "categoria": "AMBIENTAL",
            "dependencias": [Modulos.CORE],
            "preco_base_mensal": 299.0,
        },
        Modulos.AMBIENTAL_CARBONO: {
            "nome": "Gestão de Carbono",
            "descricao": "MRV, pegada de carbono, créditos de carbono",
            "categoria": "AMBIENTAL",
            "dependencias": [Modulos.CORE],
            "preco_base_mensal": 499.0,
        },

        # EXTENSÕES
        Modulos.EXTENSAO_IA_COPILOT: {
            "nome": "IA Copilot Agrônoma",
            "descricao": "LLM treinado, alertas preditivos, recomendações EMBRAPA",
            "categoria": "EXTENSAO",
            "dependencias": [Modulos.CORE],
            "preco_base_mensal": 799.0,
        },
        Modulos.EXTENSAO_IOT_SENSORES: {
            "nome": "Integração IoT",
            "descricao": "John Deere Ops Center, balanças inteligentes, sensores",
            "categoria": "EXTENSAO",
            "dependencias": [Modulos.CORE],
            "preco_base_mensal": 599.0,
        },
        Modulos.EXTENSAO_ERP_BRIDGE: {
            "nome": "Bridge ERP Corporativo",
            "descricao": "SAP, Datasul, Open Banking, Power BI",
            "categoria": "EXTENSAO",
            "dependencias": [Modulos.CORE],
            "preco_base_mensal": 1299.0,
        },
    }

    @classmethod
    def get_modulo_info(cls, modulo_id: str) -> dict:
        """Retorna informações de um módulo específico."""
        return cls.CATALOGO.get(modulo_id, {})

    @classmethod
    def calcular_preco_pacote(cls, modulos: list[str]) -> float:
        """Calcula o preço total de um conjunto de módulos."""
        return sum(
            cls.CATALOGO.get(mod, {}).get("preco_base_mensal", 0.0)
            for mod in modulos
        )

    @classmethod
    def validar_dependencias(cls, modulos: list[str]) -> tuple[bool, list[str]]:
        """
        Valida se todas as dependências estão presentes.
        Retorna (valido: bool, modulos_faltantes: list)
        """
        faltantes = []
        for mod in modulos:
            info = cls.CATALOGO.get(mod, {})
            deps = info.get("dependencias", [])
            for dep in deps:
                if dep not in modulos:
                    faltantes.append(f"{mod} requer {dep}")

        return len(faltantes) == 0, faltantes


# ==================== PERMISSÕES DO BACKOFFICE (Admin SaaS) ====================

class BackofficePermissions:
    """
    Mapeamento de permissões para administradores do SaaS.

    Formato: "recurso:acao"
    Recursos: dashboard, bi, tenants, plans, billing, users, support, config, kb
    Ações: view, create, update, delete, * (todas)
    """

    PERMISSIONS_MAP = {
        "super_admin": ["*"],  # Acesso total

        "admin": [
            "backoffice:dashboard:view",
            "backoffice:bi:view",
            "backoffice:tenants:*",
            "backoffice:plans:*",
            "backoffice:users:view",
            "backoffice:users:toggle_status",
            "backoffice:support:*",
            "backoffice:config:view",
            "backoffice:kb:*",
            "backoffice:profiles:*",
        ],

        "suporte": [
            "backoffice:dashboard:view",
            "backoffice:tenants:view",
            "backoffice:users:view",
            "backoffice:support:*",
            "backoffice:kb:*",
        ],

        "financeiro": [
            "backoffice:dashboard:view",
            "backoffice:bi:view",
            "backoffice:billing:*",
            "backoffice:tenants:view",
            "backoffice:plans:view",
            "backoffice:users:view",
        ],

        "comercial": [
            "backoffice:dashboard:view",
            "backoffice:plans:*",
            "backoffice:cupons:*",
            "backoffice:tenants:view",
            "backoffice:tenants:assign_plan",
            "backoffice:bi:view",
        ]
    }

    @classmethod
    def has_permission(cls, role: str, permission: str) -> bool:
        """Verifica se uma role tem determinada permissão."""
        user_perms = cls.PERMISSIONS_MAP.get(role, [])

        # Wildcard total
        if "*" in user_perms:
            return True

        # Permissão exata
        if permission in user_perms:
            return True

        # Wildcard de recurso (ex: "tenants:*" permite "tenants:view")
        if ":" in permission:
            resource, action = permission.split(":", 1)
            wildcard = f"{resource}:*"
            if wildcard in user_perms:
                return True

        return False


# ==================== PERFIS E PERMISSÕES DO TENANT (Assinante) ====================

class TenantRoles:
    """
    Perfis padrão do sistema para usuários de tenants.
    Podem ser customizados pelo tenant através de PerfilAcesso.
    """

    # Perfis padrão
    OWNER = "owner"
    ADMIN = "admin"
    GERENTE = "gerente"
    AGRONOMO = "agronomo"
    OPERADOR = "operador"
    CONSULTOR = "consultor"
    FINANCEIRO = "financeiro"
    AUDITOR = "auditor"

    # Descrições
    DESCRIPTIONS = {
        OWNER: "Proprietário da assinatura (acesso total)",
        ADMIN: "Administrador (gestão completa exceto billing)",
        GERENTE: "Gerente de área (módulos específicos)",
        AGRONOMO: "Técnico agrícola (Agricultura completo)",
        OPERADOR: "Operador de campo (apontamentos)",
        CONSULTOR: "Consultor externo (apenas leitura)",
        FINANCEIRO: "Gestor financeiro (módulo financeiro completo)",
        AUDITOR: "Auditor externo (leitura e exportação, sem escrita)",
    }


class TenantPermissions:
    """
    Mapeamento de permissões para usuários de tenants.

    Formato: "recurso:acao" ou "modulo:recurso:acao"
    Recursos tenant: users, permissions, fazendas, settings, billing
    Módulos: agricola, pecuaria, financeiro, operacional, rh
    """

    PERMISSIONS_MAP = {
        "owner": ["*"],  # Acesso total no contexto do tenant

        "admin": [
            # Gestão de equipe
            "tenant:users:*",
            "tenant:permissions:*",
            "tenant:invites:*",

            # Gestão de fazendas
            "tenant:fazendas:*",
            "tenant:grupos:*",

            # Configurações
            "tenant:settings:*",
            "tenant:billing:view",  # Apenas visualizar billing
            "tenant:audit:view",

            # Acesso a todos os módulos contratados (verificado via feature gate)
            "agricola:*",
            "pecuaria:*",
            "financeiro:*",
            "operacional:*",
            "rh:*",
            "ambiental:*",
        ],

        "gerente": [
            "tenant:users:view",
            "tenant:users:invite",
            "tenant:fazendas:view",
            "tenant:audit:view",

            # Módulos baseados na área do gerente (deve ser customizado)
            "agricola:*",
            "pecuaria:view",
        ],

        "agronomo": [
            "tenant:users:view",
            "tenant:fazendas:view",

            # Módulo agrícola completo
            "agricola:*",

            # Visualização de outros módulos
            "operacional:view",
            "rh:view",
        ],

        "operador": [
            "tenant:fazendas:view",

            # Operações de campo
            "agricola:operacoes:*",
            "agricola:defensivos:view",
            "agricola:monitoramento:*",

            # Pecuária - manejo
            "pecuaria:manejo:*",
            "pecuaria:lotes:view",

            # Operacional
            "operacional:frota:view",
            "operacional:ordens_servico:*",
        ],

        "consultor": [
            # Apenas leitura
            "tenant:fazendas:view",
            "agricola:view",
            "pecuaria:view",
            "financeiro:view",
            "operacional:view",
        ],

        "financeiro": [
            "tenant:users:view",
            "tenant:fazendas:view",

            # Módulo financeiro completo
            "financeiro:*",

            # Visualização de custos em outros módulos
            "agricola:custos:view",
            "pecuaria:custos:view",
            "operacional:custos:view",
        ],

        "auditor": [
            # Leitura geral de todos os módulos
            "tenant:fazendas:view",
            "agricola:*:view",
            "agricola:*:list",
            "agricola:*:export",
            "pecuaria:*:view",
            "pecuaria:*:list",
            "pecuaria:*:export",
            "financeiro:*:view",
            "financeiro:*:list",
            "financeiro:*:export",
            "operacional:*:view",
            "operacional:*:list",
            "operacional:*:export",
            "estoque:*:view",
            "estoque:*:list",
            "estoque:*:export",
        ],
    }

    @classmethod
    def has_permission(cls, role: str, permission: str, custom_permissions: dict = None) -> bool:
        """
        Verifica se uma role tem determinada permissão.

        Args:
            role: Nome do perfil
            permission: Permissão a verificar (ex: "agricola:operacoes:create")
            custom_permissions: Permissões customizadas do PerfilAcesso (dict JSON)

        Returns:
            bool: True se tem permissão
        """
        # Se tem permissões customizadas, usar elas
        if custom_permissions:
            return cls._check_custom_permissions(custom_permissions, permission)

        # Usar permissões padrão do perfil
        user_perms = cls.PERMISSIONS_MAP.get(role, [])

        # Wildcard total
        if "*" in user_perms:
            return True

        # Permissão exata
        if permission in user_perms:
            return True

        # Wildcards hierárquicos
        parts = permission.split(":")
        for i in range(len(parts)):
            wildcard = ":".join(parts[:i+1]) + ":*"
            if wildcard in user_perms:
                return True

        return False

    @staticmethod
    def _check_custom_permissions(custom_perms: dict, permission: str) -> bool:
        """
        Verifica permissão em formato granular.

        Formato do JSON (novo — lista de strings com wildcards):
        {
            "granted": ["agricola:operacoes:view", "financeiro:*", "agricola:relatorios:export"]
        }

        Formato legado (compatibilidade retroativa):
        {
            "agricola": "write",  # write, read, none
            "pecuaria": "read"
        }

        Também suporta perfis de sistema no formato:
        {
            "permissions": ["tenant:users:*", "agricola:*"]
        }
        """
        if not permission:
            return False

        # Formato novo: {"granted": [...]}
        granted = custom_perms.get("granted")
        if granted is not None:
            return TenantPermissions._match_permission_list(granted, permission)

        # Perfis de sistema: {"permissions": [...]}
        system_perms = custom_perms.get("permissions")
        if system_perms is not None:
            return TenantPermissions._match_permission_list(system_perms, permission)

        # Formato legado: {"agricola": "write", "pecuaria": "read"}
        parts = permission.split(":")
        module = parts[0]
        action = parts[-1] if len(parts) > 1 else "view"
        perm_level = custom_perms.get(module, "none")
        if perm_level == "write" or perm_level == "*":
            return True
        if perm_level == "read" and action in ["view", "list", "get", "export"]:
            return True
        return False

    @staticmethod
    def _match_permission_list(perm_list: list, permission: str) -> bool:
        """Verifica se uma permissão bate com qualquer entrada da lista (suporta wildcards)."""
        if "*" in perm_list:
            return True
        if permission in perm_list:
            return True
        parts = permission.split(":")
        for i in range(len(parts)):
            wildcard = ":".join(parts[:i + 1]) + ":*"
            if wildcard in perm_list:
                return True
        return False
