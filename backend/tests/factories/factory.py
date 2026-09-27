from pydantic import BaseModel, ConfigDict

from tests.factories.articles import ArticleFactory
from tests.factories.categories import CategoryFactory
from tests.factories.stores import StoreFactory
from tests.factories.taxes import TaxFactory


class Factory(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    stores: StoreFactory
    categories: CategoryFactory
    taxes: TaxFactory
    articles: ArticleFactory
