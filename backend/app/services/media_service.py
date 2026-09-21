from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestError
from app.models.entities import MediaStatus, MediaType, PropertyMedia

_ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp", "video/mp4", "video/webm"}


class MediaService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def validate_metadata(self, *, property_id: UUID, media_type: MediaType, storage_key: str, mime_type: str, file_size_bytes: int, is_cover: bool = False, caption: str | None = None) -> PropertyMedia:
        if mime_type.lower() not in _ALLOWED_MIME:
            raise BadRequestError("Unsupported media MIME type")
        if file_size_bytes <= 0:
            raise BadRequestError("Media file size must be positive")
        if is_cover:
            self.db.query(PropertyMedia).filter(PropertyMedia.property_id == property_id, PropertyMedia.is_cover.is_(True), PropertyMedia.status != MediaStatus.DELETED.value).update({PropertyMedia.is_cover: False})
        media = PropertyMedia(property_id=property_id, media_type=media_type.value, storage_key=storage_key, mime_type=mime_type, file_size_bytes=file_size_bytes, is_cover=is_cover, caption=caption)
        self.db.add(media)
        self.db.commit()
        self.db.refresh(media)
        return media
