from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash
from .functions import search_yt, download_mp3, download_mp3_blank
import requests

views = Blueprint('views', __name__)

@views.route("/")
def home():
    return render_template("index.html")

@views.route("/about")
def about():
    return render_template("about.html")

@views.route("/faq")
def faq():
    return render_template("faq.html")

@views.route("/donate")
def donate():
    return render_template("donate.html")

@views.route("/search")
def search():
    try:
        if 'q' in request.args:
            query = request.args.get('q')

            if len(query.strip()) < 1:
                return redirect(url_for('views.home'))
            else:
                videos = search_yt(query, 10)
                return render_template("search.html", query=query, videos=videos)
        else:
            return redirect(url_for('views.home'))
    except Exception as e:
        return render_template("error_search.html", query=query, error=e)
        
@views.route("/contact", methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get("name")
        email = request.form.get("email")
        msg = request.form.get("msg")

        flash(f"Thank you for your feedback, a response will typically take 2-4 business days.", category="submited")

    return render_template("contact.html")

@views.route("/copyright")
def copyright_page():
    return render_template("copyright.html")

@views.route("/privacy-policy")
def privacy_policy():
    return render_template("privacy-policy.html")

@views.route("/terms-of-use")
def terms_of_use():
    return render_template("terms-of-use.html")

@views.route("/tags/<query>")
def search_tags(query):
    url = f"https://api.deezer.com/search/track?q={query}"
    res = requests.get(url)
    tracks = res.json()
    tracks = tracks['data']

    return jsonify(tracks)

@views.route("/download/", methods=['POST'])
def download():
    id = request.json.get("id")
    deezer_id = request.json.get("deezer_id")
    title = request.json.get("title")
    artist = request.json.get("artist")
    album = request.json.get("album")
    album_id = request.json.get("album_id")
    cover = request.json.get("cover")

    album_url = f"https://api.deezer.com/album/{album_id}"
    res = requests.get(album_url)
    album_json = res.json()

    year = album_json['release_date'].split("-")[0]
    track_number = get_track_number(deezer_id, album_json['tracks']['data'])
    genre = album_json['genres']['data'][0]['name']

    response = download_mp3(id, title, artist, album, cover, year, genre, track_number)

    if response['ok']:
        return jsonify({
            "ok" : True,
            "url" : f"{response['file_path']}"
        })
    else :
        return jsonify({
            "ok" : False,
            "msg" : response['error']
        })

@views.route("/download-blank/", methods=['POST'])
def download_blank():
    id = request.json.get("id")
    file_path = download_mp3_blank(id)

    return jsonify({
        "status" : "success",
        "url" : f"{file_path}"
    })

def get_track_number(id, tracks):
    number = 0

    for i in range(len(tracks)):
        if id == tracks[i]['id']:
            number = i+1

    return str(number)

