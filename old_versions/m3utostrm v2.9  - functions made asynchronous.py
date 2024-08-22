import os
import re
import subprocess
import sys
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from urllib.parse import quote
import requests_cache
import logging
import aiohttp
import asyncio
from urllib.parse import quote
import aiofiles

#output_files klasörü oluşturma
current_working_directory = os.getcwd()
output_folder_path = os.path.join(current_working_directory, 'output_files')
os.makedirs(output_folder_path, exist_ok=True)

# Loglama yapılandırması ve dosyalaması
logging.basicConfig(
    stream=sys.stdout, 
    format='%(asctime)s - %(levelname)s - %(message)s', 
    level=logging.INFO,
    encoding='utf-8'
)
log_file_path = os.path.join(output_folder_path, 'app.log')  # 'app.log' dosyasının tam yolunu oluşturur
file_handler = logging.FileHandler(log_file_path)  # 'app.log' adında bir log dosyası oluşturur
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(file_handler)

# Version information
logger.info("m3utostrm v2.9")
logger.info("functions made asynchronous")

# Kullanıcı verileri
tmdb_api_key = 'YOUR_API_KEY'
iptvurl = 'YOUR_IPTV_URL'  # Buraya IPTV URL'nizi yazın
iptvusername = 'YOUR_IPTV_USERNAME'   # Buraya IPTV kullanıcı adınızı yazın
iptvpassword = 'YOUR_IPTV_PASSWORD'   # Buraya IPTV şifrenizi yazın

# Filtrelenecek ülke kodu
your_language_code = 'TR'

# Group-title çeviri sözlüğü
category_translation = {
    "general": "Genel",
    "business": "İş",
    "children": "Çocuk",
    "classic": "Klasik",
    "comedy": "Komedi",
    "documentary": "Belgesel",
    "education": "Eğitim",
    "entertainment": "Eğlence",
    "family": "Aile",
    "game": "Oyun",
    "legislative": "Mevzuat",
    "lifestyle": "Yaşam Tarzı",
    "movies": "Filmler",
    "music": "Müzik",
    "news": "Haberler",
    "religious": "Dini",
    "science": "Bilim",
    "shop": "Alışveriş",
    "sports": "Spor",
    "travel": "Seyahat",
    "weather": "Hava Durumu"
}

DEFAULT_CATEGORY = "Bilinmeyen"

def translate_category(category):
    return category_translation.get(category.lower(), DEFAULT_CATEGORY)

def update_missing_translations(channels):
    missing_categories = set()
    for channel in channels:
        category = channel.get('group-title', 'Bilinmeyen')
        if category.lower() not in category_translation:
            missing_categories.add(category)
    
    if missing_categories:
        logger.info("Eksik çeviriler:")
        for category in missing_categories:
            logger.info(f"- {category}")

async def fetch_and_process_channels(api_url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                response.raise_for_status()  # HTTP hatalarını kontrol et
                channels = await response.json()
                update_missing_translations(channels)
                # Kanalları işle
                return channels
    except aiohttp.ClientError as e:
        logging.error(f"API isteği başarısız oldu: {e}")
        return []

# Kütüphane listesi
required_libraries = [
    "requests",
    "requests-cache"
]

def install(package):
    """Belirtilen paketi yükler."""
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def main():
    for library in required_libraries:
        try:
            __import__(library)
        except ImportError:
            logging.info(f"{library} yüklü değil. Yükleniyor...")
            install(library)
        else:
            logging.info(f"{library} zaten yüklü.")

if __name__ == "__main__":
    main()

# Kaynak M3U dosyasını indirme
url = f"{iptvurl}/get.php?username={iptvusername}&password={iptvpassword}&type=m3u"
m3u_file_path = os.path.join(output_folder_path, 'm3u2strm.m3u')
try:
    # Dosyayı indirme işlemi
    response = requests.get(url)
    
    # Yanıtın başarılı olup olmadığını kontrol et
    if response.status_code == 200:
        # Dosyayı belirtilen yolda kaydet
        with open(m3u_file_path, 'wb') as file:
            file.write(response.content)
        print(f"Dosya başarıyla indirildi ve '{m3u_file_path}' olarak kaydedildi.")
    else:
        print(f"HTTP {response.status_code} hata kodu ile karşılaşıldı.")
except RequestException as e:
    print(f"Dosya indirme başarısız. Hata: {e}")

# STRM ve NFO dosyalarını kaydetmek için klasör oluşturun
movies_folder_path = os.path.join(output_folder_path, 'movies')
os.makedirs(movies_folder_path, exist_ok=True)
logging.info(f"Movies Klasörü oluşturuldu: {movies_folder_path}")
series_folder_path = os.path.join(output_folder_path, 'series')
os.makedirs(series_folder_path, exist_ok=True)
logging.info(f"Series Klasörü oluşturuldu: {series_folder_path}")
porn_folder_path = os.path.join(output_folder_path, 'porn')
os.makedirs(porn_folder_path, exist_ok=True)
logging.info(f"Porn Klasörü oluşturuldu: {porn_folder_path}")

# Api hata mesajı kontrolü
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

# Önbelleği başlat (cache dosyası 'api_cache' olarak adlandırılır ve 1 saat süreyle geçerli olur)
cache_path = 'output_files/api_cache'
expire_after = 3600
requests_cache.install_cache(cache_path, expire_after=expire_after)
logging.info(f"Ön bellek dosyası şu süre için oluşturuldu: {expire_after} saniye.")

# Suffix pattern
suffix_pattern = re.compile(r'\s*(\[.*?\])(?:\s*\[.*?\]|\s*H\.265|\s*[A-Z]{2,})?\s*$', re.IGNORECASE)

# URL'nin "porn" içerip içermediğini kontrol etme fonksiyonu
def is_porn_url(url):
    porn_patterns = [
        r'xxx', r'XxX', r'XXX', r'xxx1', r'XXX\.', r'2xxX', 
        r'porn', r'Porn', r'SEX', r'Adult', r'NSFW', 
        r'pay-per-view', r'live-stream', r'free-videos'
    ]
    combined_pattern = '|'.join(porn_patterns)
    return re.search(combined_pattern, url, re.IGNORECASE) is not None

# Dosya ve klasör isimlerindeki geçersiz karakterleri temizleme fonksiyonu
def sanitize_filename(filename):
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '')
    return filename

# Ad temizleme fonksiyonu (film ve dizi için)
def clean_name(name, is_tv=False):
    if is_tv:
        name = re.sub(r'\s*S\d{2}\s*E\d{2}', '', name)
    else:
        name = re.sub(r'\s*\(\d{4}\)', '', name)
        name = re.sub(r'\s*[-]?\s*\d{4}', '', name)
    return sanitize_filename(name.strip())

# TMDb arama fonksiyonu
async def fetch_data(session, url):
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.json()
    except aiohttp.ClientError as e:
        logging.error(f"API isteği başarısız oldu: {e}")
        return None

async def search_tmdb(query, is_tv=False):
    search_type = 'tv' if is_tv else 'movie'
    query_encoded = quote(query)
    search_url = f"https://api.themoviedb.org/3/search/{search_type}?api_key={tmdb_api_key}&query={query_encoded}&language={your_language_code}"
    
    async with aiohttp.ClientSession() as session:
        data = await fetch_data(session, search_url)
    
    if data:
        results = data.get('results', [])
        if results:
            return results[0]
        else:
            logging.warning(f"Uyarı: '{query}' için TMDb'de sonuç bulunamadı.")
    else:
        logging.error(f"Uyarı: TMDb API isteği başarısız oldu.")
    return None

# NFO dosyası oluşturma fonksiyonu (film ve dizi için)
async def create_nfo(data, file_path, is_tv=False):
    try:
        if is_tv:
            content = generate_tv_nfo_content(data)
        else:
            content = generate_movie_nfo_content(data)
        
        async with aiofiles.open(file_path, 'w', encoding='utf-8') as nfo_file:
            await nfo_file.write(content)
        logging.info(f"NFO dosyası oluşturuldu: {file_path}")
    except Exception as e:
        logging.error(f"Bir hata oluştu: {e}")

def generate_tv_nfo_content(data):
    name = data.get('name', 'Bilinmiyor')
    original_name = data.get('original_name', name)
    rating = data.get('vote_average', 'Bilinmiyor')
    year = data.get('first_air_date', '')[:4]
    votes = data.get('vote_count', 'Bilinmiyor')
    overview = data.get('overview', 'Açıklama mevcut değil.')
    poster_path = data.get('poster_path', '')
    backdrop_path = data.get('backdrop_path', '')
    mpaa = 'TV-MA' if data.get('adult') else 'TV-G'
    country = ', '.join(data.get('origin_country', ['Bilinmiyor']))
    premiered = data.get('first_air_date', 'Bilinmiyor')
    status = data.get('status', 'Bilinmiyor')
    tv_id = data.get('id', 'Bilinmiyor')
    genre = ', '.join([genre.get('name', 'Bilinmiyor') for genre in data.get('genres', [])])
    studio = ', '.join([company.get('name', 'Bilinmiyor') for company in data.get('production_companies', [])])
    
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

    # Oyuncular
    for cast in data.get('credits', {}).get('cast', [])[:10]:  # İlk 10 oyuncu
        name = cast.get('name', 'Bilinmiyor')
        role = cast.get('character', 'Bilinmiyor')
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
    title = data.get('title', 'Bilinmiyor')
    original_title = data.get('original_title', 'Bilinmiyor')
    rating = data.get('vote_average', 'Bilinmiyor')
    year = data.get('release_date', '')[:4]
    votes = data.get('vote_count', 'Bilinmiyor')
    outline = data.get('overview', 'Açıklama mevcut değil.')
    plot = data.get('overview', 'Açıklama mevcut değil.')
    tagline = data.get('tagline', 'Bilinmiyor')
    runtime = data.get('runtime', 'Bilinmiyor')
    poster_path = data.get('poster_path', '')
    backdrop_path = data.get('backdrop_path', '')
    mpaa = 'PG-13' if data.get('adult') else 'G'
    country = ', '.join([country.get('name', 'Bilinmiyor') for country in data.get('production_countries', [])])
    premiered = data.get('release_date', 'Bilinmiyor')
    status = 'Released' if data.get('status') == 'Released' else 'Bilinmiyor'
    imdb_id = data.get('imdb_id', 'Bilinmiyor')
    movie_id = data.get('id', 'Bilinmiyor')
    genre = ', '.join([genre.get('name', 'Bilinmiyor') for genre in data.get('genres', [])])
    studio = ', '.join([company.get('name', 'Bilinmiyor') for company in data.get('production_companies', [])])
    trailer = 'https://www.youtube.com/watch?v=' + data.get('videos', {}).get('results', [{}])[0].get('key', '') if data.get('videos', {}).get('results') else 'Bilinmiyor'
    director = ', '.join([member.get('name', 'Bilinmiyor') for member in data.get('credits', {}).get('crew', []) if member.get('job') == 'Director'])
    credits = ', '.join([member.get('name', 'Bilinmiyor') for member in data.get('credits', {}).get('crew', []) if member.get('job') == 'Writer'])
    
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

    # Oyuncular
    for cast in data.get('credits', {}).get('cast', [])[:10]:  # İlk 10 oyuncu
        name = cast.get('name', 'Bilinmiyor')
        role = cast.get('character', 'Bilinmiyor')
        thumb = cast.get('profile_path', '')
        content += f"""
    <actor>
        <name>{name}</name>
        <role>{role}</role>
        <thumb>https://image.tmdb.org/t/p/original{thumb}</thumb>
    </actor>"""

    content += "\n</movie>"
    return content

# M3U dosyasını okuyun ve STRM/NFO dosyalarını oluşturun
async def fetch_iptv_channels(api_url, country_code):
    async with aiohttp.ClientSession() as session:
        response = await fetch_data(session, api_url)
        if response:
            logging.info("iptv-org API cache dosyası oluşturuldu")
            return [channel for channel in response if channel.get('country') == country_code]
        else:
            logging.error("Uyarı: IPTV-Org API isteği başarısız oldu.")
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
    group_title = translated_categories if categories else 'Bilinmeyen'
    
    # Asenkron olarak dosyayı yaz
    async with aiofiles.open(output_file_path, mode='a', encoding='utf-8') as output_file:
        await output_file.write(f"#EXTINF:-1 group-title=\"{group_title}; {bracketsin}\" tvg-id=\"{id_}\" tvg-name=\"{channel_name}\" tvg-logo=\"{logo}\" tvg-country=\"TR\" is-nsfw=\"{is_nsfw}\", {media_name}\n{url_line}\n")
    
    logging.info(f"URL '.ts' ile bitiyor ve {output_file_path} dosyasına eklendi: {url_line}")

async def write_default_channel_info(media_name, url_line, bracketsin, output_file_path):
    file_name = "updated_channels.m3u"
    output_file_path = os.path.join(output_folder_path, file_name)
    group_title = 'Bilinmeyen'
    content = f"#EXTINF:-1 group-title=\"{group_title}; {bracketsin}\" tvg-name=\"{sanitize_filename(media_name)}\" tvg-country=\"TR\" is-nsfw=\"false\", {media_name}\n{url_line}\n"
    
    # Asenkron olarak dosyayı yaz
    async with aiofiles.open(output_file_path, mode='a', encoding='utf-8') as output_file:
        await output_file.write(content)
    
    logging.warning(f"Uyarı: '{media_name}' için IPTV-Org kanal bilgisi bulunamadı.")

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
    porn_strm_path = os.path.join(porn_folder_path, f"{sanitize_filename(media_name)}.strm")
    
    async with aiofiles.open(porn_strm_path, 'w', encoding='utf-8') as porn_strm_file:
        await porn_strm_file.write(url_line)
        logging.info(f"Porno için STRM dosyası oluşturuldu: {porn_strm_path}")

async def create_tv_show_files(show_name, tmdb_data, url_line, media_name):
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
    
    # STRM dosyasını oluştur
    async with aiofiles.open(episode_strm_path, 'w', encoding='utf-8') as episode_strm_file:
        await episode_strm_file.write(url_line)
        logging.info(f"STRM dosyası oluşturuldu: {episode_strm_path}")
    
    async with aiohttp.ClientSession() as session:
        # Dizi detaylarını TMDb API'den al ve NFO dosyalarını oluştur
        show_details_url = f"https://api.themoviedb.org/3/tv/{tmdb_data['id']}?api_key={tmdb_api_key}&language=tr&append_to_response=credits,videos"
        show_details_response = await fetch_data(session, show_details_url)
        if show_details_response:
            await create_nfo(show_details_response, series_nfo_path, is_tv=True)
            
            season_details_url = f"https://api.themoviedb.org/3/tv/{tmdb_data['id']}/season/{season}?api_key={tmdb_api_key}&language=tr"
            season_details_response = await fetch_data(session, season_details_url)
            if season_details_response:
                await create_nfo(season_details_response, season_nfo_path, is_tv=True)
                
                episode_details = next((ep for ep in season_details_response.get('episodes', []) if ep['episode_number'] == int(episode)), None)
                if episode_details:
                    await create_nfo(episode_details, episode_nfo_path, is_tv=True)
                else:
                    logging.warning(f"Uyarı: '{media_name}' için bölüm verisi bulunamadı.")
            else:
                logging.error(f"Uyarı: Sezon detayları için TMDb API isteği başarısız oldu.")
        else:
            logging.error(f"Uyarı: Dizi detayları için TMDb API isteği başarısız oldu.")

async def create_movie_files(movie_name, tmdb_data, url_line):
    # Film için klasör oluştur
    movie_folder = os.path.join(movies_folder_path, movie_name)
    os.makedirs(movie_folder, exist_ok=True)
    
    # STRM ve NFO dosyalarının yollarını tanımla
    movie_strm_path = os.path.join(movie_folder, f"{movie_name}.strm")
    movie_nfo_path = os.path.join(movie_folder, f"{movie_name}.nfo")
    
    # STRM dosyasını oluştur
    async with aiofiles.open(movie_strm_path, 'w', encoding='utf-8') as movie_strm_file:
        await movie_strm_file.write(url_line)
        logging.info(f"STRM dosyası oluşturuldu: {movie_strm_path}")
    
    async with aiohttp.ClientSession() as session:
        # Film detaylarını TMDb API'den al ve NFO dosyasını oluştur
        movie_id = tmdb_data['id']
        movie_details_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={tmdb_api_key}&language=tr&append_to_response=credits,videos"
        movie_details_response = await fetch_data(session, movie_details_url)
        
        if movie_details_response:
            await create_nfo(movie_details_response, movie_nfo_path, is_tv=False)
        else:
            logging.error(f"Uyarı: Film detayları için TMDb API isteği başarısız oldu.")

async def create_default_strm(media_name, url_line):
    media_folder = os.path.join(movies_folder_path, sanitize_filename(media_name))
    os.makedirs(media_folder, exist_ok=True)
    media_strm_path = os.path.join(media_folder, f"{sanitize_filename(media_name)}.strm")
    
    async with aiofiles.open(media_strm_path, 'w', encoding='utf-8') as media_strm_file:
        await media_strm_file.write(url_line)
        logging.warning(f"Uyarı: '{media_name}' için TMDb verisi bulunamadı. STRM dosyası oluşturuldu: {media_strm_path}")

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

# Kullanım:

async def main():
    m3u_file_path = r'C:\Users\csmbs\Downloads\2024.m3u'
    output_folder_path = r'C:\Users\csmbs\Downloads\output_files'
    
    # fetch_iptv_channels çağrısını await ile yapın
    channels_data = await fetch_iptv_channels("https://iptv-org.github.io/api/channels.json", your_language_code)
    
    await process_m3u_file(m3u_file_path, output_folder_path, channels_data)

if __name__ == '__main__':
    asyncio.run(main())
