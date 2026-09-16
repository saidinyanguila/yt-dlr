from .. import db
from flask_login import UserMixin

user_artist = db.Table(
    "user_artist",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
    db.Column("artist_id", db.Integer, db.ForeignKey("artist.id"), primary_key=True)
)

user_album = db.Table(
    "user_album",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
    db.Column("album_id", db.Integer, db.ForeignKey("album.id"), primary_key=True)
)

user_song = db.Table(
    "user_song",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
    db.Column("song_id", db.Integer, db.ForeignKey("song.id"), primary_key=True)
)

user_recents = db.Table(
    "user_recents",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
    db.Column("song_id", db.Integer, db.ForeignKey("song.id"), primary_key=True)
)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    f_name = db.Column(db.String(32), nullable=False)
    l_name = db.Column(db.String(32))
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(32), nullable=False)
    user_img_path = db.Column(db.String(255), nullable=False, default="/static/img/default_user.png")

    artists = db.relationship("Artist", secondary=user_artist, back_populates="followers")
    albums = db.relationship("Album", secondary=user_album, back_populates="fans")
    liked_songs = db.relationship("Song", secondary=user_song, back_populates="fans")

    recents = db.relationship("Song", secondary=user_recents)

    def follow_artist (self, artist):
        if artist not in self.artists:
            self.artists.append(artist)
            return True
        else:
            self.artists.remove(artist)
            return False

    def is_following(self, artist):
        return artist in self.artists

    def like_album (self, album):
        if album not in self.albums:
            self.albums.append(album)
            return True
        else:
            self.albums.remove(album)
            return False

    def is_album_liked(self, album):
        return album in self.albums

    def like_song (self, song):
        if song not in self.liked_songs:
            self.liked_songs.append(song)
            return True
        else:
            self.liked_songs.remove(song)
            return False

    def is_song_liked(self, song):
        return song in self.liked_songs


class Artist(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    deezer_id = db.Column(db.Integer)
    name  = db.Column(db.String(32), nullable=False)
    picture_xl = db.Column(db.String(256), nullable=False)

    followers = db.relationship("User", secondary=user_artist, back_populates="artists")

class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    deezer_id = db.Column(db.Integer)
    title = db.Column(db.String(64), nullable=False)
    cover_xl = db.Column(db.String(256), nullable=False)

    artist_id = db.Column(db.Integer)
    artist_name = db.Column(db.String(64), nullable=False)

    fans = db.relationship("User", secondary=user_album, back_populates="albums")

class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    deezer_id = db.Column(db.Integer)
    title = db.Column(db.String(64), nullable=False)
    cover_xl = db.Column(db.String(256), nullable=False)

    artist_id = db.Column(db.Integer)
    artist_name = db.Column(db.String(64), nullable=False)

    album_id = db.Column(db.Integer)
    album_name = db.Column(db.String(64), nullable=False)

    fans = db.relationship("User", secondary=user_song, back_populates="liked_songs")

