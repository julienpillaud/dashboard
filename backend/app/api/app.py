from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.api.articles.router import router as articles_router
from app.api.auth.router import router as auth_router
from app.api.categories.router import router as categories_router
from app.api.exceptions import add_exception_handlers
from app.api.inventories.router import router as inventories_router
from app.api.lifespan import lifespan_factory
from app.api.taxes.router import router as taxes_router
from app.core.settings import Settings


def create_fastapi_app(settings: Settings) -> FastAPI:
    app = FastAPI(
        swagger_ui_parameters={
            "tryItOutEnabled": True,
            "displayRequestDuration": True,
            "persistAuthorization": True,
        },
        lifespan=lifespan_factory(settings=settings),
    )

    app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)
    add_exception_handlers(app=app, settings=settings)
    app.mount(
        path="/static",
        app=StaticFiles(directory=settings.paths.static),
        name="static",
    )

    app.include_router(auth_router)
    app.include_router(taxes_router)
    app.include_router(categories_router)
    app.include_router(articles_router)
    app.include_router(inventories_router)

    return app
