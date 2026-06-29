from cleanstack import BaseEntity


class Store(BaseEntity):
    name: str
    slug: str
    tactill_api_key: str
