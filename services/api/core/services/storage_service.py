"""
StorageService — abstração para local / S3 / MinIO.

Backend configurado via settings.storage_backend:
  - "local": salva em settings.storage_local_path
  - "s3": AWS S3
  - "minio": MinIO (usa s3_endpoint_url)

Funções de rastreamento (increment_storage / decrement_storage) atualizam
Tenant.storage_usado_mb no banco após cada operação de upload/deleção.
Sempre chame commit() na camada acima após usar essas funções.
"""
import os
import uuid as _uuid_mod
from pathlib import Path
from loguru import logger
from core.config import settings


class StorageService:

    @staticmethod
    def _build_path(tenant_id: str, area_rural_id: str, filename: str) -> str:
        """Gera path padronizado: geo/{tenant_id}/{area_rural_id}/{uuid}_{filename}"""
        unique = _uuid_mod.uuid4().hex[:8]
        safe_name = filename.replace(" ", "_")
        return f"geo/{tenant_id}/{area_rural_id}/{unique}_{safe_name}"

    @staticmethod
    def save(content: bytes, tenant_id: str, area_rural_id: str, filename: str) -> str:
        """
        Salva arquivo no backend configurado.
        Retorna o storage_path (key S3 ou caminho local).
        """
        path = StorageService._build_path(tenant_id, area_rural_id, filename)
        backend = settings.storage_backend.lower()

        if backend == "local":
            full_path = Path(settings.storage_local_path) / path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_bytes(content)
            logger.info(f"[storage:local] saved {full_path}")
            return path

        elif backend in ("s3", "minio"):
            import boto3
            kwargs: dict = {
                "aws_access_key_id": settings.s3_access_key,
                "aws_secret_access_key": settings.s3_secret_key,
                "region_name": settings.s3_region,
            }
            if settings.s3_endpoint_url:
                kwargs["endpoint_url"] = settings.s3_endpoint_url
            s3 = boto3.client("s3", **kwargs)
            s3.put_object(Bucket=settings.s3_bucket, Key=path, Body=content)
            logger.info(f"[storage:{backend}] uploaded s3://{settings.s3_bucket}/{path}")
            return path

        else:
            raise ValueError(f"storage_backend inválido: {backend}")

    @staticmethod
    def delete(storage_path: str) -> None:
        """Remove arquivo do backend (silencioso se não encontrar)."""
        backend = settings.storage_backend.lower()
        try:
            if backend == "local":
                full_path = Path(settings.storage_local_path) / storage_path
                if full_path.exists():
                    full_path.unlink()
            elif backend in ("s3", "minio"):
                import boto3
                kwargs: dict = {
                    "aws_access_key_id": settings.s3_access_key,
                    "aws_secret_access_key": settings.s3_secret_key,
                    "region_name": settings.s3_region,
                }
                if settings.s3_endpoint_url:
                    kwargs["endpoint_url"] = settings.s3_endpoint_url
                s3 = boto3.client("s3", **kwargs)
                s3.delete_object(Bucket=settings.s3_bucket, Key=storage_path)
        except Exception as e:
            logger.warning(f"[storage] falha ao deletar {storage_path}: {e}")

    @staticmethod
    def read(storage_path: str) -> bytes:
        """Lê arquivo do backend."""
        backend = settings.storage_backend.lower()
        if backend == "local":
            full_path = Path(settings.storage_local_path) / storage_path
            return full_path.read_bytes()
        elif backend in ("s3", "minio"):
            import boto3
            kwargs: dict = {
                "aws_access_key_id": settings.s3_access_key,
                "aws_secret_access_key": settings.s3_secret_key,
                "region_name": settings.s3_region,
            }
            if settings.s3_endpoint_url:
                kwargs["endpoint_url"] = settings.s3_endpoint_url
            s3 = boto3.client("s3", **kwargs)
            resp = s3.get_object(Bucket=settings.s3_bucket, Key=storage_path)
            return resp["Body"].read()
        else:
            raise ValueError(f"storage_backend inválido: {backend}")


# ---------------------------------------------------------------------------
# Rastreamento de storage no banco (storage_usado_mb)
# ---------------------------------------------------------------------------

import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, func


async def increment_storage(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    size_bytes: int,
) -> None:
    """Incrementa storage_usado_mb após upload bem-sucedido. Chame commit() na camada acima."""
    from core.models.tenant import Tenant
    size_mb = size_bytes / (1024 * 1024)
    await session.execute(
        update(Tenant)
        .where(Tenant.id == tenant_id)
        .values(storage_usado_mb=Tenant.storage_usado_mb + size_mb)
    )
    logger.debug(f"storage +{size_mb:.3f}MB tenant={tenant_id}")


async def decrement_storage(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    size_bytes: int,
) -> None:
    """Decrementa storage_usado_mb após deleção. Nunca vai abaixo de zero."""
    from core.models.tenant import Tenant
    from sqlalchemy import case
    size_mb = size_bytes / (1024 * 1024)
    await session.execute(
        update(Tenant)
        .where(Tenant.id == tenant_id)
        .values(
            storage_usado_mb=func.greatest(
                Tenant.storage_usado_mb - size_mb, 0
            )
        )
    )
    logger.debug(f"storage -{size_mb:.3f}MB tenant={tenant_id}")
