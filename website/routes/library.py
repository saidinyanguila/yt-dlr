from flask import Blueprint, render_template, request, url_for, jsonify
from flask_login import login_required, current_user
from ..models.models import Artist, Album, Song
import requests
from .. import db

library = Blueprint('library', __name__)

@library.route("/")
@login_required
def library_home():
    sections = [
        {
            "name" : "Artists",
            "url" : url_for('library.library_artists'),
            "icon" : "mic-vocal"
        },
        {
            "name" : "Albums",
            "url" : url_for('library.library_albums'),
            "icon" : "disc-3"
        },
        {
            "name" : "Liked Songs",
            "url" : url_for('library.library_liked'),
            "icon" : "music-2"
        },
    ]
    playlists = []

    return render_template("library.html", user=current_user, sections=sections, playlists=playlists, total_playlists=len(playlists))

@login_required
@library.route("/artists")
def library_artists():
    artists = current_user.artists
    artists = group_by_first_letter_name(artists)

    return render_template("library_artists.html", user=current_user, artist_groups=artists)

@login_required
@library.route("/albums")
def library_albums():
    albums = current_user.albums
    albums.sort(key=lambda item: item.title.lower())

    return render_template("library_albums.html", user=current_user, albums=albums, total=len(albums))

@login_required
@library.route("/liked")
def library_liked():
    liked_songs = current_user.liked_songs
    sort = "latest"

    if 'sort' in request.args:
        sort = request.args.get('sort')

        if sort == "title":
            liked_songs.sort(key=lambda item: item.title.lower())
        elif sort == "artist":
            liked_songs.sort(key=lambda item: item.artist_name.lower())
        elif sort == "album":
            liked_songs.sort(key=lambda item: item.album_name.lower())
        else :
            liked_songs.reverse()
    else :
        liked_songs.reverse()

    return render_template("library_liked_Songs.html", user=current_user, liked_songs=liked_songs, sort=sort)

###
@library.route("/follow_artist", methods=['POST'])
def follow_artist():
    artist_id = request.json.get("id")

    artist_check = Artist.query.filter_by(deezer_id=artist_id).first()
    followed = False

    if artist_check:
        followed = current_user.follow_artist(artist_check)    
    else:
        url = f"https://api.deezer.com/artist/{artist_id}"
        res = requests.get(url)
        artist = res.json()
        
        new_artist = Artist(
            deezer_id=artist['id'],
            name=artist['name'],
            picture_xl=artist['picture_xl']
        )
        db.session.add(new_artist)
        followed = current_user.follow_artist(new_artist)

    db.session.commit()
    
    return jsonify({
        "id" : artist_id,
        "code" : 1,
        "followed" : followed
    })

@library.route("/like_album", methods=['POST'])
def like_album():
    album_id = request.json.get("id")

    album_check = Album.query.filter_by(deezer_id=album_id).first()
    liked = False

    if album_check:
        liked = current_user.like_album(album_check)    
    else:
        url = f"https://api.deezer.com/album/{album_id}"
        res = requests.get(url)
        album = res.json()
        
        new_album = Album(
            deezer_id=album['id'],
            title=album['title'],
            cover_xl=album['cover_xl'],
            artist_id=album['artist']['id'],
            artist_name=album['artist']['name'],
        )
        db.session.add(new_album)
        liked = current_user.like_album(new_album)

    db.session.commit()
    
    return jsonify({
        "code" : 1,
        "liked" : liked
    })

@library.route("/like_song", methods=['POST'])
def like_song():
    song_id = request.json.get("id")
    
    song_check = Song.query.filter_by(deezer_id=song_id).first()
    liked = False

    if song_check:
        liked = current_user.like_song(song_check)   
          
        artist_check = Artist.query.filter_by(deezer_id=song_check.artist_id).first() 
    else:
        url = f"https://api.deezer.com/track/{song_id}"
        res = requests.get(url)
        song = res.json()

        # Artists Check
        artist_check = Artist.query.filter_by(deezer_id=song['artist']['id']).first()

        if not artist_check :
            new_artist = Artist(
                deezer_id=song['artist']['id'],
                name=song['artist']['name'],
                picture_xl=song['artist']['picture_xl']
            )
            db.session.add(new_artist)
            artist_check = new_artist
  
        new_song = Song(
            deezer_id=song['id'],
            title=song['title'],
            cover_xl=song['album']['cover_xl'],

            artist_id=song['artist']['id'],
            artist_name=song['artist']['name'],

            album_id=song['album']['id'],
            album_name=song['album']['title'],
        )
        db.session.add(new_song)
        liked = current_user.like_song(new_song)

    db.session.commit()
    
    return jsonify({
        "code" : 1,
        "liked" : liked
    })


def group_by_first_letter_name(arr):
    # Sort by name
    arr.sort(key=lambda item: item.name.lower())

    groups = []
    current_letter = None

    for item in arr:
        letter = item.name[0].upper()

        # Create a new group when the letter changes
        if letter != current_letter:
            groups.append({
                "letter": letter,
                "items": []
            })
            current_letter = letter

        # Add the entire object
        groups[-1]['items'].append(item)

    return groups

