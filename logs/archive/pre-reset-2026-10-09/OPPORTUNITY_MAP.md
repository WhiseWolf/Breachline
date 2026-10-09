# OPPORTUNITY MAP — Browser Game Concepts (Phase 1)

**Dokumentstand:** 2026-10-09 — externe Audit-Bereinigung
**Budget:** ADDITIONAL_COST = 0.00 EUR  
**Status:** UNVALIDATED CONCEPT DRAFTS  

---

## METHODOLOGIE

Ungeprüfte Annahmen über mögliche Social-Hooks:
- Challenge/Mini-game Spiele mit steigender Schwierigkeit
- Physik-basiertes Chaos mit emergenten Momenten
- Horror/Surprise Elemente für Shareability
- Leaderboards/Wettbewerb für Retention
- Kosmetische Monetarisierung ohne Pay-to-Win

---

## KONZEPTENTWÜRFE (1–18)

### 1. **Coin Dash Challenge**
- **Validierungsstatus:** HYPOTHESIS; Zielgruppe, Social-Potenzial und Machbarkeit nicht gemessen.
- **Belege:** Keine zugeordneten überprüften Quellen/Test-IDs im Snapshot.
- **Problem/Bedürfnis:** Kurzweiliges Skill-Spiel mit sofortigem Erfolgserlebnis
- **Zielgruppe:** 13-25 Jahre, TikTok-Nutzer, Casual Gamer
- **Kern-Loop:** Münzen sammeln → Hindernisse umgehen → Bestzeit verbessern → Leaderboard
- **Warum Browser:** Keine Installation, sofort spielbar auf Mobile/Desktop
- **Social-/Clip-Potenzial:** High - "Impossible Challenge" Clips mit Zeitdruck
- **Retention-Hypothese:** Täglich neue Challenges, persönliche Bestzeiten
- **Monetarisierung:** Kosmetische Skins für Charaktere/Hindernisse
- **Technische Komplexität:** Low (Canvas + einfache Physik)
- **Gegenargumente:** Kann zu repetitiv werden ohne Content-Frische
- **Evidenzqualität:** UNVERIFIED — keine überprüfbaren Fundstellen für die genannten Vergleichstitel

### 2. **Tower Rush Physics**
- **Validierungsstatus:** HYPOTHESIS; Zielgruppe, Social-Potenzial und Machbarkeit nicht gemessen.
- **Belege:** Keine zugeordneten überprüften Quellen/Test-IDs im Snapshot.
- **Problem/Bedürfnis:** Physik-basiertes Klettern mit emergenten Lösungen
- **Zielgruppe:** 10-30 Jahre, Puzzle-Liebhaber, Physik-Fans
- **Kern-Loop:** Plattformen bauen → Gegner überwinden → neue Wege finden → Highscore
- **Warum Browser:** Canvas-Physik leicht umsetzbar, keine Engine nötig
- **Social-/Clip-Potenzial:** High - "Wie ist das möglich?" Momente
- **Retention-Hypothese:** Neue Level mit steigender Komplexität
- **Monetarisierung:** Kosmetische Farben für Plattformen/Gegner
- **Technische Komplexität:** Medium (Physik-Engine + Level-Design)
- **Gegenargumente:** Level-Design aufwändig, Content-Frize nötig

### 3. **Pet Evolution Idle**
- **Validierungsstatus:** HYPOTHESIS; Zielgruppe, Social-Potenzial und Machbarkeit nicht gemessen.
- **Belege:** Keine zugeordneten überprüften Quellen/Test-IDs im Snapshot.
- **Problem/Bedürfnis:** Sammeln und Züchten mit narrativem Fortschritt
- **Zielgruppe:** 15-40 Jahre, Idle-Gamer, Sammler
- **Kern-Loop:** Pet füttern → evolvieren → neue Pets finden → Community-Zucht
- **Warum Browser:** Persistente Daten im LocalStorage/Server
- **Social-/Clip-Potenzial:** Medium - "Mein Monster!" Momente
- **Retention-Hypothese:** Züchtungslauf, seltene Evolutionspfade
- **Monetarisierung:** Kosmetische Accessoires, keine Pay-to-Win
- **Technische Komplexität:** Medium (State Management + Evolution Logic)
- **Gegenargumente:** Idle-Games haben lange Zykluszeiten

### 4. **Rhythm Beat Challenge**
- **Validierungsstatus:** HYPOTHESIS; Zielgruppe, Social-Potenzial und Machbarkeit nicht gemessen.
- **Belege:** Keine zugeordneten überprüften Quellen/Test-IDs im Snapshot.
- **Problem/Bedürfnis:** Musik-basiertes Timing-Spiel
- **Zielgruppe:** 12-30 Jahre, Musik-Fans, Rhythm Game Fans
- **Kern-Loop:** Noten treffen → Score erhöhen → Combo halten → Bestsong
- **Warum Browser:** Audio-API + Canvas für visuelle Rückmeldung
- **Social-/Clip-Potenzial:** High - "Perfect Timing" Clips
- **Retention-Hypothese:** Neue Songs, Challenges mit Freunden
- **Monetarisierung:** Kosmetische Note-Skins, Avatar-Ausrüstung
- **Technische Komplexität:** Medium (Audio Processing + Timing Logic)
- **Gegenargumente:** Urheberrechte an Musik, Audio-Limits

### 5. **Zombie Survival Co-op**
- **Validierungsstatus:** HYPOTHESIS; Zielgruppe, Social-Potenzial und Machbarkeit nicht gemessen.
- **Belege:** Keine zugeordneten überprüften Quellen/Test-IDs im Snapshot.
- **Problem/Bedürfnis:** Kurzweiliges Survival mit emergenten Taktiken
- **Zielgruppe:** 16-35 Jahre, Shooter-Fans, Co-op Spieler
- **Kern-Loop:** Zombies töten → Ressourcen sammeln → Basis verteidigen → Welle überstehen
- **Warum Browser:** Multiplayer via WebSockets/PeerJS
- **Social-/Clip-Potenzial:** High - "Epic Fail" und "Perfect Defense" Momente
- **Retention-Hypothese:** Neue Wellen, Co-op Challenges mit Freunden
- **Monetarisierung:** Kosmetische Waffen-Skins, keine Pay-to-Win
- **Technische Komplexität:** Medium (Multiplayer Sync + AI)
- **Gegenargumente:** Multiplayer kann technisch anspruchsvoll sein

### 6. **Merge Farm Idle**
- **Validierungsstatus:** HYPOTHESIS; Zielgruppe, Social-Potenzial und Machbarkeit nicht gemessen.
- **Belege:** Keine zugeordneten überprüften Quellen/Test-IDs im Snapshot.
- **Problem/Bedürfnis:** Merge-Mechanik mit Idle-Elementen
- **Zielgruppe:** 25-50 Jahre, Match3-Fans, Idle-Gamer
- **Kern-Loop:** Pflanzen mergen → neue Arten freischalten → Auto-Ernte → Shop
- **Warum Browser:** Persistente State im LocalStorage/Server
- **Social-/Clip-Potenzial:** Medium - "Seltene Entdeckung!" Momente
- **Retention-Hypothese:** Neue Pflanzen, seltene Evolutionspfade
- **Monetarisierung:** Kosmetische Blumen/Skins, keine Pay-to-Win
- **Technische Komplexität:** Low-Medium (Merge Logic + Idle System)
- **Gegenargumente:** Merge-Games haben hohe Retention-Ansprüche

### 7. **Parkour Dash Challenge**
- **Validierungsstatus:** HYPOTHESIS; Zielgruppe, Social-Potenzial und Machbarkeit nicht gemessen.
- **Belege:** Keine zugeordneten überprüften Quellen/Test-IDs im Snapshot.
- **Problem/Bedürfnis:** Geschicklichkeits-basiertes Parkour-Spiel
- **Zielgruppe:** 13-25 Jahre, Action-Fans, Mobile Gamer
- **Kern-Loop:** Hindernisse umgehen → Zeit sparen → Bestzeit verbessern → Leaderboard
- **Warum Browser:** Canvas + einfache Physik für Sprünge
- **Social-/Clip-Potenzial:** High - "Impossible Parkour" Clips
- **Retention-Hypothese:** Neue Levels, persönliche Bestzeiten
- **Monetarisierung:** Kosmetische Charakter-Skins
- **Technische Komplexität:** Low-Medium (Physics + Level Design)
- **Gegenargumente:** Kann zu repetitiv werden ohne neue Levels

### 8. **Horror Escape Room**
- **Validierungsstatus:** HYPOTHESIS; Zielgruppe, Social-Potenzial und Machbarkeit nicht gemessen.
- **Belege:** Keine zugeordneten überprüften Quellen/Test-IDs im Snapshot.
- **Problem/Bedürfnis:** Kurzweiliges Horror-Escape mit Überraschungen
- **Zielgruppe:** 16-35 Jahre, Horror-Fans, Puzzle-Liebhaber
- **Kern-Loop:** Rätsel lösen → Zeit überstehen → Gegner vermeiden → Entkommen
- **Warum Browser:** Keine Installation, sofort spielbar
- **Social-/Clip-Potenzial:** High - "Jump Scare" und "Epic Fail" Clips
- **Retention-Hypothese:** Neue Räume, seltene Items
- **Monetarisierung:** Kosmetische Outfits, keine Pay-to-Win
- **Technische Komplexität:** Medium (AI-Gegner + Rätsel Logic)
- **Gegenargumente:** Horror kann polarisierend sein

### 9. **Racing Stunt Challenge**
- **Validierungsstatus:** HYPOTHESIS; Zielgruppe, Social-Potenzial und Machbarkeit nicht gemessen.
- **Belege:** Keine zugeordneten überprüften Quellen/Test-IDs im Snapshot.
- **Problem/Bedürfnis:** Physik-basiertes Racer mit Stunts
- **Zielgruppe:** 12-30 Jahre, Racing-Fans, Action-Liebhaber
- **Kern-Loop:** Rennen fahren → Stunts machen → Zeit sparen → Bestzeit
- **Warum Browser:** Canvas + einfache Physik für Fahrzeuge
- **Social-/Clip-Potenzial:** High - "Epic Crash" und "Perfect Run" Clips
- **Retention-Hypothese:** Neue Strecken, persönliche Bestzeiten
- **Monetarisierung:** Kosmetische Autos/Skins
- **Technische Komplexität:** Medium (Vehicle Physics + Track Design)
- **Gegenargumente:** Vehicle Physics kann komplex sein

### 10. **Pet Battle Arena**
- **Validierungsstatus:** HYPOTHESIS; Zielgruppe, Social-Potenzial und Machbarkeit nicht gemessen.
- **Belege:** Keine zugeordneten überprüften Quellen/Test-IDs im Snapshot.
- **Problem/Bedürfnis:** Sammel- und Kämpf-Spiel mit emergenten Taktiken
- **Zielgruppe:** 15-35 Jahre, Pokémon-Fans, Strategy-Liebhaber
- **Kern-Loop:** Pets sammeln → trainieren → kämpfen → Arena-Ranking
- **Warum Browser:** Persistente State + einfache Battle Logic
- **Social-/Clip-Potenzial:** Medium - "Epic Battle" Momente
- **Retention-Hypothese:** Neue Pets, seltene Evolutionspfade
- **Monetarisierung:** Kosmetische Items, keine Pay-to-Win
- **Technische Komplexität:** Medium (Battle System + Collection Logic)
- **Gegenargumente:** Battle Balance aufwändig zu halten

### 11. **Dungeon Crawler Idle**
- **Validierungsstatus:** HYPOTHESIS; Zielgruppe, Social-Potenzial und Machbarkeit nicht gemessen.
- **Belege:** Keine zugeordneten überprüften Quellen/Test-IDs im Snapshot.
- **Problem/Bedürfnis:** Dungeon-Crawler mit Idle-Elementen
- **Zielgruppe:** 18-40 Jahre, RPG-Fans, Idle-Gamer
- **Kern-Loop:** Monster töten → Loot sammeln → Level verbessern → Boss bekämpfen
- **Warum Browser:** Persistente State + einfache Combat Logic
- **Social-/Clip-Potenzial:** Medium - "Epic Loot Drop" Momente
- **Retention-Hypothese:** Neue Dungeons, seltene Items
- **Monetarisierung:** Kosmetische Waffen/Skins
- **Technische Komplexität:** Medium (Combat + Progression System)
- **Gegenargumente:** RPGs haben hohe Content-Ansprüche

### 12. **Platformer Dash Challenge**
- **Validierungsstatus:** HYPOTHESIS; Zielgruppe, Social-Potenzial und Machbarkeit nicht gemessen.
- **Belege:** Keine zugeordneten überprüften Quellen/Test-IDs im Snapshot.
- **Problem/Bedürfnis:** Geschicklichkeits-basiertes Platformer-Spiel
- **Zielgruppe:** 10-30 Jahre, Action-Fans, Mobile Gamer
- **Kern-Loop:** Plattformen erreichen → Hindernisse umgehen → Bestzeit verbessern
- **Warum Browser:** Canvas + einfache Physik für Sprünge
- **Social-/Clip-Potenzial:** High - "Impossible Jump" Clips
- **Retention-Hypothese:** Neue Levels, persönliche Bestzeiten
- **Monetarisierung:** Kosmetische Charakter-Skins
- **Technische Komplexität:** Low-Medium (Physics + Level Design)
- **Gegenargumente:** Kann zu repetitiv werden ohne neue Levels

### 13. **Tower Defense Strategy**
- **Validierungsstatus:** HYPOTHESIS; Zielgruppe, Social-Potenzial und Machbarkeit nicht gemessen.
- **Belege:** Keine zugeordneten überprüften Quellen/Test-IDs im Snapshot.
- **Problem/Bedürfnis:** Tower Defense mit emergenten Taktiken
- **Zielgruppe:** 16-40 Jahre, Strategy-Fans, Puzzle-Liebhaber
- **Kern-Loop:** Türme platzieren → Wellen überstehen → Ressourcen optimieren → Bestscore
- **Warum Browser:** Grid-basiertes System leicht umsetzbar
- **Social-/Clip-Potenzial:** Medium - "Epic Defense" Momente
- **Retention-Hypothese:** Neue Wellen, seltene Türme
- **Monetarisierung:** Kosmetische Türme/Skins
- **Technische Komplexität:** Medium (Wave Logic + Placement System)
- **Gegenargumente:** Strategy kann repetitiv werden

### 14. **Card Battle Arena**
- **Validierungsstatus:** HYPOTHESIS; Zielgruppe, Social-Potenzial und Machbarkeit nicht gemessen.
- **Belege:** Keine zugeordneten überprüften Quellen/Test-IDs im Snapshot.
- **Problem/Bedürfnis:** Kartenspiel mit emergenten Taktiken
- **Zielgruppe:** 15-35 Jahre, Card Game Fans, Strategy-Liebhaber
- **Kern-Loop:** Karten sammeln → deck bauen → kämpfen → Ranking verbessern
- **Warum Browser:** Simple Card Logic + State Management
- **Social-/Clip-Potenzial:** Medium - "Epic Combo" Momente
- **Retention-Hypothese:** Neue Karten, seltene Evolutionspfade
- **Monetarisierung:** Kosmetische Karten-Skins
- **Technische Komplexität:** Medium (Card Logic + Matchmaking)
- **Gegenargumente:** Balance aufwändig zu halten

### 15. **Puzzle Escape Room**
- **Validierungsstatus:** HYPOTHESIS; Zielgruppe, Social-Potenzial und Machbarkeit nicht gemessen.
- **Belege:** Keine zugeordneten überprüften Quellen/Test-IDs im Snapshot.
- **Problem/Bedürfnis:** Rätsel-basiertes Escape mit Story
- **Zielgruppe:** 16-40 Jahre, Puzzle-Fans, Mystery-Liebhaber
- **Kern-Loop:** Rätsel lösen → Hinweise finden → Zeit überstehen → Entkommen
- **Warum Browser:** Keine Installation, sofort spielbar
- **Social-/Clip-Potenzial:** Medium - "Eureka!" Momente
- **Retention-Hypothese:** Neue Räume, seltene Items
- **Monetarisierung:** Kosmetische Outfits
- **Technische Komplexität:** Low-Medium (Puzzle Logic + Story)
- **Gegenargumente:** Puzzle kann frustrierend sein

### 16. **Farming Sim Idle**
- **Validierungsstatus:** HYPOTHESIS; Zielgruppe, Social-Potenzial und Machbarkeit nicht gemessen.
- **Belege:** Keine zugeordneten überprüften Quellen/Test-IDs im Snapshot.
- **Problem/Bedürfnis:** Farming-Sim mit Idle-Elementen
- **Zielgruppe:** 20-50 Jahre, Simulation-Fans, Relax-Gamer
- **Kern-Loop:** Pflanzen pflegen → ernten → verkaufen → erweitern
- **Warum Browser:** Persistente State + einfache Sim Logic
- **Social-/Clip-Potenzial:** Medium - "Rare Crop" Momente
- **Retention-Hypothese:** Neue Pflanzen, seltene Events
- **Monetarisierung:** Kosmetische Dekorationen
- **Technische Komplexität:** Low-Medium (Sim Logic + Idle System)
- **Gegenargumente:** Sims haben hohe Content-Ansprüche

### 17. **Duel Arena Challenge**
- **Validierungsstatus:** HYPOTHESIS; Zielgruppe, Social-Potenzial und Machbarkeit nicht gemessen.
- **Belege:** Keine zugeordneten überprüften Quellen/Test-IDs im Snapshot.
- **Problem/Bedürfnis:** 1v1 Kämpfe mit Skill-Fokus
- **Zielgruppe:** 15-30 Jahre, Fighting-Fans, Competitive Gamer
- **Kern-Loop:** Gegner finden → kämpfen → verbessern → Ranking verbessern
- **Warum Browser:** Multiplayer via WebSockets/PeerJS
- **Social-/Clip-Potenzial:** High - "Epic Win/Loss" Clips
- **Retention-Hypothese:** Neue Gegner, seltene Skills
- **Monetarisierung:** Kosmetische Charakter-Skins
- **Technische Komplexität:** Medium (Multiplayer + Combat Logic)
- **Gegenargumente:** Multiplayer kann technisch anspruchsvoll sein

### 18. **Rhythm Dance Challenge**
- **Validierungsstatus:** HYPOTHESIS; Zielgruppe, Social-Potenzial und Machbarkeit nicht gemessen.
- **Belege:** Keine zugeordneten überprüften Quellen/Test-IDs im Snapshot.
- **Problem/Bedürfnis:** Musik-basiertes Dance-Spiel
- **Zielgruppe:** 12-30 Jahre, Music-Fans, Dance-Liebhaber
- **Kern-Loop:** Beats treffen → Score erhöhen → Combo halten → Bestsong
- **Warum Browser:** Audio-API + Canvas für visuelle Rückmeldung
- **Social-/Clip-Potenzial:** High - "Perfect Timing" Clips
- **Retention-Hypothese:** Neue Songs, Challenges mit Freunden
- **Monetarisierung:** Kosmetische Note-Skins
- **Technische Komplexität:** Medium (Audio Processing + Timing Logic)
- **Gegenargumente:** Urheberrechte an Musik

---

## Nächster Schritt
CURRENT_WORK.md folgen. Erst Quellen-/Belegprüfung, dann begründete Auswahl.

Originale Doppelungen 19 (wie 5) und 20 (wie 6) wurden entfernt; Original im Archiv.
