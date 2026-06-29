from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.requests import Request
from fastapi.responses import RedirectResponse, Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates

from app.api.auth.utils import generate_access_token
from app.api.dependencies import (
    get_current_user,
    get_domain,
    get_optional_current_user,
    get_settings,
    get_templates,
)
from app.api.logger import logger
from app.core.domain import Domain
from app.core.settings import Settings
from app.domain.exceptions import ForbiddenError, NotFoundError
from app.domain.users.commands import authenticate_user_command
from app.domain.users.entities import UserExternal

router = APIRouter()


@router.get("/")
async def login(
    request: Request,
    current_user: Annotated[UserExternal | None, Depends(get_optional_current_user)],
    templates: Annotated[Jinja2Templates, Depends(get_templates)],
) -> Response:
    if current_user:
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
    settings: Annotated[Settings, Depends(get_settings)],
    domain: Annotated[Domain, Depends(get_domain)],
) -> Response:
    try:
        current_user = await domain.run(
            authenticate_user_command,
            name=form_data.username,
            password=form_data.password,
        )
    except NotFoundError, ForbiddenError:
        request.session["message"] = "Nom ou mot de passe incorrect"
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    access_token = generate_access_token(
        settings=settings,
        user_id=current_user.id,
    )
    response = RedirectResponse(url="/articles", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=settings.access_token_expire,
        secure=True,
        httponly=True,
        samesite="lax",
    )
    logger.info(f"User '{current_user.id}' - Logged in")
    return response


@router.post("/token")
async def post_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    settings: Annotated[Settings, Depends(get_settings)],
    domain: Annotated[Domain, Depends(get_domain)],
) -> dict[str, str]:
    try:
        current_user = await domain.run(
            authenticate_user_command,
            name=form_data.username,
            password=form_data.password,
        )
    except (NotFoundError, ForbiddenError) as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        ) from error

    access_token = generate_access_token(
        settings=settings,
        user_id=current_user.id,
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/logout")
async def logout(
    current_user: Annotated[UserExternal, Depends(get_current_user)],
) -> Response:
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(
        key="access_token",
        secure=True,
        httponly=True,
        samesite="lax",
    )
    logger.info(f"User '{current_user.id}' - Logged out")
    return response


@router.get("/articles")
async def home(
    request: Request,
    current_user: Annotated[UserExternal, Depends(get_current_user)],
    templates: Annotated[Jinja2Templates, Depends(get_templates)],
) -> Response:
    return templates.TemplateResponse(
        request=request,
        name="articles.html",
        context={"current_user": current_user},
    )
