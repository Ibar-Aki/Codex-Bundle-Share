"""Read-only SHA and saved-formula comparison. Uses Python standard library."""

import argparse
import collections
import hashlib
import json
from pathlib import Path
import posixpath
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

NS = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
FLOOR_SHEET = "塔内機器_入力①"
CALC_SHEET = "塔内機器_計算用シート"
PART_DB = "塔内機器_出力②_DB"
FLOOR_CELLS = {f"{col}{row}" for col in ("B", "K", "T") for row in range(36, 65, 4)}
FLOOR_HELPERS = {f"Z{row}" for row in range(45, 69)}


def inspect_workbook(path):
    """Count formulas including followers of shared formulas, without calculation."""
    functions = collections.Counter()
    sheets = {}
    floor_vlookup = 0
    with zipfile.ZipFile(path) as archive:
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        relationships = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        targets = {r.attrib["Id"]: r.attrib["Target"] for r in relationships}
        for sheet in workbook.find("s:sheets", NS):
            title = sheet.attrib["name"]
            target = targets[sheet.attrib[f"{{{REL_NS}}}id"]]
            member = target.lstrip("/") if target.startswith("/") else posixpath.normpath(posixpath.join("xl", target))
            root = ET.fromstring(archive.read(member))
            cells = root.findall(".//s:sheetData/s:row/s:c", NS)
            shared = {}
            for cell in cells:
                formula = cell.find("s:f", NS)
                if formula is not None and formula.attrib.get("t") == "shared" and formula.text:
                    shared[formula.attrib["si"]] = formula.text
            count = 0
            for cell in cells:
                formula = cell.find("s:f", NS)
                if formula is None:
                    continue
                count += 1
                text = formula.text
                if text is None and formula.attrib.get("t") == "shared":
                    text = shared[formula.attrib["si"]]
                if text is None:
                    raise ValueError(f"Unresolved formula: {title}!{cell.attrib['r']}")
                expression = re.sub(r'"(?:[^"]|"")*"', '""', text)
                names = re.findall(r"\b([A-Za-z][A-Za-z0-9_.]*)\s*\(", expression)
                functions.update(name.upper() for name in names)
                if title == FLOOR_SHEET and cell.attrib["r"] in FLOOR_CELLS:
                    floor_vlookup += sum(name.upper() == "VLOOKUP" for name in names)
                if title == CALC_SHEET and cell.attrib["r"] in FLOOR_HELPERS:
                    floor_vlookup += sum(name.upper() == "VLOOKUP" for name in names)
            sheets[title] = count
    return {
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "formula_cells": sum(sheets.values()),
        "vlookup_occurrences": functions["VLOOKUP"],
        "floor_lookup_occurrences": floor_vlookup,
        "part_db_formula_cells": sheets[PART_DB],
        "calculation_sheet_formula_cells": sheets[CALC_SHEET],
        "function_kinds": len(functions),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workbook-directory", required=True, type=Path)
    args = parser.parse_args()
    try:
        if not args.workbook_directory.is_dir():
            raise ValueError("Workbook directory does not exist")
        evidence = json.loads(Path(__file__).with_name("formula_comparison.json").read_text(encoding="utf-8"))
        results = []
        for source in evidence["sources"]:
            matches = list(args.workbook_directory.rglob(source["file_name"]))
            if len(matches) != 1:
                raise ValueError(f"Expected one file for {source['version']}; found {len(matches)}")
            actual = inspect_workbook(matches[0])
            mismatches = {key: {"expected": value, "actual": actual.get(key)} for key, value in source["expected"].items() if actual.get(key) != value}
            results.append({"version": source["version"], "status": "FAIL" if mismatches else "PASS", "actual": actual, "mismatches": mismatches})
        status = "PASS" if all(result["status"] == "PASS" for result in results) else "FAIL"
        print(json.dumps({"status": status, "scope": "saved formulas and file SHA; no recalculation or device test", "results": results}, ensure_ascii=False, indent=2))
        return 0 if status == "PASS" else 1
    except Exception as error:
        print(json.dumps({"status": "FAIL", "error": str(error)}, ensure_ascii=False, indent=2))
        return 1


if __name__ == "__main__":
    sys.exit(main())
