from typing import Annotated

from cleanstack import EntityId
from fastapi import APIRouter, Depends, status
from fastapi.requests import Request
from fastapi.responses import Response, StreamingResponse
from fastapi.templating import Jinja2Templates

from app.api.dependencies.app import QueryDomain, get_pdf_converter, get_templates
from app.api.dependencies.user import get_current_user_id
from app.domain.inventories.entities import Inventory, InventorySummary
from app.domain.inventories.use_cases import (
    create_inventory,
    get_inventories,
    get_inventory_by_id,
)
from app.domain.protocols import PDFConverterProtocol

router = APIRouter(
    prefix="/inventories",
    tags=["Inventories"],
    dependencies=[Depends(get_current_user_id)],
)


@router.get("", summary="Get inventories")
async def get_inventories_endpoint(
    domain: QueryDomain,
    store_id: EntityId,
) -> list[InventorySummary]:
    return await domain.run(get_inventories, store_id=store_id)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Create inventory",
)
async def create_inventory_endpoint(
    domain: QueryDomain,
    store_id: EntityId,
) -> Inventory:
    return await domain.run(create_inventory, store_id=store_id)


@router.get("/{inventory_id}/preview")
async def preview_inventory_pdf(
    request: Request,
    domain: QueryDomain,
    templates: Annotated[Jinja2Templates, Depends(get_templates)],
    inventory_id: EntityId,
    store_id: EntityId,
) -> Response:
    inventory = await domain.run(
        get_inventory_by_id,
        store_id=store_id,
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
    domain: QueryDomain,
    templates: Annotated[Jinja2Templates, Depends(get_templates)],
    pdf_converter: Annotated[PDFConverterProtocol, Depends(get_pdf_converter)],
    inventory_id: EntityId,
    store_id: EntityId,
) -> StreamingResponse:
    inventory = await domain.run(
        get_inventory_by_id,
        store_id=store_id,
        inventory_id=inventory_id,
    )
    html_content = templates.get_template("inventory_pdf.html").render(
        {"request": request, "inventory": inventory}
    )
    filename = f"inventaire_{store_id}_{inventory.created_at:%Y-%m-%d}.pdf"
    return StreamingResponse(
        pdf_converter.stream_pdf(html_content),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
