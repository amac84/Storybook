# Review evidence

Source reviewed: `37f50fd93fde00a6918425b638a9a34e580fab25` on `cursor/childrens-book-studio-b801`.

These files preserve review-time evidence. They are not production pipeline changes or a claim that visual quality has been evaluated.

- `tests-compatible.log`: 42 existing tests passed, unchanged.
- `run_tests.py`: disposable runner; normalizes only temporary-directory creation under its own temporary parent from mode 0700 to 0777 to accommodate this Windows sandbox.
- `repro_visual_gates.py`: nine assertion-backed cases exercising the original quality validator and archive CLI. It intentionally writes synthetic book/canon fixtures into the disposable `source` export beside the script.
- `repro-results.json`: captured outcomes, including a correctly blocked uppercase FAIL control and the permissive/bypass cases.

Python 3.14 with preinstalled PyYAML 6.0.3 was used. No dependencies were installed. No paid API was called.

To repeat, run from the repository root in PowerShell. These commands create a fresh OS-temp directory and export the original commit; they do not switch branches. Always use a fresh export, since the reproduction harness intentionally mutates its disposable fixtures. Run the existing tests before the harness.

```powershell
$reviewScratch = Join-Path $env:TEMP ('cove-mars-review-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $reviewScratch | Out-Null
$reviewArchive = Join-Path $reviewScratch 'source.zip'
git archive --format=zip "--output=$reviewArchive" 37f50fd93fde00a6918425b638a9a34e580fab25
Expand-Archive -LiteralPath (Join-Path $reviewScratch 'source.zip') -DestinationPath (Join-Path $reviewScratch 'source')
Copy-Item -LiteralPath 'docs/review-evidence/run_tests.py' -Destination $reviewScratch
Copy-Item -LiteralPath 'docs/review-evidence/repro_visual_gates.py' -Destination $reviewScratch
py -3.14 (Join-Path $reviewScratch 'run_tests.py')
py -3.14 (Join-Path $reviewScratch 'repro_visual_gates.py')
```

The source export is deliberately not bundled with these evidence files. The scripts must not be placed alongside a production checkout named `source`.
