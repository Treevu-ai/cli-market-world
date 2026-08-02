"""Sync the Estación 90 menu JSON to Hostinger.

Hostinger shared hosting (estacion90.pe) exposes no API — the only way
to publish menu.json is uploading it to public_html/api/menu.json over
FTP, which today is a manual step (see FLY_HORECA_DEPLOY.md). This
script automates that upload over FTPS (FTP+TLS, stdlib ftplib, no
extra dependency) and then re-fetches the public URL to confirm the
live file actually matches what was uploaded.

Usage:
    python ops/horeca/sync_estacion90_menu.py --dry-run
    python ops/horeca/sync_estacion90_menu.py

Required env vars (not needed for --dry-run):
    HOSTINGER_ESTACION90_FTP_HOST
    HOSTINGER_ESTACION90_FTP_USER
    HOSTINGER_ESTACION90_FTP_PASSWORD
Optional:
    HOSTINGER_ESTACION90_FTP_PORT      (default: 21)
    HOSTINGER_ESTACION90_REMOTE_PATH   (default: public_html/api/menu.json)
    HOSTINGER_ESTACION90_PUBLIC_URL    (default: https://estacion90.pe/api/menu.json)
"""

from __future__ import annotations

import argparse
import ftplib
import hashlib
import json
import os
import sys
import time
from pathlib import Path

import httpx

DEFAULT_LOCAL_PATH = (
    Path(__file__).resolve().parent.parent.parent / "hostinger" / "estacion90" / "api" / "menu.json"
)
DEFAULT_REMOTE_PATH = "public_html/api/menu.json"
DEFAULT_PUBLIC_URL = "https://estacion90.pe/api/menu.json"


def _connect(host: str, user: str, password: str, port: int) -> ftplib.FTP_TLS:
    ftps = ftplib.FTP_TLS()
    ftps.connect(host, port, timeout=30)
    ftps.login(user, password)
    ftps.prot_p()  # encrypt the data channel too, not just the login
    return ftps


def _ensure_remote_dir(ftps: ftplib.FTP_TLS, remote_dir: str) -> None:
    for part in (p for p in remote_dir.split("/") if p):
        try:
            ftps.cwd(part)
        except ftplib.error_perm:
            ftps.mkd(part)
            ftps.cwd(part)


def upload(local_path: Path, remote_path: str, *, host: str, user: str, password: str, port: int = 21) -> None:
    remote_dir, remote_name = remote_path.rsplit("/", 1)
    ftps = _connect(host, user, password, port)
    try:
        _ensure_remote_dir(ftps, remote_dir)
        with local_path.open("rb") as fh:
            ftps.storbinary(f"STOR {remote_name}", fh)
    finally:
        ftps.quit()


def verify(local_path: Path, public_url: str, *, retries: int = 3, delay: float = 2.0) -> bool:
    """Re-fetch the public URL and compare its hash to the uploaded file.

    Hostinger's edge cache or a slow propagation can serve the old file
    for a few seconds right after upload, so this retries instead of
    failing on the first mismatch.
    """
    local_hash = hashlib.sha256(local_path.read_bytes()).hexdigest()
    last_error = "sin intentos"
    for attempt in range(1, retries + 1):
        try:
            resp = httpx.get(public_url, timeout=15)
            resp.raise_for_status()
            remote_hash = hashlib.sha256(resp.content).hexdigest()
            if remote_hash == local_hash:
                return True
            last_error = f"hash no coincide (local={local_hash[:8]} remote={remote_hash[:8]})"
        except httpx.HTTPError as exc:
            last_error = str(exc)
        if attempt < retries:
            time.sleep(delay)
    print(f"Verificación falló tras {retries} intentos: {last_error}", file=sys.stderr)
    return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--local-path", type=Path, default=DEFAULT_LOCAL_PATH)
    parser.add_argument("--remote-path", default=os.getenv("HOSTINGER_ESTACION90_REMOTE_PATH", DEFAULT_REMOTE_PATH))
    parser.add_argument("--public-url", default=os.getenv("HOSTINGER_ESTACION90_PUBLIC_URL", DEFAULT_PUBLIC_URL))
    parser.add_argument("--dry-run", action="store_true", help="Validar el JSON local sin subir nada")
    parser.add_argument("--skip-verify", action="store_true", help="No re-consultar la URL pública tras subir")
    args = parser.parse_args(argv)

    if not args.local_path.is_file():
        print(f"No existe {args.local_path}", file=sys.stderr)
        return 1

    # A malformed menu.json published live would 500 horeca_menu_cost.py
    # in production, so validate before touching the remote file at all.
    try:
        json.loads(args.local_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"{args.local_path} no es JSON válido: {exc}", file=sys.stderr)
        return 1

    if args.dry_run:
        host = os.getenv("HOSTINGER_ESTACION90_FTP_HOST", "<host no configurado>")
        print(f"[dry-run] JSON válido. Subiría {args.local_path} -> {host}:{args.remote_path}")
        return 0

    host = os.environ["HOSTINGER_ESTACION90_FTP_HOST"]
    user = os.environ["HOSTINGER_ESTACION90_FTP_USER"]
    password = os.environ["HOSTINGER_ESTACION90_FTP_PASSWORD"]
    port = int(os.getenv("HOSTINGER_ESTACION90_FTP_PORT", "21"))

    print(f"Subiendo {args.local_path} -> {host}:{args.remote_path} ...")
    upload(args.local_path, args.remote_path, host=host, user=user, password=password, port=port)
    print("Subida completa.")

    if args.skip_verify:
        return 0

    print(f"Verificando {args.public_url} ...")
    if verify(args.local_path, args.public_url):
        print("menu.json en vivo coincide con el archivo local.")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
