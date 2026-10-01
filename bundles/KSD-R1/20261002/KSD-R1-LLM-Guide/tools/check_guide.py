"""Check the guide package only; do not evaluate or edit an Excel workbook."""

import csv
import hashlib
import json
import re
from pathlib import Path


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def main():
    root = Path(__file__).resolve().parent.parent
    manifest = read_json(root / "PACKAGE_MANIFEST.json")
    checked = set()
    for item in manifest["files"]:
        relative_path = item["path"]
        path = (root / relative_path).resolve()
        if not path.is_relative_to(root) or relative_path in checked:
            raise ValueError(f"Unsafe or duplicate manifest path: {relative_path}")
        checked.add(relative_path)
        data = path.read_bytes()
        if len(data) != item["size_bytes"]:
            raise ValueError(f"Size mismatch: {relative_path}")
        if hashlib.sha256(data).hexdigest() != item["sha256"]:
            raise ValueError(f"SHA mismatch: {relative_path}")

    actual = {
        p.relative_to(root).as_posix()
        for p in root.rglob("*")
        if p.is_file()
        and p.name != "PACKAGE_MANIFEST.json"
        and not p.name.startswith("bundle_")
        and "__pycache__" not in p.parts
    }
    if actual != checked:
        raise ValueError(f"Manifest coverage mismatch: {actual ^ checked}")

    main_md = root / "LLM_IMPLEMENTATION_GUIDE.md"
    main_txt = root / "LLM_IMPLEMENTATION_GUIDE.txt"
    if main_md.read_bytes() != main_txt.read_bytes():
        raise ValueError("MD/TXT contents differ")

    link_count = 0
    for path in root.glob("*.md"):
        content = path.read_text(encoding="utf-8")
        if "作成日:" not in content or "作成者: Codex (GPT-6)" not in content:
            raise ValueError(f"Missing document metadata: {path.name}")
        for target in re.findall(r"\]\(([^)]+)\)", content):
            if target.startswith(("https://", "http://", "#")):
                continue
            destination = (path.parent / target.split("#")[0]).resolve()
            if not destination.is_relative_to(root) or not destination.is_file():
                raise ValueError(f"Broken package link: {path.name}: {target}")
            link_count += 1

    formulas = read_json(root / "reference/formulas.json")
    if len(formulas) != 936:
        raise ValueError("Reference formula count differs from the old source")
    by_cell = {(f["sheet"], f["cell"]): f["formula"] for f in formulas}
    if len(by_cell) != 936:
        raise ValueError("Duplicate reference formula cell")
    anchors = read_json(root / "reference/anchors.json")
    targets = anchors["output_roles"]
    if len(targets) != 10 or len({t["role_id"] for t in targets}) != 10:
        raise ValueError("Expected ten distinct output roles")
    for item in targets:
        old = item["reference"]
        if by_cell[(old["sheet"], old["cell"])] != old["formula"]:
            raise ValueError(f"Reference formula mismatch: {item['role_id']}")
    if sum(t["reference"]["formula"].count("VLOOKUP(") for t in targets) != 12:
        raise ValueError("Reference lookup count mismatch")
    main_key = anchors["key_roles"][0]["ordered_reference_cells"]
    alt_key = anchors["key_roles"][1]["ordered_reference_cells"]
    if len(main_key) != 9 or len(alt_key) != 9 or main_key == alt_key:
        raise ValueError("Two distinct nine-element key roles are required")
    for item in targets:
        key = next(k for k in anchors["key_roles"] if k["role_id"] == item["key_role"])
        refs = ",".join(f"{key['reference_sheet']}!{cell}" for cell in key["ordered_reference_cells"])
        if f"CONCATENATE({refs})" not in item["reference"]["formula"]:
            raise ValueError(f"Key order does not match archived formula: {item['role_id']}")

    summary = read_json(root / "templates/evaluation_summary.json")
    if len(summary["gates"]) != 9:
        raise ValueError("Expected nine acceptance gates")
    if any(g["status"] != "NOT_RUN" for g in summary["gates"]):
        raise ValueError("Template must not claim completed acceptance")
    if summary["adoption_decision"] != "NOT_EVALUATED":
        raise ValueError("Template must not claim candidate adoption")
    if summary["production_deployed"] or summary["workbook_modified"]:
        raise ValueError("Template must not claim changes or deployment")
    bindings = read_json(root / "templates/bindings.json")
    if any(b["status"] != "UNRESOLVED" for b in bindings["roles"]):
        raise ValueError("Template must not claim verified live bindings")
    target_ids = {t["role_id"] for t in targets}
    if not target_ids.issubset({b["role_id"] for b in bindings["roles"]}):
        raise ValueError("Missing output binding template")
    for path in (root / "templates").glob("*.json"):
        read_json(path)
    for path in (root / "templates").glob("*.csv"):
        with path.open(encoding="utf-8", newline="") as stream:
            reader = csv.DictReader(stream)
            if not reader.fieldnames or len(set(reader.fieldnames)) != len(reader.fieldnames):
                raise ValueError(f"Invalid CSV header: {path.name}")
            for row in reader:
                if None in row:
                    raise ValueError(f"Invalid CSV row: {path.name}")

    print(json.dumps({
        "status": "PASS",
        "scope": "Guide package integrity only; candidate acceptance NOT_RUN",
        "manifest_files": len(checked),
        "local_links": link_count,
        "reference_formulas": len(formulas),
        "output_roles": len(targets),
        "live_acceptance_gates": "NOT_RUN",
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
