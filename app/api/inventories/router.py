from typing import Annotated

from cleanstack import EntityId, PaginatedResponse, Pagination
from fastapi import APIRouter, Depends
from fastapi.requests import Request
from fastapi.responses import Response, StreamingResponse
from fastapi.templating import Jinja2Templates

from app.api.dependencies import (
    get_current_user,
    get_domain,
    get_pdf_converter,
    get_templates,
)
from app.core.domain import Domain
from app.domain.inventories.commands import (
    create_inventory_command,
    get_inventories_command,
    get_inventory_command,
)
from app.domain.inventories.entities import Inventory
from app.domain.protocols import PDFConverterProtocol

router = APIRouter(
    prefix="/api/inventories",
    tags=["Inventories"],
    dependencies=[Depends(get_current_user)],
)


@router.get("")
async def get_inventories(
    domain: Annotated[Domain, Depends(get_domain)],
    pagination: Annotated[Pagination, Depends()],
    store_slug: str,
) -> PaginatedResponse[Inventory]:
    return await domain.run(
        get_inventories_command,
        pagination=pagination,
        store_slug=store_slug,
    )


@router.post("")
async def create_inventory(
    domain: Annotated[Domain, Depends(get_domain)],
    store: str,
) -> Inventory:
    return await domain.run(create_inventory_command, store_slug=store)


@router.get("/{inventory_id}/preview")
async def preview_inventory_pdf(
    request: Request,
    domain: Annotated[Domain, Depends(get_domain)],
    templates: Annotated[Jinja2Templates, Depends(get_templates)],
    inventory_id: EntityId,
    store: str,
) -> Response:
    inventory = await domain.run(
        get_inventory_command,
        store_slug=store,
        inventory_id=inventory_id,
    )
    return templates.TemplateResponse(
        request=request,
        name="inventory_pdf.html",
        context={"inventory": inventory},
    )


@router.get("/{inventory_id}/pdf")
async def download_inventory_pdf(
    request: Request,
    domain: Annotated[Domain, Depends(get_domain)],
    templates: Annotated[Jinja2Templates, Depends(get_templates)],
    pdf_converter: Annotated[PDFConverterProtocol, Depends(get_pdf_converter)],
    inventory_id: EntityId,
    store: str,
) -> StreamingResponse:
    inventory = await domain.run(
        get_inventory_command,
        store_slug=store,
        inventory_id=inventory_id,
    )
    html_content = templates.get_template("inventory_pdf.html").render(
        {"request": request, "inventory": inventory}
    )
    filename = f"inventaire_{store}_{inventory.created_at:%Y-%m-%d}.pdf"
    return StreamingResponse(
        pdf_converter.stream_pdf(html_content),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
