import json
from pathlib import Path
from typing import Any, Iterable
from dataclasses import asdict, is_dataclass


def to_jsonable(record: Any) -> dict:
    if is_dataclass(record):
        return asdict(record)

    if isinstance(record, dict):
        return record

    raise TypeError(f"Unsupported record type: {type(record)}")


def write_jsonl(records: Iterable[Any], output_path: str) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        for record in records:
            json_record = to_jsonable(record)
            f.write(json.dumps(json_record, ensure_ascii=False) + "\n")