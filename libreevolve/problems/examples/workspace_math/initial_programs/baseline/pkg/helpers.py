import json
from pathlib import Path


# EVOLVE-BLOCK-START helper
def base_value():
    root = Path(__file__).resolve().parents[1]
    config = json.loads((root / "data" / "config.json").read_text(encoding="utf-8"))
    asset = (root / "assets" / "offset.bin").read_bytes()
    if asset != b"\xffLESTATIC\n":
        raise ValueError("unexpected static asset")
    return int(config["base"]) + int(config["asset_offset"])
# EVOLVE-BLOCK-END
