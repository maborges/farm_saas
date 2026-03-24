class AgroSaaSError(Exception):
    """Base para todas as exceções do domínio."""
    pass

class EntityNotFoundError(AgroSaaSError):
    """Quando uma entidade não for encontrada."""
    pass

class TenantViolationError(AgroSaaSError):
    """Tentativa de acesso a dados de outro tenant / fazenda não autoriazada."""
    pass

class ModuleNotContractedError(AgroSaaSError):
    """Tentativa de usar rotas de módulos não comprados no plano."""
    pass

class BusinessRuleError(AgroSaaSError):
    """Violação de regra de negócio, validação explícita de campos."""
    pass
