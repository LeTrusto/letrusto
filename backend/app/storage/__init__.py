from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


_MOCK_OBJECTS: dict[str, tuple[bytes, str]] = {}


class ObjectStorage(Protocol):
    def create_upload_target(self, key: str, mime_type: str, expires_in: int) -> "UploadTarget": ...
    def upload(self, key: str, content: bytes, mime_type: str) -> None: ...
    def delete(self, key: str) -> None: ...
    def public_url(self, key: str) -> str | None: ...
    def inspect(self, key: str) -> "StoredObject | None": ...


@dataclass(frozen=True)
class UploadTarget:
    url: str
    headers: dict[str, str]
    expires_at: datetime


@dataclass(frozen=True)
class StoredObject:
    size: int
    content_type: str
    prefix: bytes


class S3ObjectStorage:
    def __init__(self, settings) -> None:
        import boto3

        self.bucket = settings.STORAGE_BUCKET
        self.public_base_url = settings.STORAGE_PUBLIC_BASE_URL.rstrip("/")
        self.client = boto3.client(
            "s3",
            endpoint_url=settings.STORAGE_ENDPOINT or None,
            region_name=settings.STORAGE_REGION,
            aws_access_key_id=settings.STORAGE_ACCESS_KEY,
            aws_secret_access_key=settings.STORAGE_SECRET_KEY,
        )

    def create_upload_target(self, key: str, mime_type: str, expires_in: int) -> UploadTarget:
        from datetime import timedelta, timezone

        now = datetime.now(timezone.utc)
        url = self.client.generate_presigned_url(
            "put_object",
            Params={"Bucket": self.bucket, "Key": key, "ContentType": mime_type},
            ExpiresIn=expires_in,
            HttpMethod="PUT",
        )
        return UploadTarget(url=url, headers={"Content-Type": mime_type}, expires_at=now + timedelta(seconds=expires_in))

    def upload(self, key: str, content: bytes, mime_type: str) -> None:
        self.client.put_object(Bucket=self.bucket, Key=key, Body=content, ContentType=mime_type)

    def delete(self, key: str) -> None:
        self.client.delete_object(Bucket=self.bucket, Key=key)

    def public_url(self, key: str) -> str | None:
        return f"{self.public_base_url}/{key}" if self.public_base_url else None

    def inspect(self, key: str) -> StoredObject | None:
        from botocore.exceptions import ClientError

        try:
            metadata = self.client.head_object(Bucket=self.bucket, Key=key)
            response = self.client.get_object(Bucket=self.bucket, Key=key, Range="bytes=0-15")
            return StoredObject(
                size=int(metadata["ContentLength"]),
                content_type=str(metadata.get("ContentType") or "").lower(),
                prefix=response["Body"].read(16),
            )
        except ClientError as exc:
            if exc.response.get("Error", {}).get("Code") in {"404", "NoSuchKey", "NotFound"}:
                return None
            raise


class MockObjectStorage:
    """Development-only in-memory adapter; production configuration rejects it."""

    def create_upload_target(self, key: str, mime_type: str, expires_in: int) -> UploadTarget:
        from datetime import timedelta, timezone

        now = datetime.now(timezone.utc)
        return UploadTarget(url=f"mock://{key}", headers={"Content-Type": mime_type}, expires_at=now + timedelta(seconds=expires_in))

    def upload(self, key: str, content: bytes, mime_type: str) -> None:
        self.put(key, content, mime_type)

    def delete(self, key: str) -> None:
        _MOCK_OBJECTS.pop(key, None)

    def public_url(self, key: str) -> str | None:
        return f"http://127.0.0.1:8000/api/v1/seller/media/mock-public/{key}"

    def inspect(self, key: str) -> StoredObject | None:
        value = _MOCK_OBJECTS.get(key)
        if not value:
            return None
        content, content_type = value
        return StoredObject(size=len(content), content_type=content_type, prefix=content[:16])

    @staticmethod
    def put(key: str, content: bytes, content_type: str) -> None:
        _MOCK_OBJECTS[key] = (content, content_type.lower())

    @staticmethod
    def get(key: str) -> tuple[bytes, str] | None:
        return _MOCK_OBJECTS.get(key)
