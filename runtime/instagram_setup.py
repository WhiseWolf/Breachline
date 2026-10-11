#!/usr/bin/env python3
"""Store the Instagram token locally; never print it or send it over the network."""
import getpass
import json
import os
from pathlib import Path
import sys
import tempfile

USERNAME = "breachlineagent"
INSTAGRAM_USER_ID = "17841416428554896"


def save_credentials(token, folder):
    if not token or any(c.isspace() for c in token):
        raise ValueError("Token leer oder mit Leerzeichen/Zeilenumbruechen.")
    if folder.is_symlink():
        raise ValueError("Konfigurationsordner darf kein symbolischer Link sein.")
    folder.mkdir(parents=True, exist_ok=True, mode=0o700)
    folder.chmod(0o700)
    path = folder / "instagram.json"
    fd, temporary = tempfile.mkstemp(prefix=".instagram-", suffix=".tmp", dir=folder)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            os.fchmod(stream.fileno(), 0o600)
            json.dump({
                "access_token": token,
                "instagram_user_id": INSTAGRAM_USER_ID,
                "username": USERNAME,
            }, stream, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return path


def main():
    if not sys.stdin.isatty():
        print("Bitte direkt in einem interaktiven Ubuntu-/tmux-Terminal starten.", file=sys.stderr)
        return 1
    folder = Path.home() / ".config" / "breachline-agent"
    path = folder / "instagram.json"
    try:
        if path.exists() or path.is_symlink():
            answer = input("Vorhandenen Instagram-Token ersetzen? [j/N]: ").strip().lower()
            if answer not in {"j", "ja"}:
                print("Abgebrochen; vorhandener Token bleibt erhalten.")
                return 0
        token = getpass.getpass("Instagram-Token einfuegen (unsichtbar), dann Enter: ").strip()
        path = save_credentials(token, folder)
    except (EOFError, KeyboardInterrupt):
        print("\nAbgebrochen.")
        return 1
    except (OSError, ValueError):
        print("Speichern fehlgeschlagen. Token leer/ungueltig oder lokale Schreibrechte fehlen.",
              file=sys.stderr)
        return 1
    print(f"Token lokal gespeichert: {path}")
    print("Nur dein Ubuntu-Benutzer hat Dateizugriff (0600); Ordnerrechte: 0700.")
    print("Keine API-Abfrage ausgefuehrt. Jarvis-Anbindung ist noch separat einzurichten.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
