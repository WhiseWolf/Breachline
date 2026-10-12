#!/usr/bin/env python3
"""Read-only check of the locally imported Breachline Facebook Page token."""
import json
from pathlib import Path
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, build_opener, HTTPRedirectHandler

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

def main():
    token = ''
    try:
        path = Path.home() / '.config/breachline-agent/facebook.json'
        config = json.loads(path.read_text(encoding='utf-8'))
        token = config['access_token']
        if not isinstance(token, str) or not token or any(c.isspace() for c in token):
            raise ValueError()
        if config.get('page_id') != '1411966515325246' or config.get('token_type') != 'PAGE':
            raise ValueError()
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        print('FEHLER: Facebook-Konfiguration fehlt oder ist ungueltig. Import-Skript ausfuehren.')
        return 1
    request = Request('https://graph.facebook.com/v26.0/me?' + urlencode({
        'fields': 'id,name', 'access_token': token
    }), headers={'Accept': 'application/json', 'User-Agent': 'BreachlineAgent-FacebookCheck/1.0'})
    try:
        with build_opener(NoRedirect()).open(request, timeout=30) as response:
            data = json.load(response)
        if not isinstance(data, dict) or str(data.get('id')) != '1411966515325246' or data.get('name') != 'Breachline Agent':
            print('FEHLER: Token gehoert nicht zur bestaetigten Facebook-Seite Breachline Agent.')
            return 1
        print('OK: Facebook-Seite Breachline Agent verifiziert.')
        print('Seiten-ID: 1411966515325246')
        print('Meta-Debugger beim Export: PAGE, gueltig, Token-Ablaufdatum Nie.')
        print('Datenzugriffsfrist beim Export (Unix): ' + str(config.get('data_access_expires_at', 'UNKNOWN')))
        print('Dieser Test liest nur die Seitenidentitaet. Keine Veroeffentlichung ausgefuehrt.')
        return 0
    except HTTPError as error:
        raw = error.read(8192).decode('utf-8', errors='replace').replace(token, '[TOKEN]')
        print('Facebook HTTP ' + str(error.code))
        print(raw[:1500] or '(leere Fehlerantwort)')
    except (URLError, OSError, ValueError, TypeError):
        print('FEHLER: Verbindung oder API-Antwort ungueltig; Internet und Systemzeit pruefen.')
    return 1

if __name__ == '__main__':
    sys.exit(main())
