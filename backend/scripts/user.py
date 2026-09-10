import argparse
import asyncio
import uuid

from app.domain.security import get_password_hash
from scripts.commons import get_context


async def main(database: str, user_id: str, name: str, password: str) -> None:
    context = await get_context(database=database)
    await context.database["users"].insert_one(
        {
            "_id": uuid.UUID(user_id),
            "name": name,
            "hashed_password": get_password_hash(password),
        }
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("database")
    parser.add_argument("id")
    parser.add_argument("name")
    parser.add_argument("password")

    args = parser.parse_args()
    asyncio.run(
        main(
            database=args.database,
            user_id=args.id,
            name=args.name,
            password=args.password,
        )
    )
