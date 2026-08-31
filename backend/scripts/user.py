import argparse
import asyncio
import uuid
from pathlib import Path

from app.core.settings import Settings
from app.domain.security import get_password_hash
from app.infrastructure.mongo.resource.asynchronous import MongoResource

project_path = Path(__file__).parents[1]


async def main(name: str, password: str) -> None:
    settings = Settings(_env_file=project_path / ".env")
    resource = await MongoResource.from_settings(settings)
    await resource.database["users"].insert_one(
        {
            "_id": uuid.uuid7(),
            "name": name,
            "hashed_password": get_password_hash(password),
        }
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name")
    parser.add_argument("--password")

    args = parser.parse_args()
    asyncio.run(main(args.name, args.password))
