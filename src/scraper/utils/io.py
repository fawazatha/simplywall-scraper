import json
import re

from pathlib import Path


def write_json(payload: list | dict, filename: str | Path) -> None:
    with open(filename, 'w', encoding="utf-8") as file:
        json.dump(payload, file, indent=2)


def sanitize_filename(company_name: str) -> str:
    sanitized = re.sub(r'[^\w\s-]', '', company_name)
    sanitized = re.sub(r'\s+', '_', sanitized.strip().lower())
    return sanitized


def clean_company_suffix(company_name: str) -> str:
    pattern = r'\s*\b(Ltd\.?|Limited)\b\s*'
    return re.sub(pattern, '', company_name, flags=re.IGNORECASE).strip()
