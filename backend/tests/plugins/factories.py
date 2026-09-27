import pytest
from cleanstack.mongo import MongoDocument
from pymongo.synchronous.database import Database

from tests.factories.articles import ArticleFactory
from tests.factories.categories import CategoryFactory
from tests.factories.factory import Factory
from tests.factories.stores import StoreFactory
from tests.factories.taxes import TaxFactory


@pytest.fixture
def factory(database: Database[MongoDocument]) -> Factory:
    return Factory(
        stores=StoreFactory(database=database),
        categories=CategoryFactory(database=database),
        taxes=TaxFactory(database=database),
        articles=ArticleFactory(database=database),
    )
