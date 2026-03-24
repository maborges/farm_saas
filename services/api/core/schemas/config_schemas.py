from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict

class SMTPConfig(BaseModel):
    host: str = Field(..., example="smtp.mailtrap.io")
    port: int = Field(587, example=587)
    user: Optional[str] = None
    pwd: Optional[str] = Field(None, alias="pass")
    mail_from: str = Field(..., alias="from", example="noreply@agrosaas.com.br")

    class Config:
        populate_by_name = True

class SaaSConfigResponse(BaseModel):
    chave: str
    valor: Dict
    descricao: Optional[str]
    ativo: bool

class SaaSConfigUpdate(BaseModel):
    valor: Dict
    descricao: Optional[str] = None
    ativo: Optional[bool] = None

class TenantConfigResponse(BaseModel):
    categoria: str
    chave: str
    valor: Dict
    descricao: Optional[str]
    ativo: bool

    class Config:
        from_attributes = True

class TenantConfigUpdate(BaseModel):
    valor: Dict
    descricao: Optional[str] = None
    ativo: Optional[bool] = None
