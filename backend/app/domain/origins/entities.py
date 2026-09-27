from cleanstack import BaseEntity


class Origin(BaseEntity):
    name: str
    code: str | None = None
