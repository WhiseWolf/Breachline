#!/usr/bin/env python3
"""Read-only Instagram connectivity test; credentials remain on Ubuntu."""
import json
from pathlib import Path
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from urllib.parse import urlencode

def main():
    path = Path.home() / ".config" / "breachline-agent" / "instagram.json"
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
        token = config["access_token"]
        if not isinstance(token, str) or not token.strip():
            raise ValueError("empty token")
    except (OSError, ValueError, KeyError, TypeError):
        print("FEHLER: Gespeicherter Token fehlt oder die Konfigurationsdatei ist ungueltig.")
        return 1

    request = Request(
        "https://graph.instagram.com/v26.0/me?" + urlencode({
            "fields": "user_id,username", "access_token": token
        }),
        headers={"Accept": "application/json", "User-Agent": "BreachlineAgent-InstagramCheck/1.1"}
    )
    try:
        with urlopen(request, timeout=30) as response:
            data = json.load(response)
        if isinstance(data, dict) and isinstance(data.get("data"), list):
            entries = data["data"]
            if len(entries) != 1:
                raise ValueError("ambiguous account")
            data = entries[0]
        if not isinstance(data, dict):
            raise ValueError("unexpected response")
        username = data.get("username")
        user_id = data.get("user_id")
        if not username or not user_id:
            raise ValueError("missing identity")
        print("Konto: @" + str(username).replace(token, "[TOKEN]"))
        print("Instagram User-ID: " + str(user_id).replace(token, "[TOKEN]"))
        expected = str(config.get("username", "breachlineagent")).lstrip("@").lower()
        if str(username).lower() != expected:
            print("FEHLER: Das zurueckgegebene Konto entspricht nicht dem erwarteten Konto.")
            return 1
        print("OK: Instagram akzeptiert den Token fuer den Kontozugriff.")
        print("Dieser Test veroeffentlicht nichts. Posting-Rechte und Jarvis-Anbindung sind noch nicht getestet.")
        return 0
    except HTTPError as error:
        print("Instagram-Fehler: HTTP " + str(error.code))
        raw = error.read(8192).decode("utf-8", errors="replace").replace(token, "[TOKEN]")
        try:
            payload = json.loads(raw)
            details = payload.get("error", payload) if isinstance(payload, dict) else payload
            if isinstance(details, dict):
                print("API-Code: " + str(details.get("code", "unbekannt")))
                print(str(details.get("message", json.dumps(details, ensure_ascii=False)))[:1500])
            else:
                print(str(details)[:1500])
        except ValueError:
            print("Antwortformat: " + str(error.headers.get("Content-Type", "unbekannt")))
            print("Antwort: " + (raw[:1500] or "(leer)"))
        return 1
    except (URLError, OSError, TimeoutError):
        print("FEHLER: Verbindung zu Instagram fehlgeschlagen. Internet und Systemzeit pruefen.")
        return 1
    except (ValueError, TypeError):
        print("FEHLER: Instagram lieferte keine eindeutige Kontoantwort.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
