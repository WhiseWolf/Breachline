#!/usr/bin/env python3
"""One-time encrypted Facebook Page credential import. Requires Python 3 and OpenSSL."""
import base64
import getpass
import hashlib
import hmac
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

CIPHERTEXT = 'U2FsdGVkX1/yrmHjZw9aYw3hwzPR9z61PGEB2Tm96Q+zb7tLCF+mzl3lRIsq3my2yAwXJknmJtH7/F6OEJT/MhzqYTOkkFjfPYd7Vt31wUvQlgbuDBh1PieLzONJcPY607GgwyfjXgdl6BYGMNrebJCH3mQN5XBaf/k72Ao48YRqoP0wRMFlw06gBPxcYsgRoe72yco2RdcqvK+EM6eb/W0Z4fFaL6Srz/9zxiylrLNHEioPkuhUqS7KZUY0B9SKbMOhHSL/i9PaqAR2IudECGCYrLcv+/tYFziMwVTUAfIvbo8itCoKNBCBM64+H4yuJogrZTiMLLet/ojLU5/kSva8FAxDgSFGHIDA1cD8mmyPkh/x5La0kFypLqVMVSdNEuTxaj6o4688z3bqfQ2akDu4UM4habpq9hU0/YTT4PUlYRQuhT6/iK4V1Fp1ysVnog32T+HSvTUq5G0w/t9HuAPUiYKik3e53aa9Jw6ahX/gkH1+jpZBjUbYTA3gflh3i+rR1cdzgIk7J3KD8lAKOhUijdnafDU1hfsGlp9azD+hryExcE4o55PvhiQfuEEQgrtg1G2q0I1ekLfMW2yb9vblOixY2W0FGT5e3Nyi67vzgNTRdFb3Zildy3QmPKZ6NGIZKhFHDQz5lgitrhdTPzgvMLHEY7+RfvcqCYX3eNf39vVS6xSYJD3OTGiXja5ZfgotXESljB8lgo1m5U4w/t1afsWH+VDN1cplVUvr5igNi9hDSZdG8+njiiH532v2'
MAC_SALT = '403349eb577b056c9fdfabb033eb4c4cb2e9347fda2422dcc0f9034417d29df8'
MAC = 'd986925d97c78aa25bea89a15cb2c35b65257dd60e2e4f458892298c99b852fb'

def main():
    if not sys.stdin.isatty():
        raise ValueError('Bitte in einem interaktiven Terminal starten.')
    if not shutil.which('openssl'):
        raise ValueError('OpenSSL fehlt. Zuerst: sudo apt install openssl')
    password = getpass.getpass('Entsperrcode (unsichtbar), dann Enter: ').strip().replace('-', '').replace(' ', '').lower()
    encrypted = base64.b64decode(CIPHERTEXT)
    key = hashlib.pbkdf2_hmac('sha256', password.encode(), bytes.fromhex(MAC_SALT), 200000)
    if not hmac.compare_digest(hmac.new(key, encrypted, hashlib.sha256).hexdigest(), MAC):
        raise ValueError('Entsperrcode falsch; nichts gespeichert.')
    read_fd, write_fd = os.pipe()
    os.write(write_fd, (password + '\n').encode())
    os.close(write_fd)
    try:
        result = subprocess.run(['openssl', 'enc', '-d', '-aes-256-cbc', '-pbkdf2', '-iter', '200000', '-pass', f'fd:{read_fd}'], input=encrypted, stdout=subprocess.PIPE, stderr=subprocess.PIPE, pass_fds=(read_fd,))
    finally:
        os.close(read_fd)
    if result.returncode:
        raise ValueError('Entschluesselung fehlgeschlagen; nichts gespeichert.')
    credentials = json.loads(result.stdout.decode('utf-8'))
    token = credentials.get('access_token', '')
    if not isinstance(token, str) or not token or any(c.isspace() for c in token):
        raise ValueError('Ungueltiger Token; nichts gespeichert.')
    if credentials.get('page_id') != '1411966515325246' or credentials.get('token_type') != 'PAGE':
        raise ValueError('Falsche Facebook-Seite; nichts gespeichert.')
    folder = Path.home() / '.config' / 'breachline-agent'
    if folder.is_symlink():
        raise ValueError('Konfigurationsordner darf kein symbolischer Link sein.')
    folder.mkdir(parents=True, exist_ok=True, mode=0o700)
    folder.chmod(0o700)
    fd, temporary = tempfile.mkstemp(prefix='.instagram-', dir=folder)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            os.fchmod(stream.fileno(), 0o600)
            json.dump(credentials, stream, indent=2)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, folder / 'facebook.json')
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    print('Facebook-Seiten-Token lokal gespeichert (0600). Kein API-Test ausgefuehrt.')
    try:
        Path(__file__).resolve().unlink()
        print('Lokale Import-Datei geloescht. Nicht erneut aus Git wiederherstellen.')
    except OSError:
        print('Import-Datei bitte manuell loeschen.')

if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, UnicodeError, TypeError, AttributeError):
        print('Import fehlgeschlagen: Code, OpenSSL oder Schreibrechte pruefen. Datei bleibt erhalten.', file=sys.stderr)
        raise SystemExit(1)
    except (EOFError, KeyboardInterrupt):
        print('Abgebrochen; Datei bleibt erhalten.', file=sys.stderr)
        raise SystemExit(1)
