import re
from pathlib import Path

path = Path(r"C:\Users\acuba\AppData\Roaming\Python\Python314\site-packages\market_ui.py")
src = path.read_text(encoding="utf-8")

# Fix 1: error_next_commands signature + add list guard
src = re.sub(
    r"def error_next_commands\(status: int \| None, message: str\) -> list\[str\]:\n    msg = \(message or \"\"\)\.lower\(\)",
    "def error_next_commands(status: int | None, message: str | list | None) -> list[str]:\n    if isinstance(message, list):\n        message = \" \".join(str(m) for m in message)\n    msg = (message or \"\").lower()",
    src,
)

# Fix 2: print_actionable_error signature + add list guard
src = re.sub(
    r"(def print_actionable_error\(\n    console: Console,\n    message: str,)",
    "def print_actionable_error(\n    console: Console,\n    message: str | list | None,",
    src,
)
src = re.sub(
    r"(\) -> None:\n    en = is_en\(\)\n    cmds = error_next_commands)",
    ") -> None:\n    if isinstance(message, list):\n        message = \" \".join(str(m) for m in message)\n    en = is_en()\n    cmds = error_next_commands",
    src,
)

path.write_text(src, encoding="utf-8")
print("✅ Patch aplicado correctamente")