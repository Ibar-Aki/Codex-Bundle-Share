"""Rebuild the delivery inventory after reviewing intended changes; does not edit Excel."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
files = {}
for path in sorted(root.rglob('*')):
    relative = path.relative_to(root)
    if not path.is_file() or '.git' in relative.parts or '__pycache__' in relative.parts or relative.as_posix() == 'PACKAGE_MANIFEST.json':
        continue
    content = path.read_bytes()
    files[relative.as_posix()] = {'bytes': len(content), 'sha256': hashlib.sha256(content).hexdigest()}
(root / 'PACKAGE_MANIFEST.json').write_text(json.dumps({'schema': 1, 'role': 'REFERENCE_WORKBOOK_AND_REVIEW_PROPOSAL', 'workbook_changes': 0, 'files': files}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
print('Manifest written for', len(files), 'files.')
