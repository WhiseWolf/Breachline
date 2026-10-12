# Neuer lokaler Jarvis-Scheduler

## Systemaudit-Korrektur 2026-10-12
Checkpoint-Sicherung und fachliche CURRENT_WORK-Änderung sind getrennt. Ohne fachliche Übergabe lautet der Rückkehrstatus HANDOFF_REQUIRED; der nächste Zyklus erhält strukturierte Aktions-/Artefaktbelege und holt die Übergabe nach. Kein automatischer fachlicher Erfolg aus einer Dateiänderung. Der letzte vollständige Tool-Austausch bleibt beim Rollen im aktiven Kontext. Die unveränderte Regel-/Tool-Präfixgröße wird anhand gemeldeter Prompt-Nutzung mit Reserve geplant; neue Inhalte behalten die konservative Schätzung.

Der bestehende shell_exec-Ausführungspfad samt Sicherheitsrichtlinie wird um eine Exitstatusprüfung ergänzt. Rust-Ausgabeheader und Metadaten müssen konsistent sein. Widersprüchliche oder fehlende Prozessbelege werden nicht als Erfolg geführt. Unklare Schreibwirkungen bleiben blockiert; kein automatisches Replay. Checkout-/Switch-Befehle durch den Scheduler werden vor Ausführung blockiert, der Steuerungs-Checkout vor/nach Shell-Ausführung geprüft. Git-Worktrees bleiben für Spiele verfügbar. Das ist kein allgemeiner Shell-Sandboxersatz.

### Vorhandenen Ubuntu-Stand übernehmen
1. Im Scheduler-Terminal einmal Ctrl+C; auf die Meldung Scheduler stopped warten. Nicht Logs/Receipts löschen.
2. Den bestehenden Steuerungs-Checkout ohne Reset wieder auf agent-lab bringen. Git muss lokale Änderungen erhalten; bei Konflikten nichts erzwingen.
3. agent-lab aktualisieren und Offline-Briefings mit dem geprüften Helper übernehmen. Er sichert geänderte Briefings und verweigert unerkannte lokale Änderungen. Aktive Logs bleiben erhalten.

```bash
cd /home/pagi/breachline-agent
git -C repo switch agent-lab
git -C repo pull --ff-only origin agent-lab
python3 repo/runtime/sync_briefing.py
~/.openjarvis/.venv/bin/python -u repo/runtime/jarvis_loop.py
```

Abnahme: zwei echte aufeinanderfolgende Zyklen setzen einen bestehenden Artefakt-/Teststand fort; nächste Manifeste zeigen neue Scheduler-/Briefinghashes, reale Exitstatus und fachliche Übergabe. Mock-Tests bestätigen keinen lokalen Ollama-/Gameplay-Erfolg. Bestehende Prototypen zuerst inventarisieren; keine neuen Ordner durch den Nutzer anlegen und keine Mission zurücksetzen.

Dieser Scheduler verwendet `/home/pagi/.openjarvis/config.toml` als Runtime-Konfiguration.
Modell, Agent, Temperatur, max_tokens, max_turns und konfigurierte lokale Werkzeuge
werden daraus gelesen. Toollisten aus [agent] und [tools] werden zusammengeführt.
Die registrierten Basiswerkzeuge file_read, file_write und shell_exec werden explizit
ergänzt, wenn sie in der TOML-Liste fehlen. Keine neue config.toml wird erzeugt und
keine Laufgrenze erhöht. Die Container-Werkzeuge code_interpreter_docker
und docker_shell_exec werden für diese Host-Entwicklungsmission ausdrücklich
ausgeschlossen. Die TOML bleibt unverändert; der Ausschluss steht im Terminal
und unter excluded_host_incompatible_tools im Manifest.
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
- Rückkehrzyklen ohne erfolgreiche Erkenntnis-/Ausführungstools und geändertes
  CURRENT_WORK laufen mit einem bis 300 Sekunden begrenzten Backoff weiter. Nur think, calculator, file_write,
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
Passt der geschützte Kontext auch an der Obergrenze nicht, greift die unten
beschriebene geprüfte Kontextübergabe; ohne sicheren Checkpoint stoppt der Loop.
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

Ältere unterbrochene Läufe ohne action_receipts werden anhand gepaarter Start-/End-
Ereignisse und gespeicherter Resultate geprüft. Die Prüfung erzeugt ausschließlich
legacy_action_review.json; ursprüngliche Manifeste/Ergebnisse bleiben erhalten.
Bestätigte Rückgaben dürfen fortgesetzt werden, fehlende Rückgaben bleiben gesperrt.
Eine eng begrenzte Ausnahme erkennt beim code_interpreter_docker den DockerException-
Fehler "Error while fetching server API version" mit FileNotFoundError(2): dieser
entsteht beim Docker-Verbindungsaufbau vor containers.run, Status NOT_EXECUTED.
Jarvis darf danach eine kostenlose erlaubte Alternative nutzen. Docker-Timeouts,
Container-Ausführungsfehler und unbekannte Fehlermeldungen sind keine solche Ausnahme.
Das ist eine Prüfung des Ausführungsstatus, keine Bestätigung korrekter Inhalte und
keine automatische Wiederholung erfolgreicher Shell-Aktionen.

### Behebung des QuickPuzzle-Abbruchs (2026-10-11)

Der offizielle code_interpreter_docker startet `python -c` in einem Container mit
read_only=True, temporärem /tmp, standardmäßig ohne Netzwerk und **ohne Host-Mounts**.
`/home/pagi/breachline-agent/repo/quickpuzzle/index.html` kann dort nicht auf dem Host
geschrieben werden. docker_shell_exec benötigt dagegen einen aktiven TerminalBench-
Taskcontainer und ist ausdrücklich kein Host-Shell-Ersatz. Ein manuell auf Ubuntu angelegter Ordner behebt diesen Fehler
nicht. Neue Spieldateien über file_write mit create_dirs=true im autorisierten
Spiel-Worktree schreiben, mit file_read zurücklesen und mittels shell_exec mit
explizitem working_dir prüfen. Das Briefing für main/game-Zweige bleibt maßgeblich.

Beim Start prüft der Scheduler den vorhandenen letzten Run erneut. Nur ein gepaarter,
abgeschlossener Docker-Fehler mit vollständig gespeicherten FileNotFoundError-
Traceback darf als FAILED_ISOLATED geprüft werden. Dafür müssen die installierte
Konstruktor und execute-Methode der Docker-Implementierung den geprüften
AST-Fingerprints entsprechen. Docstrings, Beschreibungen und Kommentare sind
für diese Prüfung unerheblich. Die Factory wird ohne Ausführung entlang des
Docker-Zweigs geprüft: ausschließlich Standardinstanziierung tool_cls() ohne
Argumente oder weitere ausgeführte Schritte. Unbenutzte Memory-/Channel-Zweige
dürfen zwischen Versionen variieren. Unbekannte Ausführungsänderungen, Timeout,
fehlende Rückgabe, fremder Artefaktpfad oder weitere unklare
Host-/Shell-/Social-Aktion bleibt gesperrt. Es wird kein Container ausgeführt.

Die Fingerprints nutzen portable-v1: einen eigenen AST-Serializer mit einheitlicher
Behandlung leerer Felder. Das behebt die reproduzierte Fehlablehnung unter Python
3.13/3.14, deren ast.dump standardmäßig leere Listen auslässt. Die geprüften
Konstruktor-/execute-Inhalte und das Isolationskriterium bleiben maßgeblich.
Die Review-Datei nennt das verwendete Format. Regressionen laufen unter Python
3.12, 3.13 und 3.14 mit demselben offiziellen Methodenfixture.

Die Prüfung schreibt isolated_action_review.json mit Quelldigest, Ergebnisdigest,
Original-Receipt-Digest und geprüften Aktionen. Originale Manifeste, Ergebnisse
und action_receipts.json bleiben unverändert. Der nächste Zyklus erhält den
Fehler-/Prüfverweis und wählt einen korrigierten Host-Schritt; das alte Skript wird
nicht wiederholt. FAILED_ISOLATED ist kein erfolgreicher Spielbau.

Nach dem Update mit den obigen pull-/Startbefehlen sollte beim gezeigten Fehler
RECOVERY ISOLATED_FAILURE_REVIEW erscheinen. Falls die installierte Implementierung
abweicht, erklärt RECOVERY SOURCE_CHECK_BLOCKED den konkreten Grund und bei
Methodenänderungen den tatsächlichen AST-Digest samt Quelldatei. Fehler bei
Ereignispaarung oder Resultaten melden RECOVERY EVENTS_BLOCKED bzw.
RECOVERY RESULT_BLOCKED. Eine konkrete Prüfung bleibt dann erforderlich;
keine Protokolle löschen.
Bei einem erneuten Fehler speichert failure_snapshot.json die tatsächliche
Nachrichtenhistorie und Aktionsbelege, auch wenn ein normaler Checkpoint gesperrt
ist. Zurückgegebene Antwort/Tool-Ergebnisse werden vor der Abschlussprüfung gesichert.
Fehler ohne Bus-Ereignis werden pro Aufruf abgeglichen, nicht nur pro Werkzeugname.

Audit, Ursachen, Testumfang und Grenzen: [AUDIT_2026-10-11.md](AUDIT_2026-10-11.md).

Offizielle Grundlagen:
- https://github.com/open-jarvis/OpenJarvis/blob/main/src/openjarvis/cli/ask.py
- https://github.com/open-jarvis/OpenJarvis/blob/main/src/openjarvis/core/config.py
- https://github.com/open-jarvis/OpenJarvis/blob/main/src/openjarvis/engine/ollama.py
- https://github.com/open-jarvis/OpenJarvis/blob/main/src/openjarvis/tools/code_interpreter_docker.py
- https://github.com/open-jarvis/OpenJarvis/blob/main/src/openjarvis/tools/file_write.py
- https://github.com/open-jarvis/OpenJarvis/blob/main/src/openjarvis/tools/shell_exec.py

## Tests

```bash
python3 -m unittest discover -s tests -p 'test_jarvis_loop.py'
```

## Regelmäßige Sicherung und rollender Kontext

Vor dem fünften Modellaufruf und danach alle vier Aufrufe speichert der Scheduler
die tatsächliche Nachrichtenhistorie und Aktionsbelege als checkpoint-NNNN.json.
Zusätzlich sichert er bei Zyklusrückkehr. CURRENT_WORK erhält einen atomar ersetzten,
begrenzten Scheduler-Abschnitt; der fachliche Arbeitsstand darüber bleibt erhalten.
Das benötigt keinen file_write-Aufruf des Modells. Assistant-Aussagen im Checkpoint
sind ausdrücklich ungeprüft, nicht als bestätigter Fortschritt ausgewiesen.

Vor jeder Anfrage wird Platz für die Antwort und eine adaptive Kontextreserve
eingeplant. Bei knapper Reserve werden vollständig abgeschlossene Assistant-/Tool-
Dialoge zuerst archiviert und dann im laufenden Nachrichtenverlauf durch einen
kurzen Artefaktverweis mit den jüngsten Assistant-Aussagen ersetzt. Alle initialen
Nachrichten und spätere System-/Nutzeranweisungen bleiben erhalten. Tool-IDs müssen
vollständig gepaart und Schreibwirkungen geklärt sein; keine Werkzeugwiederholung.
RECOVERY CHECKPOINT_SAVED und RECOVERY CONTEXT_ROLL zeigen die tatsächlichen Schritte.
Die Tokenplanung bleibt eine konservative Schätzung, keine exakte Tokenisierung.

## Verbleibende Kontextgrenzen

Wenn auch die begrenzte Vergrößerung und Archivierung langer Werkzeugausgaben
nicht ausreichen, wird die blockierte Anfrage in `context_overflow.json` gesichert.
Nur bei geändertem CURRENT_WORK, einem erfolgreichen Schreibwerkzeug und vollständig
geklärten Aktionsbelegen endet der Zyklus als `CONTEXT_HANDOFF`. Nach dem normalen
Intervall lädt ein frischer Agent die aktuellen Briefings und aktiven Logs sowie den
Verweis auf die vorige Ausführung. Werkzeuge werden dabei nicht erneut abgespielt.
Der Status bestätigt weder die Qualität des Checkpoints noch eine abgeschlossene
Recherchephase. Jarvis muss Belege und vorgeschlagene nächste Schritte erneut gegen
Briefing und Freigaben prüfen. GitHub-Pages-Testhosting ist im dokumentierten Umfang
der Nutzerfreigabe vom 2026-10-11 erlaubt; der Scheduler erteilt keine zusätzlichen
Rechte und richtet Pages nicht selbst ein.

Kontextübergaben haben keine feste Drei-Zyklen-Pause mehr. Der rollende Kontext
verhindert den bisherigen Abbruch durch anwachsende abgeschlossene Tool-Historie.
Bei nicht kürzbaren übergroßen Anweisungen oder ungeklärten Schreibaktionen kann
weiterhin eine konkrete Prüfung nötig sein. Passt bereits der
vollständige Startkontext nicht in die Obergrenze, ist eine geprüfte Verdichtung der
aktiven Logs nötig; Regeln werden nicht abgeschnitten. `--once` führt auch bei einer
Kontextübergabe keinen weiteren Zyklus aus. Kein Reset bestehender Logs.


## Instagram-Token lokal einrichten

Nach der Token-Erstellung in Meta for Developers auf Ubuntu starten:

```bash
python3 /home/pagi/breachline-agent/repo/runtime/instagram_setup.py
```

Das Skript benoetigt nur Python 3, fragt den Token unsichtbar im interaktiven
Terminal ab und speichert ihn atomar unter
`~/.config/breachline-agent/instagram.json` (Ordner 0700, Datei 0600).
Es ist fuer das Konto `breachlineagent` mit der in Meta angezeigten ID
`17841416428554896` vorbereitet. Ein vorhandener Token wird nur nach Rueckfrage
ersetzt. Kein Token in Kommandoargumente, GitHub, Briefings oder Logs kopieren.

Das Skript speichert nur: Es sendet keine Netzwerkanfrage, prueft weder Gueltigkeit
noch Berechtigungen und schaltet keine Jarvis-Integration frei. API-Test, sichere
Token-Erneuerung und Runtime-Anbindung sind separate Schritte. Die Speicherung ist
lokal mit Dateirechten geschuetzt, nicht verschluesselt.
