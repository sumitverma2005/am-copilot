#!/usr/bin/env python3
"""Entry point: generate batch 1 synthetic calls (syn_001–syn_015)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from synthetic_data.generator import generate_all

OUTPUT_DIR = Path(__file__).parents[2] / "data" / "synthetic"

if __name__ == "__main__":
    print(f"Generating 30 synthetic calls → {OUTPUT_DIR}")
    generate_all(OUTPUT_DIR)
    print("Done.")
