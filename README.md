- [English](./README.md)
- [Türkçe - Turkish](./readme/README.tr.md)
- [Русский - Russian](./readme/README.ru.md)
- [中國人 - Chinese](./readme/README.ch.md)
- [Español - Spanish](./readme/README.es.md)
- [Deutsch - German](./readme/README.ge.md)
- [Italiano - Italian](./readme/README.it.md)
- [日本語 - Japanese](./readme/README.ja.md)

# m3utostrm
This project is designed to learn chatgpt, iptv-org and tmdb APIs. The codes are completely written by chatgpt, so I don't know what's missing, what's extra or what's wrong. I don't know if I can edit it for any requests in the future. In the latest m3utostrm.py file, all the explanations, directions and settings are in English. But in the old versions in the 'old_versions' folder, it says my own language, Turkish. If this will be a problem for those who want to use the old versions, I'm sorry about that.

It uses Python to scan the contents of '.m3u' files downloaded from IPTV service providers and create '.strm' files for movies and TV shows. It also creates '.nfo' files using the TMDB API and organizes TV broadcasts in '.m3u' files with the IPTVORG API.

The application follows the following path to perform these operations;
1) If the python libraries to be used are not installed, it loads them,

2) Downloads the '.m3u' file with the iptv provider information provided by the user, naming it according to the date and time the application was run,

3) If there are no other '.m3u' files in the folder where the downloaded '.m3u' file is located, it also saves it as the 'tobeprocess.m3u' file,

4) If there are other '.m3u' files in the folder where the downloaded '.m3u' file is located, it finds the most recent one by looking at their names,

5) Saves the url lines that are not in the most recent '.m3u' file it finds but are in the newly downloaded '.m3u' file as the 'tobeprocess.m3u' file,

6) Counts the urls in the 'tobeprocess.m3u' file and keeps track of the remaining number of processes,

7) Saves '.strm' and '.nfo' files as 'movies' for movies, creates folders for series 'series' and 'porn' for porn content,

8) Edits the names of iptv channel broadcasts with the suffix pattern found in the code,

9) Creates '.strm' files in the 'porn' folder for 'urls' that are suitable for porn naming,

10) Separates the remaining 'urls' as movies and series by using the tmdb api key,

11) Creates a folder with its own name for each movie in the 'movies' folder and creates a '.strm' file containing the 'url' of the movie and an '.nfo' file containing the information obtained from the tmdb site,

12) Creates a folder with its own name for each series in the 'series' folder, creates a folder for seasons and creates a '.strm' file containing the 'url' of the series and an '.nfo' file containing the information obtained from the tmdb site,

13) Downloaded Creates a new file named 'updated_channels.m3u' for iptv channel broadcasts in '.m3u' file and edits its content with iptv-org api,

Developments planned to be made;
- Option to download '.m3u' file or process existing file,
