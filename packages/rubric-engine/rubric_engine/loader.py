from pathlib import Path

import yaml
from pydantic import ValidationError

from .schema import Rubric


def load_rubric(path: Path) -> Rubric:
    """Load and validate a rubric YAML file. Returns a validated Rubric object.

    Raises:
        FileNotFoundError: if the path does not exist.
        ValueError: with a human-readable field-level message if validation fails.
    """
    if not path.exists():
        raise FileNotFoundError(f"Rubric file not found: {path}")

    with open(path) as f:
        raw = yaml.safe_load(f)

    try:
        return Rubric.model_validate(raw)
    except ValidationError as exc:
        lines = [f"Rubric file '{path.name}' failed validation:"]
        for error in exc.errors():
            loc = " → ".join(str(p) for p in error["loc"])
            lines.append(f"  Field '{loc}': {error['msg']}")
        raise ValueError("\n".join(lines)) from exc
