"""Restore the exact delivered SA900-01 workbook from the text-bundle payload."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NAME = "SA900-01_据付寸法計算_境界条件修正版_v4_20260924.xlsx"
SHA256 = "8d634d87e92446c53977173b0fe69d5bb745a33d6b9f8c691f1e6334eb1da4da"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "workbook")
    args = parser.parse_args()

    payload = json.loads((ROOT / "payload" / "WorkbookPayload.json").read_text(encoding="utf-8"))
    if payload.get("schema") != 1 or payload.get("file") != NAME or payload.get("sha256") != SHA256:
        raise SystemExit("FAIL: unexpected payload identity")
    try:
        data = base64.b64decode(payload["base64"], validate=True)
    except (ValueError, KeyError) as exc:
        raise SystemExit("FAIL: invalid Base64 payload") from exc
    if len(data) != payload.get("bytes") or digest(data) != SHA256:
        raise SystemExit("FAIL: payload length or SHA-256 differs")

    output_dir = args.output_dir.resolve()
    target = output_dir / NAME
    if target.exists():
        if target.is_file() and digest(target.read_bytes()) == SHA256:
            print(f"PASS_EXISTING: {target}")
            return
        raise SystemExit(f"FAIL: existing workbook differs; refusing to overwrite: {target}")

    output_dir.mkdir(parents=True, exist_ok=True)
    created = False
    try:
        descriptor = os.open(target, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
        created = True
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        if digest(target.read_bytes()) != SHA256:
            raise RuntimeError("restored workbook SHA-256 differs")
    except Exception:
        if created:
            target.unlink(missing_ok=True)
        raise
    print(f"PASS_RESTORED: {target}")


if __name__ == "__main__":
    main()
