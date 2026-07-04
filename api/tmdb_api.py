import asyncio
import aiohttp
import logging
import itertools
import os
from urllib.parse import quote
from utils.string_utils import clean_name_for_search, extract_year
from config_manager import config_manager
from api.fanart_api import fetch_data, download_image

class APIRequestError(Exception):
    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.status_code = status_code

async def download_tmdb_images(session, tmdb_data, folder, media_type="movie"):
    tasks = []
    base_url = "https://image.tmdb.org/t/p/original"
    
    if media_type == "movie":
        if config_manager.get("img_movie_poster", True) and tmdb_data.get("poster_path"):
            tasks.append(download_image(session, base_url + tmdb_data["poster_path"], os.path.join(folder, "poster.jpg")))
        if config_manager.get("img_movie_fanart", True) and tmdb_data.get("backdrop_path"):
            tasks.append(download_image(session, base_url + tmdb_data["backdrop_path"], os.path.join(folder, "fanart.jpg")))
    else:
        if config_manager.get("img_series_poster", True) and tmdb_data.get("poster_path"):
            tasks.append(download_image(session, base_url + tmdb_data["poster_path"], os.path.join(folder, "poster.jpg")))
        if config_manager.get("img_series_bg", True) and tmdb_data.get("backdrop_path"):
            tasks.append(download_image(session, base_url + tmdb_data["backdrop_path"], os.path.join(folder, "fanart.jpg")))

    if tasks:
        await asyncio.gather(*tasks)

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
    tmdb_api_key = config_manager.get('tmdb_api_key', '').strip()
    tmdb_language = config_manager.get('tmdb_language', 'en-US')
    
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

tmdb_cache = {}

async def search_tmdb(query, is_tv=False, year=None):
    search_type = 'tv' if is_tv else 'movie'
    cache_key = f"{query}_{search_type}_{year}"
    
    if cache_key in tmdb_cache:
        return tmdb_cache[cache_key]

    tmdb_language = config_manager.get('tmdb_language', 'en-US')

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

