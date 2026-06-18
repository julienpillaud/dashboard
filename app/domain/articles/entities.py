from cleanstack import BaseEntity, EntityId

from app.domain.entities import BaseRawEntity


class RawArticle(BaseRawEntity):
    category_id: str
    taxes: list[str]
    name: str
    icon_text: str
    color: str
    barcode: str | None
    in_stock: bool
    reference: str | None
    full_price: float | None
    stock_quantity: int | None


class Article(BaseEntity):
    store_id: EntityId
    external_id: str
    category: str
    tax_rate: float
    raw: RawArticle
