import asyncio
import aiohttp
import logging
import aiofiles
import os
from config_manager import config_manager

api_semaphore = asyncio.Semaphore(10)

async def download_image(session, url, file_path):
    if not url: return
    if os.path.exists(file_path): return
    try:
        async with api_semaphore:
            async with session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    content = await resp.read()
                    async with aiofiles.open(file_path, "wb") as f:
                        await f.write(content)
    except Exception as e:
        logging.error(f"Image download failed: {url} -> {e}")

async def fetch_fanart_data(session, item_id, folder, media_type="movie", tvdb_id=None):
    fanart_api_key = config_manager.get('fanart_api_key', '').strip()
    if not fanart_api_key: return
    
    if media_type == "movie":
        if not any(config_manager.get(k, True) for k in ['img_movie_clearart', 'img_movie_discart', 'img_movie_banner', 'img_movie_thumb', 'img_movie_logo']): return
        url = f"https://webservice.fanart.tv/v3/movies/{item_id}?api_key={fanart_api_key}"
        prefix = ""
    else:
        if not any(config_manager.get(k, True) for k in ['img_series_clearart', 'img_series_character', 'img_series_banner', 'img_series_thumb', 'img_series_logo']): return
        if not tvdb_id: return
        url = f"https://webservice.fanart.tv/v3/tv/{tvdb_id}?api_key={fanart_api_key}"
        prefix = ""

    try:
        async with api_semaphore:
            async with session.get(url, timeout=10) as resp:
                if resp.status != 200: return
                data = await resp.json()

        def get_best_image(img_list):
            if not img_list: return None
            target_lang = config_manager.get('tmdb_language', 'en-US').split('-')[0]
            for lang in [target_lang, 'en', '00', '']:
                for img in img_list:
                    if img.get('lang') == lang: return img.get('url')
            return None

        tasks = []
        if media_type == "movie":
            if config_manager.get("img_movie_clearart", True) and ('hdmovieclearart' in data or 'movieclearart' in data):
                img_url = get_best_image(data.get('hdmovieclearart') or data.get('movieclearart'))
                tasks.append(download_image(session, img_url, os.path.join(folder, f"{prefix}clearart.png")))
            if config_manager.get("img_movie_discart", True) and 'moviedisc' in data:
                img_url = get_best_image(data.get('moviedisc'))
                tasks.append(download_image(session, img_url, os.path.join(folder, f"{prefix}discart.png")))
            if config_manager.get("img_movie_banner", True) and 'moviebanner' in data:
                img_url = get_best_image(data.get('moviebanner'))
                tasks.append(download_image(session, img_url, os.path.join(folder, f"{prefix}banner.jpg")))
            if config_manager.get("img_movie_thumb", True) and 'moviethumb' in data:
                img_url = get_best_image(data.get('moviethumb'))
                tasks.append(download_image(session, img_url, os.path.join(folder, f"{prefix}landscape.jpg")))
            if config_manager.get("img_movie_logo", True) and ('hdmovielogo' in data or 'movielogo' in data):
                img_url = get_best_image(data.get('hdmovielogo') or data.get('movielogo'))
                tasks.append(download_image(session, img_url, os.path.join(folder, f"{prefix}clearlogo.png")))
        else:
            if config_manager.get("img_series_clearart", True) and ('hdclearart' in data or 'clearart' in data):
                img_url = get_best_image(data.get('hdclearart') or data.get('clearart'))
                tasks.append(download_image(session, img_url, os.path.join(folder, f"{prefix}clearart.png")))
            if config_manager.get("img_series_character", True) and 'characterart' in data:
                img_url = get_best_image(data.get('characterart'))
                tasks.append(download_image(session, img_url, os.path.join(folder, f"{prefix}characterart.png")))
            if config_manager.get("img_series_banner", True) and 'tvbanner' in data:
                img_url = get_best_image(data.get('tvbanner'))
                tasks.append(download_image(session, img_url, os.path.join(folder, f"{prefix}banner.jpg")))
            if config_manager.get("img_series_thumb", True) and 'tvthumb' in data:
                img_url = get_best_image(data.get('tvthumb'))
                tasks.append(download_image(session, img_url, os.path.join(folder, f"{prefix}landscape.jpg")))
            if config_manager.get("img_series_logo", True) and ('hdtvlogo' in data or 'clearlogo' in data):
                img_url = get_best_image(data.get('hdtvlogo') or data.get('clearlogo'))
                tasks.append(download_image(session, img_url, os.path.join(folder, f"{prefix}clearlogo.png")))
        
        if tasks:
            await asyncio.gather(*tasks)

    except Exception as e:
        logging.error(f"Fanart fetch failed: {e}")

async def fetch_data(session, url, retries=4, delay=2.0):
    for attempt in range(retries):
        try:
            async with api_semaphore:
                async with session.get(url) as response:
                    if response.status == 429:
                        retry_after = int(response.headers.get("Retry-After", delay))
                        logging.warning(f"Rate limited (429). Retrying after {retry_after}s for {url}")
                        await asyncio.sleep(retry_after)
                        delay *= 2
                        continue
                    response.raise_for_status()
                    return await response.json()
        except aiohttp.ClientResponseError as e:
            if e.status == 404:
                logging.warning(f"API request failed: 404 Not Found - {url}")
                return None
            else:
                logging.error(f"API request failed (attempt {attempt + 1}/{retries}): {e} - Status Code: {e.status}")
                if attempt < retries - 1:
                    await asyncio.sleep(delay)
                    delay *= 2
                else:
                    return None
        except aiohttp.ClientError as e:
            logging.error(f"API request failed (attempt {attempt + 1}/{retries}): {e}")
            if attempt < retries - 1:
                await asyncio.sleep(delay)
                delay *= 2
            else:
                return None
        except asyncio.TimeoutError as e:
            logging.error(f"API request timeout (attempt {attempt + 1}/{retries}): {e}")
            if attempt < retries - 1:
                await asyncio.sleep(delay)
                delay *= 2
            else:
                return None
    return None

