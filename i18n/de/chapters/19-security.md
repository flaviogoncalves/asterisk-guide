# Asterisk Security

Seit Beginn ist das Thema Sicherheit für Asterisk von entscheidender Bedeutung. SIP, Session Initiation Protocol, ist das am häufigsten angegriffene Protokoll im Internet laut CERT.BR. Jeder, der einen Honeypot betreibt, kann das bestätigen. Das Problem des Internet Revenue Share Fraud ist sehr ernst und kann zu Verlusten in Höhe von mehreren hunderttausend Dollar führen. Sie sollten niemals einen Asterisk‑Server, der mit dem Internet verbunden ist, ohne geeignete Sicherheitsmaßnahmen installieren. In diesem Kapitel lernen Sie, wie Sie die wichtigsten Angriffstypen, denen Sie ausgesetzt sein können, erkennen und wie Sie sie mithilfe einer geeigneten Sicherheitsrichtlinie verhindern. Zu guter Letzt erfahren Sie, wie Sie die vorgeschlagene Sicherheitsrichtlinie implementieren.

Dieses Kapitel richtet sich an **Asterisk 22 LTS**, bei dem PJSIP (`res_pjsip` / `chan_pjsip`) der einzige SIP‑Kanal ist. (Der alte `chan_sip`‑Treiber wurde in Asterisk 21 entfernt — siehe das Kapitel *Legacy Channels*, wenn Sie ein älteres System migrieren.) Eine sicherheitsrelevante Konsequenz: Fehlgeschlagene Authentifizierungen werden jetzt über das Asterisk **security event framework** und den dedizierten `security`‑Logger‑Kanal ausgegeben, was die Konfiguration von Fail2Ban ändert (später in diesem Kapitel behandelt).

## Ziele

Am Ende dieses Kapitels sollten Sie in der Lage sein:

- Die wichtigsten Angriffstypen zu identifizieren, die häufig gegen Asterisk-Server gerichtet werden
- Eine effektive Sicherheitspolitik zu definieren
- Die Sicherheitspolitik umzusetzen
- IPTABLES für Asterisk zu installieren und zu konfigurieren
- Fail2Ban für Asterisk zu installieren und zu konfigurieren
- TLS und SRTP für Verschlüsselung zu installieren und zu konfigurieren

## Hauptangriffe auf die IP-Telefonie

Die Hauptangriffe auf die IP‑Telefonie können als DOS/DDOS, Service‑Diebstahl/Toll Fraud und Abhören klassifiziert werden. Einige der Bezeichnungen können verwirrend sein und verschiedene Quellen haben manchmal unterschiedliche Namen für denselben Angriff. Service Theft, Toll Fraud, Internet Revenue Share Fraud, Phone Fraud sind verschiedene Bezeichnungen für Hacker, die Ihre PBX nutzen, um Verkehr zu einer Premium‑Rate‑Nummer zu leiten und Rückvergütungen vom Anbieter zu erhalten.

### DDoS/DOS

Denial of Service und Distributed Denial of Service sind beliebte Angriffe auf jede IT‑Infrastruktur. Es ist nicht anders bei SIP und anderen Voice over IP‑Protokollen. Distributed denial of service wird in der Regel von einem Botnet durchgeführt, während DOS nur von einem einzelnen Computer ausgeführt wird. Im Februar 2011 führte das Sality‑Botnet einen heimlichen, koordinierten Scan des gesamten IPv4‑Adressraums durch, um nach verwundbaren SIP‑Servern zu suchen — Forscher, die das UCSD Network Telescope beobachteten, schrieben dies etwa drei Millionen unterschiedlichen Quell‑IPs zu, die UDP‑Port 5060 ansprachen, höchstwahrscheinlich um SIP‑Konten für Toll‑Fraud zu bruteforcen.[^sality]

[^sality]: A. Dainotti et al., „Analyse eines ‘/0’-Stealth-Scans von einem Botnetz“, *IEEE/ACM Transactions on Networking*, 2015 (DOI 10.1109/TNET.2013.2297678).

![Ein Peer-to-Peer-Botnetz, das Tausende von SIP-Registrierungsversuchen an einen Server richtet](../images/19-security-fig01.png)

Der DOS wird normalerweise durch Techniken wie Fuzzing und Flooding angewendet. Flooding kann SIP, IAX, RTP und andere Protokolle verwenden. Sie können den Dienst vollständig stoppen oder die Sprachqualität verschlechtern. Sie sind sehr schwer zu mitigieren, wenn die Ports zum Internet offen sind. Nachfolgend sind einige der von Angreifern verwendeten Werkzeuge aufgeführt.

**Fuzzing:**

- **PROTOS Test Suite (c07-sip)** — von der University of Oulu OUSPG. Sendet tausende fehlerhafte Pakete, um Fehlfunktionen wie einen Buffer Overflow zu provozieren, der die Software stoppt.  
- **Voiper** — erzeugt mehr als 200.000 Tests, die alle SIP‑Attribute abdecken, und prüft, ob Ihr Server die Nachrichten effektiv verarbeiten kann. <http://voiper.sourceforge.net/>

**Überschwemmung:**

- **INVITE Flooder** — überflutet den Server mit SIP INVITE‑Anfragen. <http://www.hackingvoip.com/tools/inviteflood.tar.gz>
- **IAX Flooder** — überflutet den Server mit IAX2‑Verkehr. <http://www.hackingvoip.com/tools/iaxflood.tar.gz>
- **RTP Flooder** — überflutet aktive Mediensitzungen mit RTP‑Paketen, um die Sprachqualität zu verschlechtern. <http://www.hackingvoip.com/tools/rtpflood.tar.gz>

### Mitigationstechniken für DoS/DDoS

Meine Empfehlungen sind

1. Exponieren Sie Ihren Asterisk-Server nicht im Internet, es sei denn, es ist mit angemessenem Schutz (SBC) erforderlich.  
2. Im internen Netzwerk verwenden Sie ein Virtual LAN für Sprache, insbesondere wenn Sie an einer Universität oder Hochschule sind, wo die Nutzerzahl hoch ist.  
3. Verwenden Sie VPN oder TLS für den externen Zugriff.

### Internet-Umsatzbeteiligungsbetrug

Dieser Betrug ist etwas schwierig zu verstehen. Der Schlüssel ist, das Konzept einer International Premium Rate Number (IPRN) zu verstehen.

![Die drei Schritte des Internet Revenue Share Fraud: Kauf einer Premium-Rate-Nummer, Finden eines verwundbaren VoIP-Geräts und Anrufen der Nummer, dann Einziehen der Auszahlung](../images/19-security-fig02.png)

Ein IPRN ist eine Nummer, die Sie bei einigen speziellen Internet‑Telefonunternehmen kostenlos zuweisen können. Suchen Sie nach Internet Premium Rate Number Providers und Sie werden eine Reihe davon finden. Bei diesem Betreiber können Sie beispielsweise eine Nummer in einem Satellitennetzwerk wie Iridium zuweisen, ein Ziel, das dem Anrufer Zehntel von Dollar pro Minute kostet. Der IPRN‑Anbieter zahlt Ihnen einen Prozentsatz des Umsatzes (10 bis 20 % des Einkommens) für jede empfangene Minute zurück.

![Eine IPRN-Anbieter-Preisliste, die Auszahlungsraten pro Land und Testnummern zeigt](../images/19-security-fig03.png)

Nach der Zuweisungsphase versucht der Hacker, einen offenen Asterisk‑Server zu finden, der die zugewiesene IPRN wählen kann. Die vom Hacker kontrollierte PBX des Opfers wird Hunderte von Anrufen zur IPRN‑Nummer tätigen und damit eine große Rückzahlung für den Hacker sowie eine enorme Telefonrechnung für das Opfer erzeugen. Oftmals mehrere hunderttausend Dollar an einem einzigen Wochenende.

Hauptwerkzeuge, die Hacker zum Angriff auf eine PBX verwenden:

1. **SIPVicious**: http://code.google.com/p/sipvicious/. Sipvicious ist ein leicht zu benutzendes Sicherheitstool-Set. Sein Hauptziel ist es, verwundbare PBXs zu erkennen und die SIP‑Passwörter mittels eines Brute‑Force‑Angriffs zu knacken. Das am häufigsten genutzte Tool ist svcrack. Das Tool ist in der Lage, Tausende von Passwörtern pro Sekunde zu testen.  
2. **Phone vulnerabilities**. Ein weiterer von Hackern häufig genutzter Angriffsvektor ist das Telefon selbst. Viele Personen, die Asterisk installieren, ändern das Standardpasswort in der Weboberfläche des Telefons nicht. Sobald diese Telefone im Internet erreichbar sind, können Hacker versuchen, das Standard‑Interface‑Passwort zu verwenden, um die Konfiguration herunterzuladen, in der sie oft das geheime SIP‑Passwort finden.

#### TFTPDiebstahl:

Wenn Sie die automatische Bereitstellung von Telefonen über TFTP verwenden, sind Sie wahrscheinlich für diese Art von Angriff anfällig. TFTP ist eine einfache und unsichere Form eines Dateitransferprotokolls.

![Ein Angreifer lädt erratbare .cfg-Dateien von einem TFTP-Server herunter und sammelt Klartext-Anmeldeinformationen aus den Konfigurationsdateien](../images/19-security-fig04.png)

Der Name der Konfigurationsdateien ist leicht zu erraten, indem man die mac address verwendet und .cfg anhängt (z. B. 001A2B3C4D5E.cfg). Ein erfahrener Hacker kann leicht ein Dienstprogramm erstellen, das alle MAC‑Adressen nacheinander ausprobiert, oder einfach ein Werkzeug dafür herunterladen. Die Konfigurationsdatei ist normalerweise unverschlüsselt und enthält das geheime SIP‑Passwort.

#### Abschwächung von Brute-Force-Angriffen und TFTP-Diebstahl

Um diese Angriffe zu mindern, können Sie die nachstehenden Lösungen anwenden.  

Brute force: Die beste Lösung, um Brute‑Force‑Angriffe zu verhindern, besteht darin, sequentielle unautorisierte Versuche zu unterbinden. Fast jeder Asterisk‑Installer verwendet das Dienstprogramm fail2ban dafür. Wenn fail2ban mehrere Versuche mit falschem Passwort oder falschem Benutzernamen erkennt, sperrt es die IP des Angreifers für eine bestimmte Zeit. Die zweite Maßnahme gegen Brute Force besteht darin, starke Passwörter zu verwenden, die länger als 12 Zeichen sind und mindestens ein Sonderzeichen enthalten.  

Tftptheft: Um TFTPTheft zu verhindern, konfigurieren Sie die Bereitstellung so, dass https mit Name und Passwort verwendet wird. Die Datei wird verschlüsselt übertragen und ein Name sowie ein Passwort verhindern, dass Angreifer versuchen, irgendwelche Dateien herunterzuladen.

### Abhören

Wir sehen nicht viele dieser Angriffsarten, weil sie in den meisten Fällen einfach nicht erkannt werden. Abhören ist in einer IP‑Umgebung sehr schwer zu erkennen. Werkzeuge wie UCsniff, die frei verfügbar sind, können in den meisten Netzwerken einen VoIP‑Anruf abhören. Die Haupttechnik besteht darin, ARP‑Spoofing zu verwenden, um den Datenverkehr durch den Computer zu leiten, auf dem UCsniff läuft, und die Anrufe aufzuzeichnen.

#### Minderung von Abhören

Sie können das Abhören verhindern, indem Sie Ihren VoIP‑Verkehr verschlüsseln. Der andere Weg ist, Man‑in‑the‑Middle‑Angriffe (MITM) in Ihrem Netzwerk zu verhindern. ARP‑Inspection ist sehr effektiv, um MITM in Layer‑2‑Netzwerken zu verhindern. Fragen Sie Ihren Netzwerk‑Tech‑Support, um zu verstehen, wie man das implementiert. Später in diesem Buch werden wir lernen, wie man Verschlüsselung auf Basis von TLS und SRRT installiert. Sie können auch ARPWatch verwenden, um zu entdecken, ob jemand das ARP‑Protokoll missbraucht, um Ihr Netzwerk anzugreifen.

## Sicherheitsrichtlinie für Asterisk

Der beste Weg, Sicherheit zu implementieren, ist die Erstellung einer Sicherheitsrichtlinie. Für dieses Training schlage ich eine Sicherheitsrichtlinie für die meisten Asterisk-Installationen vor. Verwenden Sie sie als Ausgangspunkt und passen Sie sie Ihren Bedürfnissen an. Die vorgeschlagene Sicherheitsrichtlinie folgt unten:

1. Keine unnötigen UDP/TCP‑Ports offen
2. Kein Zugriff auf irgendeine Administrationsoberfläche (SSH/HTTPS) aus dem Internet.
3. Für den Zugriff auf SSH und/oder HTTP/HTTPS sollte es explizite Ausnahmen in der IPTABLES‑Firewall geben
4. Starke Passwörter mit 12 Zeichen und mindestens einem Sonderzeichen
5. IP‑Adressen, die sich mehr als 10‑mal bei der Authentifizierung fehlgeschlagen haben, mit Fail2ban sperren
6. Passwortbestätigung für internationale Anrufe
7. Zugriff auf den SIP‑Port auf Ihren bekannten IP‑Adressbereich beschränken

Wenn Sie externen Zugriff auf Ihre PBX benötigen, gibt es zwei Möglichkeiten. Verwenden Sie einen SBC (Session Border Controller), um Ihren Server vor DOS/DDOS zu schützen, oder nutzen Sie ein VPN, wann immer Sie externen Zugriff benötigen. Wenn Sie den Port 5060 offen im Internet lassen, ohne einen SBC oder VPN, sind Sie einem DOS/DDOS‑Angriff ausgesetzt. Das Risiko liegt bei Ihnen.

### PJSIP-Ära-Härtung (Asterisk 22)

Jenseits der Firewall und Fail2Ban bietet der PJSIP‑Stack von Asterisk 22 mehrere konfigurationsbezogene Steuerungen, die Teil Ihrer Sicherheitsrichtlinie sein sollten. Diese ergänzen (ersetzen nicht) die oben genannten Netzwerk­kontrollen:

- **Per-endpoint authentication.** Jeder Endpunkt sollte auf einen dedizierten `type=auth`‑Abschnitt mit einem starken, eindeutigen `password` (`auth_type=digest`) verweisen. Verwenden Sie niemals dieselben Anmeldedaten für mehrere Endpunkte.  
- **Anonymous handling is built in.** PJSIP gibt nicht preis, ob ein Benutzername existiert, wenn die Authentifizierung fehlschlägt. Um anonyme Anrufe überhaupt zu akzeptieren, müssen Sie explizit einen Endpunkt namens `anonymous` erstellen und `type=identify`‑Abschnitte (basierend auf der Quell‑IP) verwenden, um bekannte Peers Endpunkten zuzuordnen. Wenn Sie keine anonymen Anrufe zulassen wollen, erstellen Sie einfach keinen `anonymous`‑Endpunkt, und nicht zugeordnete Anfragen werden herausgefordert/abgewiesen.  
- **ACLs.** Beschränken Sie, wer einen Endpunkt erreichen kann, mit `/etc/asterisk/acl.conf`‑benannten ACLs, die vom Endpunkt über `acl=` (signalling/source ACL) und `contact_acl=` (beschränkt die Kontakt‑/Registrierungsadresse) referenziert werden. Sie können auch permit/deny direkt am Endpunkt setzen.  
- **`qualify`.** Setzen Sie `qualify_frequency` (und `qualify_timeout`) auf das AOR, damit Asterisk aktiv die Erreichbarkeit registrierter Kontakte überwacht und tote Einträge entfernt.  
- **PJSIP transport hardening / DoS protection.** Der `type=transport` stellt keine client‑seitige Begrenzung pro Transport bereit, sodass der Schutz vor Verbindungsfluten über die Firewall (die iptables/Fail2Ban‑Regeln in diesem Kapitel) erfolgt und nicht über eine PJSIP‑Option. Was der Transport *bietet*, ist die Feinabstimmung von TCP‑Keep‑Alive (`tcp_keepalive_enable`, `tcp_keepalive_idle_time`, `tcp_keepalive_interval_time`, `tcp_keepalive_probe_count`), um tote/halb‑offene Verbindungen zu entfernen, sowie `local_net`/`external_*`‑Einstellungen für korrektes NAT‑Handling. Kombinieren Sie diese mit den Firewall‑Regeln, um Verbindungsflut‑Angriffe abzumildern.  
- **TLS + SRTP for media.** Verschlüsseln Sie das Signalling mit einem TLS‑Transport und die Medien mit `media_encryption=sdes` (oder `dtls` für WebRTC) am Endpunkt — später in diesem Kapitel behandelt.  
- **AMI/ARI access control.** Beschränken Sie das Asterisk Manager Interface (`manager.conf`) und ARI (`ari.conf` / `http.conf`) auf localhost oder ein vertrauenswürdiges Verwaltungsnetzwerk, verwenden Sie starke, eindeutige Secrets, binden Sie den HTTP‑Server an ein privates Interface und stellen Sie diese niemals dem Internet zur Verfügung.

All of the option names above are confirmed against Asterisk 22.10: the `type=transport` section exposes `tcp_keepalive_enable`, `tcp_keepalive_idle_time`, `tcp_keepalive_interval_time`, `tcp_keepalive_probe_count`, `tos`, `cos`, `local_net`, and the `external_*` family, but it has **no** `max_clients` option — connection-flood protection comes from the firewall, not from the transport. The `acl` and `contact_acl` endpoint options take section names from `acl.conf`, and source-IP matching for unauthenticated peers is done with `type=identify` sections (`match=`).

### Entfernen unnötiger Ports

Anstatt alle Schwachstellen aller Asterisk‑Protokolle zu ermitteln, vereinfachen wir das Problem, indem wir die unnötigen Ports entfernen. Um alle vom Asterisk‑Server geöffneten Ports aufzulisten, verwenden Sie:

```
netstat -pantu |grep asterisk
```

Der Output des Befehls wird unten gezeigt.

![netstat output showing the many ports bound by Asterisk, including 4569 (IAX) and 2727 (MGCP)](../images/19-security-fig05.png)

Wenn Sie sich den Output ansehen, werden Sie feststellen, dass viele Ports geöffnet sind. Brauchen wir sie? Nicht unbedingt, 2727 ist das MGCP‑Protokoll (chan_mgcp), 4569 ist das IAX (chan_iax2). Wenn Sie diese Protokolle nicht verwenden, können Sie das Modul einfach aus der Konfigurationsdatei modules.conf entfernen.

Sie werden bemerken, dass Asterisk einen hochnumerierten UDP‑Port bindet. Dieser stammt von `res_pjsip`'s Resolver, der ausgehende DNS‑Abfragen stellt (der Quellport ist ephemer, wie bei jeder Client‑DNS‑Abfrage), nicht von einem eingehenden Listener – Ihre Firewall muss nur **established/related** Rückverkehr dafür zulassen (die iptables `conntrack ESTABLISHED,RELATED`‑Regel unten deckt das bereits ab). Sie müssen **nicht** einen breiten eingehenden hoch‑UDP‑Bereich nur für PJSIP DNS öffnen.

Um die unnötigen Ports zu entfernen, deaktivieren Sie die Module, die Sie nicht nutzen. Bearbeiten Sie die Datei modules.conf und fügen Sie `noload`‑Zeilen für die Kanäle und Protokolle hinzu, die Sie nicht verwenden. **Laden Sie** `res_pjsip`, `res_pjproject`, oder `chan_pjsip` **nicht** mit noload – diese werden für SIP in Asterisk 22 benötigt.

```
; res_pjsip / res_pjproject / chan_pjsip are REQUIRED in Asterisk 22 - keep them loaded
noload => chan_iax2.so
noload => chan_unistim.so
```

(In Asterisk 22 müssen Sie **nicht** mehr `chan_mgcp` oder `chan_skinny` noloaden — diese Treiber wurden in Asterisk 21 *entfernt* und sind in einem Standard‑Build von 22 nicht mehr enthalten.) Mit den obigen Anweisungen habe ich alle unnötigen Kanäle entfernt und nur PJSIP beibehalten. Sie können beliebige Protokollmodule auswählen, entfernen Sie einfach die nicht genutzten. Das Ergebnis ist im Screenshot unten zu sehen — nur der SIP‑Port (5060), der von Ihrem PJSIP‑Transport gebunden wird, ist jetzt eingehend erreichbar.

![netstat‑Ausgabe nach Deaktivierung der nicht genutzten Module: nur UDP‑Port 5060 bleibt von Asterisk gebunden](../images/19-security-fig06.png)

### Implementierung der Sicherheitsrichtlinie mit IPTABLES

IPTABLES bzw. netfilter ist eine Standard‑Firewall, die in den meisten Linux‑Distributionen vorhanden ist. In diesem Labor konfigurieren wir iptables und fail2ban. Ziel ist es, die empfohlene Sicherheitsrichtlinie für Asterisk umzusetzen und sämtlichen unnötigen Datenverkehr zu blockieren. Folgen Sie den nachstehenden Schritten:

1. Blockieren Sie gesamten externen Datenverkehr
2. Erlauben Sie SSH‑Verkehr von einem internen Netzwerk oder einem einzelnen Host
3. Erlauben Sie SIP‑Verkehr über UDP und TCP auf den Port 5060
4. Erlauben Sie RTP‑Verkehr im UDP‑Medienport‑Bereich. Es gibt keinen einzigen eingebauten Standard — Asterisk’s eigene `rtp.conf` greift auf die Ports 5000–31000 zurück, wenn nichts konfiguriert ist, aber die mitgelieferte `rtp.conf.sample` konfiguriert `rtpstart=10000` / `rtpend=20000`, sodass wir hier diesen Beispiel‑Bereich verwenden. Passen Sie Ihre Firewall‑Regel an das an, was Sie tatsächlich in `rtpstart`/`rtpend` in `rtp.conf` festgelegt haben.

Stellen Sie sicher, dass Sie Konsolenzugriff auf den Server haben; Sie wollen sich nicht selbst aus dem System aussperren. Seien Sie vorsichtig.

1. Installieren Sie das Paket net‑persistent.```
   sudo apt-get install iptables-persistent
   ```

2. Erlaube gesamten Datenverkehr von der Loopback```
   sudo iptables -I INPUT -i lo -j ACCEPT
   sudo iptables -I OUTPUT -o lo -j ACCEPT
   ```

3. Erlaubte etablierte Verbindungen```
   sudo iptables -I INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
   ```

4. Erlaube SSH/HTTPS‑Verkehr vom Netzwerk 192.168.0.0```
   sudo iptables -I INPUT -p tcp -s 192.168.0.0/16 --dport 22 -m conntrack --ctstate
   NEW,ESTABLISHED -j ACCEPT
   sudo iptables -I INPUT -p tcp -s 192.168.0.0/16 --dport 443 -m conntrack --ctstate
   NEW,ESTABLISHED -j ACCEPT
   ```

5. Fügen Sie die Asterisk-Regeln ein```
   sudo iptables -I INPUT -p udp -m udp --dport 5060 -j ACCEPT
   sudo iptables -I INPUT -p tcp -m tcp --dport 5060 -j ACCEPT
   sudo iptables -I INPUT -p tcp -m tcp --dport 5061 -j ACCEPT
   sudo iptables -I INPUT -p udp -m udp --dport 10000:20000 -j ACCEPT
   ```

   Note that port 5061 (SIP over TLS) is **TCP**, not UDP. The rules above open 5060 on both UDP and TCP and 5061 on TCP. If you only run TLS, you can drop the plain 5060 rules entirely. Only open the ports your PJSIP transports actually bind to.

   `-I` means PREPEND

6. The last rule has to be a drop```
   sudo iptables -A INPUT -j DROP
   ```

`-A` bedeutet APPEND. Hinweis: Achten Sie beim Pflegen neuer Regeln darauf, dass Sie Regeln vor dem DROP hinzufügen müssen. Verwenden Sie PREPEND für neue Regeln `-I`

7. Speichern Sie die Regeln und starten Sie iptables neu```
   sudo iptables-save >/etc/iptables/rules.v4
   sudo /etc/init.d/netfilter-persistent restart
   ```

### Verwendung von Fail2Ban zum Blockieren mehrerer fehlgeschlagener Authentifizierungsversuche

Fail2Ban ist fast ein Standard für Asterisk. Die meisten Benutzer setzen es ein, um die Sicherheit zu erhöhen. Dieses Dienstprogramm durchsucht die Asterisk‑Logs nach fehlgeschlagenen Versuchen und sperrt die IP‑Adressen der Angreifer. Im Folgenden gebe ich die Anweisungen zur Installation von Fail2Ban.

In Asterisk 22 meldet PJSIP fehlgeschlagene Authentifizierungen und andere Sicherheitsereignisse über das Asterisk **security event framework**, das in den dedizierten **`security`**‑Logger‑Kanal geschrieben wird. Damit Fail2Ban funktioniert, müssen Sie:

1. Den Sicherheitskanal in `/etc/asterisk/logger.conf` aktivieren. Die Syntax ist `<filename> => <levels>`, also um die Sicherheitsstufe in eine Datei namens `security` zu schreiben:

```
[logfiles]
security => security
```

Führen Sie dann `logger reload` von der CLI aus. Dies erzeugt `/var/log/asterisk/security` mit einer Zeile pro Sicherheitsevent, in der Form:

```
[2026-01-15 10:23:45] SECURITY[1234] res_security_log.c: SecurityEvent="InvalidPassword",...,RemoteAddress="IPV4/UDP/203.0.113.7/5060",...
```

Die Ereignisse, die Fail2Ban interessieren, sind `InvalidPassword`, `ChallengeResponseFailed`, `InvalidAccountID` und `FailedACL`, wobei jedes ein `RemoteAddress="IPV4/UDP/<ip>/<port>"`‑Feld enthält, das den Täter identifiziert. (Beachten Sie, dass die Adresse als `IPV4/UDP/.../...` gekapselt ist, nicht als reine IP — Ihr Filter muss den Host aus diesem String extrahieren.)

2. Richten Sie das `asterisk`‑Jail auf diese Datei (`logpath = /var/log/asterisk/security`) und verwenden Sie einen Filter, der dieses security‑event‑Format analysiert.

Moderne Versionen von Fail2Ban liefern einen `asterisk`‑Filter, dessen `failregex` bereits die oben genannten Ereignisse abgleicht und `<HOST>` aus dem `RemoteAddress`‑Feld extrahiert, zum Beispiel:

```
failregex = ^SecurityEvent="(?:FailedACL|InvalidAccountID|ChallengeResponseFailed|InvalidPassword)".*,RemoteAddress="IPV[46]/[^/"]+/<HOST>/\d+"
```

PBX-Distributionen (FreePBX/Sangoma) liefern äquivalente Filter. Verwenden Sie nach Möglichkeit den mitgelieferten Filter anstelle eines selbstgeschriebenen, da die genauen Ereignis‑Strings versionsabhängig sind. Ein Hinweis, den Sie beachten sollten: Ein kürzlich behobener Sicherheitshinweis (GHSA-5743-x3p5-3rg7) zeigte, dass speziell gestalteter PJSIP‑Verkehr gefälschte Log‑Einträge injizieren konnte — halten Sie sowohl Asterisk als auch Ihren Fail2Ban‑Filter aktuell.

Im Folgenden finden Sie die Anweisungen zur Installation von Fail2Ban

1. Installieren Sie fail2ban unter Linux```
   sudo apt-get install fail2ban
   ```

2. Fail2ban für Asterisk und SSH```
   sudo vi /etc/fail2ban/jails.d/defaults-debian.conf
   ```

   Fügen Sie die folgenden Zeilen hinzu, um fail2ban für ssh und asterisk zu aktivieren```
   [sshd]
   enabled = true
   [asterisk]
   enabled=true
   ```

3. Neustart von fail2ban```
   /etc/init.d/fail2ban restart
   ```

4. Verifizieren. Ändern Sie das Secret von Ihrem Softphone und versuchen Sie, sich 10‑mal erneut zu registrieren. Verwenden Sie `iptables -L`, um zu prüfen, ob die Softphone‑Adresse als blockierte Adresse aufgenommen wurde.  
5. Entfernen Sie die Adresse aus dem Bann (angenommen, die Adresse ist 192.168.0.5)```
   sudo fail2ban-client set asterisk unbanip 192.168.0.5
   ```

Note: In the command replace 192.168.0.5 by the ip address of your phone

### Implementierung von TLS und SRTP

Ich werde diesen Abschnitt in zwei Teile gliedern. Im ersten Teil behandeln wir TLS zur Verschlüsselung der Signalisierung und im zweiten Teil SRTP zur Verschlüsselung der Medien. Das Ziel ist, Asterisk für diese Ressourcen zu konfigurieren.

#### TLS

TLS (Transport Layer Security) ist der Verschlüsselungsmechanismus, der zum Schutz der SIP‑Signalisierung definiert wurde. Die nachstehende Tabelle fasst zusammen, gegen welche Angriffe TLS schützt:

| Type of attack | Protected? | Notes |
|----------------|-----------|-------|
| Signaling attacks | Yes | TLS assures the integrity of the messages |
| Man in the middle | Yes | TLS checks the server certificate |
| Eavesdropping | No | TLS encrypts signaling, not media |

Für die Medien‑(Sprach‑/Video‑)Verschlüsselung verwenden Sie SRTP.

#### Selbstsignierte digitale Zertifikate

Es gibt zwei Arten von Zertifikaten: selbstsignierte und kommerzielle. Selbstsignierte Zertifikate werden von Ihrem eigenen Server signiert, während kommerzielle Zertifikate von einer externen Behörde signiert werden. Für VoIP können Sie Ihre eigene Zertifizierungsstelle sein. Es besteht keine Notwendigkeit für ein externes Zertifikat wie GoDaddy oder Verisign; das wäre ein unnötiger Aufwand. Wir werden unsere eigenen Zertifikate mit ast_tls_cert erzeugen.

#### Konfiguration von TLS mit selbstsignierten Zertifikaten

Im Folgenden finden Sie eine Schritt‑für‑Schritt‑Anleitung zur Implementierung von TLS. Zuerst erzeugen wir die Zertifikate, dann konfigurieren wir den PJSIP TLS‑Transport (siehe „Configuring TLS with chan_pjsip“), und schließlich richten wir das Softphone darauf ein. Wir verwenden das SipPulse Softphone, das TLS und SRTP nativ unterstützt. (Jedes TLS/SRTP‑fähige SIP‑Softphone funktioniert auf dieselbe Weise.)

**Step 1.** Erstellen Sie einen privaten RSA‑Schlüssel mit 3DES‑Verschlüsselung und einer Länge von 4096 Bit für unsere Zertifizierungsstelle. Der unten stehende Befehl im Verzeichnis /usr/src/asterisk-22.x.y/contrib/scripts erzeugt die Certification Authority und das Asterisk‑Zertifikat. Passen Sie die Anweisungen wie üblich an, wenn nötig, da Versionen und Verzeichnisse sich ändern können. Bitte achten Sie genau darauf, was Sie tun. Verwenden Sie Ihre Domain oder IP‑Adresse in der –C‑Option. Der Befehl ast_tls_cert hat drei Optionen.

- -C host or IP address (I have used 192.168.0.74, the IP address of my VM)
- -O Organizational name
- -d Directory where to store the keys

```
mkdir /etc/asterisk/keys
cd /usr/src/asterisk-22.0.0/contrib/scripts
root@asterisk:/usr/src/asterisk-22.0.0/contrib/scripts# ./ast_tls_cert -C 192.168.0.74 -O "AsteriskGuide" -d /etc/asterisk/keys
No config file specified, creating '/etc/asterisk/keys/tmp.cfg'
You can use this config file to create additional certs without
re-entering the information for the fields in the certificate
Creating CA key /etc/asterisk/keys/ca.key
Generating RSA private key, 4096 bit long modulus
........................................................++
........................................................++
e is 65537 (0x010001)
Enter pass phrase for /etc/asterisk/keys/ca.key:
Verifying - Enter pass phrase for /etc/asterisk/keys/ca.key:
Creating CA certificate /etc/asterisk/keys/ca.crt
Enter pass phrase for /etc/asterisk/keys/ca.key:
Creating certificate /etc/asterisk/keys/asterisk.key
Generating RSA private key, 2048 bit long modulus
........................++++++
......................++++++
e is 65537 (0x010001)
Creating signing request /etc/asterisk/keys/asterisk.csr
Creating certificate /etc/asterisk/keys/asterisk.crt
Signature ok
subject=CN = 192.168.0.74, O = AsteriskGuide
Getting CA Private Key
Enter pass phrase for /etc/asterisk/keys/ca.key:
Combining key and crt into /etc/asterisk/keys/asterisk.pem
root@asterisk:/usr/src/asterisk-22.0.0/contrib/scripts#
```

Ich werde kein Client‑Zertifikat erzeugen, weil wir das Zertifikat nicht zur Authentifizierung des Clients verwenden. Der Client muss sein eigenes Zertifikat nicht vorlegen.

**Step 2.** Konfigurieren Sie Asterisk, um unseren Client über TLS zu unterstützen. Dies geschieht in `pjsip.conf` (ein TLS‑Transport plus die Endpoint‑Einstellungen) – die vollständige Konfiguration ist im nächsten Abschnitt „Configuring TLS with chan_pjsip“ zu sehen. Wir authentifizieren nicht mit Zertifikaten, sondern verschlüsseln nur den Datenverkehr.

**Step 3.** Installieren Sie ein TLS‑fähiges SIP‑Softphone (der Autor verwendet das SipPulse Softphone).

**Step 4.** Kopieren Sie die Zertifizierungsstelle auf den Computer, auf dem das Softphone läuft. Nachdem Sie sie installiert haben, kopieren Sie die Datei `/etc/asterisk/keys/ca.crt` auf den Computer, auf dem das Softphone läuft (verwenden Sie scp oder WinSCP unter Windows), falls Sie ein selbstsigniertes Zertifikat benutzen.

**Step 5.** Erstellen Sie das Konto im Softphone. Im Kontobildschirm fügen Sie das Konto wie jedes andere SIP‑Konto normal hinzu. Verwenden Sie das richtige Passwort, die Authentifizierung basiert weiterhin auf dem Passwort.

**Step 6.** Setzen Sie TLS als Transport in den Kontoeinstellungen. Im SipPulse Softphone‑Kontobildschirm (unten) wählen Sie **TLS** als Transport und verwenden Port 5061. Passen Sie Ihre Firewall an, um TCP‑Port 5061 zu öffnen.

![The SipPulse Softphone account screen — enter the Server (your Asterisk IP or domain), Username, Password, and Display Name, then choose the Transport (UDP, TCP, or TLS).](../images/softphone/sipphone-account.png){width=35%}

**Step 7.** Vertrauen Sie der Zertifizierungsstelle. Wenn Ihr Asterisk‑TLS‑Zertifikat von einer öffentlichen CA signiert ist (zum Beispiel Let’s Encrypt – siehe das *Deployment*‑Kapitel), vertraut ein modernes Softphone wie das SipPulse Softphone ihm automatisch über den System‑Zertifikats‑Store, ohne manuelle Importierung. Wenn Sie ein selbstsigniertes Zertifikat verwenden, importieren Sie dessen CA (`/etc/asterisk/keys/ca.crt`) in den Client oder den Betriebssystem‑Trust‑Store, oder akzeptieren Sie es bei der Eingabeaufforderung.

**Step 8.** Sie benötigen **kein** Client‑Zertifikat. Ein verbreiteter Irrglaube ist, dass jedes Telefon ein eigenes Zertifikat zur Authentifizierung benötigt – das ist nicht der Fall. An diesem Punkt verschlüsselt Asterisk nur die Sitzung; die Authentifizierung erfolgt weiterhin über Benutzername und Passwort. Asterisk prüft standardmäßig keine Client‑Zertifikate, sodass kein per‑Client‑Zertifikat verteilt werden muss.

**Step 9.** Nach dem Ändern des Zertifikats oder des Transports starten Sie das Softphone vollständig neu (beenden und neu starten, nicht nur das Fenster schließen), damit es sich über den neuen Transport wieder verbindet.

### Configuring TLS with chan_pjsip

Jetzt lernen wir, wie man PJSIP für TLS konfiguriert. PJSIP ist der einzige SIP‑Channel in Asterisk 22, daher gibt es nichts umzuschalten – stellen Sie lediglich sicher, dass `res_pjsip`, `res_pjproject` und `chan_pjsip` geladen sind. Schritt 1: Bestätigen Sie, dass PJSIP in /etc/asterisk/modules.conf aktiviert ist.

```
; res_pjsip / res_pjproject / chan_pjsip must be loaded (do NOT noload them)
noload => chan_iax2.so
noload => chan_unistim.so
```

Schritt 2: Konfigurieren Sie PJSIP, um TLS zu unterstützen. Fügen Sie einen Abschnitt für den TLS‑Transport in der Datei /etc/asterisk/pjsip.conf hinzu.

```
[transport-tls]
type=transport
protocol=tls
bind=0.0.0.0:5061
cert_file=/etc/asterisk/keys/asterisk.crt
priv_key_file=/etc/asterisk/keys/asterisk.key
method=tlsv1_2
```

Use `method=tlsv1_2` (or `tlsv1_3` if your OpenSSL/PJSIP build supports it) — TLS 1.0/1.1 are obsolete and insecure and should not be used.

Step 3: Configure the endpoint for blink. Edit `pjsip.conf` and edit the section for blink. Let PJSIP choose the transport automatically.

```
[blink]
type=endpoint
aors=blink
auth=blink
context=from-internal
disallow=all
allow=ulaw
dtmf_mode=rfc4733
media_encryption=sdes
[blink]
type=aor
max_contacts=2
remove_existing=yes
[blink]
type=auth
auth_type=digest
username=blink
password=supersecret
```

Schritt 4: Verifizierung. Um zu überprüfen, dass die Registrierung über TLS erfolgt ist, verwenden Sie den folgenden Befehl in der Asterisk‑Konsole.

```text
asterisk*CLI> pjsip show aor blink

      Aor:  <Aor.............................................>  <MaxContact>
    Contact:  <Aor/ContactUri........................> <Hash....> <Status> <RTT(ms)..>
==========================================================================================

      Aor:  blink                                                2
    Contact:  blink/sip:03694827@192.168.0.67:56295;transp 620d91556d NonQual    nan
 ParameterName        : ParameterValue
 ====================================================================
 authenticate_qualify : false
 contact              : sip:03694827@192.168.0.67:56295;transport=tls
 default_expiration   : 3600
 max_contacts         : 2
 maximum_expiration   : 7200
 minimum_expiration   : 60
 qualify_frequency    : 0
 qualify_timeout      : 3.000000
 remove_existing      : true
 support_path         : false
```

### Making secure calls using SRTP

Das für die Medienverschlüsselung verantwortliche Protokoll ist das Secure Real Time Protocol (SRTP), definiert in RFC3711. Einer der Nachteile des Protokolls ist das Fehlen einer standardisierten Methode zum Austausch von Schlüsseln. Asterisk verwendet SDES zum Schlüsselaustausch über das SDP‑Protokoll, das durch die Signalisierungsverschlüsselung mittels TLS geschützt ist. Es gibt auch andere Verfahren wie MIKEY und ZRTP. ZRTP, entwickelt von Philipp Zimmermann, gehört zu den anspruchsvollsten Methoden für Schlüsselaustausch und Medienverschlüsselung. Einige Softphones und Hardphones unterstützen ZRTP. Der Standardweg ist jedoch weiterhin SDES, und Sie werden diese Methode in fast jedem auf dem Markt erhältlichen Telefon finden. Nachfolgend ein Beispiel einer Anfrage mit den im SDP definierten Krypto‑Schlüsseln in den Zeilen a=crypto:1 und a=crypto:2.

```
INVITE sip:8000@192.168.1.237 SIP/2.0
Via:
SIP/2.0/tls
192.168.1.192:65525;rport;branch=z9hG4bKPj9fa224a14b17488ea15625ead833ea3a
Max-Forwards: 70
From:
"Flavio"
<sip:flavio@192.168.1.237>;tag=35afe6cc11274934867b24e43c805638
To: <sip:8000@192.168.1.237>
Contact: <sip:pyhkxnjz@192.168.1.192:65524;transport=tls>
Call-ID: 530a339c72af47f0a76e7ecb2a58ac43
CSeq: 5669 INVITE
Allow: SUBSCRIBE, NOTIFY, PRACK, INVITE, ACK, BYE, CANCEL, UPDATE, MESSAGE
Supported: 100rel
User-Agent: Blink 0.2.5 (Windows)
Authorization: Digest username="flavio", realm="asterisk", nonce="72ff51ad",
uri="sip:8000@192.168.1.237",
response="ba8c10672751baa7007d82eb34e2340e",
algorithm=MD5
Content-Type: application/sdp
Content-Length: 544
v=0
o=- 3509174186 3509174186 IN IP4 192.168.1.192
s=Blink 0.2.5 (Windows)
c=IN IP4 192.168.1.192
t=0 0
m=audio 50004 RTP/SAVP 9 104 103 102 0 8 101
a=rtcp:50005
a=rtpmap:9 G722/8000
a=rtpmap:104 speex/32000
a=rtpmap:103 speex/16000
a=rtpmap:102 speex/8000
a=rtpmap:0 PCMU/8000
a=rtpmap:8 PCMA/8000
a=rtpmap:101 telephone-event/8000
a=fmtp:101 0-15
a=crypto:1
AES_CM_128_HMAC_SHA1_80
inline:WrtZH82ztz93albRNT8o+oMcK9GvlAHRoaR1STvJ
a=crypto:2
AES_CM_128_HMAC_SHA1_32
inline:4Ma9jJOCEEGMPzzkmgyf6ttp1qhN16yumdXB7eRv
a=sendrecv
```

#### SRTP auf Asterisk konfigurieren

Um SRTP auf Asterisk zu konfigurieren, ist es sehr einfach. Setzen Sie `media_encryption=sdes` am Endpunkt; Sie können es auch mit `media_encryption_optimistic=no` erzwingen, sodass unverschlüsselte Medien abgewiesen werden, anstatt stillschweigend erlaubt zu werden. Beachten Sie, dass SDES verlangt, dass die Signalisierung über TLS läuft, damit die Schlüssel nicht im Klartext gesendet werden.

**Schritt 1.** Asterisk-Konfiguration

Setzen Sie das Folgende im `type=endpoint`‑Abschnitt in `pjsip.conf`:

```
[blink]
type=endpoint
aors=blink
auth=blink
context=from-internal
disallow=all
allow=ulaw
transport=transport-tls
media_encryption=sdes
media_encryption_optimistic=no
```

**Step 2.** Softphone-Konfiguration

Im Softphone aktivieren Sie SRTP für die Kontomediadaten (setzen Sie die **SRTP (Media Encryption)**‑Option auf *Mandatory*), damit die Sprache verschlüsselt wird.

![Die SipPulse Softphone Kontoeinstellungen (unterer Abschnitt) — setzen Sie **Transport** auf TLS und **SRTP (Media Encryption)** auf *Mandatory*, damit Signalisierung und Medien beide verschlüsselt sind.](../images/softphone/sipphone-config.png){width=35%}

## Enabling two way authentication for international calls

Manchmal ist der beste Weg, keine internationalen Routen zu haben. Wenn Sie jedoch wirklich internationale Anrufe tätigen müssen, verwenden Sie ein zusätzliches Passwort. Wir werden die Asterisk‑Anwendung **vmauthenticate** einsetzen, um vor dem internationalen Wählen nach dem Voicemail‑Passwort zu fragen. Dies wird im Dialplan in der **extensions.conf** konfiguriert. Siehe das Beispiel unten. So benötigt ein Angreifer, selbst wenn er ein Peer‑Passwort entdeckt oder ein Telefon kompromittiert hat, immer noch das Voicemail‑Passwort, um dieses Ziel zu wählen.

```
exten=_9011.,1,Playback(pleasedialyourvmpassword)
exten=_9011.,2,VMAuthenticate(${CALLERID(num)}@default,s)
exten=_9011.,3,Dial(PJSIP/${EXTEN:1}@my_trunk,20,tT)
exten=_9011.,4,Hangup()
```

`VMAuthenticate` ist weiterhin eine Standard‑Anwendung in Asterisk 22. Der `Dial()` oben leitet den Anruf über einen SIP/PJSIP‑Trunk (`PJSIP/<number>@<trunk>`) weiter, was bei den meisten modernen Installationen die Anbindung an das PSTN darstellt — passen Sie `my_trunk` an Ihren eigenen Trunk‑Namen an und verwenden Sie `DAHDI/g1/...` nur, wenn Sie tatsächlich einen DAHDI‑Span besitzen. Die Toll‑Fraud‑Abwehr im Dialplan — ein zweiter Faktor wie dieser, kombiniert mit der Beschränkung, welche Contexts Ihre ausgehenden und internationalen Routen erreichen können — bleibt einer der wichtigsten Schutzmechanismen, die Sie einsetzen können.

## Zusammenfassung

In diesem Kapitel haben Sie die Risiken kennengelernt, die ein IP PBX bei einer Internetverbindung mit sich bringt. Dann haben wir gelernt, wie wir unser PBX durch die Implementierung einer Sicherheitsrichtlinie schützen können. In dieser Sicherheitsrichtlinie haben wir iptables, fail2ban, TLS, SRTP und eine gegenseitige Authentifizierung für internationale Anrufe implementiert. Ich hoffe, Ihnen hat dieses Kapitel gefallen.

## Quiz

1. Was ist die wichtigste Gegenmaßnahme gegen Internet Revenue Share Fraud?
   - A. SRTP implementieren
   - B. Asterisk aktuell halten
   - C. TLS implementieren
   - D. Starke Passwörter verwenden
2. SIP‑Fuzzing ist definiert als:
   - A. Ein DoS‑Angriff mit fehlerhaften Anfragen und Antworten
   - B. Service-Diebstahl, bei dem Passwörter bruteforced werden
   - C. Abhören aktueller Anrufe
   - D. Ein DDoS mit einer Flut von SIP‑Anfragen
3. TFTPTheft tritt auf, wenn der Server Konfigurationsdateien über TFTP bereitstellt. Sie können dies vermeiden durch:
   - A. FTP
   - B. HTTP
   - C. HTTPS mit Benutzername und Passwort
   - D. SCP
4. Man-in-the-Middle‑Angriffe verwenden eine Technik namens:
   - A. TFTP theft
   - B. ARP‑Spoofing
   - C. MAC‑Poisoning
   - D. dsniff
5. Für SRTP verwendet Asterisk das folgende System zum Austausch von Schlüsseln:
   - A. MIKEY
   - B. SDES
   - C. ZRTP
   - D. Pluto
6. Das Dienstprogramm, das die Zertifizierungsstelle und Zertifikate erzeugt und sich in `/usr/src/asterisk-22.x.y/contrib/scripts` befindet, ist:
   - A. ast_tls_cert
   - B. gen_tls
   - C. gen_ast_tls
   - D. tls_generator
7. Gültige Strategien zur Verhinderung von Abhören (alle zutreffenden auswählen):
   - A. Analoge Abhördetektoren implementieren
   - B. Das ARPwatch‑Dienstprogramm verwenden, um ARP‑Spoofing zu erkennen
   - C. ARP‑Spoofing‑Erkennung in den Switches aktivieren
   - D. SRTP verwenden
8. Asterisk unterstützt starke Authentifizierung durch Überprüfung von Client‑Zertifikaten. (Der PJSIP TLS‑Transport kann das Client‑Zertifikat verlangen und prüfen.)
   - A. Wahr
   - B. Falsch
9. In Asterisk 22, welche PJSIP‑Endpoint‑Einstellung aktiviert die SRTP‑Medienverschlüsselung mittels In‑SDP (SDES)‑Schlüsseln?
   - A. `encryption=yes`
   - B. `media_encryption=sdes`
   - C. `srtp=mandatory`
   - D. `transport=tls`
10. In Asterisk 22 muss Fail2Ban PJSIP‑Fehlauthentifizierungs‑Ereignisse aus dem dedizierten ________‑Logger‑Kanal lesen (aktiviert in `logger.conf`).
   - A. `console`
   - B. `messages`
   - C. `security`
   - D. `verbose`

**Answers:** 1 — D · 2 — A · 3 — C · 4 — B · 5 — B · 6 — A · 7 — B, C, D · 8 — A · 9 — B · 10 — C
