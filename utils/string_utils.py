import re
import unicodedata
import string
import os
from config_manager import config_manager

def translate_category(category):
    return category_translation.get(category.lower(), DEFAULT_CATEGORY)

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

def extract_media_name(line):
    in_quotes = False
    for i, char in enumerate(line):
        if char == '"':
            in_quotes = not in_quotes
        elif char == ',' and not in_quotes:
            return line[i+1:].strip()
    return line.split(',', 1)[-1].strip()

def extract_bracketsin(media_name):
    bracketsin_match = re.search(r'\[(.*?)\]', media_name)
    return bracketsin_match.group(1).replace(' ', '') if bracketsin_match else ''

