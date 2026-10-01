"""Read-only integrity check for the delivered SA900-01 v4 package."""

from __future__ import annotations

import base64
import hashlib
import json
import re
import zipfile
from pathlib import Path, PurePosixPath
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parents[1]
BOOK = "SA900-01_据付寸法計算_境界条件修正版_v4_20260924.xlsx"
BOOK_SHA = "8d634d87e92446c53977173b0fe69d5bb745a33d6b9f8c691f1e6334eb1da4da"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def verify_manifest() -> int:
    manifest = read_json("PACKAGE_MANIFEST.json")
    require(manifest.get("schema") == 1, "manifest schema differs")
    expected = manifest.get("files")
    require(isinstance(expected, dict), "manifest files missing")
    actual = {
        path.relative_to(ROOT).as_posix()
        for path in ROOT.rglob("*")
        if path.is_file() and path.name != "PACKAGE_MANIFEST.json"
    }
    require(actual == set(expected), f"manifest entry mismatch: missing={set(expected)-actual}, extra={actual-set(expected)}")
    for relative, record in expected.items():
        part = PurePosixPath(relative)
        require(not part.is_absolute() and ".." not in part.parts, f"unsafe manifest path: {relative}")
        path = ROOT.joinpath(*part.parts)
        require(path.stat().st_size == record["bytes"], f"size mismatch: {relative}")
        require(sha256(path) == record["sha256"], f"SHA-256 mismatch: {relative}")
    return len(expected)


def verify_workbook() -> int:
    path = ROOT / "workbook" / BOOK
    require(sha256(path) == BOOK_SHA, "workbook identity differs")
    with zipfile.ZipFile(path) as archive:
        require(archive.testzip() is None, "workbook ZIP CRC failure")
        tree = ElementTree.fromstring(archive.read("xl/workbook.xml"))
    namespace = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
    names = [sheet.attrib["name"] for sheet in tree.iter(namespace + "sheet")]
    require(len(names) == 14, "workbook sheet count differs")
    for name in ("塔内機器_出力①", "塔内機器_出力②", "塔内機器_出力③", "塔内機器_計算用シート"):
        require(name in names, f"workbook sheet missing: {name}")
    require("ExcelOutputSetting" not in names, "unexpected ExcelOutputSetting sheet")
    payload = read_json("payload/WorkbookPayload.json")
    require(payload.get("schema") == 1 and payload.get("file") == BOOK, "payload identity differs")
    data = base64.b64decode(payload["base64"], validate=True)
    require(len(data) == payload["bytes"] == path.stat().st_size, "payload length differs")
    require(hashlib.sha256(data).hexdigest() == payload["sha256"] == BOOK_SHA, "payload SHA-256 differs")
    return len(names)


def verify_evidence() -> int:
    latest = read_json("evidence/latest_summary.json")
    static = read_json("evidence/static_validation.json")
    finish = read_json("evidence/native_finish.json")
    native = read_json("evidence/native_acceptance.json")
    require(latest["status"] == "passed" and latest["candidateSha256"] == BOOK_SHA, "latest gate differs")
    require(latest["cases"] == 115 and latest["regressionCases"] == 100 and latest["adversarialCases"] == 15, "case totals differ")
    require(latest["formulaErrors"] == 0 and latest["output2Pages"] == 1, "gate result differs")
    require(latest["iphoneTested"] is False and latest["manufacturerRulesVerified"] is False, "verification limits differ")
    require(static["passed"] is True and static["sha256"] == BOOK_SHA and static["intentional_changes"] == 92, "static gate differs")
    require(finish["completed"] is True and finish["sha256"] == BOOK_SHA and finish["reopen"] is True, "native finish differs")
    require(native["completed"] is True and native["targetSha256"] == BOOK_SHA, "native acceptance differs")
    require(native["runId"] == latest["runId"] and len(native["cases"]) == 115, "native case identity differs")
    require(all(case["pass"] for case in native["cases"]), "native case failure recorded")
    require(len(native["checks"]) == 6 and all(check["pass"] for check in native["checks"]), "protection check differs")
    return len(native["cases"])


def verify_links() -> int:
    checked = 0
    for path in ROOT.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        for target in re.findall(r"\]\(([^)]+)\)", text):
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            local = target.split("#", 1)[0]
            if not local:
                continue
            require((path.parent / local).exists(), f"broken link: {path.relative_to(ROOT)} -> {target}")
            checked += 1
    return checked


def main() -> None:
    count = verify_manifest()
    sheets = verify_workbook()
    cases = verify_evidence()
    links = verify_links()
    print(json.dumps({"status": "PASS", "files": count, "sheets": sheets, "cases": cases, "localLinks": links, "workbookSha256": BOOK_SHA}, ensure_ascii=False))


if __name__ == "__main__":
    main()
