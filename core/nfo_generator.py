import aiofiles
import logging
import os
from xml.sax.saxutils import escape
from config_manager import config_manager

async def create_nfo(data, file_path, is_tv=False):
    try:
        if is_tv:
            content = generate_tv_nfo_content(data)
        else:
            content = generate_movie_nfo_content(data)
        
        async with aiofiles.open(file_path, 'w', encoding='utf-8') as nfo_file:
            await nfo_file.write(content)
        logging.info(f"NFO file created: {file_path}")
    except Exception as e:
        logging.error(f"An error occurred: {e}")

def safe_escape(value):
    if value is None:
        return ""
    return escape(str(value))

def generate_tv_nfo_content(data):
    name = safe_escape(data.get('name', 'Unknown'))
    original_name = safe_escape(data.get('original_name', data.get('name', 'Unknown')))
    rating = data.get('vote_average', 'Unknown')
    year = data.get('first_air_date', '')[:4]
    votes = data.get('vote_count', 'Unknown')
    overview = safe_escape(data.get('overview', 'Description not available.'))
    poster_path = data.get('poster_path', '')
    backdrop_path = data.get('backdrop_path', '')
    mpaa = safe_escape('TV-MA' if data.get('adult') else 'TV-G')
    country = safe_escape(', '.join(data.get('origin_country', ['Unknown'])))
    premiered = safe_escape(data.get('first_air_date', 'Unknown'))
    status = safe_escape(data.get('status', 'Unknown'))
    tv_id = data.get('id', 'Unknown')
    genre = safe_escape(', '.join([genre.get('name', 'Unknown') for genre in data.get('genres', [])]))
    studio = safe_escape(', '.join([company.get('name', 'Unknown') for company in data.get('production_companies', [])]))
    
    content = f"""
<tvshow>
    <title>{name}</title>
    <originaltitle>{original_name}</originaltitle>
    <sorttitle>{name}</sorttitle>
    <rating>{rating}</rating>
    <year>{year}</year>
    <votes>{votes}</votes>
    <outline>{overview}</outline>
    <plot>{overview}</plot>
    <thumb>https://image.tmdb.org/t/p/original{poster_path}</thumb>
    <fanart>https://image.tmdb.org/t/p/original{backdrop_path}</fanart>
    <mpaa>{mpaa}</mpaa>
    <country>{country}</country>
    <premiered>{premiered}</premiered>
    <status>{status}</status>
    <id>{tv_id}</id>
    <genre>{genre}</genre>
    <studio>{studio}</studio>
"""
    for cast in data.get('credits', {}).get('cast', [])[:10]:
        actor_name = safe_escape(cast.get('name', 'Unknown'))
        role = safe_escape(cast.get('character', 'Unknown'))
        profile_path = cast.get('profile_path', '')
        content += f"""
    <actor>
        <name>{actor_name}</name>
        <role>{role}</role>
        <thumb>https://image.tmdb.org/t/p/original{profile_path}</thumb>
    </actor>"""

    content += "\n</tvshow>"
    return content

def generate_movie_nfo_content(data):
    title = safe_escape(data.get('title', 'Unknown'))
    original_title = safe_escape(data.get('original_title', 'Unknown'))
    rating = data.get('vote_average', 'Unknown')
    year = data.get('release_date', '')[:4]
    votes = data.get('vote_count', 'Unknown')
    outline = safe_escape(data.get('overview', 'Description not available.'))
    plot = safe_escape(data.get('overview', 'Description not available.'))
    tagline = safe_escape(data.get('tagline', 'Unknown'))
    runtime = data.get('runtime', 'Unknown')
    poster_path = data.get('poster_path', '')
    backdrop_path = data.get('backdrop_path', '')
    mpaa = safe_escape('PG-13' if data.get('adult') else 'G')
    country = safe_escape(', '.join([country.get('name', 'Unknown') for country in data.get('production_countries', [])]))
    premiered = safe_escape(data.get('release_date', 'Unknown'))
    status = safe_escape('Released' if data.get('status') == 'Released' else 'Unknown')
    imdb_id = data.get('imdb_id', 'Unknown')
    movie_id = data.get('id', 'Unknown')
    genre = safe_escape(', '.join([genre.get('name', 'Unknown') for genre in data.get('genres', [])]))
    studio = safe_escape(', '.join([company.get('name', 'Unknown') for company in data.get('production_companies', [])]))
    
    trailer_key = data.get('videos', {}).get('results', [{}])[0].get('key', '') if data.get('videos', {}).get('results') else ''
    trailer = safe_escape('https://www.youtube.com/watch?v=' + trailer_key if trailer_key else 'Unknown')
    
    director = safe_escape(', '.join([member.get('name', 'Unknown') for member in data.get('credits', {}).get('crew', []) if member.get('job') == 'Director']))
    credits = safe_escape(', '.join([member.get('name', 'Unknown') for member in data.get('credits', {}).get('crew', []) if member.get('job') == 'Writer']))
    
    content = f"""
<movie>
    <title>{title}</title>
    <originaltitle>{original_title}</originaltitle>
    <sorttitle>{title}</sorttitle>
    <rating>{rating}</rating>
    <year>{year}</year>
    <votes>{votes}</votes>
    <outline>{outline}</outline>
    <plot>{plot}</plot>
    <tagline>{tagline}</tagline>
    <runtime>{runtime}</runtime>
    <thumb>https://image.tmdb.org/t/p/original{poster_path}</thumb>
    <fanart>https://image.tmdb.org/t/p/original{backdrop_path}</fanart>
    <mpaa>{mpaa}</mpaa>
    <playcount>0</playcount>
    <country>{country}</country>
    <premiered>{premiered}</premiered>
    <status>{status}</status>
    <code>{imdb_id}</code>
    <id>{movie_id}</id>
    <genre>{genre}</genre>
    <studio>{studio}</studio>
    <trailer>{trailer}</trailer>
    <director>{director}</director>
    <credits>{credits}</credits>
"""
    for cast in data.get('credits', {}).get('cast', [])[:10]:
        actor_name = safe_escape(cast.get('name', 'Unknown'))
        role = safe_escape(cast.get('character', 'Unknown'))
        thumb = cast.get('profile_path', '')
        content += f"""
    <actor>
        <name>{actor_name}</name>
        <role>{role}</role>
        <thumb>https://image.tmdb.org/t/p/original{thumb}</thumb>
    </actor>"""

    content += "\n</movie>"
    return content
