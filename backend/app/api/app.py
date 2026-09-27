from fastapi import APIRouter, FastAPI

from app.api.articles.router import router as articles_router
from app.api.auth.router import router as auth_router
from app.api.categories.router import router as categories_router
from app.api.exceptions import add_exception_handlers
from app.api.inventories.router import router as inventories_router
from app.api.lifespan import lifespan_factory
from app.api.origins.router import router as origins_router
from app.api.pricing.router import router as pricing_router
from app.api.stores.router import router as stores_router
from app.api.taxes.router import router as taxes_router
from app.core.settings import AppEnvironment, Settings


def create_fastapi_app(settings: Settings) -> FastAPI:
    app = FastAPI(
        **settings.docs,
        lifespan=lifespan_factory(settings=settings),
    )
    add_exception_handlers(app=app)

    api_router = APIRouter(prefix=settings.api_prefix)
    api_router.include_router(auth_router)
    api_router.include_router(taxes_router)
    api_router.include_router(categories_router)
    api_router.include_router(articles_router)
    api_router.include_router(pricing_router)
    api_router.include_router(origins_router)
    api_router.include_router(stores_router)
    api_router.include_router(inventories_router)
    app.include_router(api_router)

    if settings.environment == AppEnvironment.PRODUCTION:
        app.frontend("/", directory="dist")

    return app
