from uuid import UUID, uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import BadRequestError
from app.models.entities import MediaStatus, MediaType, PropertyMedia, User
from app.services.property_audit_service import AuditService
from app.storage import ObjectStorage

_ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp", "video/mp4", "video/webm"}
_IMAGE_SIGNATURES = {"image/jpeg": lambda prefix: prefix.startswith(b"\xff\xd8\xff"), "image/png": lambda prefix: prefix.startswith(b"\x89PNG\r\n\x1a\n"), "image/webp": lambda prefix: prefix[:4] == b"RIFF" and prefix[8:12] == b"WEBP"}


class MediaService:
    def __init__(self, db: Session, storage: ObjectStorage) -> None:
        self.db = db
        self.storage = storage
        self.settings = get_settings()
        self.audit = AuditService(db)

    def _validate_request(self, media_type: MediaType, mime_type: str, file_size_bytes: int) -> str:
        normalized = mime_type.lower().strip()
        if normalized not in _ALLOWED_MIME:
            raise BadRequestError("Unsupported media MIME type")
        if media_type == MediaType.IMAGE and not normalized.startswith("image/"):
            raise BadRequestError("Image uploads require an image MIME type")
        if media_type == MediaType.VIDEO and not normalized.startswith("video/"):
            raise BadRequestError("Video uploads require a video MIME type")
        max_size = self.settings.IMAGE_MAX_SIZE_MB if media_type == MediaType.IMAGE else self.settings.VIDEO_MAX_SIZE_MB
        if file_size_bytes > max_size * 1024 * 1024:
            raise BadRequestError(f"Media exceeds the {max_size} MB size limit")
        return normalized

    def create_upload_target(self, *, property_id: UUID, media_type: MediaType, mime_type: str, file_size_bytes: int, is_cover: bool = False, caption: str | None = None) -> tuple[PropertyMedia, object]:
        normalized = self._validate_request(media_type, mime_type, file_size_bytes)
        key = f"properties/{property_id}/media/{uuid4()}/original"
        target = self.storage.create_upload_target(key, normalized, self.settings.STORAGE_UPLOAD_EXPIRE_SECONDS)
        media = PropertyMedia(property_id=property_id, media_type=media_type.value, storage_key=key, mime_type=normalized, file_size_bytes=file_size_bytes, is_cover=False, caption=caption, status=MediaStatus.UPLOADING.value, sort_order=self._next_order(property_id))
        self.db.add(media)
        self.db.commit()
        self.db.refresh(media)
        return media, target

    def _next_order(self, property_id: UUID) -> int:
        return int(self.db.scalar(select(func.max(PropertyMedia.sort_order)).where(PropertyMedia.property_id == property_id)) or -1) + 1

    def complete(self, *, property_id: UUID, media_id: UUID) -> PropertyMedia:
        media = self.db.scalar(select(PropertyMedia).where(PropertyMedia.id == media_id, PropertyMedia.property_id == property_id))
        if not media or media.status == MediaStatus.DELETED.value:
            raise BadRequestError("Media upload is not available")
        if media.status == MediaStatus.READY.value:
            return media
        stored = self.storage.inspect(media.storage_key)
        if not stored or stored.size != media.file_size_bytes or stored.content_type != media.mime_type:
            media.status = MediaStatus.REJECTED.value
            media.public_url = None
            media.is_cover = False
            self.db.commit()
            raise BadRequestError("Uploaded media could not be validated")
        signature_check = _IMAGE_SIGNATURES.get(media.mime_type)
        if signature_check and not signature_check(stored.prefix):
            media.status = MediaStatus.REJECTED.value
            media.public_url = None
            media.is_cover = False
            self.db.commit()
            raise BadRequestError("Uploaded file content does not match its media type")
        media.status = MediaStatus.PROCESSING.value
        media.public_url = self.storage.public_url(media.storage_key)
        if not media.public_url:
            media.status = MediaStatus.REJECTED.value
            self.db.commit()
            raise BadRequestError("Media storage has no public delivery URL")
        if media.is_cover or not self.db.scalar(select(PropertyMedia.id).where(PropertyMedia.property_id == property_id, PropertyMedia.is_cover.is_(True), PropertyMedia.status == MediaStatus.READY.value)):
            self.db.query(PropertyMedia).filter(PropertyMedia.property_id == property_id, PropertyMedia.id != media.id, PropertyMedia.is_cover.is_(True), PropertyMedia.status != MediaStatus.DELETED.value).update({PropertyMedia.is_cover: False})
            media.is_cover = media.media_type == MediaType.IMAGE.value
        media.status = MediaStatus.READY.value
        self.db.commit()
        self.db.refresh(media)
        return media

    def delete(self, *, property_id: UUID, media_id: UUID, actor: User) -> None:
        media = self.db.scalar(select(PropertyMedia).where(PropertyMedia.id == media_id, PropertyMedia.property_id == property_id))
        if not media:
            raise BadRequestError("Media not found")
        self.storage.delete(media.storage_key)
        media.status = MediaStatus.DELETED.value
        media.public_url = None
        media.is_cover = False
        self.audit.record(actor_user_id=actor.id, entity_type="PROPERTY_MEDIA", entity_id=media.id, action="MEDIA_DELETED")
        self.db.commit()
