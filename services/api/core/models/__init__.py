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

# Cadastros — pessoas
from core.cadastros.pessoas.models import (
    Pessoa, PessoaDocumento, PessoaContato, PessoaEndereco, PessoaBancario,
    TipoRelacionamento, PessoaRelacionamento,
    PessoaConsentimento, PessoaAcessoLog,
)

# Cadastros — propriedades / áreas rurais
from core.cadastros.propriedades.models import (
    AreaRural, MatriculaImovel, RegistroAmbiental,
)

# Cadastros — equipamentos
from core.cadastros.equipamentos.models import Equipamento

# Cadastros — produtos (insumos / almoxarifado)
from core.cadastros.produtos.models import (
    Produto, ProdutoAgricola, ProdutoEstoque, ProdutoEPI, ProdutoCultura,
)

# Cadastros — commodities (produtos de saída / receita)
from core.cadastros.commodities.models import Commodity, CommodityClassificacao

# RH
from rh.models import ColaboradorRH, LancamentoDiaria, Empreitada

# Pecuária
from pecuaria.animal.models import LoteAnimal, Animal, EventoAnimal
from pecuaria.producao.models import ProducaoLeite
from pecuaria.models.manejo import ManejoLote

# Operacional
from operacional.models.frota import PlanoManutencao, OrdemServico, ItemOrdemServico, RegistroManutencao
from operacional.models.estoque import Deposito, SaldoEstoque, MovimentacaoEstoque, LoteEstoque, RequisicaoMaterial, ItemRequisicao, ReservaEstoque
from operacional.models.compras import Fornecedor, PedidoCompra, ItemPedidoCompra, CotacaoFornecedor
