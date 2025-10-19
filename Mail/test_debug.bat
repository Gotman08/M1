@echo off
echo Starting debug test...
python main.py --debug --dry-run --no-interactive --no-apis --folder Inbox --limit 3
echo.
echo Test complete!
pause
