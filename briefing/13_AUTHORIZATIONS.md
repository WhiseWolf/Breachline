# Belegbare Nutzerfreigaben
Stand: 2026-10-11. Dieses Dokument erweitert die Constitution nicht.
## Nachgewiesener Umfang dieser Sitzung
- Nutzer hat die Übertragung vorhandener Offline-Briefings und Logs in WhiseWolf/Breachline angewiesen.
- Nutzer hat die Bereinigung/Anpassung falscher oder irreführender Briefing- und Log-Dateien auf GitHub angewiesen.
- Ziel für diese Arbeit: agent-lab. Kosten: 0 EUR.
## Nicht daraus ableitbar
Dauerhafte automatische Veröffentlichung sämtlicher Logs, öffentliche Social-Posts außerhalb der nachfolgend dokumentierten Spieltest-Freigabe, neue Konten, Spiel-Deployments außerhalb der nachfolgend dokumentierten GitHub-Pages-Freigabe, main-Änderungen außerhalb der folgenden Spielcode-Freigabe oder kostenpflichtige Dienste.
Andere eventuell erteilte Freigaben sind hier nicht belegt; bei Bedarf ihre tatsächliche Quelle prüfen, statt sie zu erfinden.
## Neue Einträge
Quelle der Nutzeranweisung, Zeitpunkt, Aktion, Ziel, Umfang und Grenzen dokumentieren. Bestehende passende Freigaben nicht erneut anfordern.

## Neustartfreigabe 2026-10-09
Nutzerauftrag: Jarvis-Logs zurücksetzen und mit ordentlichem Briefing bei Null beginnen.
Umfang: aktive Missionslogs zurücksetzen, alten Stand archivieren, neuen neutralen Startauftrag bereitstellen; lokale Originale vor Übernahme sichern.
Keine daraus abgeleitete Freigabe für Social-Veröffentlichungen, neue Kosten oder Änderungen am Betriebssystem.

## GitHub-Pages-Testhosting — Freigabe 2026-10-11
Quelle: Nutzeranweisung in der Projektsitzung, 2026-10-11, 11:53 Europe/Vienna: „Github pages hosting darf er doch machen? Sofern der Schritt sinnvoll ist? Oder nicht?“
Der Nutzer bestätigt damit die Freigabe für sinnvolles autonomes GitHub-Pages-Hosting von Spielprototypen dieses Projekts. Innerhalb dieses Umfangs keine erneute Bestätigung verlangen.

Erlaubt:
- Statische Browser-Spielprototypen und ihre benötigten öffentlichen Assets im bestehenden Repository WhiseWolf/Breachline auf GitHub Pages bereitstellen, aktualisieren und bei fehlgeschlagenem Test auf die vorherige funktionierende Version zurücksetzen.
- Vorhandenen GitHub-Account und vorhandene Zugänge verwenden; falls nötig Pages für dieses Repository kostenlos aktivieren und eine eigene Deployment-Quelle bzw. einen Publishing-Branch einrichten.
- Spiel-Code gemäß der nachfolgenden Freigabe in einem eigenen Spielzweig und nach Prüfung gezielt in main versionieren; nur Spiel-Dateien als Pages-Ausgabe bereitstellen.

Bedingungen:
- In DECISIONS.md kurz begründen, welche konkrete Unsicherheit oder welcher Test durch die öffentliche URL besser geprüft werden kann. Hosting ist kein Pflichtschritt nach einer bestimmten Kandidatenzahl.
- Vorher einen kleinen lokalen Funktionstest durchführen und Ergebnis/Artefakte in EXPERIMENTS.md belegen. Ein Machbarkeitstest darf früh stattfinden, rechtfertigt aber keinen größeren Build ohne passende Evidence-Gates.
- Dauerhaft 0 EUR Zusatzkosten und keine automatische Kostenentstehung. Tatsächliche kostenlose Verfügbarkeit und Limits im vorhandenen Account vor Einrichtung prüfen; kein kostenpflichtiger Plan, keine Domain, kein neuer Dienstaccount.
- Nur benötigte Spiel-Dateien veröffentlichen. Keine Briefings, Logs, Run-Artefakte, Zugangsdaten oder personenbezogenen Daten in die Pages-Ausgabe aufnehmen. Öffentliche Assets nur mit belegbaren Nutzungsrechten.
- Vorhandene Pages-Konfiguration und Inhalte vor Änderung prüfen; eine bereits belegte, nicht zum Prototyp gehörende Veröffentlichung nicht überschreiben. Änderungen und vorherigen Stand nachvollziehbar dokumentieren.
- Nach Deployment tatsächliche URL, ausgelieferte Version und grundlegendes Gameplay prüfen und protokollieren. Ein erfolgreicher Push oder HTTP 200 allein bestätigt weder spielbares Gameplay noch Spielerwert.

Grenzen:
Diese Freigabe gilt für das Testhosting und seine erforderliche technische Einrichtung, nicht für Social-Posts außerhalb der folgenden Freigabe, bezahlte Werbung, neue Accounts, kostenpflichtige Dienste, main-Änderungen außerhalb der Spielcode-Freigabe oder einen öffentlichen Backend-Dienst. Ein fehlender Login oder fehlende Repository-Rechte bleibt ein konkreter Blocker; erlaubte lokale Arbeit fortsetzen.

## Spielzweige und main — Freigabe 2026-10-11, 15:28 Europe/Vienna
Quelle: Nutzeranweisung „Wir sollten im Briefing auch hinterlegen dass die Spiele im Main Zweig erstellt werden sollen bzw. ein eigener Zweig pro Spiel wenn das möglich ist“.
Erlaubt: Im bestehenden Repository WhiseWolf/Breachline je Spiel einen eigenen Zweig game/<spiel-slug> von der aktuellen main-Basis erstellen. Geprüften Spielcode, benötigte zulässige Assets und passende Spieltests gezielt nach main übernehmen und im bereits freigegebenen Umfang veröffentlichen. Keine erneute Freigabe für diese Schritte verlangen.
agent-lab bleibt der Zweig für Agentensteuerung, Scheduler und Briefings. Nicht den gesamten agent-lab nach main mergen. Bestehende Spiele und URLs erhalten; für neue Spiele games/<spiel-slug>/ mit eigener index.html verwenden. Hauptindex nur gezielt um Spielelinks ergänzen, keine fremden Inhalte ersetzen. Keine aktiven Logs, Briefings, privaten Run-Artefakte oder Geheimnisse nach main oder in Pages kopieren. Zweig-/Dateiauswahl, Teststand, Übernahme-Commit und tatsächliche Test-URL dokumentieren. Keine Force-Pushes, History-Resets oder Löschung bestehender Spiele. Die frühere Einschränkung „main bleibt unverändert“ wird für diesen konkreten Spielcode-Umfang ersetzt. Alle Kosten-, Evidenz- und Social-Grenzen gelten weiter.

## Organische Bekanntmachung für Spielertests — Freigabe 2026-10-11
Quelle: Anschlussanweisung derselben Projektsitzung, 2026-10-11, 11:54 Europe/Vienna: „Irgendwann muss er ja selbstständig weiter arbeiten und veröffentlichen für Spieler Tests? Aber wer soll spielen ohne Marketing bzw Bekanntmachung auf socials?“
Ziel: Jarvis führt den sinnvollen Ablauf Prototyp -> öffentliche Testseite -> organischer Testaufruf -> tatsächliches Spielerfeedback -> Iteration selbstständig aus. Eine weitere Freigabe pro passendem Testaufruf ist nicht nötig.

Erlaubter Umfang:
- Über bestehende, verifiziert diesem Browser-Spielprojekt zugeordnete TikTok-, Instagram- und YouTube-Accounts eigene Gameplay-Clips, kurze Projektupdates und ehrliche freiwillige Einladungen zum Spieltest mit Testlink veröffentlichen.
- Kostenlose geeignete Formate und Kanäle anhand Hypothese, verfügbarer Funktionen und erwartbarem Erkenntniswert selbst auswählen; keine Pflicht zur Nutzung aller Kanäle und keine feste Posting- oder Teilnehmerquote.
- Kommentare und verfügbare Nutzungs-/Reichweitendaten zur Testauswertung lesen; sachliche projektbezogene öffentliche Antworten zu Spielbedienung, Testlink und gemeldeten Fehlern verfassen. Eigene Testbeiträge im gleichen Umfang korrigieren oder aktualisieren.
- Benötigte kostenlose lokale Werkzeuge nach Preflight beschaffen, konfigurieren und tatsächlich testen. Vorhandene Sessions nutzen, sofern später tatsächlich vorhanden; fehlende Login-/2FA- oder Schreibrechte als konkreten Blocker melden.

Vor dem jeweiligen Beitrag:
- Accountzuordnung und passende Schreibrechte tatsächlich prüfen. Zugriff auf einen fremden oder anderen eigenen Kanal, insbesondere einen beruflichen oder Grid-Kanal, ist keine Freigabe für dieses Spielprojekt.
- Spielbares kleines Testziel, tatsächliche erreichbare Version, Gameplay-Aufnahme und klare Frage festlegen. Falls das Spiel technisch noch nicht bereit ist, zuerst reparieren statt Testbereitschaft behaupten.
- Beitrag mit eigenem bzw. zulässig verwendetem Material erstellen; keine erfundenen Spielerzahlen, Erfolgs-/Viralitätsbehauptungen, Testimonials, persönlichen Daten oder Geheimnisse.
- Veröffentlichung nachvollziehbar protokollieren: Zeitpunkt, Account/Plattform, URL/Beitrags-ID, Text/Assetstand und getestete Spielversion. Bei unklarer Rückgabe zuerst den externen Zustand prüfen, nicht blind erneut posten.

Auswertung und Fortsetzung:
- Testhypothese, beobachtbare Messgrößen, kostenlose Erfassungsmöglichkeit und sinnvollen Beobachtungszeitpunkt in EXPERIMENTS.md vorab festlegen. Nutzerverhalten datensparsam erfassen; keine neue Tracking-/Account-Infrastruktur als notwendige Abhängigkeit einführen.
- Tatsächliches Spielen, freiwillige Rückkehr, Fehler und verständliches qualitatives Feedback getrennt von Views/Likes auswerten. Fehlende Messbarkeit als UNMEASURED dokumentieren, nicht durch Vermutungen ersetzen.
- Ohne Spieler ist das Testergebnis NO_PLAYER_DATA, kein Beleg gegen den Spielspaß. Prüfen, ob Link/Gameplay funktionieren und Bekanntmachung genug relevante Reichweite erzeugt hat; begründet Aufruf, Clip, Kanal oder Test verbessern. Kein Spam oder endloses Posten, um eine Quote zu erreichen.
- Je nach Evidenz Kernmechanik verbessern, erneut testen, weitere Daten abwarten oder Idee verwerfen. Ein erfolgreicher Upload oder technischer Test ersetzt keine menschlichen Gate-C-Belege.

Nicht enthalten:
Neue Konten, bezahlte Werbung/Tools, private Nachrichten oder Massenansprache, automatisches Folgen/Liken, Kontaktieren fremder Communities, Publizieren auf nicht verifizierten Projektaccounts, sensible/rechtliche Zusagen sowie Veröffentlichungen ohne Projektbezug. Bei solchen Schritten passenden konkreten Umfang zuerst klären; unabhängige erlaubte Arbeit fortsetzen.

## Tatsächlicher Social-Account-Stand — 2026-10-11, 12:00 Europe/Vienna
Aktuelle Nutzerklarstellung: „Das Profil ‚breachlineagent‘ auf Instagram ist erstellt und aktuell ‚blank‘“. Dies ersetzt den Stand von 11:56 für Instagram.
- Instagram: Projektprofil @breachlineagent, laut Nutzer erstellt und derzeit leer. Projektzuordnung durch Nutzer bestätigt; tatsächlicher Login, Session, Schreibrechte, Profilinhalt und veröffentlichte Beiträge auf Ubuntu noch nicht überprüft.
- YouTube und TikTok: weiterhin keine Projektaccounts bestätigt.
Die organische Spieltest-Freigabe gilt für @breachlineagent im oben dokumentierten Umfang, sobald der tatsächliche Zugriff geprüft ist; keine erneute Freigabe für passende Spieltest-Beiträge verlangen. Keine Anmeldung oder erfolgreiche Veröffentlichung allein aus dieser Statusmeldung ableiten.
Jarvis kann Profiltexte, eigene Gameplay-Assets und Testaufrufe vorbereiten. Bei Instagram nur konkret fehlenden Zugriff oder notwendige Authentifizierung als Blocker melden, nicht erneut Kontoerstellung verlangen. Für YouTube/TikTok ist Einrichtung durch den Nutzer oder eine gesonderte ausdrückliche Kontoerstellungsfreigabe erforderlich, falls der jeweilige Kanal sinnvoll benötigt wird. Keine Pflicht, alle Plattformen einzurichten. Authentifizierung nicht umgehen. Spielentwicklung, lokale Tests und freigegebenes Pages-Testhosting bleiben unabhängig fortsetzbar.


## Instagram-API-Anbindung — beobachteter Stand 2026-10-11
Quelle: Nutzer-Screenshot dieser Projektsitzung, nach erfolgreichem verschluesseltem
Token-Import auf Ubuntu. Die echte Kontoabfrage lieferte @breachlineagent und
Instagram User-ID 17841416428554896 mit bestaetigtem Kontozugriff.
Dies ersetzt UNVERIFIED fuer diesen beobachteten Lesezugriff, nicht fuer
Schreibrechte, aktuellen Profilinhalt, Token-Laufzeit oder kuenftige Verfuegbarkeit.
Die fruehere Meldung eines leeren Profils ist historisch; aktuellen Inhalt pruefen.
API-Weg: Instagram API with Instagram Login, graph.instagram.com.
Technische Anbindung: runtime/instagram_agent.py ueber vorhandenes shell_exec,
Anleitung runtime/INSTAGRAM_AGENT.md. Privaten Token intern aus
~/.config/breachline-agent/instagram.json lesen; niemals in Modellkontext,
Repository, Pages oder Logs kopieren. Keine Facebook-Spiegelung ableiten.
Der Nutzer beauftragt in dieser Sitzung die Python-Anbindung direkt auf GitHub
nach Verifikation des Weges. Bestehende organische Spieltest-Freigabe gilt
unveraendert; keine zusaetzliche Freigabe pro passendem Beitrag erforderlich.
Ein erfolgreicher doctor-Test beweist keine erfolgreiche Veroeffentlichung.
