from collections.abc import Iterator
from typing import Any

from cleanstack.mongo import MongoDocument


def iter_dicts(value: dict[Any, Any]) -> Iterator[dict[Any, Any]]:
    stack: list[Any] = [value]

    while stack:
        node = stack.pop()

        if isinstance(node, dict):
            yield node
            stack.extend(node.values())

        elif isinstance(node, list):
            stack.extend(node)


def normalize_ids(document: MongoDocument) -> None:
    for d in iter_dicts(document):
        if "_id" in d:
            d["id"] = str(d.pop("_id"))
