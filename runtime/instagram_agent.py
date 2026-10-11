#!/usr/bin/env python3
"""Instagram Login adapter for Jarvis via shell_exec. Python standard library only."""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, urlopen, build_opener, HTTPRedirectHandler

ACCOUNT = "breachlineagent"
USER_ID = "17841416428554896"
BASE = "https://graph.instagram.com/v26.0/"


class AdapterError(RuntimeError):
    pass


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    path.parent.chmod(0o700)
    fd, temporary = tempfile.mkstemp(prefix=".instagram-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            os.fchmod(stream.fileno(), 0o600)
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


class Client:
    def __init__(self, credentials=None):
        self.path = credentials or Path.home() / ".config/breachline-agent/instagram.json"
        try:
            self.config = json.loads(self.path.read_text())
            self.token = self.config["access_token"]
            if not isinstance(self.token, str) or not self.token or any(c.isspace() for c in self.token):
                raise ValueError()
        except (OSError, ValueError, KeyError, TypeError):
            raise AdapterError("Token-Datei fehlt oder ist ungueltig; instagram_setup.py verwenden.") from None

    def clean(self, value):
        # Never emit tokens, API paging URLs, or raw transport exception URLs.
        text = json.dumps(value, ensure_ascii=False).replace(self.token, "[TOKEN]")
        return json.loads(text)

    def api(self, method, path, params=None, unversioned=False):
        values = dict(params or {}, access_token=self.token)
        base = "https://graph.instagram.com/" if unversioned else BASE
        url = base + path
        body = urlencode(values).encode() if method == "POST" else None
        if method == "GET":
            url += "?" + urlencode(values)
        request = Request(url, data=body, method=method, headers={
            "Accept": "application/json", "User-Agent": "BreachlineAgent/1.0",
            "Content-Type": "application/x-www-form-urlencoded"})
        try:
            # No redirects: token must only be sent to the fixed Meta API host.
            with build_opener(NoRedirect()).open(request, timeout=30) as response:
                data = json.load(response)
        except HTTPError as error:
            raw = error.read(8192).decode(errors="replace").replace(self.token, "[TOKEN]")
            raise AdapterError(f"Instagram HTTP {error.code}: {raw[:1200]}") from None
        except (URLError, OSError, ValueError):
            raise AdapterError("API-Verbindung oder Antwort fehlgeschlagen. Schreibwirkung kann unklar sein; Beleg pruefen, nicht blind wiederholen.") from None
        if not isinstance(data, dict) or "error" in data:
            raise AdapterError(str(self.clean(data))[:1200])
        return data

    def identity(self):
        data = self.api("GET", "me", {"fields": "user_id,username"})
        if "data" in data:
            if not isinstance(data["data"], list) or len(data["data"]) != 1:
                raise AdapterError("Kontoantwort ist nicht eindeutig.")
            data = data["data"][0]
        if not isinstance(data, dict) or str(data.get("user_id")) != USER_ID or str(data.get("username", "")).lower() != ACCOUNT:
            raise AdapterError("Falsches Konto: nur @breachlineagent mit bestaetigter User-ID erlaubt.")
        return {"username": ACCOUNT, "user_id": USER_ID}

    def collection(self, path, params=None):
        data = self.api("GET", path, params)
        return self.clean({"data": data.get("data", []),
                           "has_more": bool(data.get("paging", {}).get("next")),
                           "after": data.get("paging", {}).get("cursors", {}).get("after")})


def public_url(value, project=False):
    parsed = urlsplit(value)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise AdapterError("Nur oeffentliche HTTPS-URLs ohne Login, Query oder Fragment verwenden.")
    if project and (parsed.hostname.lower() != "whisewolf.github.io" or not parsed.path.startswith("/Breachline/")):
        raise AdapterError("Testlink muss zur freigegebenen WhiseWolf/Breachline-Pages-Seite gehoeren.")
    if not project and (parsed.hostname.lower() != "whisewolf.github.io" or not parsed.path.startswith("/Breachline/")):
        raise AdapterError("Assets fuer diesen Adapter auf den freigegebenen Projekt-Pages bereitstellen.")
    return value


def job_data(path):
    job = json.loads(path.read_text())
    if not isinstance(job, dict):
        raise AdapterError("Job muss ein JSON-Objekt sein.")
    for key in ("kind", "asset_url", "caption", "test_url", "game_version", "purpose", "gameplay_evidence", "asset_rights"):
        if not isinstance(job.get(key), str) or not job[key].strip():
            raise AdapterError("Job-Feld fehlt: " + key)
    if job["kind"] not in {"IMAGE", "REELS"} or len(job["caption"]) > 2200:
        raise AdapterError("Format muss IMAGE oder REELS sein; Caption maximal 2200 Zeichen.")
    public_url(job["test_url"], project=True)
    public_url(job["asset_url"])
    suffix = urlsplit(job["asset_url"]).path.lower()
    if job["kind"] == "IMAGE" and not suffix.endswith((".jpg", ".jpeg")):
        raise AdapterError("Bilder als JPEG bereitstellen.")
    if job["kind"] == "REELS" and not suffix.endswith((".mp4", ".mov")):
        raise AdapterError("Reels als MP4 oder MOV bereitstellen; Meta-Spezifikationen vorher pruefen.")
    evidence = Path(job["gameplay_evidence"]).expanduser()
    if not evidence.is_absolute():
        evidence = path.parent / evidence
    if not evidence.is_file() or evidence.stat().st_size == 0:
        raise AdapterError("Lokaler Gameplay-Testbeleg fehlt oder ist leer.")
    job["gameplay_evidence"] = str(evidence.resolve())
    with evidence.open("rb") as stream:
        digest = hashlib.sha256()
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    job["evidence_sha256"] = digest.hexdigest()
    return job


def reachable(url, image=False):
    # Public asset probes never receive the Instagram token.
    try:
        with urlopen(Request(url, headers={"User-Agent": "BreachlineAgent/1.0"}), timeout=30) as response:
            final = public_url(response.geturl())
            sample = response.read(3)
            if image and sample != b"\xff\xd8\xff":
                raise AdapterError("Asset ist kein JPEG.")
            if not sample:
                raise AdapterError("Oeffentliche Datei ist leer.")
            return final
    except (HTTPError, URLError, OSError):
        raise AdapterError("Oeffentlicher Testlink oder Asset nicht erreichbar.") from None


def fingerprint(job):
    content = {k: job[k] for k in ("kind", "asset_url", "caption", "game_version", "test_url")}
    return hashlib.sha256(json.dumps(content, sort_keys=True).encode()).hexdigest()


def publish(client, job, state, execute=False):
    key = fingerprint(job)
    path = state / (key + ".json")
    if not execute:
        return {"status": "PREVIEW_ONLY", "fingerprint": key, "job": job,
                "note": "Kein API-Schreibaufruf. --execute nur nach Briefing-Preflight."}
    state.mkdir(parents=True, exist_ok=True, mode=0o700)
    state.chmod(0o700)
    with (state / "adapter.lock").open("a") as lock:
        os.chmod(lock.name, 0o600)
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        receipt = json.loads(path.read_text()) if path.exists() else {"job": job, "fingerprint": key}
        if receipt.get("status") == "PUBLISHED":
            return receipt
        if receipt.get("status") in {"CREATING", "PUBLISHING"}:
            raise AdapterError("Unklare fruehere Schreibwirkung. status --receipt " + str(path) + "; keine automatische Wiederholung.")
        client.identity()
        reachable(job["test_url"])
        reachable(job["asset_url"], image=job["kind"] == "IMAGE")
        if not receipt.get("container_id"):
            # Persist before each POST; crash/timeout can never silently replay it.
            receipt.update(status="CREATING", started_at=int(time.time()))
            save(path, receipt)
            params = {"caption": job["caption"]}
            if job["kind"] == "IMAGE":
                params["image_url"] = job["asset_url"]
            else:
                params.update(media_type="REELS", video_url=job["asset_url"], share_to_feed="true")
            result = client.api("POST", USER_ID + "/media", params)
            container = str(result.get("id", ""))
            if not re.fullmatch(r"[0-9]+", container):
                raise AdapterError("Keine gueltige Container-ID; CREATING-Beleg pruefen.")
            receipt.update(status="CREATED", container_id=container)
            save(path, receipt)
        status = client.api("GET", receipt["container_id"], {"fields": "status_code,status"})
        receipt["container_status"] = client.clean(status)
        save(path, receipt)
        if status.get("status_code") != "FINISHED":
            return {"status": "NOT_READY", "receipt": str(path), "container": client.clean(status),
                    "next": "Bei IN_PROGRESS spaeter denselben Job verwenden, keinen neuen Container erstellen."}
        receipt.update(status="PUBLISHING", publish_started_at=int(time.time()))
        save(path, receipt)
        result = client.api("POST", USER_ID + "/media_publish", {"creation_id": receipt["container_id"]})
        media_id = str(result.get("id", ""))
        if not re.fullmatch(r"[0-9]+", media_id):
            raise AdapterError("Keine gueltige Beitrags-ID; PUBLISHING-Beleg pruefen.")
        receipt.update(status="PUBLISHED", media_id=media_id, published_at=int(time.time()))
        save(path, receipt)
        # A failed permalink read must not lose the durable published ID.
        try:
            receipt["media"] = client.clean(client.api("GET", media_id, {"fields": "id,permalink,timestamp"}))
            save(path, receipt)
        except AdapterError:
            receipt["note"] = "Beitrags-ID gespeichert; Permalink-Abfrage separat wiederholen."
        return receipt


def refresh(client):
    client.identity()
    result = client.api("GET", "refresh_access_token", {"grant_type": "ig_refresh_token"}, unversioned=True)
    token, seconds = result.get("access_token"), result.get("expires_in")
    if not isinstance(token, str) or not token or not isinstance(seconds, int) or seconds <= 0:
        raise AdapterError("Keine gueltige Refresh-Antwort; vorhandener Token bleibt erhalten.")
    data = dict(client.config, access_token=token, refreshed_at=int(time.time()), expires_at=int(time.time()) + seconds)
    save(client.path, data)
    return {"status": "REFRESHED", "expires_at": data["expires_at"], "token": "[NOT_DISPLAYED]"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="command", required=True)
    subs.add_parser("doctor")
    for name in ("media", "comments"):
        sub = subs.add_parser(name)
        sub.add_argument("--after")
        if name == "comments":
            sub.add_argument("--media-id", required=True)
    sub = subs.add_parser("publish")
    sub.add_argument("--job", type=Path, required=True)
    sub.add_argument("--execute", action="store_true")
    sub = subs.add_parser("status")
    sub.add_argument("--receipt", type=Path, required=True)
    subs.add_parser("refresh")
    args = parser.parse_args(argv)
    client = None
    try:
        client = Client()
        state = Path.home() / ".local/state/breachline-agent/instagram"
        if args.command == "publish":
            result = publish(client, job_data(args.job.resolve()), state, args.execute)
        elif args.command == "refresh":
            state.mkdir(parents=True, exist_ok=True, mode=0o700)
            with (state / "adapter.lock").open("a") as lock:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                result = refresh(client)
        else:
            identity = client.identity()
            if args.command == "doctor":
                result = {"status": "ACCOUNT_VERIFIED", **identity,
                          "publishing": "UNVERIFIED_UNTIL_REAL_PUBLISH",
                          "expires_at": client.config.get("expires_at", "UNKNOWN"),
                          "integration": "shell_exec -> python3 repo/runtime/instagram_agent.py",
                          "note": "Token nicht im Modellkontext lesen. Fuer Ablaufkontrolle: runtime/INSTAGRAM_AGENT.md."}
                save(state / "account-check.json", dict(result, checked_at=int(time.time())))
            elif args.command == "media":
                result = client.collection(USER_ID + "/media", {"fields": "id,caption,media_type,permalink,timestamp,like_count,comments_count", "limit": 50, **({"after": args.after} if args.after else {})})
            elif args.command == "comments":
                if not re.fullmatch(r"[0-9]+", args.media_id):
                    raise AdapterError("Ungueltige Media-ID.")
                owned = client.collection(USER_ID + "/media", {"fields": "id", "limit": 50})
                if args.media_id not in {str(x.get("id")) for x in owned["data"]}:
                    raise AdapterError("Media-ID nicht unter den letzten 50 eigenen Beitraegen verifiziert.")
                result = client.collection(args.media_id + "/comments", {"fields": "id,text,timestamp", "limit": 50, **({"after": args.after} if args.after else {})})
            else:
                path = args.receipt.expanduser().resolve()
                if path.parent != state.resolve():
                    raise AdapterError("Beleg muss im privaten Adapter-State-Verzeichnis liegen.")
                result = json.loads(path.read_text())
                if result.get("container_id"):
                    result["live_container"] = client.api("GET", result["container_id"], {"fields": "status_code,status"})
                if result.get("media_id"):
                    result["live_media"] = client.api("GET", result["media_id"], {"fields": "id,permalink,timestamp"})
                result["note"] = "Lesepruefung; unklare Schreibbelege werden nicht automatisch freigegeben."
        print(json.dumps(client.clean(result), ensure_ascii=False, indent=2))
        return 0
    except (AdapterError, OSError, ValueError, TypeError, KeyError) as error:
        message = str(error) if isinstance(error, AdapterError) else "Lokale Datei, Format oder Sperre pruefen."
        if client:
            message = message.replace(client.token, "[TOKEN]")
        print(json.dumps({"status": "ERROR", "message": message}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
