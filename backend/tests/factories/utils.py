from typing import Any

from app.domain.entities import normalize_datetime
from tests.factories.fake import faker


def generate_base_raw_fields(**kwargs: Any) -> dict[str, Any]:  # noqa: ANN401
    return {
        "id": faker.hexify(text="^" * 24),
        "name": kwargs.get("name", faker.word()),
        "deprecated": kwargs.get("deprecated", False),
        "created_at": kwargs.get("created_at", normalize_datetime(faker.date_time())),
        "updated_at": kwargs.get("updated_at", normalize_datetime(faker.date_time())),
    }
