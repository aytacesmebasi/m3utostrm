import aiohttp
import logging
from config_manager import config_manager
from api.fanart_api import fetch_data

async def fetch_iptv_channels(api_url):
    async with aiohttp.ClientSession() as session:
        response = await fetch_data(session, api_url)
        if response:
            logging.info("iptv-org API cache file created")
            return response  # Tüm kanalları döndür (ülke kısıtlaması olmadan)
        else:
            logging.warning("Warning: IPTV-Org API request failed.")
            return []

