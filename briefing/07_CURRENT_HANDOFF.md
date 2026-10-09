# CURRENT TECHNICAL HANDOFF – 2026-10-04

## Test-PC
- ASUS MAXIMUS VI HERO
- Intel Core i7-4770K
- 24 GB RAM
- NVIDIA GeForce GTX 1050 Ti 4 GB
- Windows 10 vorhanden
- UEFI-System
- SanDisk SSD 500 GB nominal

## Partitionierungsstand
Windows C: wurde erfolgreich auf ungefähr 337.75 GiB verkleinert.
Ungefähr 128 GiB sind auf der SanDisk für Ubuntu vorgesehen.

Ziel:
- eigene Ubuntu-EFI-Partition im freien Bereich
- Ubuntu-root ext4 im restlichen freien Bereich
- bestehende Windows-Partitionen und andere Festplatten nicht verändern

## Ubuntu-Medium
Ubuntu Server 26.04.1 LTS AMD64 ISO wurde geladen.

SHA-256:
CC8A95CDE20F6CED61A322420DE00F10CC3C90CED545DAA46CB9C1A117F1D927

Rufus 4.15 wurde geladen und die Windows-Code-Signatur als gültig geprüft.

## Netzwerkproblem Windows
Große Downloads brechen sporadisch ab.
Windows curl meldete:
SEC_E_INVALID_TOKEN (0x80090308)

Ein Resume-Loop konnte die Ubuntu-ISO vollständig laden.

FRITZ!WLAN USB Stick AC 860:
Treiber 9.9.5.0 vom 2021-08-09.

Die Ursache ist noch nicht bewiesen.

## Nach Ubuntu-Installation
Noch nicht automatisch Ollama/Agent starten.

Reihenfolge:
1. Netzwerk prüfen
2. SSH einrichten
3. NVIDIA-Treiber prüfen/installieren
4. GPU-Funktion verifizieren
5. Ollama installieren
6. geeignetes kleines Modell testen
7. Agentenruntime aufsetzen
8. dieses Briefing als persistente Systemgrundlage einbinden
9. kurze Tests
10. erst dann längere autonome Läufe
