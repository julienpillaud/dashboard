import asyncio
from pathlib import Path

from app.domain.taxes.use_cases import synchronize_taxes
from scripts.commons import get_context, get_stores, setup_logging

project_path = Path(__file__).parents[1]


async def main() -> None:
    setup_logging(project_path)
    context = await get_context()
    stores = await get_stores(context)
    await context.database["taxes"].delete_many({})
    await asyncio.gather(
        *(synchronize_taxes(context, store_slug=store.slug) for store in stores)
    )


if __name__ == "__main__":
    asyncio.run(main())
