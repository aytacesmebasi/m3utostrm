import os
import re
import subprocess
import sys
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from urllib.parse import quote
import logging
import aiohttp
import asyncio
import aiofiles
from datetime import datetime

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
file_handler = logging.FileHandler(log_file_path, encoding='utf-8')  # Creates a log file named 'm3u2strm.log'
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Version information
logger.info("m3utostrm v3.9")
logger.info("it processes the differences between the old and new downloaded m3u files")

# User data
tmdb_api_key = 'YOUR_API_KEY'
iptvurl = 'YOUR_IPTV_URL'  # Write your IPTV URL here
iptvusername = 'YOUR_IPTV_USERNAME'   # Write your IPTV username here
iptvpassword = 'YOUR_IPTV_PASSWORD'   # Write your IPTV password here

# Country code to filter
your_language_code = 'TR'

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
    "news": "News,
    "religious": "Religious",
    "science": "Science",
    "shop": "Shop",
    "sports": "Sports",
    "travel": "Travel",
    "weather": "Weather"
}

DEFAULT_CATEGORY = "Unknownn"

def translate_category(category):
    return category_translation.get(category.lower(), DEFAULT_CATEGORY)

def update_missing_translations(channels):
    missing_categories = set()
    for channel in channels:
        category = channel.get('group-title', 'Unknownn')
        if category.lower() not in category_translation:
            missing_categories.add(category)
    
    if missing_categories:
        logger.info("Missing translations:")
        for category in missing_categories:
            logger.info(f"- {category}")

async def fetch_and_process_channels(api_url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                response.raise_for_status()  # Check for HTTP errors
                channels = await response.json()
                update_missing_translations(channels)
                # Process channels
                return channels
    except aiohttp.ClientError as e:
        logging.error(f"API request failed: {e}")
        return []

# Library list
required_libraries = [
    "requests",
    "aiohttp",
    "aiohttp"
]

def install(package):
    """Installs the specified package."""
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def main():
    for library in required_libraries:
        try:
            __import__(library)
        except ImportError:
            logging.info(f"{library} is not loaded. Loading...")
            install(library)
        else:
            logging.info(f"{library} is already installed.")

if __name__ == "__main__":
    main()

# Get date and time information for file name
now = datetime.now()
formatted_date = now.strftime('%d%m%y%H%M')  # gg, aa, yy, ss, dd formatted
filename = f'{formatted_date}.m3u'
file_path = os.path.join(output_folder_path, filename)

# Download M3U file
def download_m3u(url, username, password, filename):
    try:
        # Create URL
        full_url = f"{url}/get.php?username={username}&password={password}&type=m3u"
        
        # Make a request
        response = requests.get(full_url)
        response.raise_for_status()  # Throws an exception if there is an error
        
        # Save the file
        with open(filename, 'wb') as file:
            file.write(response.content)
        
        logger.info(f"{filename} was downloaded successfully.")
    
    except requests.RequestException as e:
        logger.error(f"Download failed: {e}")

# Call the function
download_m3u(iptvurl, iptvusername, iptvpassword, file_path)

# Directory containing '.m3u' files
directory = output_folder_path

# Get file names, exclude the file we downloaded
files = [f for f in os.listdir(directory) if f.endswith('.m3u') and f != filename]

def parse_filename(filename):
    # Split file name into day, month, year, hour and minute
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

# Parse file names and compare dates
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
    latest_file = None  # If the latest file is not available, the comparison will not be made.

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

    # Find URLs in the new file that are not in the old file
    difference = {url: new_urls_with_extinf[url] for url in new_urls_with_extinf if url not in old_urls_with_extinf}

    return difference

def write_new_m3u(difference, output_file):
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write("#EXTM3U\n")  # M3U file title
        for url, extinf in difference.items():
            file.write(f"{extinf}\n{url}\n")

# Specify file paths
m3u_file_path = os.path.join(output_folder_path, 'tobeprocess.m3u')

# Comparison operation and writing the results
if latest_file:
    new_urls_not_in_old = compare_m3u_files(os.path.join(directory, latest_file), file_path)
    
    if new_urls_not_in_old:
        logging.info("URLs and related #EXTINF lines that are not in the old file but are in the new file are written to the new file...")
        write_new_m3u(new_urls_not_in_old, m3u_file_path)
        logging.info(f"New M3U file saved as '{m3u_file_path}'.")
    else:
        # Create an empty file if all URLs exist in the old file
        logging.info("All URLs are present in old file. Creating empty 'tobeprocess.m3u' file...")
        with open(m3u_file_path, 'w', encoding='utf-8') as file:
            file.write("#EXTM3U\n")  # M3U file title
        logging.info(f"Empty M3U file saved as '{m3u_file_path}'.")
    
    # Delete the newest file
    os.remove(os.path.join(directory, latest_file))
    logging.info(f"The newest file '{latest_file}' was deleted.")
else:
    # If there is no latest file, we just save the downloaded file as 'tobeprocess.m3u'
    logging.info("The latest file was not found, only the downloaded file is saved as 'tobeprocess.m3u'...")
    with open(file_path, 'r', encoding='utf-8') as new_file:
        new_lines = new_file.readlines()
    with open(m3u_file_path, 'w', encoding='utf-8') as output_file:
        output_file.writelines(new_lines)
    logging.info(f"The downloaded M3U file was saved as '{m3u_file_path}'.")

# Function to count URLs in M3U file
url_count = 0
logging.info(f"Initially url_count was defined as {url_count}.")
def count_urls_in_m3u(m3u_file_path):
    with open(m3u_file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    # http veya https ile başlayan satırları say
    url_count = sum(1 for line in lines if line.startswith("http"))
    return url_count
url_count = count_urls_in_m3u(m3u_file_path)
remaining_url_count = url_count
logging.info(f"There are {url_count} URLs in the file.")

# Create a folder to save STRM and NFO files
movies_folder_path = os.path.join(output_folder_path, 'movies')
os.makedirs(movies_folder_path, exist_ok=True)
logging.info(f"Movies Folder created: {movies folder path}")

series_folder_path = os.path.join(output_folder_path, 'series')
os.makedirs(series_folder_path, exist_ok=True)
logging.info(f"Series Folder created: {series_folder_path}")

porn_folder_path = os.path.join(output_folder_path, 'porn')
os.makedirs(porn_folder_path, exist_ok=True)
logging.info(f"Porn Folder created: {porn_folder_path}")

# Check API error message
async def get_with_retries(url, retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504)):
    delay = backoff_factor
    for attempt in range(retries):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status in status_forcelist:
                        raise aiohttp.ClientResponseError(
                            request_info=response.request_info,
                            history=response.history,
                            status=response.status,
                            message="Server error"
                        )
                    response.raise_for_status()
                    return await response.text()
        except (aiohttp.ClientResponseError, aiohttp.ClientConnectionError) as e:
            logging.warning(f"Request failed (attempt {attempt + 1}/{retries}): {e}")
            if attempt < retries - 1:
                await asyncio.sleep(delay)
                delay *= 2  # Exponential backoff
            else:
                logging.error(f"Failed to fetch {url} after {retries} attempts.")
                return None

# Suffix pattern
suffix_pattern = re.compile(r'\s*(\[.*?\])(?:\s*\[.*?\]|\s*H\.265|\s*[A-Z]{2,})?\s*$', re.IGNORECASE)

# Function to check if URL contains "porn"
def is_porn_url(url):
    porn_patterns = [
        r'xxx', r'XxX', r'XXX', r'xxx1', r'XXX\.', r'2xxX', 
        r'porn', r'Porn', r'SEX', r'Adult', r'NSFW', 
        r'pay-per-view', r'live-stream', r'free-videos'
    ]
    combined_pattern = '|'.join(porn_patterns)
    return re.search(combined_pattern, url, re.IGNORECASE) is not None

# Function to remove invalid characters from file and folder names
def sanitize_filename(filename):
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '')
    return filename

# Name cleaning function (for movies and series)
def clean_name(name, is_tv=False):
    if is_tv:
        name = re.sub(r'\s*S\d{2}\s*E\d{2}', '', name)
    else:
        name = re.sub(r'\s*\(\d{4}\)', '', name)
        name = re.sub(r'\s*[-]?\s*\d{4}', '', name)
    return sanitize_filename(name.strip())

# TMDb search function
class APIRequestError(Exception):
    """Custom error class for API requests."""
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
            return None  # Return None on 404 error
        else:
            logging.error(f"API request failed: {e} - Status Code: {e.status}")
            raise APIRequestError(f"API request failed: {e.message}", status_code=e.status)
    except aiohttp.ClientError as e:
        logging.error(f"API request failed: {e}")
        raise APIRequestError(f"API request failed: {e}")


async def search_tmdb(query, is_tv=False):
    search_type = 'tv' if is_tv else 'movie'
    query_encoded = quote(query)
    search_url = f"https://api.themoviedb.org/3/search/{search_type}?api_key={tmdb_api_key}&query={query_encoded}&language={your_language_code}"
    
    async with aiohttp.ClientSession() as session:
        try:
            data = await fetch_data(session, search_url)
            results = data.get('results', [])
            if results:
                return results[0]
            else:
                logging.warning(f"Warning: No results found in TMDb for '{query}'.")
        except APIRequestError as e:
            logging.error(f"TMDb API request failed: {e}")
    
    return None

# NFO file creation function (for movies and series)
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

    # Players
    for cast in data.get('credits', {}).get('cast', [])[:10]:  # Top 10 players
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

    # Players
    for cast in data.get('credits', {}).get('cast', [])[:10]:  # Top 10 players
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

# Read M3U file and create STRM/NFO files
async def fetch_iptv_channels(api_url, country_code):
    async with aiohttp.ClientSession() as session:
        response = await fetch_data(session, api_url)
        if response:
            logging.info("iptv-org API cache file created")
            return [channel for channel in response if channel.get('country') == country_code]
        else:
            logging.warning("Warning: IPTV-Org API request failed.")
            return []

async def process_extinf_line(extinf_line, url_line, channels_data, output_file):
    media_name = extinf_line.split(',', 1)[1].strip()
    url_line_lower = url_line.lower()
    
    if url_line_lower.endswith('.ts'):
        await handle_ts_url(media_name, url_line, channels_data, output_file)
    else:
        await handle_non_ts_url(media_name, url_line)

async def handle_ts_url(media_name, url_line, channels_data, output_file):
    cleaned_media_name = suffix_pattern.sub('', media_name).strip()
    cleaned_media_name = sanitize_filename(cleaned_media_name)

    bracketsin = extract_bracketsin(media_name)
    
    channel_info = next((channel for channel in channels_data if channel["name"].lower() == cleaned_media_name.lower()), None)
    if channel_info:
        await write_channel_info(channel_info, media_name, url_line, bracketsin, output_file)
    else:
        await write_default_channel_info(media_name, url_line, bracketsin, output_file)

def extract_bracketsin(media_name):
    bracketsin_match = re.search(r'\[(.*?)\]', media_name)
    return bracketsin_match.group(1).replace(' ', '') if bracketsin_match else ''

async def write_channel_info(channel_info, media_name, url_line, bracketsin, output_file_path):
    global url_count  # Use global variable
    global remaining_url_count  # Use global variable
    file_name = "updated_channels.m3u"
    output_file_path = os.path.join(output_folder_path, file_name)
    channel_name = channel_info.get("name", media_name)
    logo = channel_info.get("logo", "")
    id_ = channel_info.get("id", "")
    owners = ', '.join(channel_info.get("owners", []))
    languages = ', '.join(channel_info.get("languages", []))
    is_nsfw = channel_info.get("is_nsfw", False)
    
    categories = ', '.join(channel_info.get("categories", []))
    translated_categories = ', '.join([category_translation.get(cat, cat) for cat in categories.split(', ')])
    group_title = translated_categories if categories else 'Unknown'
    
    # Write file asynchronously
    async with aiofiles.open(output_file_path, mode='a', encoding='utf-8') as output_file:
        await output_file.write(f"#EXTINF:-1 group-title=\"{group_title}; {bracketsin}\" tvg-id=\"{id_}\" tvg-name=\"{channel_name}\" tvg-logo=\"{logo}\" tvg-country=\"{your_language_code}\" is-nsfw=\"{is_nsfw}\", {media_name}\n{url_line}\n")
    
    remaining_url_count -= 1  # Decrease countdown
    logging.info(f"{url_count} / {remaining_url_count} left - URL ends with '.ts' and added to {output_file_path}: {url_line}")

async def write_default_channel_info(media_name, url_line, bracketsin, output_file_path):
    global url_count  # Use global variable
    global remaining_url_count  # Use global variable
    file_name = "updated_channels.m3u"
    output_file_path = os.path.join(output_folder_path, file_name)
    group_title = 'Unknown'
    content = f"#EXTINF:-1 group-title=\"{group_title}; {bracketsin}\" tvg-name=\"{sanitize_filename(media_name)}\" tvg-country=\"{your_language_code}\" is-nsfw=\"false\", {media_name}\n{url_line}\n"
    
    # Write file asynchronously
    async with aiofiles.open(output_file_path, mode='a', encoding='utf-8') as output_file:
        await output_file.write(content)
    
    remaining_url_count -= 1  # Decrease countdown
    logging.warning(f"{url_count} / {remaining_url_count} remaining - Warning: No IPTV-Org channel information found for '{media_name}'.")

async def handle_non_ts_url(media_name, url_line):
    if is_porn_url(media_name):
        await create_porn_strm(media_name, url_line)
    else:
        is_tv = 'S' in media_name and 'E' in media_name
        cleaned_media_name = clean_name(media_name, is_tv=is_tv)
        tmdb_data = await search_tmdb(cleaned_media_name, is_tv=is_tv)
        
        if tmdb_data:
            if is_tv:
                await create_tv_show_files(cleaned_media_name, tmdb_data, url_line, media_name)
            else:
                await create_movie_files(cleaned_media_name, tmdb_data, url_line)
        else:
            await create_default_strm(media_name, url_line)

async def create_porn_strm(media_name, url_line):
    global url_count  # Use global variable
    global remaining_url_count  # Use global variable
    porn_strm_path = os.path.join(porn_folder_path, f"{sanitize_filename(media_name)}.strm")
    
    # Check for existence of STRM file
    if not os.path.exists(porn_strm_path):
        async with aiofiles.open(porn_strm_path, 'w', encoding='utf-8') as porn_strm_file:
            await porn_strm_file.write(url_line)
            remaining_url_count -= 1  # Decrease countdown
            logging.info(f"{url_count} / {remaining_url_count} left - STRM file created for porn: {porn_strm_path}")
    else:
        remaining_url_count -= 1  # Decrease countdown
        logging.info(f"{url_count} / {remaining_url_count} left - STRM file already exists: {porn_strm_path}")

async def create_tv_show_files(show_name, tmdb_data, url_line, media_name):
    global url_count  # Use global variable
    global remaining_url_count  # Use global variable
    year = tmdb_data.get('first_air_date', '')[:4]
    season_episode_match = re.search(r'\s*S(\d{2})\s*E(\d{2})', media_name)
    season = season_episode_match.group(1) if season_episode_match else '01'
    episode = season_episode_match.group(2) if season_episode_match else '01'
    
    show_folder = os.path.join(series_folder_path, f"{show_name} ({year})")
    season_folder = os.path.join(show_folder, f"Season {int(season)}")
    os.makedirs(season_folder, exist_ok=True)
    
    series_nfo_path = os.path.join(show_folder, f"{show_name} ({year}).nfo")
    season_nfo_path = os.path.join(season_folder, f"{show_name} ({year}) S{season}.nfo")
    episode_strm_path = os.path.join(season_folder, f"{show_name} ({year}) S{season}E{episode}.strm")
    episode_nfo_path = os.path.join(season_folder, f"{show_name} ({year}) S{season}E{episode}.nfo")
    
    # Check if STRM file exists, create it if not
    if not os.path.exists(episode_strm_path):
        async with aiofiles.open(episode_strm_path, 'w', encoding='utf-8') as episode_strm_file:
            await episode_strm_file.write(url_line)
            remaining_url_count -= 1  # Decrease countdown
            logging.info(f"{url_count} / {remaining_url_count} left - STRM file created: {episode_strm_path}")
    else:
        remaining_url_count -= 1  # Decrease countdown
        logging.info(f"{url_count} / {remaining_url_count} remaining - STRM file already exists: {episode_strm_path}")
    
    # Check for existence of NFO files, create them if not
    if not os.path.exists(series_nfo_path) or not os.path.exists(season_nfo_path) or not os.path.exists(episode_nfo_path):
        async with aiohttp.ClientSession() as session:
            # Get sequence details from TMDb API and create NFO files
            show_details_url = f"https://api.themoviedb.org/3/tv/{tmdb_data['id']}?api_key={tmdb_api_key}&language={your_language_code}&append_to_response=credits,videos"
            show_details_response = await fetch_data(session, show_details_url)
            if show_details_response:
                if not os.path.exists(series_nfo_path):
                    await create_nfo(show_details_response, series_nfo_path, is_tv=True)
                
                season_details_url = f"https://api.themoviedb.org/3/tv/{tmdb_data['id']}/season/{season}?api_key={tmdb_api_key}&language={your_language_code}"
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
    global url_count  # Use global variable
    global remaining_url_count  # Use global variable
    
    # Create folder for movie
    year = tmdb_data.get('release_date', '')[:4]
    movie_folder = os.path.join(movies_folder_path, f"{movie_name} ({year})")
    os.makedirs(movie_folder, exist_ok=True)
    
    # Define paths of STRM and NFO files
    movie_nfo_path = os.path.join(movie_folder, f"{movie_name} ({year}).nfo")
    movie_strm_path = os.path.join(movie_folder, f"{movie_name} ({year}).strm")
    
    # Check for existence of STRM file and create it if it does not exist
    if not os.path.exists(movie_strm_path):
        async with aiofiles.open(movie_strm_path, 'w', encoding='utf-8') as movie_strm_file:
            await movie_strm_file.write(url_line)
            remaining_url_count -= 1  # Decrease countdown
            logging.info(f"{url_count} / {remaining_url_count} left - STRM file created: {movie_strm_path}")
    else:
        remaining_url_count -= 1  # Decrease countdown
        logging.info(f"{url_count} / {remaining_url_count} left - STRM file already exists: {movie_strm_path}")
    
    # Check for existence of NFO file and create it if it does not exist
    if not os.path.exists(movie_nfo_path):
        async with aiohttp.ClientSession() as session:
            movie_id = tmdb_data['id']
            movie_details_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={tmdb_api_key}&language={your_language_code}&append_to_response=credits,videos"
            movie_details_response = await fetch_data(session, movie_details_url)
            
            if movie_details_response:
                await create_nfo(movie_details_response, movie_nfo_path, is_tv=False)
            else:
                logging.warning(f"Warning: TMDb API request for movie details failed.")

async def create_default_strm(media_name, url_line):
    global url_count  # Use global variable
    global remaining_url_count  # Use global variable
    
    # Create folder for media
    media_folder = os.path.join(movies_folder_path, sanitize_filename(media_name))
    os.makedirs(media_folder, exist_ok=True)
    
    # Define the path of the STRM file
    media_strm_path = os.path.join(media_folder, f"{sanitize_filename(media_name)}.strm")
    
    # Check for existence of STRM file and create it if it does not exist
    if not os.path.exists(media_strm_path):
        async with aiofiles.open(media_strm_path, 'w', encoding='utf-8') as media_strm_file:
            await media_strm_file.write(url_line)
            remaining_url_count -= 1  # Decrease countdown
            logging.warning(f"{url_count} / {remaining_url_count} left - Warning: No TMDb data found for '{media_name}'. Created STRM file: {media_strm_path}")
    else:
        remaining_url_count -= 1  # Decrease countdown
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

# Usage:
async def main():
    
    # call fetch_iptv_channels with await
    channels_data = await fetch_iptv_channels("https://iptv-org.github.io/api/channels.json", your_language_code)
    
    await process_m3u_file(m3u_file_path, output_folder_path, channels_data)

if __name__ == '__main__':
    asyncio.run(main())
