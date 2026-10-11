#!/usr/bin/env python3
"""One-time encrypted Instagram import. Requires Python 3 and OpenSSL."""
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

CIPHERTEXT = 'U2FsdGVkX18qwTNxllXkEZsKGIbIkMVsmX14HK+CNPDdCi1O61e7FqYzdwWHHXFaK6LGttJuGsQPF/g2UOvvqP9ny08W7/G/kMaTl9UlWVKnjJt9zmgwuxwcoKLTxYOL23yx/HMVN4raXS7E0rYn6uTjyX4W+kBuKa28luIjdbK/1ue7D7cXe1lCUn/cLVyp27msq4g+zhwupGsvotFoSi7w4Rji1nUIslrV5k6a6wRd0N76Cky1F6bJPXBrdYYfvzQp711vmJGr9irkcZQCdw=='
MAC_SALT = '499a6d0baa61af94c1a007e8b055bb699a6abf9725bcea9d0093dd7af8e25d25'
MAC = '9042941bfe0f765679c406cfd3ba3e8a12da2712a2649fe0f2d9456bc327d24d'

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
    token = result.stdout.decode('utf-8').strip()
    if not token or any(c.isspace() for c in token):
        raise ValueError('Ungueltiger Token; nichts gespeichert.')
    folder = Path.home() / '.config' / 'breachline-agent'
    if folder.is_symlink():
        raise ValueError('Konfigurationsordner darf kein symbolischer Link sein.')
    folder.mkdir(parents=True, exist_ok=True, mode=0o700)
    folder.chmod(0o700)
    fd, temporary = tempfile.mkstemp(prefix='.instagram-', dir=folder)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            os.fchmod(stream.fileno(), 0o600)
            json.dump({'access_token': token, 'instagram_user_id': '17841416428554896', 'username': 'breachlineagent'}, stream, indent=2)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, folder / 'instagram.json')
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    print('Instagram-Token lokal gespeichert (0600). Kein API-Test ausgefuehrt.')
    try:
        Path(__file__).resolve().unlink()
        print('Lokale Import-Datei geloescht. Nicht erneut aus Git wiederherstellen.')
    except OSError:
        print('Import-Datei bitte manuell loeschen.')

if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, UnicodeError):
        print('Import fehlgeschlagen: Code, OpenSSL oder Schreibrechte pruefen. Datei bleibt erhalten.', file=sys.stderr)
        raise SystemExit(1)
    except (EOFError, KeyboardInterrupt):
        print('Abgebrochen; Datei bleibt erhalten.', file=sys.stderr)
        raise SystemExit(1)
