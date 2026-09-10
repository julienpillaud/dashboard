import argparse
import asyncio
from collections import defaultdict

from cleanstack import Pagination

from app.domain.articles.use_cases import get_articles_by_group
from scripts.commons import get_context


async def check_articles(database: str) -> None:
    context = await get_context(database=database)
    response = await get_articles_by_group(context, pagination=Pagination(size=3000))

    result = defaultdict(list)
    for item in response.items:
        articles = item.articles
        result[len(articles)].append(articles)

    for k, v in result.items():
        print(f"{k}: {len(v)}")

    print("\n--- Groups x 2 ---")
    for articles in result[2]:
        stores = [a.store_name for a in articles]
        print(f"{articles[0].raw.name} -> {stores}")

    print("\n--- Groups x 1 ---")
    for articles in result[1]:
        stores = [a.store_name for a in articles]
        print(f"{articles[0].raw.name} -> {stores}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("database")
    args = parser.parse_args()
    asyncio.run(check_articles(database=args.database))
