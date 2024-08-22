import os
import re
import requests

# TMDb API anahtarını girin
tmdb_api_key = 'YOUR_API_KEY'

# M3U dosya yolunu belirleyin
current_working_directory = os.getcwd()
output_folder_path = os.path.join(current_working_directory, 'output_files')
os.makedirs(output_folder_path, exist_ok=True)
m3u_file_path = os.path.join(output_folder_path, 'tobeprocess.m3u')
movies_folder_path = os.path.join(output_folder_path, 'movies')
series_folder_path = os.path.join(output_folder_path, 'series')
porn_folder_path = os.path.join(output_folder_path, 'porn')

# STRM ve NFO dosyalarını kaydetmek için klasör oluşturun
os.makedirs(movies_folder_path, exist_ok=True)
os.makedirs(series_folder_path, exist_ok=True)
os.makedirs(porn_folder_path, exist_ok=True)

# Dosya ve klasör isimlerindeki geçersiz karakterleri temizleme fonksiyonu
def sanitize_filename(filename):
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '')
    return filename

# URL'nin "porn" içerip içermediğini kontrol etme fonksiyonu
def is_porn_url(url):
    porn_patterns = [r'xxx', r'XxX', r'XXX', r'xxx1', r'XXX\.', r'2xxX']
    return any(re.search(pattern, url, re.IGNORECASE) for pattern in porn_patterns)

# Ad temizleme fonksiyonu (film ve dizi için)
def clean_name(name, is_tv=False):
    if is_tv:
        name = re.sub(r'\s*S\d{2}\s*E\d{2}', '', name)
    else:
        name = re.sub(r'\s*\(\d{4}\)', '', name)
        name = re.sub(r'\s*[-]?\s*\d{4}', '', name)
    return sanitize_filename(name.strip())

# TMDb arama fonksiyonu
def search_tmdb(query, is_tv=False):
    search_type = 'tv' if is_tv else 'movie'
    search_url = f"https://api.themoviedb.org/3/search/{search_type}?api_key={tmdb_api_key}&query={query}&language=tr"
    response = requests.get(search_url)
    if response.status_code == 200:
        results = response.json().get('results', [])
        if results:
            return results[0]  # İlk sonuç
        else:
            print(f"Uyarı: '{query}' için TMDb'de sonuç bulunamadı.")
    else:
        print(f"Uyarı: TMDb API isteği başarısız oldu. Durum Kodu: {response.status_code}")
    return None

# NFO dosyası oluşturma fonksiyonu (film ve dizi için)
def create_nfo(data, file_path, is_tv=False):
    if is_tv:
        nfo_content = f"""
<tvshow>
    <title>{data['name']}</title>
    <originaltitle>{data.get('original_name', data['name'])}</originaltitle>
    <sorttitle>{data['name']}</sorttitle>
    <rating>{data.get('vote_average', '')}</rating>
    <year>{data.get('first_air_date', '')[:4]}</year>
    <votes>{data.get('vote_count', '')}</votes>
    <outline>{data.get('overview', '')}</outline>
    <plot>{data.get('overview', '')}</plot>
    <thumb>https://image.tmdb.org/t/p/original{data.get('poster_path', '')}</thumb>
    <fanart>https://image.tmdb.org/t/p/original{data.get('backdrop_path', '')}</fanart>
    <mpaa>{'TV-MA' if data.get('adult') else 'TV-G'}</mpaa>
    <country>{', '.join(data.get('origin_country', []))}</country>
    <premiered>{data.get('first_air_date', '')}</premiered>
    <status>{data.get('status', '')}</status>
    <id>{data.get('id', '')}</id>
    <genre>{', '.join([genre['name'] for genre in data.get('genres', [])])}</genre>
    <studio>{', '.join([company['name'] for company in data.get('production_companies', [])])}</studio>
</tvshow>
"""
    else:
        nfo_content = f"""
<movie>
    <title>{data['title']}</title>
    <originaltitle>{data['original_title']}</originaltitle>
    <sorttitle>{data['title']}</sorttitle>
    <rating>{data.get('vote_average', '')}</rating>
    <year>{data.get('release_date', '')[:4]}</year>
    <votes>{data.get('vote_count', '')}</votes>
    <outline>{data.get('overview', '')}</outline>
    <plot>{data.get('overview', '')}</plot>
    <tagline>{data.get('tagline', '')}</tagline>
    <runtime>{data.get('runtime', '')}</runtime>
    <thumb>https://image.tmdb.org/t/p/original{data.get('poster_path', '')}</thumb>
    <fanart>https://image.tmdb.org/t/p/original{data.get('backdrop_path', '')}</fanart>
    <mpaa>{'PG-13' if data.get('adult') else 'G'}</mpaa>
    <playcount>0</playcount>
    <country>{', '.join([country['name'] for country in data.get('production_countries', [])])}</country>
    <premiered>{data.get('release_date', '')}</premiered>
    <status>{'Released' if data.get('status') == 'Released' else ''}</status>
    <code>{data.get('imdb_id', '')}</code>
    <id>{data.get('id', '')}</id>
    <genre>{', '.join([genre['name'] for genre in data.get('genres', [])])}</genre>
    <studio>{', '.join([company['name'] for company in data.get('production_companies', [])])}</studio>
    <trailer>{'https://www.youtube.com/watch?v=' + data['videos']['results'][0]['key'] if data.get('videos', {}).get('results') else ''}</trailer>
    <director>{', '.join([member['name'] for member in data.get('credits', {}).get('crew', []) if member['job'] == 'Director'])}</director>
    <credits>{', '.join([member['name'] for member in data.get('credits', {}).get('crew', []) if member['job'] == 'Writer'])}</credits>
</movie>
"""
        # Oyuncular
        for cast in data.get('credits', {}).get('cast', [])[:10]:  # İlk 10 oyuncu
            nfo_content += f"""
    <actor>
        <name>{cast['name']}</name>
        <role>{cast['character']}</role>
        <thumb>https://image.tmdb.org/t/p/original{cast['profile_path']}</thumb>
    </actor>"""

        nfo_content += "\n</movie>"

    with open(file_path, 'w', encoding='utf-8') as nfo_file:
        nfo_file.write(nfo_content)
    print(f"NFO dosyası oluşturuldu: {file_path}")

# Suffix pattern
suffix_pattern = re.compile(r'\s*(\[.*?\])(?:\s*\[.*?\]|\s*H\.265|\s*[A-Z]{2,})?\s*$', re.IGNORECASE)

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

# M3U dosyasını okuyun ve STRM/NFO dosyalarını oluşturun
with open(m3u_file_path, 'r', encoding='utf-8') as m3u_file:
    lines = m3u_file.readlines()

    # updated_channels.m3u dosyasını oluşturun veya açın
    updated_channels_file_path = os.path.join(output_folder_path, 'updated_channels.m3u')
    with open(updated_channels_file_path, 'w', encoding='utf-8') as updated_channels_file:
        # iptv-org API'den Türkiye kanal bilgilerini çek
        response = requests.get("https://iptv-org.github.io/api/channels.json")
        if response.status_code == 200:
            channels_data = response.json()
            channels_data = [channel for channel in channels_data if channel.get("country") == "TR"]
        else:
            print(f"Uyarı: IPTV-Org API isteği başarısız oldu. Durum Kodu: {response.status_code}")
            channels_data = []

        i = 0
        while i < len(lines):
            extinf_line = lines[i].strip()

            if extinf_line.startswith('#EXTINF:'):
                if i + 1 < len(lines):
                    url_line = lines[i + 1].strip()
                    media_name = extinf_line.split(',', 1)[1].strip()

                    # URL'nin ".ts" ile bitip bitmediğini kontrol et
                    if url_line.lower().endswith('.ts'):
                        # İsim temizleme
                        cleaned_media_name = suffix_pattern.sub('', media_name).strip()
                        cleaned_media_name = sanitize_filename(cleaned_media_name)

                        # Köşeli parantez içindeki değerleri 'bracketsin' olarak ayır
                        bracketsin_match = re.search(r'\[(.*?)\]', media_name)
                        bracketsin = bracketsin_match.group(1) if bracketsin_match else ''
                        
                        # IPTV-Org API'den kanal bilgilerini kontrol et
                        channel_info = next((channel for channel in channels_data if channel["name"].lower() == cleaned_media_name.lower()), None)
                        if channel_info:
                            channel_name = channel_info.get("name", media_name)  # Temizlenmemiş ismi kullan
                            logo = channel_info.get("logo", "")
                            id_ = channel_info.get("id", "")
                            owners = ', '.join(channel_info.get("owners", []))
                            languages = ', '.join(channel_info.get("languages", []))
                            is_nsfw = channel_info.get("is_nsfw", False)
                            
                            # Group-title değerini Türkçeleştirin
                            categories = ', '.join(channel_info.get("categories", []))
                            translated_categories = ', '.join([category_translation.get(cat, cat) for cat in categories.split(', ')])
                            group_title = translated_categories if categories else 'Bilinmeyen'
                            
                            # Temizlenmiş ismi ve diğer bilgileri .m3u dosyasına yazın
                            updated_channels_file.write(f"#EXTINF:-1 group-title=\"{group_title}; {bracketsin}\" tvg-id=\"{id_}\" tvg-name=\"{channel_name}\" tvg-logo=\"{logo}\" tvg-country=\"TR\" is-nsfw=\"{is_nsfw}\", {media_name}\n{url_line}\n")
                            print(f"URL '.ts' ile bitiyor ve updated_channels.m3u dosyasına eklendi: {url_line}")
                        else:
                            print(f"Uyarı: '{cleaned_media_name}' için IPTV-Org kanal bilgisi bulunamadı.")
                    else:
                        # Porn URL kontrolü
                        if is_porn_url(media_name):
                            porn_strm_path = os.path.join(porn_folder_path, f"{sanitize_filename(media_name)}.strm")
                            with open(porn_strm_path, 'w', encoding='utf-8') as porn_strm_file:
                                porn_strm_file.write(url_line)
                            print(f"STRM dosyası oluşturuldu: {porn_strm_path}")
                        else:
                            is_tv = 'S' in media_name and 'E' in media_name
                            cleaned_media_name = clean_name(media_name, is_tv=is_tv)
                            tmdb_data = search_tmdb(cleaned_media_name, is_tv=is_tv)
                            
                            if tmdb_data:
                                if is_tv:
                                    # Dizi
                                    show_name = cleaned_media_name
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
                                    
                                    with open(episode_strm_path, 'w', encoding='utf-8') as episode_strm_file:
                                        episode_strm_file.write(url_line)
                                    
                                    show_details_url = f"https://api.themoviedb.org/3/tv/{tmdb_data['id']}?api_key={tmdb_api_key}&language=tr&append_to_response=credits,videos"
                                    show_details_response = requests.get(show_details_url)
                                    if show_details_response.status_code == 200:
                                        show_details = show_details_response.json()
                                        create_nfo(show_details, series_nfo_path, is_tv=True)
                                        
                                        season_details_url = f"https://api.themoviedb.org/3/tv/{tmdb_data['id']}/season/{season}?api_key={tmdb_api_key}&language=tr"
                                        season_details_response = requests.get(season_details_url)
                                        if season_details_response.status_code == 200:
                                            season_details = season_details_response.json()
                                            create_nfo(season_details, season_nfo_path, is_tv=True)
                                            
                                            episode_details = next((ep for ep in season_details['episodes'] if ep['episode_number'] == int(episode)), None)
                                            if episode_details:
                                                create_nfo(episode_details, episode_nfo_path, is_tv=True)
                                            else:
                                                print(f"Uyarı: '{media_name}' için bölüm verisi bulunamadı.")
                                    else:
                                        print(f"Uyarı: TMDb API isteği başarısız oldu. Durum Kodu: {show_details_response.status_code}")
                                else:
                                    # Film
                                    movie_folder = os.path.join(movies_folder_path, cleaned_media_name)
                                    os.makedirs(movie_folder, exist_ok=True)
                                    movie_strm_path = os.path.join(movie_folder, f"{cleaned_media_name}.strm")
                                    movie_nfo_path = os.path.join(movie_folder, f"{cleaned_media_name}.nfo")
                                    
                                    with open(movie_strm_path, 'w', encoding='utf-8') as movie_strm_file:
                                        movie_strm_file.write(url_line)
                                    
                                    movie_id = tmdb_data['id']
                                    movie_details_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={tmdb_api_key}&language=tr&append_to_response=credits,videos"
                                    movie_details_response = requests.get(movie_details_url)
                                    if movie_details_response.status_code == 200:
                                        movie_details = movie_details_response.json()
                                        create_nfo(movie_details, movie_nfo_path, is_tv=False)
                                    else:
                                        print(f"Uyarı: TMDb API isteği başarısız oldu. Durum Kodu: {movie_details_response.status_code}")
                            
                            else:
                                print(f"Uyarı: '{media_name}' için TMDb verisi bulunamadı.")
                
                i += 2  # Bir sonraki #EXTINF satırına atla
            else:
                print(f"Uyarı: {extinf_line} için #EXTINF satırı bekleniyor.")
                i += 1  # Bu satırı atla ve bir sonraki satıra geç
