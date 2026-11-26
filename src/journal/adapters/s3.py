"""Static site storage in an S3 bucket. Needs boto3 (`pip install journal[aws]`)."""

import mimetypes
from typing import Any

from journal.ports import PublishError

# Pages that change on every edition must not be cached for long; editions
# themselves never change once written.
MUTABLE = {"index.html", "editions.json", "seen.json", "edicoes/index.html"}
SHORT_CACHE = "public, max-age=300"
LONG_CACHE = "public, max-age=31536000, immutable"
MISSING = {"404", "NoSuchKey", "NotFound"}
TYPES = {".json": "application/json", ".css": "text/css", ".html": "text/html"}


class S3Storage:
    """Keys under `prefix` in `bucket`. `client` is a boto3 S3 client (made if None)."""

    def __init__(self, bucket: str, prefix: str = "", client: Any = None):
        self.bucket = bucket
        self.prefix = prefix.strip("/") + "/" if prefix.strip("/") else ""
        if client is None:
            try:
                import boto3
            except ImportError as exc:
                raise PublishError("S3 storage needs boto3: pip install boto3") from exc
            client = boto3.client("s3")
        self.client = client

    def exists(self, key: str) -> bool:
        try:
            self.client.head_object(Bucket=self.bucket, Key=self.prefix + key)
            return True
        except Exception as exc:
            if _code(exc) in MISSING:
                return False
            raise self._error("check", key, exc) from exc

    def read(self, key: str) -> bytes | None:
        try:
            obj = self.client.get_object(Bucket=self.bucket, Key=self.prefix + key)
            return obj["Body"].read()
        except Exception as exc:
            if _code(exc) in MISSING:
                return None
            raise self._error("read", key, exc) from exc

    def write(self, key: str, data: bytes) -> None:
        suffix = "." + key.rsplit(".", 1)[-1] if "." in key else ""
        kind = (
            TYPES.get(suffix)
            or mimetypes.guess_type(key)[0]
            or "application/octet-stream"
        )
        try:
            self.client.put_object(
                Bucket=self.bucket,
                Key=self.prefix + key,
                Body=data,
                ContentType=f"{kind}; charset=utf-8"
                if kind.startswith(("text/", "application/json"))
                else kind,
                CacheControl=SHORT_CACHE if key in MUTABLE else LONG_CACHE,
            )
        except Exception as exc:
            raise self._error("write", key, exc) from exc

    def _error(self, action: str, key: str, exc: Exception) -> PublishError:
        return PublishError(
            f"cannot {action} s3://{self.bucket}/{self.prefix}{key}: {exc}"
        )


def _code(exc: Exception) -> str | None:
    """Error code of a botocore ClientError, without importing botocore."""
    response = getattr(exc, "response", None)
    if isinstance(response, dict):
        return str(response.get("Error", {}).get("Code"))
    return None
