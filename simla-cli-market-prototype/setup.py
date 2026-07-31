"""Setup local del prototipo Simla.com + CLI Market."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def setup_environment() -> bool:
    print("Configurando prototipo Simla.com + CLI Market...")

    (ROOT / "logs").mkdir(exist_ok=True)
    print("OK logs/")

    print("Instalando dependencias...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(ROOT / "requirements.txt")],
            check=True,
            cwd=ROOT,
        )
        print("OK dependencies")
    except subprocess.CalledProcessError as e:
        print(f"Error instalando dependencias: {e}")
        return False

    env_path = ROOT / ".env"
    example = ROOT / ".env.example"
    if not env_path.exists():
        if example.exists():
            env_path.write_text(example.read_text(encoding="utf-8"), encoding="utf-8")
            print("Creado .env desde .env.example — rellena las keys reales")
        else:
            print("Falta .env.example")
            return False

    from dotenv import load_dotenv

    load_dotenv(env_path)
    missing = [v for v in ("CLI_MARKET_API_KEY",) if not os.getenv(v) or "your-" in (os.getenv(v) or "")]
    if missing:
        print(f"Configura en .env: {', '.join(missing)}")
        print("SIMLA_API_KEY es opcional (dry-run de envío si falta).")
        return False

    required_files = [
        "src/cli_market_client.py",
        "src/simla_client.py",
        "src/intent_detector.py",
        "src/whatsapp_formatter.py",
        "src/simla_middleware.py",
    ]
    missing_files = [f for f in required_files if not (ROOT / f).exists()]
    if missing_files:
        print(f"Faltan archivos: {', '.join(missing_files)}")
        return False

    print("Setup OK")
    print()
    print("Arranque:")
    print("  cd simla-cli-market-prototype")
    print("  python -m uvicorn src.simla_middleware:app --reload --host 0.0.0.0 --port 8000")
    print("Docs: http://localhost:8000/docs")
    return True


if __name__ == "__main__":
    sys.exit(0 if setup_environment() else 1)
