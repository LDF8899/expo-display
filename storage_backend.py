import os
import tempfile
from pathlib import Path


def asset_storage_backend():
    return os.environ.get("ASSET_STORAGE_BACKEND", "local").strip().lower() or "local"


def join_url(base, key):
    return f"{base.rstrip('/')}/{key.lstrip('/')}"


class LocalAssetStorage:
    def __init__(self, upload_dir, public_base_url=""):
        self.upload_dir = Path(upload_dir)
        self.public_base_url = public_base_url.strip().rstrip("/")

    def save(self, key, payload, content_type):
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        target = self.upload_dir / key
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
        return join_url(self.public_base_url, key) if self.public_base_url else f"/uploads/{key}"

    def delete(self, key):
        target = (self.upload_dir / str(key).lstrip("/")).resolve()
        root = self.upload_dir.resolve()
        if root not in target.parents and target != root:
            raise RuntimeError("资源路径无效")
        if target.exists():
            target.unlink()


class S3AssetStorage:
    def __init__(self):
        try:
            import boto3
        except ImportError as exc:
            raise RuntimeError("使用 S3 存储时需要安装 boto3") from exc

        access_key = os.environ.get("S3_ACCESS_KEY_ID") or os.environ.get("AWS_ACCESS_KEY_ID")
        secret_key = os.environ.get("S3_SECRET_ACCESS_KEY") or os.environ.get("AWS_SECRET_ACCESS_KEY")
        region = os.environ.get("S3_REGION") or os.environ.get("AWS_REGION") or "auto"
        endpoint_url = os.environ.get("S3_ENDPOINT_URL") or None
        self.bucket = os.environ.get("S3_BUCKET", "").strip()
        self.public_base_url = os.environ.get("S3_PUBLIC_BASE_URL", "").strip().rstrip("/")
        self.acl = os.environ.get("S3_ACL", "").strip()
        if not self.bucket:
            raise RuntimeError("使用 S3 存储时必须配置 S3_BUCKET")
        self.client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            region_name=region,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )

    def save(self, key, payload, content_type):
        args = {
            "Bucket": self.bucket,
            "Key": key,
            "Body": payload,
            "ContentType": content_type,
        }
        if self.acl:
            args["ACL"] = self.acl
        self.client.put_object(**args)
        if self.public_base_url:
            return join_url(self.public_base_url, key)
        return f"s3://{self.bucket}/{key}"

    def delete(self, key):
        self.client.delete_object(Bucket=self.bucket, Key=key)


def asset_storage(upload_dir):
    backend = asset_storage_backend()
    if backend == "local":
        return LocalAssetStorage(upload_dir, os.environ.get("ASSET_PUBLIC_BASE_URL", ""))
    if backend == "s3":
        return S3AssetStorage()
    raise RuntimeError(f"不支持的 ASSET_STORAGE_BACKEND：{backend}")


def storage_status(upload_dir):
    backend = asset_storage_backend()
    if backend == "local":
        path = Path(upload_dir)
        path.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(prefix=".ready-", dir=path, delete=True) as handle:
            handle.write(b"ok")
            handle.flush()
        return {"ok": True, "backend": "local", "path": str(path)}
    if backend == "s3":
        missing = [
            name
            for name in ("S3_BUCKET", "S3_PUBLIC_BASE_URL")
            if not os.environ.get(name, "").strip()
        ]
        try:
            import boto3  # noqa: F401
        except ImportError:
            missing.append("boto3")
        return {
            "ok": not missing,
            "backend": "s3",
            "bucket": os.environ.get("S3_BUCKET", ""),
            "publicBaseUrl": os.environ.get("S3_PUBLIC_BASE_URL", ""),
            "missing": missing,
        }
    return {"ok": False, "backend": backend, "error": "不支持的资源存储后端"}
