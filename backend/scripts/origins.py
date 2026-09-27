from app.core.context import Context
from scripts.commons import logger
from scripts.data.origins import ORIGINS


async def migrate_origins(context: Context, dry_run: bool) -> None:
    if not dry_run:
        await context.database["origins"].delete_many({})
        await context.origin_repository.save_many(ORIGINS)
    else:
        logger.warning("Dry run: nothing to do")
