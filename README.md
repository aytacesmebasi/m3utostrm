- [English](./README.md)
- [Türkçe](./readme/README.tr.md)

# m3utostrm
This project is designed to learn chatgpt, iptv-org and tmdb APIs.

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
