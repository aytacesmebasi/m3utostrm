**[English](README.md)** | [Türkçe](readme/README.tr.md) | [Deutsch](readme/README.de.md) | [Español](readme/README.es.md) | [Français](readme/README.fr.md) | [Italiano](readme/README.it.md) | [Русский](readme/README.ru.md) | [Українська](readme/README.uk.md) | [العربية](readme/README.ar.md) | [日本語](readme/README.ja.md) | [한국어](readme/README.ko.md) | [简体中文](readme/README.zh_CN.md) | [繁體中文](readme/README.zh_TW.md)

<h1 align="center">M3U to STRM Converter</h1>

<p align="center">
  <strong>A powerful tool to convert your IPTV M3U playlists into STRM files for media centers like Kodi, Jellyfin, and Emby with rich TMDb metadata.</strong>
</p>

## Features
- **Automatic STRM Generation:** Converts M3U links to STRM files organized by Movies, Series, and XXX.
- **Rich Metadata & Images:** Downloads .nfo files, posters, fanarts, clearlogos, discarts, and thumbnails.
- **Smart Matching:** Uses advanced algorithms to match corrupted or complex movie/series names with TMDb.
- **Multi-language Support:** Interface available in 13 languages.
- **Resumable Processing:** Automatically remembers where it left off and avoids duplicating existing files.
- **Auto-Sync:** Background automation to keep your STRM library up to date at a specific time daily.

## Installation
1. Clone the repository: `git clone https://github.com/aytacesmebasi/m3utostrm.git`
2. Install dependencies: `pip install -r requirements.txt` (or run install.bat on Windows)
3. Run the application: `python main.py`

## Usage
1. Go to the **Settings** tab.
2. Enter your IPTV details (URL, username, password) or select a local M3U file.
3. Enter your TMDB and Fanart.tv API keys.
4. Go to the **M3U Processing Engine** tab and click **Start Processing**.

## License
This project is open-source and free to use.
