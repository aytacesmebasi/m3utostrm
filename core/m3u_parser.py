import os
import requests
import logging
from datetime import datetime
from config_manager import config_manager
from utils.state_manager import load_state
from utils.string_utils import parse_filename

logger = logging.getLogger(__name__)

def download_m3u(url, username, password, filename):
    try:
        full_url = f"{url}/get.php?username={username}&password={password}&type=m3u"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
        }
        response = requests.get(full_url, headers=headers)
        response.raise_for_status()
        with open(filename, 'wb') as file:
            file.write(response.content)
        logger.info(f"{filename} was downloaded successfully.")
        return True
    except requests.RequestException as e:
        logger.error(f"Download failed: {e}")
        return False

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
    difference = {url: new_urls_with_extinf[url] for url in new_urls_with_extinf if url not in old_urls_with_extinf}
    return difference

def write_new_m3u(difference, output_file):
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write("#EXTM3U\n")
        for url, extinf in difference.items():
            file.write(f"{extinf}\n{url}\n")

def count_urls_in_m3u(m3u_file_path):
    with open(m3u_file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    return sum(1 for line in lines if line.startswith("http"))

def prepare_files(local_m3u_path, output_folder_path, movies_folder_path, series_folder_path, porn_folder_path, iptvurl, iptvusername, iptvpassword):
    os.makedirs(movies_folder_path, exist_ok=True)
    logger.info(f"Movies Folder created: {movies_folder_path}")

    os.makedirs(series_folder_path, exist_ok=True)
    logger.info(f"Series Folder created: {series_folder_path}")

    os.makedirs(porn_folder_path, exist_ok=True)
    logger.info(f"Porn Folder created: {porn_folder_path}")

    now = datetime.now()
    formatted_date = now.strftime('%d%m%y%H%M')
    filename = f'{formatted_date}.m3u'
    file_path = os.path.join(output_folder_path, filename)
    m3u_file_path = os.path.join(output_folder_path, 'm3u2strm.txt')
    
    state = load_state()
    if state and 'last_index' in state and os.path.exists(m3u_file_path):
        url_count = state.get('total_count', count_urls_in_m3u(m3u_file_path))
        remaining_url_count = url_count - (state['last_index'] // 2)
        logger.info(f"Resuming previous session from index {state['last_index']}. Total: {url_count}, Remaining: {remaining_url_count}")
        return m3u_file_path, url_count, remaining_url_count
    
    if local_m3u_path and os.path.exists(local_m3u_path):
        import shutil
        shutil.copy2(local_m3u_path, file_path)
        logger.info(f"Local file {local_m3u_path} copied to {file_path}")
    else:
        success = download_m3u(iptvurl, iptvusername, iptvpassword, file_path)
        if not success:
            logger.error("HATA: M3U dosyası indirilemedi! Bağlantı engellendi veya sunucu yanıt vermedi. İşlem sonlandırılıyor.")
            return None, 0, 0
    
    directory = output_folder_path
    files = [f for f in os.listdir(directory) if f.endswith('.m3u') and f != filename]
    
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
        latest_file = None
        
    m3u_file_path = os.path.join(output_folder_path, 'tobeprocess.m3u')
    
    if latest_file:
        new_urls_not_in_old = compare_m3u_files(os.path.join(directory, latest_file), file_path)
        if new_urls_not_in_old:
            logger.info("URLs and related #EXTINF lines that are not in the old file but are in the new file are written to the new file...")
            write_new_m3u(new_urls_not_in_old, m3u_file_path)
            logger.info(f"New M3U file saved as '{m3u_file_path}'.")
        else:
            logger.info("All URLs are present in old file. Creating empty 'tobeprocess.m3u' file...")
            with open(m3u_file_path, 'w', encoding='utf-8') as file:
                file.write("#EXTM3U\n")
            logger.info(f"Empty M3U file saved as '{m3u_file_path}'.")
        
        os.remove(os.path.join(directory, latest_file))
        logger.info(f"The newest file '{latest_file}' was deleted.")
    else:
        logger.info("The latest file was not found, only the downloaded file is saved as 'tobeprocess.m3u'...")
        with open(file_path, 'r', encoding='utf-8') as new_file:
            new_lines = new_file.readlines()
        with open(m3u_file_path, 'w', encoding='utf-8') as output_file:
            output_file.writelines(new_lines)
        logger.info(f"The downloaded M3U file was saved as '{m3u_file_path}'.")

    url_count = count_urls_in_m3u(m3u_file_path)
    remaining_url_count = url_count
    logger.info(f"There are {url_count} URLs in the file.")
    return m3u_file_path, url_count, remaining_url_count
