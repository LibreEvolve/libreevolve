"""Identify installed trusted corpus bytes in a separate local process.

No candidate or caller-supplied module is accepted. This is preparation work,
never imported by the static renderer.
"""

import hashlib
import importlib.util
import json
from pathlib import Path


def main():
    path = Path(__file__).parent / "problems/examples/bin_packing/validate.py"
    spec = importlib.util.spec_from_file_location("bundled_share_corpus", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = {"validator_sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "corpora": {}}
    for split, function in (("training", module.training_cases), ("holdout", module.holdout_cases)):
        cases = function()
        raw = json.dumps(cases, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode("ascii")
        result["corpora"][split] = {"corpus_id": "bundled-bin-packing-" + split,
                                    "corpus_sha256": hashlib.sha256(raw).hexdigest(),
                                    "case_count": len(cases)}
    print(json.dumps(result, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
