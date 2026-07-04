import json
import os
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "log")
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR, exist_ok=True)

CONFIG_FILE = os.path.join(LOG_DIR, "config.json")
OLD_CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

DEFAULT_CONFIG = {
    "tmdb_api_key": "",
    "fanart_api_key": "",
    "iptvurl": "",
    "iptvusername": "",
    "iptvpassword": "",
    "your_language_code": "TR",
    "tmdb_language": "tr-TR",
    "theme": "Auto",
    "app_language": "tr",
    "nfo_movie": True,
    "nfo_series": True,
    "nfo_episode": True,
    "img_movie_poster": True,
    "img_movie_fanart": True,
    "img_movie_bg": True,
    "img_movie_logo": True,
    "img_movie_clearart": True,
    "img_movie_discart": True,
    "img_movie_banner": True,
    "img_movie_thumb": True,
    "img_series_poster": True,
    "img_series_bg": True,
    "img_series_banner": True,
    "img_series_logo": True,
    "img_series_thumb": True,
    "img_series_clearart": True,
    "img_series_character": True,
    "img_season_poster": True,
    "img_season_banner": True,
    "img_season_thumb": True
}

class ConfigManager:
    def __init__(self):
        self.config = {}
        self.config = self.load_config()

    def load_config(self):
        # Migrate old config if it exists
        if os.path.exists(OLD_CONFIG_FILE):
            try:
                shutil.move(OLD_CONFIG_FILE, CONFIG_FILE)
            except Exception:
                pass

        if not os.path.exists(CONFIG_FILE):
            self.save_config(DEFAULT_CONFIG)
            return DEFAULT_CONFIG.copy()
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Merge with defaults to ensure all keys exist
                config = DEFAULT_CONFIG.copy()
                config.update(data)
                return config
        except Exception:
            return DEFAULT_CONFIG.copy()

    def save_config(self, data=None):
        if data is not None:
            self.config.update(data)
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
        self.save_config()

config_manager = ConfigManager()
