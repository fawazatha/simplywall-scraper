import json

from pathlib import Path


CHECKPOINT_FILE_PATH = Path("data/checkpoint/remaining_companies.json")
CHECKPOINT_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)


def save_checkpoint(remaining_companies: list[str]) -> None:
    with CHECKPOINT_FILE_PATH.open('w') as file:
        json.dump(remaining_companies, file, indent=2)


def load_checkpoint() -> list[str] | None:
    if not CHECKPOINT_FILE_PATH.exists():
        return None
    
    with CHECKPOINT_FILE_PATH.open('r') as file:
        return json.load(file)


def clear_checkpoint() -> None:
    if CHECKPOINT_FILE_PATH.exists():
        CHECKPOINT_FILE_PATH.unlink()
