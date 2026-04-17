#!/usr/bin/env python3
"""
Gera token JWT de admin para testes.

Uso:
    source <(python3 scripts/generate_admin_token.py)
    
Ou:
    export AGROSAAS_TOKEN=$(python3 scripts/generate_admin_token.py)
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'services', 'api'))

from jose import jwt
from datetime import datetime, timedelta, timezone
from core.config import settings
import uuid

# Gerar IDs únicos
admin_user_id = str(uuid.uuid4())
tenant_id = str(uuid.uuid4())

# Claims do JWT (admin com todos os privilégios)
claims = {
    "sub": admin_user_id,
    "tenant_id": tenant_id,
    "email": "admin_agro@borgus.com.br",
    "username": "admin_agro",
    "is_superuser": True,
    "plan_tier": "PREMIUM",
    "unidades_produtivas_auth": [],
    "exp": datetime.now(timezone.utc) + timedelta(hours=24),
    "iat": datetime.now(timezone.utc),
}

# Gerar token
token = jwt.encode(claims, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

# Imprimir no formato export
print(token)
