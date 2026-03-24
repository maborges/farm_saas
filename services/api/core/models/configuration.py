import uuid
from sqlalchemy import String, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Uuid as UUID
from core.database import Base

class ConfiguracaoSaaS(Base):
    """
    Configurações globais do sistema persistidas no banco de dados.
    Permite alterar parâmetros como SMTP, chaves de API e limites sem Deploy.
    """
    __tablename__ = "configuracoes_saas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Ex: 'smtp_global', 'maintenance_mode', 'stripe_keys'
    chave: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    
    # Payload flexível para diferentes tipos de config
    valor: Mapped[dict] = mapped_column(JSON, nullable=False)
    
    descricao: Mapped[str | None] = mapped_column(String(255))
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
