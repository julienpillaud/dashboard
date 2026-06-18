from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.requests import Request
from fastapi.responses import RedirectResponse, Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates

from app.api.dependencies import (
    get_current_store,
    get_domain,
    get_optional_current_store,
    get_templates,
)
from app.core.domain import Domain
from app.domain.exceptions import ForbiddenError, NotFoundError
from app.domain.stores.commands import authenticate_store_command
from app.domain.stores.entities import Store

router = APIRouter()


@router.get("/")
async def login(
    request: Request,
    current_store: Annotated[Store | None, Depends(get_optional_current_store)],
    templates: Annotated[Jinja2Templates, Depends(get_templates)],
) -> Response:
    if current_store:
        return RedirectResponse(url="/articles", status_code=status.HTTP_302_FOUND)

    message = request.session.pop("message", None)
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"error": message},
    )


@router.post("/")
async def post_login(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    domain: Annotated[Domain, Depends(get_domain)],
) -> Response:
    try:
        store = await domain.run(
            authenticate_store_command,
            name=form_data.username,
            password=form_data.password,
        )
    except NotFoundError, ForbiddenError:
        request.session["message"] = "Nom ou mot de passe incorrect"
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    request.session["store_id"] = str(store.id)
    return RedirectResponse(url="/articles", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/logout")
async def logout(request: Request) -> Response:
    request.session.clear()
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/articles")
async def home(
    request: Request,
    current_store: Annotated[Store, Depends(get_current_store)],
    templates: Annotated[Jinja2Templates, Depends(get_templates)],
) -> Response:
    return templates.TemplateResponse(
        request=request,
        name="articles.html",
        context={"current_store": current_store},
    )
