#!/usr/bin/env python3
"""Copy audited briefing updates into the active offline briefing; never logs.

Stops on unrecognized local edits before copying any file. Backups are retained.
Run after stopping the old scheduler and updating the agent-lab checkout.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import os
import shutil
import tempfile

BASELINE = {
  "MASTER_SYSTEM_PROMPT.md": "ebd87e6ce6ab7e9ff354081eee499cf13486931a725fd065963419d39632abca",
  "00_CONSTITUTION.md": "322dc8e78db12f67d808b0c95e64fa04825de9b4d07cb5339fb51ed361a53886",
  "AGENT_BRIEFING_FULL.md": "4153f72c870ec435cf74b02324a98f03ad4205a92933e7faf56077d4ef6dcf7f",
  "00_README_FIRST.md": "7bf12b9ed1ffa83607ec00881a012c4579e49840a7a8105e4e147cead17cc41d",
  "01_GOAL.md": "00de861b50e203d9d18126de1aa0b1da153ae57590800279db9461b20bb1507e",
  "02_OPERATING_RULES.md": "36db8750a2ddfc061237e2d1320b6f1354f150222424a38007ddca5883cff6bb",
  "03_RESEARCH_PROTOCOL.md": "886931eb39e5feea7fb92f12170fd2b8d6f7d5681e49599bbbc4025e9db3c2e7",
  "04_EVIDENCE_AND_GATES.md": "0eb0ac57a8de9397dd27fce433c613efaa1ec791153b6d61b3a05b46db64953d",
  "05_AUTONOMY_AND_ESCALATION.md": "4256cfed558910128fa7998ac1cc3ee2051624ce9641975d5922bce6541a5fb1",
  "06_FIRST_RUN.md": "2f180f037d92080d698ad0ebf2ddc1a156b5fcfc785587add06834c6ec881e46",
  "07_CURRENT_HANDOFF.md": "b14e8f24afbdf1bb22c9e3ceffcc7d967f930d9edc7bb15d1528e528709eac9d",
  "08_COST_AND_PREFLIGHT_POLICY.md": "6d7d5b4e24ad39a74337dadbb307caf35b14532fbceead1d732b0529d8429371",
  "09_ADAPTATION_POLICY.md": "57fe43ec48f4f2a8a39db7979b9a7a47ba3322deb5ef127b748089b604f8839f",
  "10_AGENT_LOOP.md": "da8985b82a09616ca110a568ca991badff35792f7c71d110841850b0e2bbdc8a",
  "11_EVALUATION_SCORECARD.md": "5b85e533f88fde90c5483ae5b7d1da90f15be09610a341705dff54df3825e2b7",
  "12_EXECUTION_AND_EVIDENCE.md": "8b9e3bc146c2ad359b2f3251f04bf26e7722e9ee71789fce8f98a953ee432c10",
  "13_AUTHORIZATIONS.md": "98a2a297f58a6b3fe2cb02ea859ee580cb2f26c1a46a850578fc6f65034c4c10",
  "14_START_ACCEPTANCE.md": "e68a39e1fd883df64050a72beac8b9a2c1e6cf7f38e64d65dce86fd9605d59e6",
  "agent_config.json": "fb2cd9dbf79f3a39ed4fe72f22718051d9cb199ee466b13f2228c6cbc0a11079"
}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def sync(repo, workspace):
    source = repo / "briefing"
    destination = workspace / "briefing"
    changes = []
    # Validate the entire update before changing even one active file.
    for name, previous_hash in BASELINE.items():
        src, dst = source / name, destination / name
        if not src.is_file() or src.is_symlink() or dst.is_symlink():
            raise SystemExit("Briefing-Datei fehlt oder ist ein Symlink: " + name)
        desired_hash = sha(src)
        if dst.exists():
            current_hash = sha(dst)
            if current_hash == desired_hash:
                continue
            if current_hash != previous_hash:
                raise SystemExit("Lokale Briefing-Änderung erhalten; nichts überschrieben: " + name)
        changes.append((src, dst))
    if not changes:
        return {"status": "ALREADY_CURRENT", "changed": []}
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    backup = workspace / "briefing-backups" / stamp
    backup.mkdir(parents=True, mode=0o700)
    destination.mkdir(exist_ok=True)
    for src, dst in changes:
        if dst.exists():
            shutil.copy2(dst, backup / dst.name)
        fd, temporary = tempfile.mkstemp(prefix=".briefing-", dir=destination)
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(src.read_bytes())
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, dst)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
    return {"status": "UPDATED", "changed": [dst.name for _, dst in changes],
            "backup": str(backup), "logs": "untouched"}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path.home() / "breachline-agent")
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    print(json.dumps(sync(repo, args.workspace.expanduser().resolve()), ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()

