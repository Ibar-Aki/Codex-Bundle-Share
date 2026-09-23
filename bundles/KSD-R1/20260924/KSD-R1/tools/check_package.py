"""Read-only delivery gate; Python 3.10+, standard library only."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import posixpath
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SHA = '6afb0ea4fe142210f3f62e29f1718fa9408c95eb9d99e9a61a05b56ec4d50e20'
NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
RELS = '{http://schemas.openxmlformats.org/package/2006/relationships}'
RID = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_json(relative):
    return json.loads((ROOT / relative).read_text(encoding='utf-8-sig'))


def formulas_in_workbook(path):
    formulas = {}
    with zipfile.ZipFile(path) as archive:
        require(archive.testzip() is None, 'Workbook ZIP corruption')
        relationships = ET.fromstring(archive.read('xl/_rels/workbook.xml.rels'))
        targets = {node.attrib['Id']: node.attrib['Target'] for node in relationships.findall(RELS + 'Relationship')}
        sheets = ET.fromstring(archive.read('xl/workbook.xml')).findall('m:sheets/m:sheet', NS)
        for sheet in sheets:
            target = targets[sheet.attrib[RID]]
            member = target.lstrip('/') if target.startswith('/') else posixpath.normpath('xl/' + target)
            document = ET.fromstring(archive.read(member))
            cells = document.findall('.//m:sheetData/m:row/m:c', NS)
            shared = {}
            for cell in cells:
                formula = cell.find('m:f', NS)
                if formula is not None and formula.attrib.get('t') == 'shared' and formula.text:
                    shared[formula.attrib['si']] = (cell.attrib['r'], formula.text)
            for cell in cells:
                formula = cell.find('m:f', NS)
                if formula is not None:
                    text = formula.text
                    if formula.attrib.get('t') == 'shared' and not text:
                        origin, original = shared[formula.attrib['si']]
                        text = translate_formula(original, origin, cell.attrib['r'])
                    require(text is not None, 'Formula text missing')
                    formulas[(sheet.attrib['name'], cell.attrib['r'])] = '=' + text
    return formulas, len(sheets)


def coordinate(address):
    match = re.fullmatch(r'\$?([A-Z]+)\$?(\d+)', address)
    require(match is not None, 'Unsupported cell address: ' + address)
    col = 0
    for character in match[1]:
        col = col * 26 + ord(character) - ord('A') + 1
    return int(match[2]), col


REFERENCE = re.compile(r"(?:(?:'((?:[^']|'')+)'|([^\s()+\-*/^&,=<>!:\"']+))!)?(\$?[A-Z]{1,3}\$?\d+)(?::(\$?[A-Z]{1,3}\$?\d+))?")


def translate_formula(formula, origin, destination):
    """Expand OOXML shared formulas while preserving absolute references and strings."""
    r0, c0 = coordinate(origin)
    r1, c1 = coordinate(destination)
    def move(address):
        match = re.fullmatch(r'(\$?)([A-Z]+)(\$?)(\d+)', address)
        row, column = coordinate(address)
        row += 0 if match[3] else r1 - r0
        column += 0 if match[1] else c1 - c0
        require(row >= 1 and column >= 1, 'Invalid translated shared reference')
        letters = ''
        while column:
            column, digit = divmod(column - 1, 26)
            letters = chr(65 + digit) + letters
        return match[1] + letters + match[3] + str(row)
    def replace(match):
        start, end = match[3], match[4]
        prefix = match[0][:(match.start(3) - match.start())]
        return prefix + move(start) + (':' + move(end) if end else '')
    parts = re.split(r'("(?:[^"]|"")*")', formula)
    return ''.join(part if i % 2 else REFERENCE.sub(replace, part) for i, part in enumerate(parts))


def affected_cells(formulas, initial):
    dependencies = {}
    for cell, formula in formulas.items():
        # Excel string literals are not references.
        expression = re.sub(r'"(?:[^"]|"")*"', '""', formula)
        references = []
        for quoted, plain, start, end in REFERENCE.findall(expression):
            sheet = quoted.replace("''", "'") or plain or cell[0]
            references.append((sheet, coordinate(start), coordinate(end or start)))
        dependencies[cell] = references
    closure = set(initial)
    while True:
        old = len(closure)
        for cell, references in dependencies.items():
            for sheet, (r1, c1), (r2, c2) in references:
                if any(s == sheet and r1 <= coordinate(a)[0] <= r2 and c1 <= coordinate(a)[1] <= c2 for s, a in closure):
                    closure.add(cell)
                    break
        if len(closure) == old:
            return closure


def check(skip_manifest=False):
    workbook = ROOT / 'workbook/KSD-R1_restored.xlsx'
    raw = workbook.read_bytes()
    require(digest(raw) == EXPECTED_SHA, 'Delivered workbook identity differs')
    identity = read_json('reference/source_identity.json')
    require(identity['workbook_sha256'] == EXPECTED_SHA and identity['workbook_bytes'] == len(raw), 'Source identity differs')
    payload = read_json('payload/WorkbookPayload.json')
    decoded = base64.b64decode(payload['base64'], validate=True)
    require(payload['schema'] == 1 and payload['file'] == workbook.name and payload['sha256'] == EXPECTED_SHA, 'Payload identity differs')
    require(payload['bytes'] == len(raw) and decoded == raw, 'Payload does not reproduce delivered workbook')
    actual, sheet_count = formulas_in_workbook(workbook)
    records = read_json('reference/formulas.json')
    expected = {(item['sheet'], item['cell']): item['formula'] for item in records}
    require(len(expected) == len(records) == 936 and sheet_count == 14, 'Unexpected source coverage')
    require(actual == expected, 'Formula snapshot differs from delivered workbook')
    specification = read_json('docs/変更セル仕様.json')
    require(specification['review_source_sha256'] == EXPECTED_SHA, 'Plan bound to another workbook')
    changes = specification['changes']
    targets = {(c['sheet'], c['cell']) for c in changes}
    names = {'K45', 'Q45', 'W45', 'C57', 'D57', 'E57', 'W49', 'W62'}
    require(targets == {('基準芯出し_出力③', name) for name in names} and len(changes) == 8, 'Target set differs')
    key = specification['key_formula'][1:]
    placeholder = specification['placeholder']
    require(specification['physical_binding'] is None and specification['executable_as_is'] is False, 'Unverified physical binding')
    for change in changes:
        before = actual[(change['sheet'], change['cell'])]
        require(change['before'] == before and digest(before.encode()) == change['before_sha256'], 'Before formula differs')
        for name in ['shared_key_template', 'inline_template']:
            template = change[name]
            require(template.replace(placeholder, key) == before, 'Roundtrip changed formula semantics')
            require(template.count(placeholder) == change['occurrences'], 'Incorrect placeholder count')
            require(template.count('VLOOKUP(') == before.count('VLOOKUP('), 'Lookup count differs')
    occurrences = sum(c['occurrences'] for c in changes)
    require(occurrences == 10, 'Incorrect key count')
    closure = affected_cells(actual, targets)
    affected = read_json('reference/affected_cells.json')
    require(set(affected['changed_cells']) == {s + '!' + c for s, c in targets}, 'Affected target list differs')
    require(set(affected['transitive_dependents']) == {s + '!' + c for s, c in closure - targets}, 'Dependency list differs')
    require(len(closure) == affected['affected_formula_cell_count'] == 21, 'Affected count differs')
    for doc in [ROOT / 'README.md', *(ROOT / 'docs').glob('*.md')]:
        text = doc.read_text(encoding='utf-8')
        require('作成日:' in text and '作成者:' in text, 'Missing document metadata: ' + doc.name)
        for target in re.findall(r'\]\(([^)]+)\)', text):
            if target.startswith(('http://', 'https://', '#')):
                continue
            resolved = (doc.parent / target.split('#')[0]).resolve()
            require(resolved.is_relative_to(ROOT.resolve()) and resolved.is_file(), 'Broken or external local document link: ' + target)
    checked_files = 0
    if not skip_manifest:
        manifest = read_json('PACKAGE_MANIFEST.json')
        for path, info in manifest['files'].items():
            full = (ROOT / path).resolve()
            require(full.is_relative_to(ROOT.resolve()) and full.is_file(), 'Manifest member missing or outside package: ' + path)
            data = full.read_bytes()
            require(digest(data) == info['sha256'] and len(data) == info['bytes'], 'Manifest mismatch: ' + path)
            checked_files += 1
        actual_paths = {p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and '.git' not in p.relative_to(ROOT).parts and '__pycache__' not in p.relative_to(ROOT).parts and p.name != 'PACKAGE_MANIFEST.json'}
        require(actual_paths == set(manifest['files']), 'Extra or missing files outside manifest')
    return {'status': 'PASS', 'scope': 'Delivery integrity and static formulas only', 'source_sha256': EXPECTED_SHA, 'workbook_changed': False, 'sheets': sheet_count, 'formulas': len(actual), 'target_formulas': len(changes), 'key_occurrences': occurrences, 'affected_formulas': len(closure), 'manifest_files_checked': checked_files, 'runtime_comparison': 'NOT_RUN', 'designer_iphone_acceptance': 'NOT_RUN'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skip-manifest', action='store_true', help='Assembly only; not a release gate')
    arguments = parser.parse_args()
    try:
        result = check(arguments.skip_manifest)
        if arguments.skip_manifest:
            result['status'] = 'ASSEMBLY_CHECK_ONLY'
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as error:
        print(json.dumps({'status': 'FAIL', 'error': str(error)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
