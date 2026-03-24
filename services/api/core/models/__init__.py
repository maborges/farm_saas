from .tenant import Tenant
from .fazenda import Fazenda
from .grupo_fazendas import GrupoFazendas
from .auth import Usuario, PerfilAcesso, TenantUsuario, FazendaUsuario, ConviteAcesso
from .billing import PlanoAssinatura, AssinaturaTenant, Fatura
from .plan_changes import PlanoPricing, MudancaPlano, CobrancaAsaas, HistoricoBloqueio
from .support import ChamadoSuporte, MensagemChamado
from .knowledge_base import ConhecimentoCategoria, ConhecimentoArtigo
from .configuration import ConfiguracaoSaaS
from .tenant_config import ConfiguracaoTenant
from .admin_user import AdminUser
from .admin_impersonation import AdminImpersonation
from .sessao import SessaoAtiva
from .cupom import Cupom
from .email_template import EmailTemplate, EmailLog
from .admin_audit_log import AdminAuditLog
from .crm import PipelineEstagio, LeadCRM, AtividadeCRM

# Operacional
from operacional.models.frota import Maquinario, PlanoManutencao, RegistroManutencao, OrdemServico, ItemOrdemServico
from core.cadastros.models import ProdutoCatalogo, ProdutoAgricolaDetalhe, ProdutoEstoqueDetalhe
from core.cadastros.pessoas.models import (
    Pessoa, PessoaPII, PessoaEndereco,
    TipoRelacionamento, PessoaRelacionamento,
    PessoaConsentimento, PessoaAcessoLog,
)
from operacional.models.estoque import Deposito, SaldoEstoque, MovimentacaoEstoque, LoteEstoque, RequisicaoMaterial, ItemRequisicao, ReservaEstoque
from operacional.models.compras import Fornecedor, PedidoCompra, ItemPedidoCompra, CotacaoFornecedor

# Imóveis
from imoveis.models.imovel import ImovelRural, MatriculaImovel, Benfeitoria
