import asyncio

from scripts.articles import migrate_articles
from scripts.categories import migrate_categories
from scripts.commons import build_parser, get_context, setup_logging
from scripts.origins import migrate_origins
from scripts.pricing_rules import migrate_pricing_rules
from scripts.stores import migrate_stores
from scripts.taxes import migrate_taxes


async def run(database: str, dry_run: bool) -> None:
    context = await get_context(database=database)

    await migrate_stores(context, dry_run=dry_run)
    await migrate_taxes(context, dry_run=dry_run)
    await migrate_categories(context, dry_run=dry_run)
    await migrate_pricing_rules(context, dry_run=dry_run)
    await migrate_origins(context, dry_run=dry_run)
    await migrate_articles(context, dry_run=dry_run)


def main() -> None:
    setup_logging()
    parser = build_parser()
    args = parser.parse_args()
    asyncio.run(run(database=args.database, dry_run=args.dry_run))


if __name__ == "__main__":
    main()
