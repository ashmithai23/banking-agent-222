# Troubleshooting & Known Windows Workarounds

## 1. Windows `cp1252` Console Encoding
### Issue:
`UnicodeEncodeError: 'charmap' codec can't encode character '\U0001f4c1'`
### Solution:
VectraBank uses UTF-8 stream reconfiguration:
```python
import sys
if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
```

## 2. ChromaDB SQLite3 Version Notice
Ensure Python 3.10+ is installed, which bundles SQLite 3.35+.

## 3. Port Conflicts
Kill conflicting processes on Windows:
```powershell
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process -Force
```
