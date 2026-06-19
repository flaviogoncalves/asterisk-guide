# Deployment, monitoring & scaling

Asterisk dazu zu bringen, in einer Laborumgebung einen Anruf anzunehmen, ist eine Sache; es als Dienst zu betreiben, der Abstürze, Neustarts, Upgrades und Angreifer übersteht – und den man beobachten, sichern und skalieren kann – ist eine andere. Dieses Kapitel behandelt alles, was passiert, *nachdem* der dialplan funktioniert. Wir beginnen mit dem Supervisor, der Asterisk am Laufen hält (systemd), gehen über zum Verpacken in einen Container (unter Verwendung des Docker-Labs aus diesem Buch als praktisches Beispiel), behandeln dann Konfigurationsmanagement und Backups, Monitoring und Observability und schließlich die Muster, auf die man zurückgreift, wenn ein Server nicht ausreicht: Hochverfügbarkeit und Skalierung sowie die Realitäten des Hostings in der Cloud.

Alles Gezeigte wurde mit dem Asterisk 22-Labor des Buches in `lab/` verifiziert – demselben Container, auf dem Sie während des gesamten Buches aufgebaut haben.

## Objectives

Am Ende dieses Kapitels sollten Sie in der Lage sein:

- Asterisk 22 zuverlässig unter systemd als Nicht-Root-Benutzer mit automatischem Neustart auszuführen
- Asterisk mit Docker zu containerisieren und die Kompromisse beim Networking zu verstehen
- `/etc/asterisk` in der Versionskontrolle zu halten und den richtigen Status zu sichern
- Ein laufendes System über die CLI, CDR/CEL, AMI/ARI und Metriken zu überwachen
- Active/Standby-Hochverfügbarkeit und horizontale Skalierungsmuster anzuwenden
- Asterisk sicher in der Cloud hinter NAT und einer Firewall zu hosten

## Running Asterisk under systemd

Auf jeder aktuellen Linux-Distribution – Debian 12, Ubuntu 22.04/24.04, Rocky/AlmaLinux 9 – ist der Dienstmanager **systemd**. Das Installationskapitel zeigte, dass der Schritt `make config` (ausgeführt während `make install`) ein Distributions-Init-Skript installiert (`/etc/init.d/asterisk` auf Debian, ein `rc.d` Skript auf RedHat), das systemd dann automatisch als Dienst einbindet; Asterisk liefert auch eine native systemd-Unit unter `contrib/systemd/asterisk.service` mit, die Sie stattdessen für eine feinere Kontrolle installieren können.
So oder so ist systemd der unterstützte Weg für den produktiven Betrieb von Asterisk. Verweisen Sie auf *Installing Asterisk 22* für den Build selbst; hier konzentrieren wir uns darauf, was der Dienst Ihnen bietet und wie man ihn bedient.

### The service unit and its lifecycle

Sobald `make config` den Dienst installiert hat, folgt der Lebenszyklus dem gewöhnlichen systemd-Standard:

```
systemctl enable asterisk     # start automatically at boot
systemctl start asterisk      # start now
systemctl status asterisk     # is it running? recent log lines
systemctl restart asterisk    # full stop + start
systemctl stop asterisk       # stop
journalctl -u asterisk        # service logs via the journal
```

Ein paar betriebliche Hinweise:

- **`restart` vs. ein sanfter Reload.** `systemctl restart` beendet den Prozess und bricht jeden Anruf ab. Für Konfigurationsänderungen möchten Sie das fast nie – verwenden Sie stattdessen die Asterisk CLI: `asterisk -rx 'core reload'` (oder einen modulspezifischen Reload wie `pjsip reload`). Reservieren Sie `systemctl restart` für Upgrades oder einen blockierten Prozess.
- **An den laufenden Daemon anhängen.** Wenn Asterisk als Dienst läuft, öffnen Sie dessen Konsole mit `asterisk -r` (oder `asterisk -rvvv` für ausführliche Ausgaben). Dies verbindet sich über den Steuerungssocket mit dem bereits laufenden Daemon; es startet keine zweite Kopie.

### `Restart=` replaces safe_asterisk

Historisch gesehen wurde Asterisk über den **safe_asterisk**-Wrapper gestartet, ein Shell-Skript, das Asterisk bei einem Absturz neu startete. Unter systemd gehört diese Aufgabe zur `Restart=`-Direktive der Unit – systemd bemerkt das Beenden des Prozesses und startet ihn neu, wobei das Back-off durch `RestartSec=` und der Schutz vor Absturzschleifen durch `StartLimitIntervalSec=`/`StartLimitBurst=` gesteuert wird. Auf einem systemd-Host ist **safe_asterisk daher überflüssig** und im Allgemeinen unnötig. Falls Ihre mitgelieferte Unit dies noch nicht festlegt, ist ein Drop-in-Override der saubere Weg, um einen Neustart bei Fehlern hinzuzufügen, ohne die paketierte Datei zu bearbeiten:

```
# /etc/systemd/system/asterisk.service.d/override.conf
[Service]
Restart=always
RestartSec=2
```

Wenden Sie es mit `systemctl daemon-reload && systemctl restart asterisk` an. Die Verwendung eines Drop-ins (anstatt die installierte Unit zu bearbeiten) bedeutet, dass ein zukünftiges `make config` Ihre Änderung nicht überschreibt.

### Running as a non-root user

Asterisk sollte in der Produktion nicht als root ausgeführt werden – ein Fehler mit Remote-Code-Ausführung in einem als root laufenden Prozess ist eine vollständige Kompromittierung des Hosts, während derselbe Fehler in einem unprivilegierten Prozess eingedämmt ist. Es gibt zwei komplementäre Orte, an denen dies erzwungen wird:

- **Die Unit / asterisk.conf.** Die paketierte Unit führt Asterisk normalerweise als `asterisk`-Benutzer und -Gruppe aus. Sie können auch (oder stattdessen) `runuser` und `rungroup` im Abschnitt `[options]` von `asterisk.conf` festlegen, was der Daemon berücksichtigt, wenn er nach dem Binden die Privilegien abgibt:

  ```
  [options]
  runuser = asterisk
  rungroup = asterisk
  ```

- **Dateiberechtigungen.** Die Laufzeitverzeichnisse müssen für diesen Benutzer beschreibbar sein. Stellen Sie nach dem Erstellen des Kontos die Eigentümerschaft sicher:

  ```
  chown -R asterisk:asterisk /var/lib/asterisk /var/log/asterisk \
        /var/spool/asterisk /var/run/asterisk /etc/asterisk
  ```

Da SIP (5060) und RTP (10000+) allesamt hohe Ports sind, benötigt Asterisk **kein** root, um sie zu binden – nur privilegierte Ports im Stil von Port 25 würden dies erfordern, was Asterisk nicht nutzt. Die unprivilegierte Ausführung ist daher kostenlos. (Das Sicherheitskapitel erläutert, warum dies wichtig ist; siehe *Asterisk Security*.)

## Containerizing Asterisk

Ein Container verpackt Asterisk und seine exakten Abhängigkeiten in ein unveränderliches Image, sodass das, was Sie testen, Byte für Byte das ist, was Sie ausliefern. Der Kompromiss betrifft Echtzeitmedien: Ein SIP-Server ist empfindlich gegenüber Latenz und benötigt einen breiten, vorhersagbaren Bereich von UDP-Ports, die von außen erreichbar sind, und Container-Networking kann dabei im Weg stehen. Der Rest dieses Abschnitts führt durch das eigene Labor des Buches – `lab/Dockerfile` und `lab/docker-compose.yml` – als konkretes, funktionierendes Beispiel und erklärt dann die eine Falle, in die jeder tappt: RTP und Bridged Networking.

### The image: building Asterisk from source

Das `Dockerfile` des Labors baut Asterisk 22 aus dem Quellcode auf Debian 12. Es lohnt sich, die Struktur zu lesen, auch wenn Sie selbst nie eine schreiben:

```dockerfile
FROM debian:12-slim

ARG ASTERISK_VERSION=22.10.0
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential wget ca-certificates pkg-config \
        libedit-dev libxml2-dev libsqlite3-dev uuid-dev libssl-dev \
        libsrtp2-dev libcurl4-openssl-dev libncurses-dev \
    && rm -rf /var/lib/apt/lists/*

# ... download + tar xzf asterisk-${ASTERISK_VERSION}.tar.gz ...

RUN ./configure --with-jansson-bundled --with-pjproject-bundled \
    && make menuselect.makeopts \
    && menuselect/menuselect --enable res_srtp --enable res_http_websocket menuselect.makeopts \
    && make -j"$(nproc)" \
    && make install \
    && make install-logrotate \
    && ldconfig

EXPOSE 5060/udp 10000-10100/udp
CMD ["asterisk", "-f", "-vvv"]
```

Drei Dinge, die hervorzuheben sind:

- **Die Version ist fixiert** (`ARG ASTERISK_VERSION=22.10.0`). Reproduzierbarkeit ist der ganze Sinn der Containerisierung – ändern Sie sie bewusst, bauen Sie neu, testen Sie neu.
- **`--with-pjproject-bundled` und `--with-jansson-bundled`** bauen den SIP-Stack versionsgenau zu Asterisk, sodass Sie von weniger apt-Paketen abhängen und niemals gegen ein PJSIP der Distribution kämpfen müssen, das nicht passt.
- **`CMD ["asterisk", "-f", "-vvv"]`** führt Asterisk im *Vordergrund* aus (`-f`, "do not fork"). Dies ist der entscheidende Unterschied zu einem systemd-Host: Der Hauptprozess eines Containers darf nicht daemonisieren, sonst würde der Container sofort beendet werden. In einem Container verwenden Sie also **überhaupt nicht** die systemd-Unit – die Container-Runtime (Docker, plus `restart:`-Richtlinie) wird zum Supervisor, der die `Restart=` der Unit auf einer VM war.

### Bind-mounting `/etc/asterisk`

Das Image enthält bewusst **keine** Konfiguration. Stattdessen bindet `docker-compose.yml` das Konfigurationsverzeichnis des Hosts ein:

```yaml
services:
  asterisk:
    build: .
    image: astbook/asterisk:22.10.0
    container_name: astlab-asterisk
    restart: unless-stopped
    volumes:
      - ./asterisk/etc:/etc/asterisk:ro
    ports:
      - "5060:5060/udp"
      - "10000-10100:10000-10100/udp"
```

`./asterisk/etc:/etc/asterisk:ro` bildet das versionskontrollierte Verzeichnis `lab/asterisk/etc` auf das `/etc/asterisk` des Containers ab, schreibgeschützt (`:ro`). Der Gewinn ist groß: Das Image bleibt unveränderlich und wiederverwendbar, während die Konfiguration auf dem Host verbleibt, wo sie bearbeitet und, was entscheidend ist, in git gehalten werden kann (nächster Abschnitt). Um eine Konfigurationsänderung anzuwenden, bearbeiten Sie die Datei und laden neu – `docker compose exec asterisk asterisk -rx 'core reload'` – ohne einen Rebuild. `restart: unless-stopped` ist das Compose-Äquivalent zu systemds `Restart=`: Docker startet den Container neu, wenn Asterisk beendet wird, aber nicht, wenn Sie ihn bewusst gestoppt haben.

### Host vs. bridged networking — the RTP problem

Dies ist der häufigste Fehler bei containerisiertem Asterisk, daher lohnt es sich, ihn genau zu verstehen. Standardmäßig platziert Docker einen Container in einem **bridged** Netzwerk und Sie veröffentlichen einzelne Ports mit `ports:`. Signalisierung ist in Ordnung – 5060 ist ein Port. Das Problem sind Medien: RTP verwendet einen *Bereich* von UDP-Ports (das `rtp.conf` des Labors setzt `rtpstart=10000` / `rtpend=10100`), und **jeder** Port, der Audio übertragen könnte, muss veröffentlicht werden.

Das Labor tut genau das:

```yaml
    ports:
      - "5060:5060/udp"
      - "10000-10100:10000-10100/udp"
```

Beachten Sie, dass der RTP-Veröffentlichungsbereich (`10000-10100`) exakt mit `rtp.conf` übereinstimmt. Wenn Sie dies falsch machen – zu wenige Ports veröffentlichen oder einen anderen Bereich als `rtp.conf` – werden Anrufe zwar verbunden, haben aber **einseitiges oder gar kein Audio**, weil die RTP-Pakete auf einem Port landen, den Docker nicht weiterleitet. Zwei weitere Warnungen zum Bridged-Modus:

- **Das Veröffentlichen von Tausenden von Ports ist langsam und schwerfällig.** Ein produktiver RTP-Bereich liegt typischerweise bei 10000–20000. Dass Docker ca. 10000 Userland-Proxy-Weiterleitungen erstellt, ist beim Start teuer und fügt einen Hop im Medienpfad hinzu. Das Labor hält einen bewusst kleinen 100-Port-Bereich, da es nur ein oder zwei Testanrufe gleichzeitig ausführt.
- **NAT im SDP.** Hinter der Bridge sieht Asterisk seine private Container-IP und bewirbt sie möglicherweise im SDP. Auf einem öffentlichen Host müssen Sie PJSIP seine externe Adresse mit `external_media_address` / `external_signaling_address` am Transport mitteilen (und `local_net` setzen), genau wie Sie es hinter jedem NAT tun würden – siehe *Cloud hosting* unten.

Die Alternative ist **Host-Networking** (`network_mode: host`), das die Bridge vollständig entfernt: Der Container teilt sich den Netzwerk-Stack des Hosts, sodass 5060 und der gesamte RTP-Bereich ohne Port-Veröffentlichung und ohne zusätzlichen Medien-Hop erreichbar sind. Dies ist der empfohlene Modus für einen echten Asterisk-Container – er umgeht das RTP-Bereichs-Problem vollständig. Der Preis dafür ist die Isolation: Der Container kann jeden Host-Port binden und Sie verlieren das pro-Dienst-Netzwerk von Compose. (Host-Networking ist ein Linux-Feature; auf Docker Desktop für macOS/Windows verhält es sich anders, was teilweise der Grund ist, warum dieses Lehrlabor explizite veröffentlichte Ports verwendet.)

### Persistent volumes for spool and voicemail

Die beschreibbare Ebene eines Containers ist **flüchtig** – zerstören Sie den Container und alles, was er geschrieben hat, ist weg. Für Asterisk bedeutet das, dass Voicemail, Aufzeichnungen, der ausgehende Anruf-Spool und die lokale Datenbank bei jedem `docker compose up --build` verschwinden würden. Die Konfiguration überlebt, weil sie vom Host bind-gemountet ist; *Statusdaten* benötigen die gleiche Behandlung. Innerhalb des Containers sind die relevanten Verzeichnisbäume:

```
/var/spool/asterisk        # voicemail, monitor recordings, outgoing/, etc.
/var/lib/asterisk          # astdb.sqlite3 (the internal database)
/var/log/asterisk          # full, messages, security, cdr-csv/, cel-custom/
```

(Der laufende Container des Labors zeigt genau diese – `/var/spool/asterisk` enthält `voicemail`, `monitor`, `outgoing`, `recording`; `/var/lib/asterisk` enthält `astdb.sqlite3`.) Um sie zu bewahren, mounten Sie benannte Volumes für die Verzeichnisse, die Statusdaten enthalten, die Ihnen wichtig sind:

```yaml
    volumes:
      - ./asterisk/etc:/etc/asterisk:ro     # config (bind, in git)
      - ast-spool:/var/spool/asterisk        # voicemail + recordings (persist)
      - ast-lib:/var/lib/asterisk            # astdb (persist)
      - ast-log:/var/log/asterisk            # logs (persist)

volumes:
  ast-spool:
  ast-lib:
  ast-log:
```

Das Lehrlabor lässt diese absichtlich weg – es ist zustandslos und von Design her reproduzierbar, sodass jedes `up` ein sauberer Neuanfang ist – aber ein Produktionscontainer **muss** sie haben, sonst verlieren Sie beim ersten Redeploy Ihre Voicemails.

## Configuration management and backups

Der obige Bind-Mount deutet auf das richtige Modell hin: Behandeln Sie `/etc/asterisk` als **Code** und den Rest als **Daten**.

### Keep `/etc/asterisk` in version control

Das Konfigurationsverzeichnis ist eine flache Menge von Textdateien ohne Geheimnisse, die nicht als Template erstellt werden können – es ist ideal für git. Initialisieren Sie ein Repo in `/etc/asterisk` (oder halten Sie, wie das Labor es tut, die Konfiguration neben dem Projekt und binden Sie sie ein). Vorteile:

- Jede Änderung ist überprüfbar und rückgängig machbar (`git diff`, `git revert`).
- Sie haben einen Audit-Trail, wer was wann geändert hat.
- In Kombination mit einem Container-Image beschreiben ein bekannter guter Konfigurations-Commit plus ein fixierter Image-Tag eine Bereitstellung vollständig.

Ein paar Warnungen speziell für die Asterisk-Konfiguration:

- **Geheimnisse.** `pjsip.conf` (und `manager.conf`, `ari.conf`) enthalten Passwörter. Committen Sie keine echten Geheimnisse in Klartext in ein geteiltes Repo – erstellen Sie Templates (eine Datei pro Umgebung oder ein Secrets-Manager / Umgebungssubstitution zur Bereitstellungszeit) und behalten Sie nur Platzhalter in git. Die trivialen `Lab-6001-secret`-Passwörter des Labors sind *nur* in Ordnung, weil sie in einem privaten Docker-Subnetz leben.
- **Umgebungsspezifische Templates.** Die Realtime-Werte, die sich zwischen Dev, Staging und Produktion unterscheiden (Bind-Adressen, externe IPs, Trunk-Anmeldedaten, Datenbank-URLs), sind genau die Zeilen, die Sie als Template erstellen, während der Großteil der Konfiguration über Umgebungen hinweg identisch bleibt.

### What to back up

Die Konfiguration in git deckt den Dialplan und die Endpunkte ab, aber eine Live-PBX sammelt *Statusdaten*, die in keiner Konfigurationsdatei stehen. Ein vollständiges Backup ist:

| Was | Wo | Warum |
|------|-------|-----|
| Konfiguration | `/etc/asterisk/` | Dialplan, Endpunkte (auch in git) |
| Voicemail & Aufzeichnungen | `/var/spool/asterisk/` | Benutzerdaten — unersetzlich |
| Interne Datenbank | `/var/lib/asterisk/astdb.sqlite3` | `DB()` Schlüssel, Gerätestatus |
| CDR / CEL | `/var/log/asterisk/cdr-csv/` oder SQL-Speicher | Abrechnung & Historie |
| Externe Datenbanken | Ihre MySQL/PostgreSQL | Realtime, CDR, Voicemail |

Die **astdb** verdient eine Anmerkung: Es ist Asterisks kleiner eingebauter Key/Value-Speicher (eine SQLite-Datei unter `/var/lib/asterisk/astdb.sqlite3`), der von `DB()`-Dialplanfunktionen, Gerätestatus, Follow-me-Einstellungen und Ähnlichem verwendet wird. Sie können ihn zur Inspektion oder Sicherung über die CLI dumpen:

```
asterisk -rx 'database show'
```

Wenn Ihre CDR/CEL oder Voicemail oder PJSIP-Konfiguration in einer externen Datenbank lebt (siehe *Asterisk Real-Time* und *Asterisk Call Detail Records*), ist diese Datenbank nun die Quelle der Wahrheit für diese Daten und muss in Ihrer normalen Datenbank-Backup-Rotation enthalten sein – das Sichern von `/etc/asterisk` allein reicht nicht aus.

## Monitoring and observability

Sie können nicht betreiben, was Sie nicht sehen können. Asterisk legt seinen Status auf vier Ebenen offen, von einem schnellen menschlichen Blick bis hin zu einer Metrik-Pipeline: die **CLI**, die **CDR/CEL**-Datensätze, **AMI/ARI**-Ereignisse und **Metrik-Exporter**.

### CLI health checks

Der schnellste "Ist es gesund?"-Check ist die CLI. Die unten stehenden Befehle werden live gegen das Labor ausgeführt. Zuerst die Kanäle:

```
*CLI> core show channels
Channel              Location             State   Application(Data)
0 active channels
0 active calls
0 calls processed
```

`0 active calls` auf einem ruhigen System ist normal; auf einem ausgelasteten ist dies Ihre Echtzeit-Gleichzeitigkeit. `core show uptime` bestätigt, dass der Prozess nicht unter Ihnen neu gestartet wurde:

```
*CLI> core show uptime
System uptime: 1 hour, 40 minutes, 19 seconds
Last reload: 12 minutes, 32 seconds
```

Für die SIP-Gesundheit zeigt `pjsip show endpoints` jeden Endpunkt und ob seine registrierten Kontakte erreichbar sind. Aus dem Labor:

```
*CLI> pjsip show endpoints
 Endpoint:  6001                                                 Unavailable   0 of inf
     InAuth:  6001/6001
        Aor:  6001                                               1
 Endpoint:  6002                                                 Unavailable   0 of inf
     InAuth:  6002/6002
        Aor:  6002                                               1
 Endpoint:  webrtc-1000                                          Unavailable   0 of inf
     InAuth:  webrtc-1000/webrtc-1000
        Aor:  webrtc-1000                                        1
Objects found: 4
```

`Unavailable` bedeutet hier einfach, dass derzeit kein Telefon an diesen Endpunkten registriert ist (das Labor hat keine Live-Clients) – sobald sich ein Softphone registriert und `qualify` dies bestätigt, zeigt der Status den Kontakt als erreichbar an. Begleitbefehle: `pjsip show contacts` (aktuelle Registrierungen und Round-Trip-Zeit), `pjsip show transports` und `pjsip show aor <name>` für einen AOR. Dies sind die täglichen "Warum ist Nebenstelle X nicht erreichbar?"-Werkzeuge.

### CDR and CEL

Jeder Anruf hinterlässt einen **Call Detail Record** (CDR); **Channel Event Logging** (CEL) fügt feinere Ereignisse pro Kanal hinzu. Bestätigen Sie, dass CDR aktiv ist und welches Backend es speichert:

```
*CLI> cdr show status

Call Detail Record (CDR) settings
----------------------------------
  Logging:                    Enabled
  Mode:                       Simple
  Log calls by default:       Yes
  Log unanswered calls:       No
...
* Registered Backends
  -------------------
    (none)
```

Das Labor zeigt `(none)` unter den registrierten Backends, weil die minimale Laborkonfiguration kein CDR-Speichermodul lädt – also werden Datensätze berechnet, aber nirgendwohin geschrieben. In der Produktion laden Sie ein Backend (CSV oder `cdr_odbc`/`cdr_adaptive_odbc` in MySQL/PostgreSQL), und das wird zu Ihrer Abrechnungs- und Historienquelle. CEL ist **standardmäßig deaktiviert** (`cel show status` reports `CEL Logging: Disabled` in the lab) and you enable it in `cel.conf` nur, wenn Sie Details auf Ereignisebene benötigen. Beide werden ausführlich in *Asterisk Call Detail Records* behandelt; für das Monitoring ist der Punkt, dass CDR/CEL Ihr *historischer* Datensatz sind, während die CLI Ihre *Live*-Ansicht ist.

### AMI and ARI events

Für programmatisches Echtzeit-Monitoring möchten Sie einen Push-Feed von Ereignissen, anstatt die CLI abzufragen:

- **AMI (Asterisk Manager Interface)** ist das langjährige TCP-Ereignis/Befehlsprotokoll (`manager.conf`). Abonnieren Sie es und Sie erhalten `Newchannel`, `Hangup`, `DialBegin`, `BridgeEnter`, `PeerStatus` und ähnliche Ereignisse, während Anrufe stattfinden – das Rückgrat von Wallboards und Anrufabrechnungstools. Im Labor ist AMI standardmäßig deaktiviert (`manager show settings` meldet `Manager (AMI): No`); Sie aktivieren und sperren es in `manager.conf`.
- **ARI (Asterisk REST Interface)** ist die moderne HTTP + WebSocket-Schnittstelle (`ari.conf`, bereitgestellt vom eingebauten HTTP-Server). Sie bietet einen JSON-Ereignisstrom und eine fein abgestimmte Anrufsteuerung – die richtige Wahl für neue Integrationen.

Beide werden in *Extending Asterisk with AMI and AGI* und *The Asterisk REST Interface (ARI)* detailliert beschrieben. Die für die Bereitstellung relevante Warnung: **AMI und ARI sind mächtig und dürfen niemals dem Internet ausgesetzt werden.** Binden Sie den HTTP-Server an localhost oder ein Management-Netzwerk, verwenden Sie starke, eindeutige Geheimnisse und firewallen Sie die Ports – siehe *Asterisk Security*.

### Metrics: Prometheus and Grafana

Für Dashboards und Alarmierung liefert Asterisk 22 einen Prometheus-Exporter, **`res_prometheus.so`** (ein Modul mit *erweitertem* Support-Level), das Metriken auf einem HTTP-Endpunkt bereitstellt, den ein Prometheus-Server abfragt. Neben Kernprozessmetriken liefert es steckbare Provider, die Kanäle, Anrufe, Endpunkte, Bridges und PJSIP-ausgehende Registrierungen abdecken:

```
# core process
asterisk_core_uptime_seconds
asterisk_core_last_reload_seconds
asterisk_core_scrape_time_ms
asterisk_core_properties
# channels
asterisk_channels_count
asterisk_channels_state
asterisk_channels_duration_seconds
# calls
asterisk_calls_count
asterisk_calls_sum
# endpoints
asterisk_endpoints_count
asterisk_endpoints_state
asterisk_endpoints_channels_count
# bridges
asterisk_bridges_count
asterisk_bridges_channels_count
# PJSIP outbound registrations
asterisk_pjsip_outbound_registration_status
```

Sie können bestätigen, dass das Modul im Labor-Build vorhanden ist:

```
*CLI> module show like prometheus
Module                         Description                     Use Count  Status      Support Level
res_prometheus.so              Asterisk Prometheus Module      0          Not Running  extended
```

Es zeigt `Not Running`, weil das Labor es nicht konfiguriert oder lädt; das Aktivieren (`prometheus.conf` plus der HTTP-Server) macht Asterisk zu einem Prometheus-Ziel. Richten Sie Prometheus auf den Scrape-Endpunkt und Grafana auf Prometheus aus, und Sie erhalten Zeitreihen-Dashboards (gleichzeitige Anrufe, Registrierungen, ASR/ACD-Trends) und Alarmierung (z. B. "aktive Anrufe auf Null gefallen" oder "Registrierungsfehler häufen sich"). Für Teams, die bereits Prometheus/Grafana betreiben, ist dies der natürliche Weg, Asterisk in die bestehende Observability zu integrieren, anstatt CLI-Ausgaben zu parsen.

### SIP response codes worth watching

Unabhängig von der Pipeline signalisieren einige SIP-Ergebnisse Probleme und sind es wert, alarmiert zu werden: anhaltende `401`/`407` Challenge-Fehler oder `403 Forbidden` deuten auf einen Brute-Force- oder falsch konfigurierte Anmeldedaten-Sturm hin (verweisen Sie auf Fail2Ban in *Asterisk Security*); `503 Service Unavailable` deutet auf einen überlasteten oder überlasteten Server oder Trunk hin; und ein Anstieg bei `408 Request Timeout`/`480 Temporarily Unavailable` bedeutet normalerweise, dass Endpunkte nicht mehr erreichbar sind (NAT-Timeout, Qualify-Fehler).

## High availability and scaling

Ein Asterisk-Server ist ein Single Point of Failure und hat eine endliche Anrufobergrenze. Die beiden Probleme – *am Laufen bleiben* und *größer werden* – haben unterschiedliche Antworten.

### Active/standby with a floating IP

Das klassische, bewährte HA-Muster für Asterisk ist **Active/Standby** (nicht Active/Active – der Anrufstatus in Asterisk ist schwer live zu teilen). Zwei identische Server, einer aktiv, einer im Standby, teilen sich eine **Floating (virtuelle) IP**, die von einem Cluster-Manager wie **keepalived** (VRRP) oder **Pacemaker/Corosync** verwaltet wird. Telefone und Trunks registrieren sich bei der Floating IP, nicht bei einem der beiden echten Hosts. Wenn der aktive Knoten seinen Gesundheitscheck nicht besteht, wandert die Floating IP zum Standby, der übernimmt.

Der ehrliche Vorbehalt: Ein IP-Failover **bricht laufende Anrufe ab** – Asterisk repliziert den Live-Kanalstatus nicht zwischen Knoten, sodass jeder mitten im Gespräch neu wählen muss. Registrierungen werden innerhalb eines Qualify/Registrierungszyklus wiederhergestellt. Was Ihnen das Failover bringt, ist, dass der *Dienst* in Sekunden ohne manuelles Eingreifen wiederhergestellt wird, was für die meisten PBXs genau das Ziel ist. Damit der Standby wirklich übernehmen kann, benötigen beide Knoten die gleiche Konfiguration (Ihr git'd `/etc/asterisk`, identisch bereitgestellt) und den gleichen *Status* – was der nächste Punkt ist.

### Externalize state with PJSIP Realtime

Active/Standby funktioniert nur, wenn der Standby von denselben Endpunkten und Registrierungen weiß wie der aktive Knoten. Der Weg, dies zu erreichen, besteht darin, **aufzuhören, Statusdaten in flachen Dateien auf einer Box zu halten** und sie in eine geteilte Datenbank zu verschieben, die beide Knoten lesen. **PJSIP Realtime** (Sorcery, unterstützt durch eine Datenbank) tut genau dies: Endpunkte, AORs, Auths – und, was wichtig ist, **Registrierungen** (die `ps_contacts`-Tabelle) – leben in MySQL/PostgreSQL anstelle von `pjsip.conf` und lokalem Speicher. Beide Asterisk-Knoten zeigen auf dieselbe Datenbank, sodass ein Telefon, das über einen Knoten registriert wurde, für den anderen sichtbar ist. Dies wird in *Asterisk Real-Time* (Abschnitt PJSIP Realtime / Sorcery) behandelt; hier ist der Bereitstellungspunkt, dass **die Externalisierung des Status die Voraussetzung für HA und horizontale Skalierung ist** – ohne sie ist jeder Knoten eine Insel.

Wenden Sie die gleiche Logik auf den Rest Ihres Status an: CDR/CEL in einen geteilten SQL-Speicher, Voicemail auf geteiltem/repliziertem Speicher (oder `ODBC_STORAGE`) und die astdb-Schlüssel, von denen Sie abhängen, in eine Datenbank. Sobald der Status extern ist, werden die Asterisk-Knoten eher zu austauschbaren Front-Ends.

### SIP proxies in front (OpenSIPS)

Um *über* die Kapazität eines Servers hinaus zu skalieren, setzen Sie einen **SIP-Proxy/Load-Balancer** vor einen Pool von Asterisk-Medienservern. **OpenSIPS** ist ein zweckgebundener SIP-Proxy mit sehr hohem Durchsatz (sie verarbeiten Hunderttausende von Registrierungen und routen Signalisierung, ohne Medien zu berühren). Der Proxy präsentiert der Welt eine einzige SIP-Adresse, verwaltet den Registrierungs-/Standortdienst und verteilt Anrufe auf die Asterisk-Backends. Diese Trennung – eine leichtgewichtige Proxy-Ebene, die Registrierung und Routing übernimmt, eine horizontal skalierbare Asterisk-Ebene, die die eigentliche Anrufverarbeitung (IVR, Warteschlangen, Konferenzen, Transkodierung) übernimmt – ist der Weg, wie große Bereitstellungen über eine einzelne Box hinauswachsen. (Die SipPulse-Plattform selbst verwendet OpenSIPS vor ihren Medien-/Anwendungsservern aus genau diesem Grund.)

### Media scaling

Der Proxy verteilt *Signalisierung* kostengünstig; **Medien sind die teure Ressource**. RTP-Relaying und insbesondere das Transkodieren zwischen Codecs (z. B. Opus ↔ G.711) oder das Durchführen großer Konferenzen ist CPU-gebunden und begrenzt einen Server tatsächlich. Strategien:

- **Vermeiden Sie Transkodierung**, wo immer möglich – verhandeln Sie einen gemeinsamen Codec von Ende zu Ende, damit Asterisk nativ bridgt (Pass-Through), anstatt zu transkodieren. Dies ist der größte Gewinn bei der Medienkapazität.
- **Skalieren Sie Medien horizontal**, indem Sie Asterisk-Knoten hinter den Proxy hinzufügen; jeder trägt einen Anteil der gleichzeitigen Anrufe.
- **Lagern Sie Browser-Medien** auf ein dediziertes WebRTC-Gateway (z. B. Janus) aus, damit die PBX nicht auch noch jeden DTLS-SRTP-Stream des Browsers terminiert und relayt – siehe *WebRTC with Asterisk*, das genau diese Asterisk-plus-Gateway-Aufteilung diskutiert.

Bemessen Sie die Kapazität nach **gleichzeitigen Anrufen und Transkodierungslast**, nicht nach registrierten Benutzern – 10.000 registrierte Telefone, die meist im Leerlauf sind, sind weitaus billiger als 200 gleichzeitige transkodierte Konferenzen.

## Cloud hosting

Asterisk auf einer Cloud-VM (AWS, GCP, Azure, einem VPS) zu betreiben, ist üblich und funktioniert gut, aber das Cloud-Netzwerk ist **standardmäßig NAT'd und firewalled**, was mit SIP kollidiert. Die folgenden Punkte sind die bereitstellungsspezifischen Bedenken.

### NAT and the SDP

Eine Cloud-VM hat fast immer eine **private** IP auf ihrer NIC und eine separate **öffentliche** IP, die der Provider darauf NATet. Wenn Asterisk die private IP im SDP bewirbt, senden entfernte Telefone RTP in ein schwarzes Loch – das klassische Symptom für einseitiges/kein Audio. Teilen Sie PJSIP seine öffentliche Identität am Transport mit:

```
[transport-udp]
type=transport
protocol=udp
bind=0.0.0.0:5060
external_media_address=203.0.113.10      ; the VM's PUBLIC IP
external_signaling_address=203.0.113.10
local_net=10.0.0.0/8                     ; your private/VPC range(s)
```

`external_*` lässt Asterisk die Adresse umschreiben, die es öffentlichen Peers bewirbt, während `local_net` ihm mitteilt, welche Peers lokal sind (und *nicht* umgeschrieben werden sollten). Dies ist dieselbe NAT-Handhabung, die oben für das Bridged-Docker-Networking diskutiert wurde – eine Cloud-VM befindet sich im Grunde hinter NAT.

### Firewall and the RTP range

Zwei Firewalls gelten normalerweise auf einer Cloud-VM: die Sicherheitsgruppe / Netzwerk-ACL des **Providers** und die iptables des **Hosts**. Beide müssen dieselben Ports öffnen, und die Richtlinie ist die aus dem Sicherheitskapitel. Das gerettete Regelsatz der 1. Auflage (`docs/legacy-labs/configs/Lab7/rules.v4`) fängt die Form ein – akzeptiere SIP und den RTP-Bereich, akzeptiere established/related, verwerfe den Rest:

```
-A INPUT -p udp -m udp --dport 5060 -j ACCEPT
-A INPUT -p udp -m udp --dport 10000:20000 -j ACCEPT
-A INPUT -i lo -j ACCEPT
-A INPUT -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
-A INPUT -j DROP
```

Zwei Korrekturen, die das Sicherheitskapitel vornimmt und die hier wichtig sind: Öffnen Sie **5061 auf TCP** (nicht UDP), wenn Sie SIP/TLS betreiben, und denken Sie daran, dass der RTP-UDP-Bereich in Ihrer Firewall exakt mit `rtpstart`/`rtpend` in `rtp.conf` übereinstimmen muss – derselbe Bereich, den Sie in einem Container veröffentlichen. Duplizieren Sie den iptables/Fail2Ban-Build hier nicht; **folgen Sie den Firewall-, Fail2Ban- und TLS/SRTP-Abschnitten von *Asterisk Security*** (Fail2Ban überwacht den `security`-Logger-Kanal, den das Labor bereits in `logger.conf` aktiviert) und wenden Sie diese Richtlinie sowohl in der Host-Firewall als auch in der Cloud-Sicherheitsgruppe an.

### Latency, region and the SBC

- **Wählen Sie eine Region in der Nähe Ihrer Benutzer.** Sprache ist latenzempfindlich – eine einseitige Mund-zu-Ohr-Latenz über ~150 ms ist spürbar. Hosten Sie die VM in der Region, die Ihren Telefonen und Trunks am nächsten liegt; kontinentübergreifende Medien sind hörbar schlechter.
- **Setzen Sie einen SBC für jede internetseitige Bereitstellung davor.** Ein **Session Border Controller** terminiert SIP/RTP am Rand, verbirgt Ihre Topologie, normalisiert NAT und absorbiert DoS- und Scan-Verkehr, bevor er Asterisk erreicht. Die Kernempfehlung des Sicherheitskapitels – *setzen Sie rohes Asterisk nicht dem Internet aus* – gilt doppelt in der Cloud, wo die öffentliche IP Ihrer VM innerhalb von Minuten nach dem Hochfahren gescannt wird. Ein SBC (oder zumindest ein gehärteter SIP-Proxy wie OpenSIPS plus Fail2Ban) ist der Standard-Rand.

## Summary

Bereitstellung ist der Punkt, an dem ein funktionierender Dialplan zu einem zuverlässigen Dienst wird. Führen Sie Asterisk auf einer VM unter **systemd** als **Nicht-Root**-Benutzer aus, lassen Sie die `Restart=` der Unit es am Leben erhalten (safe_asterisk ist überholt) und verwenden Sie `core reload` anstelle von `systemctl restart` für Konfigurationsänderungen. **Containerisierung** mit Docker – wie das Labor des Buches es tut – gibt Ihnen ein unveränderliches, fixiertes Image mit Konfiguration, die von einem git'd `/etc/asterisk` **bind-gemountet** wird; der Haken sind Medien, also verwenden Sie entweder **Host-Networking** oder veröffentlichen Sie einen RTP-Portbereich, der **exakt mit `rtp.conf` übereinstimmt**, und mounten Sie **persistente Volumes** für Spool/Voicemail/astdb, damit der Status ein Redeploy überlebt. Behandeln Sie Konfiguration als Code und **sichern Sie den Status**, den die Konfiguration nicht erfasst: Voicemail, Aufzeichnungen, `astdb.sqlite3` und CDR/CEL. **Beobachten** Sie das System auf vier Ebenen – die CLI (`core show channels`, `pjsip show endpoints`) für die Live-Ansicht, **CDR/CEL** für die Historie, **AMI/ARI** für programmatische Ereignisse und den **`res_prometheus`**-Exporter in Grafana für Dashboards und Alarme – während Sie AMI/ARI aus dem öffentlichen Internet heraushalten. Um **am Laufen zu bleiben**, führen Sie Active/Standby mit einer **Floating IP** aus (unter Inkaufnahme, dass Failover Live-Anrufe abbricht); um zu **wachsen**, externalisieren Sie den Status mit **PJSIP Realtime**, stellen Sie einen Pool von Medienservern mit **OpenSIPS** voran und minimieren Sie Transkodierung, da **Medien – nicht Registrierungen – das sind, was einen Server begrenzt**. Behandeln Sie die VM in der **Cloud** schließlich als hinter NAT befindlich (`external_media_address`, `local_net`), öffnen Sie die Firewall gemäß dem Sicherheitskapitel sowohl in der Host- als auch in der Provider-Sicherheitsgruppe, wählen Sie eine Region mit geringer Latenz und setzen Sie niemals rohes Asterisk aus – platzieren Sie einen **SBC** am Rand.

## Quiz

1. Was ersetzt auf einem systemd-Host die Aufgabe des alten `safe_asterisk`-Wrappers, einen abgestürzten Asterisk neu zu starten?
   - A. Ein Cron-Job
   - B. Die `Restart=`-Direktive der Unit-Datei
   - C. `systemctl enable`
   - D. Die astdb
2. Um eine Konfigurationsänderung auf einen laufenden Asterisk anzuwenden, **ohne Anrufe abzubrechen**, sollten Sie:
   - A. `systemctl restart asterisk`
   - B. Den Server neu starten
   - C. `asterisk -rx 'core reload'`
   - D. Das Container-Image neu bauen
3. Ein containerisierter (bridged-network) Asterisk verbindet Anrufe, hat aber **kein Audio**. Die wahrscheinlichste Ursache ist:
   - A. Der Dialplan ist falsch
   - B. Der veröffentlichte RTP-UDP-Portbereich stimmt nicht mit `rtpstart`/`rtpend` in `rtp.conf` überein
   - C. CDR ist deaktiviert
   - D. Die CLI ist nicht erreichbar
4. Welche Verzeichnisse müssen als **persistente Volumes** gemountet werden, damit ein Container-Redeploy keine Statusdaten verliert? (alle zutreffenden ankreuzen)
   - A. `/var/spool/asterisk` (Voicemail, Aufzeichnungen)
   - B. `/var/lib/asterisk` (astdb)
   - C. `/etc/asterisk` (bereits vom Host bind-gemountet)
   - D. `/usr/sbin`
5. Welcher CLI-Befehl gibt die Live-Anzahl der aktiven Anrufe aus?
   - A. `cdr show status`
   - B. `core show channels`
   - C. `pjsip show transports`
   - D. `module show like prometheus`
6. In Asterisk 22 ist der unterstützte Weg, Anruf-/Kanalmetriken für einen Prometheus/Grafana-Stack offenzulegen:
   - A. Parsen der `full`-Logdatei
   - B. Das `res_prometheus.so`-Modul
   - C. AGI-Skripte
   - D. Es gibt keinen
7. Was ist die Voraussetzung sowohl für HA-Failover als auch für horizontale Skalierung über mehrere Asterisk-Knoten hinweg?
   - A. Ausführung als root
   - B. Externalisierung des Status (z. B. PJSIP Realtime-Registrierungen in einer geteilten Datenbank)
   - C. Deaktivierung von CDR
   - D. Verwendung von Bridged Networking
8. Welche Ressource begrenzt am direktesten, wie viele gleichzeitige Anrufe ein Asterisk-Server verarbeiten kann?
   - A. Die Anzahl der registrierten Benutzer
   - B. Medienverarbeitung, insbesondere Transkodierung
   - C. Die Größe von `/etc/asterisk`
   - D. Das CDR-Backend
9. Welche `pjsip.conf`-Transporteinstellungen auf einer Cloud-VM lassen Asterisk seine öffentliche Adresse bewerben, damit entferntes Audio funktioniert? (alle zutreffenden ankreuzen)
   - A. `external_media_address`
   - B. `external_signaling_address`
   - C. `local_net`
   - D. `qualify_frequency`
10. Für eine internetseitige Cloud-Bereitstellung lautet die Grundregel des Sicherheitskapitels:
    - A. Betreiben Sie immer zwei NICs
    - B. Setzen Sie niemals rohes Asterisk dem Internet aus; platzieren Sie einen SBC (oder gehärteten Proxy + Fail2Ban) am Rand
    - C. Verwenden Sie nur UDP
    - D. Deaktivieren Sie TLS

**Antworten:** 1 — B · 2 — C · 3 — B · 4 — A, B · 5 — B · 6 — B · 7 — B · 8 — B · 9 — A, B, C · 10 — B
