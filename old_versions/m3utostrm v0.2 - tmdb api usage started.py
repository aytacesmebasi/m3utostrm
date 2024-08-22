import os
import re
import requests

# Enter the TMDb API key
tmdb_api_key = 'YOUR_API_KEY'

# Specify the M3U file path
current_working_directory = os.getcwd()
output_folder_path = os.path.join(current_working_directory, 'output_files')
os.makedirs(output_folder_path, exist_ok=True)
m3u_file_path = os.path.join(output_folder_path, 'tobeprocess.m3u')

# Create a folder to save STRM and NFO files
os.makedirs(output_folder_path, exist_ok=True)

# TMDb search function
def search_tmdb(movie_name):
    search_url = f"https://api.themoviedb.org/3/search/movie?api_key={tmdb_api_key}&query={movie_name}&language=tr"
    response = requests.get(search_url)
    if response.status_code == 200:
        results = response.json().get('results', [])
        if results:
            return results[0]  # First result
        else:
            print(f"Warning: No results found in TMDb for '{movie_name}'.")
    else:
        print(f"Warning: TMDb API request failed. Status Code: {response.status_code}")
    return None

# Movie name clear function
def clean_movie_name(movie_name):
    # Remove the year information in parentheses
    cleaned_name = re.sub(r'\s*\(\d{4}\)', '', movie_name)
    # Output year information separated by hyphens and spaces
    cleaned_name = re.sub(r'\s*[-]?\s*\d{4}', '', cleaned_name)
    return cleaned_name.strip()

# NFO file creation function
def create_nfo(movie_data, file_path):
    nfo_content = f"""
<movie>
    <title>{movie_data['title']}</title>
    <originaltitle>{movie_data['original_title']}</originaltitle>
    <sorttitle>{movie_data['title']}</sorttitle>
    <set></set>
    <rating>{movie_data.get('vote_average', '')}</rating>
    <year>{movie_data.get('release_date', '')[:4]}</year>
    <top250></top250>
    <votes>{movie_data.get('vote_count', '')}</votes>
    <outline>{movie_data.get('overview', '')}</outline>
    <plot>{movie_data.get('overview', '')}</plot>
    <tagline>{movie_data.get('tagline', '')}</tagline>
    <runtime>{movie_data.get('runtime', '')}</runtime>
    <thumb>https://image.tmdb.org/t/p/original{movie_data.get('poster_path', '')}</thumb>
    <fanart>https://image.tmdb.org/t/p/original{movie_data.get('backdrop_path', '')}</fanart>
    <mpaa>{'PG-13' if movie_data.get('adult') else 'G'}</mpaa>
    <playcount>0</playcount>
    <lastplayed></lastplayed>
    <country>{', '.join([country['name'] for country in movie_data.get('production_countries', [])])}</country>
    <premiered>{movie_data.get('release_date', '')}</premiered>
    <status>{'Released' if movie_data.get('status') == 'Released' else ''}</status>
    <code>{movie_data.get('imdb_id', '')}</code>
    <id>{movie_data.get('id', '')}</id>
    <genre>{', '.join([genre['name'] for genre in movie_data.get('genres', [])])}</genre>
    <studio>{', '.join([company['name'] for company in movie_data.get('production_companies', [])])}</studio>
    <trailer>{'https://www.youtube.com/watch?v=' + movie_data['videos']['results'][0]['key'] if movie_data.get('videos', {}).get('results') else ''}</trailer>
    <director>{', '.join([member['name'] for member in movie_data.get('credits', {}).get('crew', []) if member['job'] == 'Director'])}</director>
    <credits>{', '.join([member['name'] for member in movie_data.get('credits', {}).get('crew', []) if member['job'] == 'Writer'])}</credits>
"""

    # Players
    for cast in movie_data.get('credits', {}).get('cast', [])[:10]:  # İlk 10 oyuncu
        nfo_content += f"""
    <actor>
        <name>{cast['name']}</name>
        <role>{cast['character']}</role>
        <thumb>https://image.tmdb.org/t/p/original{cast['profile_path']}</thumb>
    </actor>"""

    nfo_content += "\n</movie>"

    with open(file_path, 'w', encoding='utf-8') as nfo_file:
        nfo_file.write(nfo_content)
    print(f"NFO file created: {file_path}")

# Read M3U file and create STRM/NFO files
with open(m3u_file_path, 'r', encoding='utf-8') as m3u_file:
    lines = m3u_file.readlines()
    
    i = 0
    while i < len(lines):
        extinf_line = lines[i].strip()
        
        if extinf_line.startswith('#EXTINF:'):
            if i + 1 < len(lines):
                url_line = lines[i + 1].strip()
                movie_name = extinf_line.split(',', 1)[1].strip()
                base_file_name = os.path.join(output_folder_path, movie_name)
                
                strm_file_path = f"{base_file_name}.strm"
                nfo_file_path = f"{base_file_name}.nfo"
                
                with open(strm_file_path, 'w', encoding='utf-8') as strm_file:
                    strm_file.write(url_line)
                
                # Clear movie name and search in TMDb
                cleaned_movie_name = clean_movie_name(movie_name)
                print(f"'{movie_name}' is being searched for in its cleaned form as '{cleaned_movie_name}'.")
                tmdb_data = search_tmdb(cleaned_movie_name)
                
                # Create NFO file if there is information from TMDb
                if tmdb_data:
                    # Request detailed information by movie ID for additional information
                    movie_id = tmdb_data['id']
                    movie_details_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={tmdb_api_key}&language=tr&append_to_response=credits,videos"
                    movie_details_response = requests.get(movie_details_url)
                    if movie_details_response.status_code == 200:
                        movie_details = movie_details_response.json()
                        create_nfo(movie_details, nfo_file_path)
                    else:
                        print(f"Warning: TMDb API request failed. Status Code: {movie_details_response.status_code}")
                else:
                    print(f"Warning: No TMDb data found for '{movie_name}'.")
                
                i += 2  # Jump to next #EXTINF line
            else:
                print(f"Warning: URL for {extinf_line} is missing.")
                i += 1  # We're in the last row, just move on
        else:
            print(f"Warning: #EXTINF line expected for {extinf_line}.")
            i += 1  # Skip this line and go to the next line

print("STRM and NFO files were created successfully.")
