README.ge.md

Dieses Projekt wurde vorbereitet, um die APIs chatgpt, iptv-org und tmdb zu erlernen. Die Codes wurden vollständig von chatgpt geschrieben, daher weiß ich nicht, was fehlt, was zu viel ist oder was falsch ist. Ich weiß nicht, ob ich in Zukunft irgendwelche Vorkehrungen für Ihre Anfragen treffen kann.

Es verwendet Python, um den Inhalt von „.m3u“-Dateien zu scannen, die von IPTV-Dienstanbietern heruntergeladen wurden, und „.strm“-Dateien für Filme und Fernsehsendungen zu erstellen. Es erstellt außerdem „.nfo“-Dateien mit der TMDB-API und organisiert TV-Sendungen mit der IPTVORG-API in „.m3u“-Dateien.

Die Anwendung folgt dem folgenden Pfad, um diese Vorgänge auszuführen:
1) Installieren Sie die zu verwendenden Python-Bibliotheken, falls diese nicht installiert sind.

2) Lädt die „.m3u“-Datei mit den vom Benutzer bereitgestellten IPTV-Anbieterinformationen herunter und benennt sie entsprechend dem Datum und der Uhrzeit, zu der die Anwendung ausgeführt wird.

3) Wenn sich in dem Ordner, in dem sich die heruntergeladene „.m3u“-Datei befindet, keine anderen „.m3u“-Dateien befinden, wird sie auch als „tobeprocess.m3u“-Datei gespeichert.

4) Wenn sich in dem Ordner, in dem sich die heruntergeladene „.m3u“-Datei befindet, weitere „.m3u“-Dateien befinden, wird die aktuellste anhand ihrer Namen ermittelt.

5) Es speichert die URL-Zeilen, die sich nicht in der aktuellsten gefundenen „.m3u“-Datei, sondern in der neu heruntergeladenen „.m3u“-Datei befinden, als „tobeprocess.m3u“-Datei.

6) Es verfolgt die verbleibende Anzahl an Transaktionen, indem es die URLs in der Datei „tobeprocess.m3u“ zählt.

7) Erstellt „Filme“-Ordner für Filme, „Serien“-Ordner für Fernsehserien und „Porno“-Ordner für Pornoinhalte, um „.strm“- und „.nfo“-Dateien zu speichern.

8) Bearbeitet die Namen von IPTV-Kanalsendungen mit dem Suffixmuster im Code,

9) Erstellt „.strm“-Dateien im Ordner „porn“ für „urls“, deren Benennung für die Benennung von Pornos geeignet ist,

10) Mithilfe des Tmdb-API-Schlüssels werden die verbleibenden „URLs“ in Filme und Fernsehserien unterteilt.

11) Erstellt einen Ordner mit einem eigenen Namen für jeden Film im Ordner „movies“ und erstellt eine „.strm“-Datei, in die die „URL“ des Films geschrieben wird, sowie eine „.nfo“-Datei mit Informationen aus dem TMDB-Site,

12) Erstellt einen Ordner mit einem eigenen Namen für jede Serie innerhalb des Ordners „Series“, dieser Ordner erstellt auch einen Ordner für die Staffeln und erstellt eine „.strm“-Datei, in die die „URL“ der Serie geschrieben wird und ein „ .nfo‘-Datei mit den von der tmdb-Site erhaltenen Informationen,

13) Erstellt eine neue Datei mit dem Namen „updated_channels.m3u“ für IPTV-Kanalübertragungen in der heruntergeladenen „.m3u“-Datei und bearbeitet deren Inhalt mit der iptv-org-API.


Geplante Verbesserungen;
- Option zum Herunterladen der „.m3u“-Datei oder zum Verarbeiten einer vorhandenen Datei,
