from cleanstack.mongo import AsyncMongoRepository

from app.domain.inventories.entities import Inventory
from app.domain.inventories.repository import InventoryRepositoryProtocol


class InventoryRepository(AsyncMongoRepository[Inventory], InventoryRepositoryProtocol):
    domain_entity_type = Inventory
    collection_name = "inventories"
