<div align="center">

[![English](https://img.shields.io/badge/Lang-English-blue)](README.md)
[![Türkçe](https://img.shields.io/badge/Dil-T%C3%BCrk%C3%A7e-red)](readme/README.tr.md)
[![Deutsch](https://img.shields.io/badge/Sprache-Deutsch-yellow)](readme/README.de.md)
[![Español](https://img.shields.io/badge/Idioma-Espa%C3%B1ol-orange)](readme/README.es.md)
[![Français](https://img.shields.io/badge/Langue-Fran%C3%A7ais-blue)](readme/README.fr.md)
[![Italiano](https://img.shields.io/badge/Lingua-Italiano-green)](readme/README.it.md)
[![Русский](https://img.shields.io/badge/%D0%AF%D0%B7%D1%8B%D0%BA-%D0%A0%D1%83%D1%81%D1%81%D0%BA%D0%B8%D0%B9-lightgrey)](readme/README.ru.md)
[![Українська](https://img.shields.io/badge/%D0%9C%D0%BE%D0%B2%D0%B0-%D0%A3%D0%BA%D1%80%D0%B0%D1%97%D0%BD%D1%81%D1%8C%D0%BA%D0%B0-yellow)](readme/README.uk.md)
[![العربية](https://img.shields.io/badge/%D9%84%D8%BA%D8%A9-%D8%A7%D9%84%D8%B9%D8%B1%D8%A8%D9%8A%D8%A9-green)](readme/README.ar.md)
[![日本語](https://img.shields.io/badge/%E8%A8%80%E8%AA%9E-%E6%97%A5%E6%9C%AC%E8%AA%9E-red)](readme/README.ja.md)
[![한국어](https://img.shields.io/badge/%EC%96%B8%EC%96%B4-%ED%95%9C%EA%B5%AD%EC%96%B4-blue)](readme/README.ko.md)
[![简体中文](https://img.shields.io/badge/%E8%AF%AD%E8%A8%80-%E7%AE%80%E4%BD%93%E4%B8%AD%E6%96%87-red)](readme/README.zh_CN.md)
[![繁體中文](https://img.shields.io/badge/%E8%AA%9E%E8%A8%80-%E7%B9%81%E9%AB%94%E4%B8%AD%E6%96%87-red)](readme/README.zh_TW.md)

</div>

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
