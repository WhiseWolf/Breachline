# Neuer lokaler Jarvis-Scheduler

Dieser Scheduler verwendet `/home/pagi/.openjarvis/config.toml` als Runtime-Konfiguration.
Modell, Agent, Temperatur, max_tokens, max_turns und konfigurierte lokale Werkzeuge
werden daraus gelesen. Toollisten aus [agent] und [tools] werden zusammengeführt.
Die registrierten Basiswerkzeuge file_read, file_write und shell_exec werden explizit
ergänzt, wenn sie in der TOML-Liste fehlen. Keine neue config.toml wird erzeugt und
keine Laufgrenze erhöht.
`briefing/agent_config.json` bestimmt ausschließlich die aktiven Arbeitsdateien.

## Installation und Start auf dem vorhandenen Ubuntu

Jarvis und der alte Scheduler sind zuvor gestoppt worden. Im Checkout `agent-lab`:

```bash
git -C /home/pagi/breachline-agent/repo pull --ff-only origin agent-lab
```

Keine Briefings/Logs erneut löschen oder Startvorlagen darüberkopieren.
Der neue Scheduler liest die bereits übernommenen Offline-Dateien.

```bash
cd /home/pagi/breachline-agent
~/.openjarvis/.venv/bin/python -u repo/runtime/jarvis_loop.py
```

Dieser Interpreterpfad stammt aus dem bisherigen Setup; falls er nicht existiert,
den tatsächlich installierten OpenJarvis-Python-Interpreter verwenden. Nicht in eine
andere Umgebung installieren und nicht erneut Ubuntu einrichten.
Einmaliger Lauf: gleicher Befehl mit `--once`. Stoppen: Ctrl+C.
Für das vorhandene tmux den gleichen Befehl in einer neuen Sitzung starten:

```bash
tmux new -s jarvis-new
```

Danach den Python-Aufruf ausführen. Ablösen: Ctrl+B, dann D.
Zurückkehren: `tmux attach -t jarvis-new`.
Es wird hier kein Boot-Autostart eingerichtet.

## Ablauf

- Ein Prozess, exklusiver Lock; keine überlappenden Zyklen dieses Schedulers.
- Pro Zyklus neue Agentinstanz, Pflichtbriefings vollständig in Ladefolge und aktive
  Log-Dateien. Es werden keine alten Scheduler-Datenbanken oder Outcomes eingelesen.
- Modellaufruf erhält den vollständigen Kontext. Manifest enthält Dateihashes,
  Runtime-Einstellungen, Systemzeiten und tatsächlichen Rückkehrstatus.
- Historische Memory-Injection, Persona-Dateien und alte Memory-Tools werden nur in
  dieser Laufkonfiguration ausgeschlossen; die bestehende TOML bleibt unverändert.
- Lokales Ollama ausdrücklich gewählt; keine automatische Cloud-Modellauswahl.
- Bestehende OpenJarvis-Sicherheitsrichtlinie bleibt aktiv. Für die im Workspace
  autorisierte Toolarbeit wird der gleiche Tool-Aufrufpfad wie in der CLI verwendet.
  Die Constitution/Freigaben bleiben die Regelautorität, keine blanket Freigabe für
  Posts, Konten, Veröffentlichungen oder Systemänderungen.
- Runtime-Prompts aus alten Missionen werden nicht als neuer Auftrag verwendet;
  der aktive Auftrag steckt im vollständigen neuen Kontextpaket.
- Pause 60 Sekunden nach Rückkehr, keine feste Forschungsphase oder Ideenzahl.
- Drei Rückkehrzyklen ohne erfolgreiche Erkenntnis-/Ausführungstools und geändertes
  CURRENT_WORK pausieren die Schleife. Nur think, calculator, file_write,
  apply_patch und git_commit zählen für sich nicht als Erkenntnisfortschritt.
- `SCHEDULER_WAIT` als letzte Antwortzeile pausiert, wenn keine sinnvolle erlaubte
  unabhängige Arbeit verbleibt. NEEDS_USER ist ansonsten kein globaler Stoppschalter.

## Voraussetzungen und Grenzen

Die konfigurierte Agentklasse muss Werkzeuge unterstützen; `operative` ist geeignet.
Der Scheduler ergänzt `file_read`, `file_write`, `shell_exec` aus der lokalen Registry.
Sind deren Implementierungen nicht registriert, stoppt er mit dem tatsächlichen Fehler.
Zusätzlich werden apply_patch, git_status, git_diff, web_search und web_fetch aktiviert,
soweit diese Namen lokal registriert sind. Websuche nutzt ausdrücklich duckduckgo,
keine API-Key-basierte automatische Auswahl. Browser-/Blender-Installation ist damit
nicht bestätigt; diese Fähigkeiten kann der Agent über shell_exec projektlokal
einrichten und muss sie durch echte Tests belegen.
Weitere konfigurierte registrierte Werkzeuge werden übernommen. Unbekannte Tools
werden als Fehler angezeigt und nicht lautlos verworfen. MCP-only Tools werden von
diesem ersten Scheduler nicht unterstützt: dieser Adapter folgt dem lokalen CLI-
Registry-Aufrufpfad und prüft seine Werkzeugnamen ausdrücklich.

Kontextfenster: standardmäßig 32768 Tokens, über `JARVIS_NUM_CTX` oder `--num-ctx`
einstellbar. Das ist der Scheduler-Kontextumfang, kein neuer max_tokens/max_turns-Wert.
Vor jedem Modellaufruf erfolgt eine konservative Größenprüfung (kein exakter Tokenizer).
Lange Tool-/Assistant-Ausgaben werden vor dem Modellaufruf vollständig als Run-
Artefakte gespeichert. Der Modellkontext erhält eine markierte Kopf-/Endansicht
mit Dateipfad. Bei Kontextdruck wird diese Ansicht weiter verkleinert; Tool-Call-IDs
und die Reihenfolge bleiben erhalten. Die ursprüngliche Agenthistorie bleibt intakt.
User-/System-Nachrichten mit Pflichtbriefing und aktivem Auftrag werden nicht gekürzt.
Passt selbst dieser Kontext mit Tool-Call-Protokoll nicht, wächst das angeforderte
Fenster in 8192er-Schritten bis maximal 49152 (`--max-num-ctx`). Die Anpassung bleibt
für weitere Zyklen dieses Prozesses erhalten; max_tokens/max_turns bleiben unverändert.
Mit `--max-num-ctx 32768` lässt sich Wachstum deaktivieren. Es gibt keine unbegrenzte
Erhöhung, Modellwechsel oder automatische RAM-/GPU-Konfiguration. Ein größeres
Fenster kann auf dieser Hardware deutlich mehr Speicher und Zeit benötigen.
Passt der geschützte Kontext auch an der Obergrenze nicht, stoppt der Loop.
Aktive Logs knapp halten, ausführliche Evidenz in Artefakten mit Verweisen speichern.
Ollama/Modell muss dieses Kontextfenster unterstützen; der lokale Erstlauf ist noch
nicht abgenommen. Die Größenprüfung beweist nicht, dass der Modellserver intern
niemals truncatet; dafür ist die tatsächliche lokale Runtime-Abnahme nötig.

Die OpenJarvis-CLI-Funktion `_run_agent` ist eine interne Schnittstelle. Der Code
folgt dem am 2026-10-11 gelesenen offiziellen Stand. Eine abweichende installierte
Version kann einen Anpassungsbedarf melden; es wird keine Funktionalität erfunden.

## Beobachtung und Nachweis

Terminal: Laufstart, Modellaufrufe und Tool-Ereignisse.
`logs/runs/<run-id>/`: manifest.json, input.md, model_calls.jsonl, events.jsonl,
answer.md und tool_results.json. Dies sind aktuelle Laufartefakte, kein Serverbackup.
input.md enthält Briefing/aktive Logs, keine Kopie der privaten config.toml.
Tool-Ergebnisse können sensible Daten enthalten: nicht automatisch öffentlich pushen.

`CYCLE_RETURNED` bedeutet erfolgreiche Tool-Rückgaben plus verändertes CURRENT_WORK;
das beweist keine Marktvalidierung oder menschliche Retention. Inhaltliche Abnahme
erfordert tatsächlich gespeicherte Quellen/Tests, Gegenprüfung und passenden Handoff.
Die Tests prüfen Loader, Fortsetzung, Ausschlüsse, Wiederholungen, Aktionsbelege und
Engine-Weitergabe sowie zwei vollständige Scheduler-Zyklen mit Testdoubles. Sie
führen keinen echten lokalen Jarvis/Ollama-Lauf aus.

## Begrenzte automatische Fehlerbehandlung

Nur Modell-Inferenz wird wiederholt, niemals der ganze Agentenlauf oder ein
Werkzeug. Verbindungs-/Timeoutfehler und vorübergehende HTTP-Statuscodes
408/429/502/503/504: höchstens zwei Wiederholungen pro Anfrage nach 10 und 30 Sekunden,
höchstens sechs Wiederholungen pro Arbeitszyklus. `--inference-retries 0` deaktiviert
sie. Die Arbeitshistorie einschließlich bereits ausgeführter Werkzeuge bleibt erhalten.
Bekannte Konfigurations-, Sicherheits-, Rechte-, Speicher- und andere unbekannte
Fehler werden nicht durch Wiederholung kaschiert. Keine Cloud-Fallbacks, keine
Dienst-/Systemneustarts, kein chmod/chown und keine Änderung der Constitution.

`action_receipts.json` dokumentiert Werkzeugstart/-ende und Rückgabestatus. Ein
fehlgeschlagenes oder nicht abgeschlossenes potenziell schreibendes Werkzeug
blockiert weitere Modellaufrufe und den nächsten manuellen Neustart zur Prüfung.
Unbekannte Tools und Shell-/Docker-/Codewerkzeuge gelten vorsorglich als potenziell
schreibend. Bekannte Lesewerkzeuge sowie HTTP mit explizitem GET/HEAD/OPTIONS dürfen
scheitern, ohne unabhängige Recherche zu blockieren. Jarvis kann erlaubte Alternativen
selbst wählen; diese Werkzeuge werden nicht vom Scheduler automatisch wiederholt.
Ein Erfolgssignal ist keine Garantie für korrekte Inhalte. Aktionsbelege dürfen nicht
gelöscht werden, um den Schutz zu umgehen; unklare Auswirkungen zuerst prüfen.

Der nächste Zyklus bekommt zusätzlich einen Verweis auf die Laufartefakte der
gleichen Mission. Er muss tatsächliche Ergebnisse vor Wiederholung überprüfen,
besonders wenn CURRENT_WORK nach einem Abbruch noch NOT_STARTED zeigt. Es werden
keine alten Missionsarchive als neuer Auftrag eingebracht.
`recovery.jsonl` zeigt Kontextanpassungen und Wiederholungen. Keine automatischen
Uploads dieser Artefakte. Fehlerbehandlung ist begrenzt und ersetzt weder die
Briefing-Regeln noch eine lokale Runtime-Abnahme.

Offizielle Grundlagen:
- https://github.com/open-jarvis/OpenJarvis/blob/main/src/openjarvis/cli/ask.py
- https://github.com/open-jarvis/OpenJarvis/blob/main/src/openjarvis/core/config.py
- https://github.com/open-jarvis/OpenJarvis/blob/main/src/openjarvis/engine/ollama.py

## Tests

```bash
python3 -m unittest discover -s tests -p 'test_jarvis_loop.py'
```
