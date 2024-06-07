import json
import mysql.connector
from bs4 import BeautifulSoup
import requests

from googleapiclient.discovery import build


def getTimecodeHeatFromYoutube(youtubeID):
    # URL de la vidéo YouTube
    url = "https://www.youtube.com/watch?v=" + youtubeID

    # Effectuer une requête GET pour récupérer le contenu de la page
    response = requests.get(url)
    html_content = response.content
    # Analyser le contenu HTML avec BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Rechercher le script contenant le JSON ytInitialData
    scripts = soup.find_all('script')

    # Rechercher le script qui contient 'ytInitialData'
    yt_initial_data = None
    for script in scripts:
        if 'ytInitialData' in script.text:
            yt_initial_data = script
            break

    # Extraire le contenu JSON du script
    if yt_initial_data:
        start = yt_initial_data.text.find('ytInitialData = ') + len('ytInitialData = ')
        end = yt_initial_data.text.find('};', start) + 1
        json_str = yt_initial_data.text[start:end]
        yt_data = json.loads(json_str)
    else:
        raise ValueError("Impossible de trouver les données ytInitialData dans la page")

    # Explorer le JSON pour trouver les heat markers
    heat_markers = []
    for markers in explore_json(yt_data, 'markers'):
        for marker in markers:
            if 'startMillis' in marker and 'intensityScoreNormalized' in marker:
                heat_markers.append({
                    'start': int(marker['startMillis']),
                    'duration': int(marker['durationMillis']),
                    'intensity': marker['intensityScoreNormalized']
                })

    print(f"Heat markers trouvés: {heat_markers}")

    # Trouver le moment avec la plus haute intensité
    if heat_markers:
        most_viewed = max(heat_markers, key=lambda x: x['intensity'])

        # Convertir le moment en format lisible
        most_viewed_time = most_viewed['start'] / 1000
        most_viewed_minutes = int(most_viewed_time // 60)
        most_viewed_seconds = int(most_viewed_time % 60)
        return most_viewed['start'] / 1000
    else:
        return 0


def explore_json(obj, key):
    """
    Fonction pour explorer récursivement un objet JSON et trouver toutes les occurrences d'une clé spécifique.
    """
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == key:
                yield v
            if isinstance(v, (dict, list)):
                yield from explore_json(v, key)
    elif isinstance(obj, list):
        for item in obj:
            yield from explore_json(item, key)


def get_youtube_video_id(api_key, query):
    youtube = build('youtube', 'v3', developerKey=api_key)
    request = youtube.search().list(
        part='snippet',
        q=query,
        type='video',
        maxResults=1
    )
    response = request.execute()
    if response['items']:
        return response['items'][0]['id']['videoId']
    return None

def insert_movie(cursor, movie):
    cursor.execute('''
        INSERT INTO movie (name_EN, year, director, poster)
        VALUES (%s, %s, %s, %s)
    ''', (movie['Title'], movie['Year'], movie['Director'], movie['Poster']))
    return cursor.lastrowid

def insert_song(cursor, song, movie_id):
    print(getTimecodeHeatFromYoutube(song['VideoId']));
    cursor.execute('''
        INSERT INTO song (yt_id, movie_id, timecode)
        VALUES (%s, %s, %s)
    ''', ( song['VideoId'], movie_id, getTimecodeHeatFromYoutube(song['VideoId'])))

def dump_youtube_video_ids(api_key, movies_data, cursor):
    for movie in movies_data:
        query = f"{movie['Title']} soundtrack"
        video_id = get_youtube_video_id(api_key, query)
        if video_id:
            song = {'Title': f"{movie['Title']} Soundtrack", 'VideoId': video_id}
            movie_id = insert_movie(cursor, movie)
            insert_song(cursor, song, movie_id)
            print('Film enregistré : '+ movie['Title'] + "avec la musique : " + video_id)


def run():
    # Votre clé API YouTube
    youtube_api_key = 'AIzaSyC9Px2k6qm2Ql62tTGecXvAR1h9tMLfIaI'

    # Charger le fichier JSON
    with open('movies-250.json', 'r') as f:
        data = json.load(f)

    # Tronquer le tableau de données pour ne contenir que les cinq premiers films
    movies_data = data['movies'][:5]  # Assurez-vous que data est une liste

    # Connexion à la base de données MySQL
    conn = mysql.connector.connect(
        host='localhost',
        port=3306,
        user='root',
        password='',
        database='blindtos_poc'
    )

    cursor = conn.cursor()

    # Dump des ID vidéo YouTube pour les cinq premiers films
    dump_youtube_video_ids(youtube_api_key, movies_data, cursor)

    # Valider les transactions et fermer la connexion
    conn.commit()
    cursor.close()
    conn.close()


run()