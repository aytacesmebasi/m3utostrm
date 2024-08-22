import os
import re
import requests

# TMDb API anahtarını ve dil kodunu girin
tmdb_api_key = 'YOUR_API_KEY'
your_country_code = 'tr'  # Burada dil kodunu değiştirebilirsiniz

# M3U dosya yolunu belirleyin
current_working_directory = os.getcwd()
output_folder_path = os.path.join(current_working_directory, 'output_files')
os.makedirs(output_folder_path, exist_ok=True)
m3u_file_path = os.path.join(output_folder_path, 'tobeprocess.m3u')
movies_folder_path = os.path.join(output_folder_path, 'movies')
series_folder_path = os.path.join(output_folder_path, 'series')
porn_folder_path = os.path.join(output_folder_path, 'porn')
updated_channels_m3u_path = os.path.join(output_folder_path, 'updated_channels.m3u')

# STRM ve NFO dosyalarını kaydetmek için klasör oluşturun
os.makedirs(movies_folder_path, exist_ok=True)
os.makedirs(series_folder_path, exist_ok=True)
os.makedirs(porn_folder_path, exist_ok=True)
os.makedirs(os.path.dirname(updated_channels_m3u_path), exist_ok=True)

# Dosya ve klasör isimlerindeki geçersiz karakterleri temizleme fonksiyonu
def sanitize_filename(filename):
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '')
    return filename

# TMDb arama fonksiyonu
def search_tmdb(query, is_tv=False):
    search_type = 'tv' if is_tv else 'movie'
    search_url = f"https://api.themoviedb.org/3/search/{search_type}?api_key={tmdb_api_key}&query={query}&language={your_country_code}"
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

# M3U dosyasını okuyun ve STRM/NFO dosyalarını oluşturun
with open(m3u_file_path, 'r', encoding='utf-8') as m3u_file:
    lines = m3u_file.readlines()

    with open(updated_channels_m3u_path, 'w', encoding='utf-8') as updated_m3u_file:
        i = 0
        while i < len(lines):
            extinf_line = lines[i].strip()
            
            if extinf_line.startswith('#EXTINF:'):
                if i + 1 < len(lines):
                    url_line = lines[i + 1].strip()
                    media_name = extinf_line.split(',', 1)[1].strip()
                    
                    # URL'nin '.ts' ile bitip bitmediğini kontrol et
                    if url_line.lower().endswith('.ts'):
                        # '.ts' ile biten URL'leri updated_channels.m3u dosyasına ekle
                        updated_m3u_file.write(f"{extinf_line}\n{url_line}\n")
                        print(f"URL '.ts' ile bitiyor ve updated_channels.m3u dosyasına eklendi: {url_line}")
                    else:
                        # Diğer URL'ler için mevcut işlemleri yap
                        if is_porn_url(media_name):
                            # Porn içerikli URL'ler için
                            porn_strm_path = os.path.join(porn_folder_path, f"{sanitize_filename(clean_name(media_name))}.strm")
                            os.makedirs(os.path.dirname(porn_strm_path), exist_ok=True)
                            with open(porn_strm_path, 'w', encoding='utf-8') as porn_strm_file:
                                porn_strm_file.write(url_line)
                            print(f"Porn STRM dosyası oluşturuldu: {porn_strm_path}")
                        else:
                            is_tv = 'S' in media_name and 'E' in media_name
                            cleaned_media_name = clean_name(media_name, is_tv=is_tv)
                            
                            if is_tv:
                                # Dizi
                                show_name = cleaned_media_name
                                year = search_tmdb(cleaned_media_name, is_tv=is_tv).get('first_air_date', '')[:4]
                                season_episode_match = re.search(r'\s*S(\d{2})\s*E(\d{2})', media_name)
                                season = season_episode_match.group(1) if season_episode_match else '01'
                                strm_file_path = os.path.join(series_folder_path, show_name, f'Season {season}', f'{cleaned_media_name}.strm')
                                nfo_file_path = os.path.join(series_folder_path, show_name, f'Season {season}', f'{cleaned_media_name}.nfo')
                            else:
                                # Film
                                strm_file_path = os.path.join(movies_folder_path, f'{cleaned_media_name}.strm')
                                nfo_file_path = os.path.join(movies_folder_path, f'{cleaned_media_name}.nfo')
                            
                            # STRM dosyasını oluşturma
                            os.makedirs(os.path.dirname(strm_file_path), exist_ok=True)
                            with open(strm_file_path, 'w', encoding='utf-8') as strm_file:
                                strm_file.write(url_line)
                            print(f"STRM dosyası oluşturuldu: {strm_file_path}")

                            # NFO dosyasını oluşturma
                            tmdb_data = search_tmdb(cleaned_media_name, is_tv=is_tv)
                            if tmdb_data:
                                create_nfo(tmdb_data, nfo_file_path, is_tv=is_tv)
                
                i += 1
            i += 1
