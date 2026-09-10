import argparse
import asyncio

from scripts.articles import migrate_articles
from scripts.categories import migrate_categories
from scripts.commons import get_context, setup_logging
from scripts.stores import migrate_stores
from scripts.taxes import migrate_taxes

entities = {
    "stores": migrate_stores,
    "taxes": migrate_taxes,
    "categories": migrate_categories,
    "articles": migrate_articles,
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("database")
    parser.add_argument(
        "--dry-run",
        action=argparse.BooleanOptionalAction,
        default=True,
    )
    parser.add_argument(
        "entity",
        nargs="?",
        choices=list(entities.keys()),
        default="all",
    )
    return parser


async def run(database: str, dry_run: bool, entity: str) -> None:
    context = await get_context(database=database)
    if entity == "all":
        for func in entities.values():
            await func(context=context, dry_run=dry_run)
    else:
        await entities[entity](context=context, dry_run=dry_run)


def main() -> None:
    setup_logging()
    parser = build_parser()
    args = parser.parse_args()
    asyncio.run(
        run(
            database=args.database,
            dry_run=args.dry_run,
            entity=args.entity,
        )
    )


if __name__ == "__main__":
    main()
