import json
from pathlib import Path

import jsonschema

from explain.explanation import Explanation

_SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schema" / "ir.schema.json"
_SCHEMA = json.loads(_SCHEMA_PATH.read_text())


def validate_structural(data: dict) -> Explanation:
    validator = jsonschema.Draft202012Validator(_SCHEMA)
    errors = sorted(validator.iter_errors(data), key=lambda e: e.path)

    if not errors:
        return Explanation(stage="structural", outcome="ok", rule="STRUCTURAL_OK")

    first = errors[0]
    return Explanation(
        stage="structural",
        outcome="rejected",
        rule="STRUCTURAL_SCHEMA_VIOLATION",
        evidence=[str(first.json_path)],
        suggestion=first.message,
    )
