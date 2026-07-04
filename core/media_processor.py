import asyncio
import logging
import os
import aiofiles
import aiohttp
import re
from datetime import datetime
from config_manager import config_manager
from utils.state_manager import load_state, save_state, clear_state
from utils.string_utils import parse_filename, sanitize_filename, clean_channel_name_for_match, translate_category, extract_media_name, is_porn_url, extract_bracketsin, clean_name_for_search, extract_year
from api.iptv_api import fetch_iptv_channels
from api.tmdb_api import search_tmdb, download_tmdb_images
from api.fanart_api import fetch_fanart_data, fetch_data, download_image
from core.nfo_generator import create_nfo
from core.m3u_parser import prepare_files, count_urls_in_m3u

logger = logging.getLogger(__name__)

def check_channel_match(channel, match_name):
    if clean_channel_name_for_match(channel.get("name", "")) == match_name:
        return True
    if clean_channel_name_for_match(channel.get("id", "")) == match_name:
        return True
    for alt in channel.get("alt_names", []):
        if clean_channel_name_for_match(alt) == match_name:
            return True
    return False

class MediaProcessor:
    def __init__(self, signals=None):
        self.is_stopped = False
        self.is_paused = False
        self.url_count = 0
        self.remaining_url_count = 0
        self.file_lock = None
        
        self.signals = signals
        
        # Load API keys and settings from config
        self.config_manager = config_manager
        self.config_manager.load_config()
        self.tmdb_api_key = self.config_manager.get('tmdb_api_key', '')
        self.tmdb_language = self.config_manager.get('tmdb_language', 'en-US')
        self.your_language_code = self.config_manager.get('your_language_code', 'EN')
        
        # Paths
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.output_folder_path = os.path.join(base_dir, "output")
        self.movies_folder_path = self.config_manager.get('movies_folder_path') or os.path.join(self.output_folder_path, "Movies")
        self.series_folder_path = self.config_manager.get('series_folder_path') or os.path.join(self.output_folder_path, "Series")
        self.porn_folder_path = self.config_manager.get('porn_folder_path') or os.path.join(self.output_folder_path, "XXX")
        
        self.category_translation = {}

    def log_info(self, msg):
        logger.info(f"{self.url_count} / {self.remaining_url_count} left - {msg}")

    def log_warning(self, msg):
        logger.warning(f"{self.url_count} / {self.remaining_url_count} left - {msg}")

    async def process_extinf_line(self, extinf_line, url_line, channels_data, output_file):
        media_name = extract_media_name(extinf_line)
        url_line_lower = url_line.lower()
        
        if url_line_lower.endswith('.ts'):
            await self.handle_ts_url(media_name, url_line, channels_data, output_file)
        else:
            await self.handle_non_ts_url(media_name, url_line)

    async def handle_ts_url(self, media_name, url_line, channels_data, output_file):
        match_name = clean_channel_name_for_match(media_name)
        bracketsin = extract_bracketsin(media_name)
        
        channel_info = next((channel for channel in channels_data if check_channel_match(channel, match_name)), None)
        if channel_info:
            await self.write_channel_info(channel_info, media_name, url_line, bracketsin, output_file)
        else:
            await self.write_default_channel_info(media_name, url_line, bracketsin, output_file)

    async def write_channel_info(self, channel_info, media_name, url_line, bracketsin, output_file):
        channel_name = channel_info.get("name", media_name)
        logo = channel_info.get("logo", "")
        id_ = channel_info.get("id", "")
        is_nsfw = channel_info.get("is_nsfw", False)
        
        categories = ', '.join(channel_info.get("categories", []))
        translated_categories = ', '.join([self.category_translation.get(cat, cat) for cat in categories.split(', ')])
        group_title = translated_categories if categories else 'Unknown'
        
        content = f"#EXTINF:-1 group-title=\"{group_title}; {bracketsin}\" tvg-id=\"{id_}\" tvg-name=\"{channel_name}\" tvg-logo=\"{logo}\" tvg-country=\"{self.your_language_code}\" is-nsfw=\"{is_nsfw}\", {media_name}\n{url_line}\n"
        
        async with self.file_lock:
            await output_file.write(content)
        
        self.remaining_url_count -= 1
        self.log_info(f"URL ends with '.ts' and added: {url_line}")

    async def write_default_channel_info(self, media_name, url_line, bracketsin, output_file):
        group_title = 'Unknown'
        content = f"#EXTINF:-1 group-title=\"{group_title}; {bracketsin}\" tvg-name=\"{sanitize_filename(media_name)}\" tvg-country=\"{self.your_language_code}\" is-nsfw=\"false\", {media_name}\n{url_line}\n"
        
        async with self.file_lock:
            await output_file.write(content)
        
        self.remaining_url_count -= 1
        self.log_warning(f"Warning: No IPTV-Org channel information found for '{media_name}'.")

    async def handle_non_ts_url(self, media_name, url_line):
        if is_porn_url(media_name):
            await self.create_porn_strm(media_name, url_line)
        else:
            is_tv = 'S' in media_name and 'E' in media_name
            search_query = clean_name_for_search(media_name, is_tv=is_tv)
            year = extract_year(media_name)
            tmdb_data = await search_tmdb(search_query, is_tv=is_tv, year=year)
            
            if tmdb_data:
                if is_tv:
                    await self.create_tv_show_files(search_query, tmdb_data, url_line, media_name)
                else:
                    await self.create_movie_files(search_query, tmdb_data, url_line)
            else:
                await self.create_default_strm(media_name, url_line)

    async def create_porn_strm(self, media_name, url_line):
        porn_strm_path = os.path.join(self.porn_folder_path, f"{sanitize_filename(media_name)}.strm")
        
        if not os.path.exists(porn_strm_path):
            async with aiofiles.open(porn_strm_path, 'w', encoding='utf-8') as porn_strm_file:
                await porn_strm_file.write(url_line)
                self.remaining_url_count -= 1
                self.log_info(f"STRM file created for porn: {porn_strm_path}")
        else:
            self.remaining_url_count -= 1
            self.log_info(f"STRM file already exists: {porn_strm_path}")

    async def create_tv_show_files(self, show_name, tmdb_data, url_line, media_name):
        year = tmdb_data.get('first_air_date', '')[:4]
        clean_show_title = sanitize_filename(tmdb_data.get('name', show_name))
        
        season_episode_match = re.search(r'\s*S(\d{2})\s*E(\d{2})', media_name)
        season = season_episode_match.group(1) if season_episode_match else '01'
        episode = season_episode_match.group(2) if season_episode_match else '01'
        
        show_folder = os.path.join(self.series_folder_path, f"{clean_show_title} ({year})")
        season_folder = os.path.join(show_folder, f"Season {int(season)}")
        os.makedirs(season_folder, exist_ok=True)
        
        series_nfo_path = os.path.join(show_folder, f"{clean_show_title} ({year}).nfo")
        season_nfo_path = os.path.join(season_folder, f"{clean_show_title} ({year}) S{season}.nfo")
        episode_strm_path = os.path.join(season_folder, f"{clean_show_title} ({year}) S{season}E{episode}.strm")
        episode_nfo_path = os.path.join(season_folder, f"{clean_show_title} ({year}) S{season}E{episode}.nfo")
        
        if not os.path.exists(episode_strm_path):
            async with aiofiles.open(episode_strm_path, 'w', encoding='utf-8') as episode_strm_file:
                await episode_strm_file.write(url_line)
                self.remaining_url_count -= 1
                self.log_info(f"STRM file created: {episode_strm_path}")
        else:
            self.remaining_url_count -= 1
            self.log_info(f"STRM file already exists: {episode_strm_path}")
        
        if not os.path.exists(series_nfo_path) or not os.path.exists(season_nfo_path) or not os.path.exists(episode_nfo_path):
            async with aiohttp.ClientSession() as session:
                show_details_url = f"https://api.themoviedb.org/3/tv/{tmdb_data['id']}?api_key={self.tmdb_api_key}&language={self.tmdb_language}&append_to_response=credits,videos"
                show_details_response = await fetch_data(session, show_details_url)
                if show_details_response:
                    if not os.path.exists(series_nfo_path) and self.config_manager.get('nfo_series', True):
                        await create_nfo(show_details_response, series_nfo_path, is_tv=True)
                    
                    await download_tmdb_images(session, show_details_response, show_folder, media_type="tv")
                    
                    tvdb_id = None
                    if self.config_manager.get('fanart_api_key', '').strip():
                        ext_ids_url = f"https://api.themoviedb.org/3/tv/{tmdb_data['id']}/external_ids?api_key={self.tmdb_api_key}"
                        ext_ids_response = await fetch_data(session, ext_ids_url)
                        if ext_ids_response and ext_ids_response.get('tvdb_id'):
                            tvdb_id = ext_ids_response.get('tvdb_id')
                    
                    await fetch_fanart_data(session, tmdb_data['id'], show_folder, media_type="tv", tvdb_id=tvdb_id)
                    
                    season_details_url = f"https://api.themoviedb.org/3/tv/{tmdb_data['id']}/season/{int(season)}?api_key={self.tmdb_api_key}&language={self.tmdb_language}"
                    season_details_response = await fetch_data(session, season_details_url)
                    if season_details_response:
                        if not os.path.exists(season_nfo_path) and self.config_manager.get('nfo_season', True):
                            await create_nfo(season_details_response, season_nfo_path, is_tv=True)
                        
                        tasks = []
                        base_url = "https://image.tmdb.org/t/p/original"
                        if self.config_manager.get('img_season_poster', True) and season_details_response.get('poster_path'):
                            tasks.append(download_image(session, base_url + season_details_response['poster_path'], os.path.join(season_folder, f"season{int(season)}-poster.jpg")))
                        if tasks:
                            await asyncio.gather(*tasks)
                        
                        episode_details = next((ep for ep in season_details_response.get('episodes', []) if ep['episode_number'] == int(episode)), None)
                        if episode_details and not os.path.exists(episode_nfo_path) and self.config_manager.get('nfo_episode', True):
                            await create_nfo(episode_details, episode_nfo_path, is_tv=True)
                        else:
                            logger.warning(f"Warning: Episode data for '{media_name}' not found or NFO file already exists.")
                    else:
                        logger.warning(f"Warning: TMDb API request for season details failed.")
                else:
                    logger.warning(f"Warning: TMDb API request for series details failed.")
        else:
            logger.info("All NFO files are already available.")

    async def create_movie_files(self, movie_name, tmdb_data, url_line):
        year = tmdb_data.get('release_date', '')[:4]
        clean_movie_title = sanitize_filename(tmdb_data.get('title', movie_name))
        
        movie_folder = os.path.join(self.movies_folder_path, f"{clean_movie_title} ({year})")
        os.makedirs(movie_folder, exist_ok=True)
        
        movie_nfo_path = os.path.join(movie_folder, f"{clean_movie_title} ({year}).nfo")
        movie_strm_path = os.path.join(movie_folder, f"{clean_movie_title} ({year}).strm")
        
        if not os.path.exists(movie_strm_path):
            async with aiofiles.open(movie_strm_path, 'w', encoding='utf-8') as movie_strm_file:
                await movie_strm_file.write(url_line)
                self.remaining_url_count -= 1
                self.log_info(f"STRM file created: {movie_strm_path}")
        else:
            self.remaining_url_count -= 1
            self.log_info(f"STRM file already exists: {movie_strm_path}")
        
        if not os.path.exists(movie_nfo_path):
            async with aiohttp.ClientSession() as session:
                movie_id = tmdb_data['id']
                movie_details_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={self.tmdb_api_key}&language={self.tmdb_language}&append_to_response=credits,videos"
                movie_details_response = await fetch_data(session, movie_details_url)
                
                if movie_details_response:
                    if self.config_manager.get('nfo_movie', True):
                        await create_nfo(movie_details_response, movie_nfo_path, is_tv=False)
                    await download_tmdb_images(session, movie_details_response, movie_folder, media_type="movie")
                    await fetch_fanart_data(session, movie_id, movie_folder, media_type="movie")
                else:
                    logger.warning(f"Warning: TMDb API request for movie details failed.")

    async def create_default_strm(self, media_name, url_line):
        media_name_clean = sanitize_filename(media_name).replace('.', ' ').strip()
        default_folder = os.path.join(self.movies_folder_path, media_name_clean)
        os.makedirs(default_folder, exist_ok=True)
        
        media_strm_path = os.path.join(default_folder, f"{media_name_clean}.strm")
        
        if not os.path.exists(media_strm_path):
            async with aiofiles.open(media_strm_path, 'w', encoding='utf-8') as media_strm_file:
                await media_strm_file.write(url_line)
                self.remaining_url_count -= 1
                self.log_warning(f"Warning: No TMDb data found for '{media_name}'. Created STRM file: {media_strm_path}")
        else:
            self.remaining_url_count -= 1
            self.log_info(f"STRM file already exists: {media_strm_path}")

    async def process_m3u_file(self, m3u_file_path, channels_data):
        async with aiofiles.open(m3u_file_path, 'r', encoding='utf-8') as m3u_file:
            lines = await m3u_file.readlines()

        updated_channels_file_path = os.path.join(self.output_folder_path, 'updated_channels.m3u')
        
        state = load_state()
        i = state.get('last_index', 0)
        self.is_stopped = False
        
        mode = 'a' if i > 0 else 'w'
        batch_size = 5
        tasks_batch = []
        
        async with aiofiles.open(updated_channels_file_path, mode, encoding='utf-8') as updated_channels_file:
            while i < len(lines):
                while self.is_paused:
                    await asyncio.sleep(0.5)
                if self.is_stopped:
                    break
                    
                extinf_line = lines[i].strip()
                if extinf_line.startswith('#EXTINF:'):
                    if i + 1 < len(lines):
                        url_line = lines[i + 1].strip()
                        tasks_batch.append(self.process_extinf_line(extinf_line, url_line, channels_data, updated_channels_file))
                        i += 2
                    else:
                        i += 1
                else:
                    i += 1
                    
                if len(tasks_batch) >= batch_size or i >= len(lines):
                    if tasks_batch:
                        await asyncio.gather(*tasks_batch)
                        tasks_batch.clear()
                        save_state(i, self.url_count)
                    
        if not self.is_stopped:
            clear_state()

    async def run(self, local_m3u_path=None):
        self.file_lock = asyncio.Lock()
        iptvurl = self.config_manager.get("iptvurl")
        iptvusername = self.config_manager.get("iptvusername")
        iptvpassword = self.config_manager.get("iptvpassword")

        m3u_file_path, self.url_count, self.remaining_url_count = prepare_files(
            local_m3u_path, self.output_folder_path, self.movies_folder_path, 
            self.series_folder_path, self.porn_folder_path,
            iptvurl, iptvusername, iptvpassword
        )
        if m3u_file_path:
            channels_data = await fetch_iptv_channels("https://iptv-org.github.io/api/channels.json")
            if not channels_data:
                channels_data = []
            await self.process_m3u_file(m3u_file_path, channels_data)
