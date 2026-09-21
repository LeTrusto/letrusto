import pytest

from app.core.exceptions import BadRequestError
from app.models.entities import MediaType
from app.services.media_service import MediaService
from app.storage import MockObjectStorage


def test_mock_storage_round_trip_supports_browser_upload_completion():
    storage = MockObjectStorage()
    storage.put("properties/p/media/1/original", b"\x89PNG\r\n\x1a\nimage", "image/png")

    stored = storage.inspect("properties/p/media/1/original")

    assert stored is not None
    assert stored.size == 13
    assert stored.content_type == "image/png"
    assert stored.prefix.startswith(b"\x89PNG")
    assert storage.public_url("properties/p/media/1/original").endswith("/properties/p/media/1/original")


def test_media_validation_rejects_wrong_type_and_oversized_uploads():
    service = MediaService.__new__(MediaService)
    service.settings = type("Settings", (), {"IMAGE_MAX_SIZE_MB": 1, "VIDEO_MAX_SIZE_MB": 2})()

    with pytest.raises(BadRequestError, match="Unsupported media MIME type"):
        service._validate_request(MediaType.IMAGE, "application/pdf", 10)

    with pytest.raises(BadRequestError, match="exceeds"):
        service._validate_request(MediaType.IMAGE, "image/png", 2 * 1024 * 1024)


def test_mock_storage_delete_removes_object():
    storage = MockObjectStorage()
    key = "properties/p/media/2/original"
    storage.put(key, b"content", "image/png")

    storage.delete(key)

    assert storage.inspect(key) is None
