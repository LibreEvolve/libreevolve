"""Private subprocess entry point. Local execution, not a security sandbox."""

from __future__ import annotations

import json
import math
import os
import sys
import time
from pathlib import Path


def main() -> None:
    # The parent releases execution only after assigning its Windows job (or
    # establishing the POSIX process group). No candidate runs before this gate.
    release = Path(os.environ.pop("LIBREEVOLVE_ALPHA_RELEASE"))
    deadline = time.monotonic() + 30
    while not release.exists():
        if time.monotonic() >= deadline:
            raise TimeoutError("Verification parent did not release worker")
        time.sleep(0.01)
    request = json.loads(sys.stdin.buffer.read(12_100_000))
    # Suppress candidate/validator prints, including writes to the OS descriptors.
    output = os.fdopen(os.dup(1), "w", encoding="utf-8")
    with open(os.devnull, "w") as sink:
        os.dup2(sink.fileno(), 1)
        os.dup2(sink.fileno(), 2)
        namespace = {"__name__": "_alpha_bundled_validator"}
        result = {"status": "error", "correctness": None, "score": None}
        try:
            exec(compile(request["validator"], "<bundled-validator>", "exec"), namespace)
            metrics = namespace[request["entrypoint"]](request["code"])
            if not isinstance(metrics, dict) or type(metrics.get("is_valid")) is not bool:
                raise ValueError("Validator did not return boolean is_valid")
            score = metrics.get("quality")
            if type(score) not in (int, float) or not math.isfinite(score):
                raise ValueError("Validator did not return finite quality")
            result.update(status="completed", correctness=metrics["is_valid"],
                          score=score, metrics=metrics)
        except BaseException as exc:
            result["error"] = type(exc).__name__ + ": " + str(exc)[:500]
        result["code_sha256"] = request["code_sha256"]
        result["validator_sha256"] = request["validator_sha256"]
        encoded = json.dumps(result, allow_nan=False)
        if len(encoded.encode("utf-8")) > 65536:
            encoded = json.dumps({"status": "output_limit", "correctness": None,
                                  "score": None, "code_sha256": request["code_sha256"],
                                  "validator_sha256": request["validator_sha256"]})
        output.write(encoded)
        output.flush()


if __name__ == "__main__":
    main()
