import uuid
from sqlalchemy import String, Boolean, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Uuid as UUID
from core.database import Base

class ConfiguracaoTenant(Base):
    """
    Configurações específicas de cada assinante (Tenant).
    Permite ativar/desativar novas funcionalidades e ajustar parâmetros técnicos do mapa, RH, etc.
    """
    __tablename__ = "configuracoes_tenant"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    
    # Categoria para facilitar agrupamento na UI (ex: 'mapas', 'rh', 'frota')
    categoria: Mapped[str] = mapped_column(String(30), index=True, nullable=False)
    
    # Nome da configuração (ex: 'enable_3d_terrain', 'kml_import_limit')
    chave: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Valor flexível (Pode ser string, numero, booleano ou objeto)
    valor: Mapped[dict] = mapped_column(JSON, nullable=False)
    
    # Para ajudar o admin a entender o que essa config faz
    descricao: Mapped[str | None] = mapped_column(String(255))

    # Permite registrar a configuração mas mantê-la inativa
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
