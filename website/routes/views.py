from flask import Blueprint, render_template, request, url_for, jsonify
from flask_login import login_required, current_user
from ..models.models import Artist, Album, Song
import requests
from .. import db

views = Blueprint('views', __name__)

welcomeItems = [
    {
        "name" : "New Music",
        "info" : "Desc",
        "bg" : "#bd2b2b",
        "label" : "New Releases", 
        "url" : "/"
    },
    {
        "name" : "Popular",
        "info" : "",
        "bg" : "#00ff37",
        "label" : "Trending", 
        "url" : "/"
    },
    {
        "name" : "Set The Mood",
        "info" : "",
        "bg" : "#aaaaff",
        "label" : "Made For You", 
        "url" : "/"
    },
    {
        "name" : "",
        "info" : "Drake & Similar Artists",
        "bg" : "#4d4d4d",
        "label" : "Featuring Drake", 
        "url" : "/"
    },
]

@views.route("/")
@login_required
def home():
    recents = current_user.recents
    recents.reverse()

    return render_template('index.html', user=current_user, welcomeItems=welcomeItems, recents=recents)

@views.route("/search", methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        query = request.json.get("q")

        if len(query.strip()) < 1:
            return jsonify({"status" : "error", "message" : "invalid query"})
        else:
            tracks_url = f"https://api.deezer.com/search/track?q={query}"
            res = requests.get(tracks_url)
            tracks = res.json()['data']
            tracks = sorted(tracks, key=lambda item: item["rank"], reverse=True)

            artists_url = f"https://api.deezer.com/search/artist?q={query}"
            res = requests.get(artists_url)
            artists = res.json()['data']
            artists = sorted(artists, key=lambda item: item["nb_fan"], reverse=True)
           
            albums_url = f"https://api.deezer.com/search/album?q={query}"
            res = requests.get(albums_url)
            albums = res.json()['data']

            return jsonify({
                "tracks" : tracks,
                "artists" : artists,
                "albums" : albums,
            })    
    else:
        if 'q' in request.args:
            query = request.args.get('q')

            if len(query.strip()) < 1:
                return render_template('search.html', searched=False)
            else:
                url = f"https://api.deezer.com/search/track?q={query}"
                res = requests.get(url)
                results = res.json()
                
                return render_template('search.html', searched=True, results=results)
        else:
            return render_template('search.html', user=current_user, searched=False)

###

@views.route("/artist/<id>")
def artist(id):
    # try :
    url = f"https://api.deezer.com/artist/{id}"
    res = requests.get(url)
    artist = res.json()

    albums_url = f"https://api.deezer.com/artist/{id}/albums"
    res = requests.get(albums_url)
    albums = res.json()
        
    tracks_url = artist['tracklist']
    res = requests.get(tracks_url)
    top_tracks = res.json()

    collabs = find_collabs(artist['id'], top_tracks['data']) 

    # Is Following
    is_following = False
    db_artist = Artist.query.filter_by(deezer_id=id).first()

    if db_artist :
        is_following = current_user.is_following(db_artist)

    return render_template('artist.html', user=current_user, is_following=is_following, artist=artist, albums=albums, top_tracks=[top_tracks['data'][i:i+5] for i in range(0, 15, 5)], collabs=collabs)
    # except:
    #     return 'ERROR'

@views.route("/album/<id>")
def album(id):
    try :
        url = f"https://api.deezer.com/album/{id}"
        res = requests.get(url)
        album = res.json()

        artist_url = f"https://api.deezer.com/artist/{album['artist']['id']}"
        res = requests.get(artist_url)
        artist = res.json()

        others_url = f"https://api.deezer.com/artist/{artist['id']}/albums"
        res = requests.get(others_url)
        other_albums = res.json()
        other_albums = other_albums['data']

        # Is Liked
        is_liked = False
        db_album = Album.query.filter_by(deezer_id=id).first()

        if db_album :
            is_liked = current_user.is_album_liked(db_album)
            
        return render_template('album.html', user=current_user, album=album, is_liked=is_liked, more_albums=other_albums)
    except:
        return 'ERROR'

@login_required
@views.route("/track/<id>")
def track(id):
    url = f"https://api.deezer.com/track/{id}"
    res = requests.get(url)
    result = res.json()

    # 
    song_check = Song.query.filter_by(deezer_id=id).first()
    if song_check:
        current_user.recents.append(song_check)    
    else:
        new_song = Song(
            deezer_id=result['id'],
            title=result['title'],
            cover_xl=result['album']['cover_xl'],

            artist_id=result['artist']['id'],
            artist_name=result['artist']['name'],

            album_id=result['album']['id'],
            album_name=result['album']['title'],
        )
        db.session.add(new_song)
        current_user.recents.append(new_song) 

    db.session.commit()

    # for i in range(len(recents)):
    #     if (recents[i]['album'] == result['album']) :
    #         r = recents.pop(i)  # Removes track and returns it
    #         recents.insert(0, r)  # Inserts track at index 0
    #         return jsonify(result)    
    #       
    # recents.insert(0, result)
    
    return jsonify(result)

@login_required
@views.route("/track_info/<id>")
def track_info(id):
    url = f"https://api.deezer.com/track/{id}"
    res = requests.get(url)
    result = res.json()

    song_check = Song.query.filter_by(deezer_id=id).first()

    if song_check:
        pass 

    return jsonify({
        "status": "success",
        "track": result
    })


def find_collabs(id, tracks):
    collabs = []

    for track in tracks:
        if (len(track['contributors']) > 1):
            for artist in track['contributors']:
                if (artist['id'] != id):
                    collabs.append(artist)

    collabs = list({item["id"]: item for item in collabs}.values())

    return collabs

