from __future__ import annotations
import json
from pathlib import Path
import subprocess
import sys
import yaml

BASE = Path(__file__).resolve().parent
ROOT = BASE / 'source'
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'tests'))
from studio.quality_gates import evaluate
from studio.config import quality_gates
from test_studio import SAMPLE

# Fixtures and all real archive writes remain exclusively inside the disposable export.
book = ROOT / 'books' / '991'
(book / 'art' / 'approved').mkdir(parents=True, exist_ok=True)
def write_yaml(path, obj):
    path.write_text(yaml.safe_dump(obj), encoding='utf-8')
write_yaml(book / 'brief.yaml', {'working_title': 'Disposable validation fixture'})
(book / 'manuscript-final.md').write_text(SAMPLE, encoding='utf-8')
gates = quality_gates()
editorial = {key: True for key, value in gates.items() if value is True}
editorial.update({'engagement_score': 100, 'story_score': 100, 'character_score': 100, 'values_score': 100})
write_yaml(book / 'editorial-v2.yaml', editorial)
write_yaml(book / 'book-report.yaml', {'human_approval': 'approved'})
write_yaml(book / 'art' / 'direction.yaml', {})
qa_path = book / 'art' / 'qa.yaml'
results = []
def record(case):
    try:
        output = evaluate(991, 'approval')
        item = {'case': case, 'passed': output['passed'], 'failures': output['failures'], 'warnings': output['warnings'], 'approved_image_count': len(list((book / 'art' / 'approved').glob('*')))}
    except Exception as exc:
        item = {'case': case, 'exception': type(exc).__name__, 'message': str(exc)}
    results.append(item)
    return item
assert record('missing_qa_and_zero_images')['passed'] is True
write_yaml(qa_path, {'result': 'PASS', 'images': []})
assert record('qa_pass_zero_images_and_empty_direction')['passed'] is True
write_yaml(qa_path, {'result': 'fail'})
assert record('lowercase_fail')['passed'] is True
write_yaml(qa_path, {'result': 'PENDING'})
assert record('qa_pending')['passed'] is True
write_yaml(qa_path, {'result': 'FAIL'})
assert record('uppercase_fail_control')['passed'] is False
write_yaml(book / 'book-report.yaml', {'human_approval': 'approved', 'quality_gate_overrides': [{'gate': 'visual_qa', 'reason': 'Test override'}]})
assert record('uppercase_fail_with_override')['passed'] is True
write_yaml(book / 'book-report.yaml', {'human_approval': 'approved'})
write_yaml(qa_path, ['PASS'])
assert record('qa_nonmapping')['exception'] == 'AttributeError'
write_yaml(qa_path, {'result': 'PASS', 'images': [{'spread': 1, 'image': 'art/approved/deleted.png', 'result': 'FAIL'}]})
assert record('top_level_pass_missing_and_failed_image_record')['passed'] is True

minimal = ROOT / 'books' / '992'
minimal.mkdir(exist_ok=True)
write_yaml(minimal / 'book-report.yaml', {'human_approval': 'approved'})
write_yaml(minimal / 'brief.yaml', {'working_title': 'Disposable archive bypass fixture'})
validation = evaluate(992, 'approval')
assert validation['passed'] is False
archive = subprocess.run([sys.executable, str(ROOT / 'scripts' / 'archive-book.py'), '992', '--approved'], cwd=ROOT, capture_output=True, text=True)
ledger = json.loads((ROOT / 'canon' / 'series-ledger.json').read_text(encoding='utf-8'))
case = {'case': 'archive_cli_bypasses_approval_gate', 'validation_passed': validation['passed'], 'validation_failures': validation['failures'], 'archive_returncode': archive.returncode, 'archive_stdout': archive.stdout.strip(), 'archive_stderr': archive.stderr.strip(), 'ledger_books_approved': ledger['books_approved'], 'ledger_contains_fixture': any(b['book_number'] == 992 for b in ledger['approved_books'])}
results.append(case)
assert archive.returncode == 0 and case['ledger_contains_fixture'] is True
(BASE / 'repro-results.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
print(json.dumps(results, indent=2))
