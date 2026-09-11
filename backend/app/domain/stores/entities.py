from cleanstack import BaseEntity


class Store(BaseEntity):
    name: str
    slug: str
    pos_api_key: str
