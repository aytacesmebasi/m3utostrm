import os
import re
import subprocess
import sys
import logging
import asyncio
from datetime import datetime
from urllib.parse import quote

# Library list and auto-installer
required_libraries = [
    "requests",
    "aiohttp",
    "aiofiles"
]

def install(package):
    """Installs the specified package."""
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def install_libraries():
    for library in required_libraries:
        try:
            __import__(library)
        except ImportError:
            logging.info(f"{library} is not loaded. Loading...")
            install(library)
        else:
            logging.info(f"{library} is already installed.")

if __name__ == "__main__":
    install_libraries()

# Post-install imports
import requests
import aiohttp
import aiofiles

# Create output_files folder
current_working_directory = os.getcwd()
output_folder_path = os.path.join(current_working_directory, 'output_files')
os.makedirs(output_folder_path, exist_ok=True)

# Logging configuration and filing
logging.basicConfig(
    stream=sys.stdout, 
    format='%(asctime)s - %(levelname)s - %(message)s', 
    level=logging.INFO,
    encoding='utf-8'
)
logger = logging.getLogger()
log_file_path = os.path.join(output_folder_path, 'm3u2strm.log')
file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Version information
logger.info("m3utostrm v3.9 (Refactored)")
logger.info("it processes the differences between the old and new downloaded m3u files")

# User data
tmdb_api_key = 'YOUR_API_KEY'
iptvurl = 'YOUR_IPTV_URL'  # Write your IPTV URL here
iptvusername = 'YOUR_IPTV_USERNAME'   # Write your IPTV username here
iptvpassword = 'YOUR_IPTV_PASSWORD'   # Write your IPTV password here

# Country code to filter
your_language_code = 'TR'

# TMDB Language code for NFO metadata and TMDB searches (ISO 639-1)
tmdb_language = 'tr-TR'

# For those who want to use Group-title translation dictionary for IPTV broadcasts in languages ​​other than English
category_translation = {
    "general": "General",
    "business": "Business",
    "children": "Children",
    "classic": "Classic",
    "comedy": "Comedy",
    "documentary": "Documentary",
    "education": "Education",
    "entertainment": "Entertainment",
    "family": "Family",
    "game": "Game",
    "legislative": "Legislative",
    "lifestyle": "Lifestyle",
    "movies": "Movies",
    "music": "Music",
    "news": "News",
    "religious": "Religious",
    "science": "Science",
    "shop": "Shop",
    "sports": "Sports",
    "travel": "Travel",
    "weather": "Weather"
}

DEFAULT_CATEGORY = "Unknown"

# Global Variables
url_count = 0
remaining_url_count = 0
tmdb_cache = {}  # Cache dictionary for TMDb searches

# Paths
movies_folder_path = os.path.join(output_folder_path, 'movies')
series_folder_path = os.path.join(output_folder_path, 'series')
porn_folder_path = os.path.join(output_folder_path, 'porn')

def translate_category(category):
    return category_translation.get(category.lower(), DEFAULT_CATEGORY)

def update_missing_translations(channels):
    missing_categories = set()
    for channel in channels:
        category = channel.get('group-title', 'Unknown')
        if category.lower() not in category_translation:
            missing_categories.add(category)
    
    if missing_categories:
        logger.info("Missing translations:")
        for category in missing_categories:
            logger.info(f"- {category}")

def parse_filename(filename):
    base, ext = os.path.splitext(filename)
    if len(base) == 10 and base[2].isdigit() and base[4].isdigit() and base[6].isdigit() and base[8].isdigit():
        try:
            g = int(base[:2])
            a = int(base[2:4])
            y = int(base[4:6])
            s = int(base[6:8])
            d = int(base[8:10])
            return (y, a, g, s, d)
        except ValueError:
            return None
    return None

def download_m3u(url, username, password, filename):
    try:
        full_url = f"{url}/get.php?username={username}&password={password}&type=m3u"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
        }
        response = requests.get(full_url, headers=headers)
        response.raise_for_status()
        with open(filename, 'wb') as file:
            file.write(response.content)
        logger.info(f"{filename} was downloaded successfully.")
        return True
    except requests.RequestException as e:
        logger.error(f"Download failed: {e}")
        return False

def extract_lines_from_m3u(file_path):
    urls_with_extinf = {}
    current_extinf = None
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line.startswith("#EXTINF:"):
                current_extinf = line
            elif line and not line.startswith("#"):
                if current_extinf:
                    urls_with_extinf[line] = current_extinf
                current_extinf = None
    return urls_with_extinf

def compare_m3u_files(old_file, new_file):
    old_urls_with_extinf = extract_lines_from_m3u(old_file)
    new_urls_with_extinf = extract_lines_from_m3u(new_file)
    difference = {url: new_urls_with_extinf[url] for url in new_urls_with_extinf if url not in old_urls_with_extinf}
    return difference

def write_new_m3u(difference, output_file):
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write("#EXTM3U\n")
        for url, extinf in difference.items():
            file.write(f"{extinf}\n{url}\n")

def count_urls_in_m3u(m3u_file_path):
    with open(m3u_file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    return sum(1 for line in lines if line.startswith("http"))

def prepare_files():
    global url_count, remaining_url_count
    
    os.makedirs(movies_folder_path, exist_ok=True)
    logger.info(f"Movies Folder created: {movies_folder_path}")
    
    os.makedirs(series_folder_path, exist_ok=True)
    logger.info(f"Series Folder created: {series_folder_path}")
    
    os.makedirs(porn_folder_path, exist_ok=True)
    logger.info(f"Porn Folder created: {porn_folder_path}")

    now = datetime.now()
    formatted_date = now.strftime('%d%m%y%H%M')
    filename = f'{formatted_date}.m3u'
    file_path = os.path.join(output_folder_path, filename)
    
    success = download_m3u(iptvurl, iptvusername, iptvpassword, file_path)
    if not success:
        logger.error("HATA: M3U dosyası indirilemedi! Bağlantı engellendi veya sunucu yanıt vermedi. İşlem sonlandırılıyor.")
        sys.exit(1)
    
    directory = output_folder_path
    files = [f for f in os.listdir(directory) if f.endswith('.m3u') and f != filename]
    
    latest_file = None
    latest_date = None
    for file in files:
        parsed_date = parse_filename(file)
        if parsed_date:
            current_date = datetime(year=2000 + parsed_date[0], month=parsed_date[1], day=parsed_date[2], hour=parsed_date[3], minute=parsed_date[4])
            if latest_date is None or current_date > latest_date:
                latest_date = current_date
                latest_file = file

    if latest_file:
        logger.info(f"Latest file: {latest_file}")
    else:
        logger.error("No valid '.m3u' file found.")
        latest_file = None
        
    m3u_file_path = os.path.join(output_folder_path, 'tobeprocess.m3u')
    
    if latest_file:
        new_urls_not_in_old = compare_m3u_files(os.path.join(directory, latest_file), file_path)
        if new_urls_not_in_old:
            logging.info("URLs and related #EXTINF lines that are not in the old file but are in the new file are written to the new file...")
            write_new_m3u(new_urls_not_in_old, m3u_file_path)
            logging.info(f"New M3U file saved as '{m3u_file_path}'.")
        else:
            logging.info("All URLs are present in old file. Creating empty 'tobeprocess.m3u' file...")
            with open(m3u_file_path, 'w', encoding='utf-8') as file:
                file.write("#EXTM3U\n")
            logging.info(f"Empty M3U file saved as '{m3u_file_path}'.")
        
        os.remove(os.path.join(directory, latest_file))
        logging.info(f"The newest file '{latest_file}' was deleted.")
    else:
        logging.info("The latest file was not found, only the downloaded file is saved as 'tobeprocess.m3u'...")
        with open(file_path, 'r', encoding='utf-8') as new_file:
            new_lines = new_file.readlines()
        with open(m3u_file_path, 'w', encoding='utf-8') as output_file:
            output_file.writelines(new_lines)
        logging.info(f"The downloaded M3U file was saved as '{m3u_file_path}'.")

    url_count = count_urls_in_m3u(m3u_file_path)
    remaining_url_count = url_count
    logging.info(f"There are {url_count} URLs in the file.")
    return m3u_file_path

suffix_pattern = re.compile(r'\s*(\[.*?\])(?:\s*\[.*?\]|\s*H\.265|\s*[A-Z]{2,})?\s*$', re.IGNORECASE)

def is_porn_url(url):
    porn_patterns = [
        r'xxx', r'XxX', r'XXX', r'xxx1', r'XXX\.', r'2xxX', 
        r'porn', r'Porn', r'SEX', r'Adult', r'NSFW', 
        r'pay-per-view', r'live-stream', r'free-videos'
    ]
    combined_pattern = '|'.join(porn_patterns)
    return re.search(combined_pattern, url, re.IGNORECASE) is not None

def sanitize_filename(filename):
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '')
    return filename

def clean_name_for_search(name, is_tv=False):
    # IPTV listelerinde filmin başında yer alan "FR", "DE", "TR" gibi ülke kodlarını temizle
    name = re.sub(r'^(?:FR|DE|TR|EN|IT|ES|RU|US|UK)\s+', '', name, flags=re.IGNORECASE)
    
    if is_tv:
        name = re.sub(r'\s*S\d{2}\s*E\d{2}', '', name, flags=re.IGNORECASE)
    else:
        name = re.sub(r'\s*\(\d{4}\)', '', name)
        name = re.sub(r'\s*[-]?\s*\d{4}', '', name)
    return name.strip()

def extract_year(name):
    match = re.search(r'\s*\((\d{4})\)', name)
    if match:
        return match.group(1)
    match = re.search(r'\b(19\d{2}|20\d{2})\b', name)
    if match:
        return match.group(1)
    return None

def clean_channel_name_for_match(name):
    name = re.sub(r'\[.*?\]', '', name)
    name = re.sub(r'\(.*?\)', '', name)
    name = re.sub(r'\|.*?\|', '', name)
    name = re.sub(r'\b(HD|FHD|UHD|SD|HEVC|H\.265|H265|1080p|720p|VIP|PREMIUM|PLUS)\b', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\b(TR|EN|DE|FR|AT|UK|US)\b', '', name, flags=re.IGNORECASE)
    # Tüm özel karakterleri (nokta, tire, yıldız vs.) silerek harf/rakam tabanlı kusursuz eşleşme sağla
    name = re.sub(r'[^a-zA-Z0-9]', '', name)
    name = name.lower().strip()
    name = name.replace('tv', '')
    return name

def check_channel_match(channel, match_name):
    if clean_channel_name_for_match(channel.get("name", "")) == match_name:
        return True
    if clean_channel_name_for_match(channel.get("id", "")) == match_name:
        return True
    for alt in channel.get("alt_names", []):
        if clean_channel_name_for_match(alt) == match_name:
            return True
    return False

class APIRequestError(Exception):
    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.status_code = status_code

async def fetch_data(session, url):
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.json()
    except aiohttp.ClientResponseError as e:
        if e.status == 404:
            logging.warning(f"API request failed: 404 Not Found - {url}")
            return None
        else:
            logging.error(f"API request failed: {e} - Status Code: {e.status}")
            raise APIRequestError(f"API request failed: {e.message}", status_code=e.status)
    except aiohttp.ClientError as e:
        logging.error(f"API request failed: {e}")
        raise APIRequestError(f"API request failed: {e}")

import itertools

SPECIAL_CHARS_MAP = {
    'tr-TR': ['ı', 'ğ', 'ş', 'ü', 'ö', 'ç'],
    'tr': ['ı', 'ğ', 'ş', 'ü', 'ö', 'ç'],
    'de-DE': ['ä', 'ö', 'ü', 'ß'],
    'de': ['ä', 'ö', 'ü', 'ß'],
    'fr-FR': ['é', 'à', 'è', 'ù', 'â', 'ê', 'î', 'ô', 'û', 'ç'],
    'es-ES': ['ñ', 'á', 'é', 'í', 'ó', 'ú'],
}
UNIVERSAL_SPECIAL_CHARS = list(set([char for chars in SPECIAL_CHARS_MAP.values() for char in chars]))

async def execute_tmdb_search(session, query, search_type, year=None, lang=None):
    if lang is None:
        lang = tmdb_language
    query_encoded = quote(query)
    search_url = f"https://api.themoviedb.org/3/search/{search_type}?api_key={tmdb_api_key}&query={query_encoded}&language={lang}"
    if year:
        if search_type == 'movie':
            search_url += f"&primary_release_year={year}"
        else:
            search_url += f"&first_air_date_year={year}"
            
    try:
        data = await fetch_data(session, search_url)
        results = data.get('results', [])
        if results:
            return results[0]
    except APIRequestError as e:
        logging.error(f"TMDb API request failed: {e}")
    return None

async def search_tmdb(query, is_tv=False, year=None):
    search_type = 'tv' if is_tv else 'movie'
    cache_key = f"{query}_{search_type}_{year}"
    
    if cache_key in tmdb_cache:
        return tmdb_cache[cache_key]

    async with aiohttp.ClientSession() as session:
        # 1. Try original query
        result = await execute_tmdb_search(session, query, search_type, year)
        if result:
            tmdb_cache[cache_key] = result
            return result
            
        # 2. Try handling dots if present
        if '.' in query:
            # Try removing dots
            query_no_dots = query.replace('.', '')
            result = await execute_tmdb_search(session, query_no_dots, search_type, year)
            if result:
                tmdb_cache[cache_key] = result
                return result
                
            # Try replacing with space
            query_space_dots = query.replace('.', ' ')
            result = await execute_tmdb_search(session, query_space_dots, search_type, year)
            if result:
                tmdb_cache[cache_key] = result
                return result

            # Try permutations for special characters
            dot_count = query.count('.')
            if 0 < dot_count <= 5:
                chars_to_try = SPECIAL_CHARS_MAP.get(tmdb_language, SPECIAL_CHARS_MAP.get(tmdb_language.split('-')[0], UNIVERSAL_SPECIAL_CHARS))
                
                # Limit combinations to avoid API bans (max ~100 requests)
                combinations = list(itertools.product(chars_to_try, repeat=dot_count))
                for combo in combinations[:100]:
                    temp_query = query
                    for char in combo:
                        temp_query = temp_query.replace('.', char, 1)
                    
                    result = await execute_tmdb_search(session, temp_query, search_type, year)
                    if result:
                        tmdb_cache[cache_key] = result
                        logging.info(f"TMDB Search Match: Original '{query}' matched as '{temp_query}' using permutations.")
                        return result
                        
        # 3. Try splitting by hyphen (e.g., LocalName - OriginalName)
        if '-' in query:
            parts = [p.strip() for p in query.split('-') if len(p.strip()) > 3]
            for part in parts:
                result = await execute_tmdb_search(session, part, search_type, year)
                if result:
                    tmdb_cache[cache_key] = result
                    return result

        # 4. Fallback to English language search (if the title is in English but our TMDB language is TR)
        if tmdb_language != 'en-US':
            result = await execute_tmdb_search(session, query, search_type, year, lang='en-US')
            if result:
                tmdb_cache[cache_key] = result
                logging.info(f"TMDB Search Match: '{query}' found using en-US fallback.")
                return result

        logging.warning(f"Warning: No results found in TMDb for '{query}'.")
    
    tmdb_cache[cache_key] = None
    return None

async def create_nfo(data, file_path, is_tv=False):
    try:
        if is_tv:
            content = generate_tv_nfo_content(data)
        else:
            content = generate_movie_nfo_content(data)
        
        async with aiofiles.open(file_path, 'w', encoding='utf-8') as nfo_file:
            await nfo_file.write(content)
        logging.info(f"NFO file created: {file_path}")
    except Exception as e:
        logging.error(f"An error occurred: {e}")

def generate_tv_nfo_content(data):
    name = data.get('name', 'Unknown')
    original_name = data.get('original_name', name)
    rating = data.get('vote_average', 'Unknown')
    year = data.get('first_air_date', '')[:4]
    votes = data.get('vote_count', 'Unknown')
    overview = data.get('overview', 'Description not available.')
    poster_path = data.get('poster_path', '')
    backdrop_path = data.get('backdrop_path', '')
    mpaa = 'TV-MA' if data.get('adult') else 'TV-G'
    country = ', '.join(data.get('origin_country', ['Unknown']))
    premiered = data.get('first_air_date', 'Unknown')
    status = data.get('status', 'Unknown')
    tv_id = data.get('id', 'Unknown')
    genre = ', '.join([genre.get('name', 'Unknown') for genre in data.get('genres', [])])
    studio = ', '.join([company.get('name', 'Unknown') for company in data.get('production_companies', [])])
    
    content = f"""
<tvshow>
    <title>{name}</title>
    <originaltitle>{original_name}</originaltitle>
    <sorttitle>{name}</sorttitle>
    <rating>{rating}</rating>
    <year>{year}</year>
    <votes>{votes}</votes>
    <outline>{overview}</outline>
    <plot>{overview}</plot>
    <thumb>https://image.tmdb.org/t/p/original{poster_path}</thumb>
    <fanart>https://image.tmdb.org/t/p/original{backdrop_path}</fanart>
    <mpaa>{mpaa}</mpaa>
    <country>{country}</country>
    <premiered>{premiered}</premiered>
    <status>{status}</status>
    <id>{tv_id}</id>
    <genre>{genre}</genre>
    <studio>{studio}</studio>
"""
    for cast in data.get('credits', {}).get('cast', [])[:10]:
        name = cast.get('name', 'Unknown')
        role = cast.get('character', 'Unknown')
        profile_path = cast.get('profile_path', '')
        content += f"""
    <actor>
        <name>{name}</name>
        <role>{role}</role>
        <thumb>https://image.tmdb.org/t/p/original{profile_path}</thumb>
    </actor>"""

    content += "\n</tvshow>"
    return content

def generate_movie_nfo_content(data):
    title = data.get('title', 'Unknown')
    original_title = data.get('original_title', 'Unknown')
    rating = data.get('vote_average', 'Unknown')
    year = data.get('release_date', '')[:4]
    votes = data.get('vote_count', 'Unknown')
    outline = data.get('overview', 'Description not available.')
    plot = data.get('overview', 'Description not available.')
    tagline = data.get('tagline', 'Unknown')
    runtime = data.get('runtime', 'Unknown')
    poster_path = data.get('poster_path', '')
    backdrop_path = data.get('backdrop_path', '')
    mpaa = 'PG-13' if data.get('adult') else 'G'
    country = ', '.join([country.get('name', 'Unknown') for country in data.get('production_countries', [])])
    premiered = data.get('release_date', 'Unknown')
    status = 'Released' if data.get('status') == 'Released' else 'Unknown'
    imdb_id = data.get('imdb_id', 'Unknown')
    movie_id = data.get('id', 'Unknown')
    genre = ', '.join([genre.get('name', 'Unknown') for genre in data.get('genres', [])])
    studio = ', '.join([company.get('name', 'Unknown') for company in data.get('production_companies', [])])
    trailer = 'https://www.youtube.com/watch?v=' + data.get('videos', {}).get('results', [{}])[0].get('key', '') if data.get('videos', {}).get('results') else 'Unknown'
    director = ', '.join([member.get('name', 'Unknown') for member in data.get('credits', {}).get('crew', []) if member.get('job') == 'Director'])
    credits = ', '.join([member.get('name', 'Unknown') for member in data.get('credits', {}).get('crew', []) if member.get('job') == 'Writer'])
    
    content = f"""
<movie>
    <title>{title}</title>
    <originaltitle>{original_title}</originaltitle>
    <sorttitle>{title}</sorttitle>
    <rating>{rating}</rating>
    <year>{year}</year>
    <votes>{votes}</votes>
    <outline>{outline}</outline>
    <plot>{plot}</plot>
    <tagline>{tagline}</tagline>
    <runtime>{runtime}</runtime>
    <thumb>https://image.tmdb.org/t/p/original{poster_path}</thumb>
    <fanart>https://image.tmdb.org/t/p/original{backdrop_path}</fanart>
    <mpaa>{mpaa}</mpaa>
    <playcount>0</playcount>
    <country>{country}</country>
    <premiered>{premiered}</premiered>
    <status>{status}</status>
    <code>{imdb_id}</code>
    <id>{movie_id}</id>
    <genre>{genre}</genre>
    <studio>{studio}</studio>
    <trailer>{trailer}</trailer>
    <director>{director}</director>
    <credits>{credits}</credits>
"""
    for cast in data.get('credits', {}).get('cast', [])[:10]:
        name = cast.get('name', 'Unknown')
        role = cast.get('character', 'Unknown')
        thumb = cast.get('profile_path', '')
        content += f"""
    <actor>
        <name>{name}</name>
        <role>{role}</role>
        <thumb>https://image.tmdb.org/t/p/original{thumb}</thumb>
    </actor>"""

    content += "\n</movie>"
    return content

async def fetch_iptv_channels(api_url):
    async with aiohttp.ClientSession() as session:
        response = await fetch_data(session, api_url)
        if response:
            logging.info("iptv-org API cache file created")
            return response  # Tüm kanalları döndür (ülke kısıtlaması olmadan)
        else:
            logging.warning("Warning: IPTV-Org API request failed.")
            return []

def extract_media_name(line):
    in_quotes = False
    for i, char in enumerate(line):
        if char == '"':
            in_quotes = not in_quotes
        elif char == ',' and not in_quotes:
            return line[i+1:].strip()
    return line.split(',', 1)[-1].strip()

async def process_extinf_line(extinf_line, url_line, channels_data, output_file):
    media_name = extract_media_name(extinf_line)
    url_line_lower = url_line.lower()
    
    if url_line_lower.endswith('.ts'):
        await handle_ts_url(media_name, url_line, channels_data, output_file)
    else:
        await handle_non_ts_url(media_name, url_line)

async def handle_ts_url(media_name, url_line, channels_data, output_file):
    match_name = clean_channel_name_for_match(media_name)
    bracketsin = extract_bracketsin(media_name)
    
    channel_info = next((channel for channel in channels_data if check_channel_match(channel, match_name)), None)
    if channel_info:
        await write_channel_info(channel_info, media_name, url_line, bracketsin, output_file)
    else:
        await write_default_channel_info(media_name, url_line, bracketsin, output_file)

def extract_bracketsin(media_name):
    bracketsin_match = re.search(r'\[(.*?)\]', media_name)
    return bracketsin_match.group(1).replace(' ', '') if bracketsin_match else ''

async def write_channel_info(channel_info, media_name, url_line, bracketsin, output_file):
    global url_count, remaining_url_count
    channel_name = channel_info.get("name", media_name)
    logo = channel_info.get("logo", "")
    id_ = channel_info.get("id", "")
    is_nsfw = channel_info.get("is_nsfw", False)
    
    categories = ', '.join(channel_info.get("categories", []))
    translated_categories = ', '.join([category_translation.get(cat, cat) for cat in categories.split(', ')])
    group_title = translated_categories if categories else 'Unknown'
    
    content = f"#EXTINF:-1 group-title=\"{group_title}; {bracketsin}\" tvg-id=\"{id_}\" tvg-name=\"{channel_name}\" tvg-logo=\"{logo}\" tvg-country=\"{your_language_code}\" is-nsfw=\"{is_nsfw}\", {media_name}\n{url_line}\n"
    await output_file.write(content)
    
    remaining_url_count -= 1
    logging.info(f"{url_count} / {remaining_url_count} left - URL ends with '.ts' and added: {url_line}")

async def write_default_channel_info(media_name, url_line, bracketsin, output_file):
    global url_count, remaining_url_count
    group_title = 'Unknown'
    content = f"#EXTINF:-1 group-title=\"{group_title}; {bracketsin}\" tvg-name=\"{sanitize_filename(media_name)}\" tvg-country=\"{your_language_code}\" is-nsfw=\"false\", {media_name}\n{url_line}\n"
    
    await output_file.write(content)
    
    remaining_url_count -= 1
    logging.warning(f"{url_count} / {remaining_url_count} remaining - Warning: No IPTV-Org channel information found for '{media_name}'.")

async def handle_non_ts_url(media_name, url_line):
    if is_porn_url(media_name):
        await create_porn_strm(media_name, url_line)
    else:
        is_tv = 'S' in media_name and 'E' in media_name
        search_query = clean_name_for_search(media_name, is_tv=is_tv)
        year = extract_year(media_name)
        tmdb_data = await search_tmdb(search_query, is_tv=is_tv, year=year)
        
        if tmdb_data:
            if is_tv:
                await create_tv_show_files(search_query, tmdb_data, url_line, media_name)
            else:
                await create_movie_files(search_query, tmdb_data, url_line)
        else:
            await create_default_strm(media_name, url_line)

async def create_porn_strm(media_name, url_line):
    global url_count, remaining_url_count
    porn_strm_path = os.path.join(porn_folder_path, f"{sanitize_filename(media_name)}.strm")
    
    if not os.path.exists(porn_strm_path):
        async with aiofiles.open(porn_strm_path, 'w', encoding='utf-8') as porn_strm_file:
            await porn_strm_file.write(url_line)
            remaining_url_count -= 1
            logging.info(f"{url_count} / {remaining_url_count} left - STRM file created for porn: {porn_strm_path}")
    else:
        remaining_url_count -= 1
        logging.info(f"{url_count} / {remaining_url_count} left - STRM file already exists: {porn_strm_path}")

async def create_tv_show_files(show_name, tmdb_data, url_line, media_name):
    global url_count, remaining_url_count
    year = tmdb_data.get('first_air_date', '')[:4]
    
    # TMDB sitesinden gelen temiz ve resmi ismi (eğer varsa) kullan
    clean_show_title = sanitize_filename(tmdb_data.get('name', show_name))
    
    season_episode_match = re.search(r'\s*S(\d{2})\s*E(\d{2})', media_name)
    season = season_episode_match.group(1) if season_episode_match else '01'
    episode = season_episode_match.group(2) if season_episode_match else '01'
    
    show_folder = os.path.join(series_folder_path, f"{clean_show_title} ({year})")
    season_folder = os.path.join(show_folder, f"Season {int(season)}")
    os.makedirs(season_folder, exist_ok=True)
    
    series_nfo_path = os.path.join(show_folder, f"{clean_show_title} ({year}).nfo")
    season_nfo_path = os.path.join(season_folder, f"{clean_show_title} ({year}) S{season}.nfo")
    episode_strm_path = os.path.join(season_folder, f"{clean_show_title} ({year}) S{season}E{episode}.strm")
    episode_nfo_path = os.path.join(season_folder, f"{clean_show_title} ({year}) S{season}E{episode}.nfo")
    
    if not os.path.exists(episode_strm_path):
        async with aiofiles.open(episode_strm_path, 'w', encoding='utf-8') as episode_strm_file:
            await episode_strm_file.write(url_line)
            remaining_url_count -= 1
            logging.info(f"{url_count} / {remaining_url_count} left - STRM file created: {episode_strm_path}")
    else:
        remaining_url_count -= 1
        logging.info(f"{url_count} / {remaining_url_count} remaining - STRM file already exists: {episode_strm_path}")
    
    if not os.path.exists(series_nfo_path) or not os.path.exists(season_nfo_path) or not os.path.exists(episode_nfo_path):
        async with aiohttp.ClientSession() as session:
            show_details_url = f"https://api.themoviedb.org/3/tv/{tmdb_data['id']}?api_key={tmdb_api_key}&language={tmdb_language}&append_to_response=credits,videos"
            show_details_response = await fetch_data(session, show_details_url)
            if show_details_response:
                if not os.path.exists(series_nfo_path):
                    await create_nfo(show_details_response, series_nfo_path, is_tv=True)
                
                season_details_url = f"https://api.themoviedb.org/3/tv/{tmdb_data['id']}/season/{season}?api_key={tmdb_api_key}&language={tmdb_language}"
                season_details_response = await fetch_data(session, season_details_url)
                if season_details_response:
                    if not os.path.exists(season_nfo_path):
                        await create_nfo(season_details_response, season_nfo_path, is_tv=True)
                    
                    episode_details = next((ep for ep in season_details_response.get('episodes', []) if ep['episode_number'] == int(episode)), None)
                    if episode_details and not os.path.exists(episode_nfo_path):
                        await create_nfo(episode_details, episode_nfo_path, is_tv=True)
                    else:
                        logging.warning(f"Warning: Episode data for '{media_name}' not found or NFO file already exists.")
                else:
                    logging.warning(f"Warning: TMDb API request for season details failed.")
            else:
                logging.warning(f"Warning: TMDb API request for series details failed.")
    else:
        logging.info("All NFO files are already available.")

async def create_movie_files(movie_name, tmdb_data, url_line):
    global url_count, remaining_url_count
    year = tmdb_data.get('release_date', '')[:4]
    
    # TMDB sitesinden gelen temiz ve resmi ismi (eğer varsa) kullan
    clean_movie_title = sanitize_filename(tmdb_data.get('title', movie_name))
    
    movie_folder = os.path.join(movies_folder_path, f"{clean_movie_title} ({year})")
    os.makedirs(movie_folder, exist_ok=True)
    
    movie_nfo_path = os.path.join(movie_folder, f"{clean_movie_title} ({year}).nfo")
    movie_strm_path = os.path.join(movie_folder, f"{clean_movie_title} ({year}).strm")
    
    if not os.path.exists(movie_strm_path):
        async with aiofiles.open(movie_strm_path, 'w', encoding='utf-8') as movie_strm_file:
            await movie_strm_file.write(url_line)
            remaining_url_count -= 1
            logging.info(f"{url_count} / {remaining_url_count} left - STRM file created: {movie_strm_path}")
    else:
        remaining_url_count -= 1
        logging.info(f"{url_count} / {remaining_url_count} left - STRM file already exists: {movie_strm_path}")
    
    if not os.path.exists(movie_nfo_path):
        async with aiohttp.ClientSession() as session:
            movie_id = tmdb_data['id']
            movie_details_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={tmdb_api_key}&language={tmdb_language}&append_to_response=credits,videos"
            movie_details_response = await fetch_data(session, movie_details_url)
            
            if movie_details_response:
                await create_nfo(movie_details_response, movie_nfo_path, is_tv=False)
            else:
                logging.warning(f"Warning: TMDb API request for movie details failed.")

async def create_default_strm(media_name, url_line):
    global url_count, remaining_url_count
    # M3U içerisindeki isimde nokta varsa klasör isminde boşlukla değiştir
    media_name_clean = sanitize_filename(media_name).replace('.', ' ').strip()
    
    default_folder = os.path.join(movies_folder_path, media_name_clean)
    os.makedirs(default_folder, exist_ok=True)
    
    media_strm_path = os.path.join(default_folder, f"{media_name_clean}.strm")
    
    if not os.path.exists(media_strm_path):
        async with aiofiles.open(media_strm_path, 'w', encoding='utf-8') as media_strm_file:
            await media_strm_file.write(url_line)
            remaining_url_count -= 1
            logging.warning(f"{url_count} / {remaining_url_count} left - Warning: No TMDb data found for '{media_name}'. Created STRM file: {media_strm_path}")
    else:
        remaining_url_count -= 1
        logging.info(f"{url_count} / {remaining_url_count} left - STRM file already exists: {media_strm_path}")

async def process_m3u_file(m3u_file_path, output_folder_path, channels_data):
    async with aiofiles.open(m3u_file_path, 'r', encoding='utf-8') as m3u_file:
        lines = await m3u_file.readlines()

    updated_channels_file_path = os.path.join(output_folder_path, 'updated_channels.m3u')
    async with aiofiles.open(updated_channels_file_path, 'w', encoding='utf-8') as updated_channels_file:
        i = 0
        while i < len(lines):
            extinf_line = lines[i].strip()
            if extinf_line.startswith('#EXTINF:'):
                if i + 1 < len(lines):
                    url_line = lines[i + 1].strip()
                    await process_extinf_line(extinf_line, url_line, channels_data, updated_channels_file)
                    i += 2
                else:
                    i += 1
            else:
                i += 1

async def main():
    m3u_file_path = prepare_files()
    channels_data = await fetch_iptv_channels("https://iptv-org.github.io/api/channels.json")
    await process_m3u_file(m3u_file_path, output_folder_path, channels_data)

if __name__ == '__main__':
    # Library installation check is already run above
    asyncio.run(main())
