from app.domain.inventories.entities import Inventory
from app.domain.protocols import RepositoryProtocol


class InventoryRepositoryProtocol(RepositoryProtocol[Inventory]): ...
