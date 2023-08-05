import os

from flask import Flask, session, request, redirect, render_template
from flask_session import Session

from apscheduler.schedulers.background import BackgroundScheduler
import spotipy

from db import db, User
from worker import refresh_playlist, refresh_all_playlists

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///' + os.path.join(basedir, 'project.db')
app.config['SECRET_KEY'] = os.urandom(64)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'

scope = "user-library-read playlist-read-private playlist-modify-private playlist-modify-public"
#TODO config.py file
#TODO create_app 
#TODO dev compose and production compose
#TODO run it in a venv
#TODO tests 
#TODO comments
#TODO scope in config
#TODO extra auth/spotify function

#TODO multi page playlists
#TODO individual song number up till 100
#TODO timezone specific refreshs, grab timezone from browser

db.init_app(app)
Session(app)

sched = BackgroundScheduler(daemon=True)
sched.add_job(refresh_all_playlists,trigger='cron', hour='2', minute='30')

@app.route('/')
def index():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope=scope, cache_handler=cache_handler)


    # not signed in
    # TODO turn into own function thogether with auth_manager und cache_handler
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        auth_url = auth_manager.get_authorize_url()
        return f'<h2><a href="{auth_url}">Sign in</a></h2>'

    # Signed in 
    spotify = spotipy.Spotify(auth_manager=auth_manager)

    # User in database, refresh token or create new
    current_user = db.session.query(User).filter_by(username=spotify.current_user()["id"]).first() 
    if current_user is not None: # User existiert
        current_user.token = session["token_info"]
        app.logger.info("UPDATE:" + str(current_user))
        db.session.commit()
    else: # User existiert nicht
        current_user = User(
            username = spotify.current_user()["id"],
            timezone = "UTC",
            playlist = "Last100",
            token = session["token_info"]
        )
        app.logger.info("NEW: " + str(current_user))

        db.session.add(current_user)
        db.session.commit()
    app.logger.info("AUTH: " + str(auth_manager))
    return f'<h2>Hi {spotify.me()["display_name"]}, ' \
           f'<small><a href="/sign_out">[sign out]<a/></small></h2>' \
           f'<a href="/playlist">change playlist</a> | ' \
           f'<a href="/refresh">Refresh your playlist</a> | ' \
           f'<a href="/timezone">set your timezone/refresh time</a> | ' \

@app.route("/callback")
def spotify_callback():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope=scope,
                                               cache_handler=cache_handler,
                                               show_dialog=True)
    if request.args.get("code"):
        auth_manager.get_access_token(request.args.get("code"))
        spotify = spotipy.Spotify(auth_manager=auth_manager)
    return redirect('/')

@app.route('/sign_out')
def sign_out():
    session.pop("token_info", None)
    return redirect('/')

@app.route('/playlist')
def playlists():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope=scope, cache_handler=cache_handler)
    
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')

    spotify = spotipy.Spotify(auth_manager=auth_manager)
    playlists = spotify.current_user_playlists()
    render_playlist = []
    for playlist in playlists["items"]:
        app.logger.info(playlist["name"])
        render_playlist.append({
                "id": playlist["id"],
                "name": playlist["name"]})
    return render_template('playlists.html', playlists=render_playlist)

@app.route('/playlist/<string:playlist_id>')
def set_playlist(playlist_id):
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope=scope, cache_handler=cache_handler)
    
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    
    #TODO check if playlist exsits and if its editable
    
    current_user = db.session.query(User).filter_by(username=spotify.current_user()["id"]).first() 
    if current_user is not None: # User existiert
        current_user.playlist = playlist_id
        db.session.commit()
    
    return "Set Playlist ID: " + playlist_id + "<br> <a href=\"/\">Return</a>"

@app.route('/refresh')
def refresh():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope=scope, cache_handler=cache_handler)
    
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    
    user = db.session.query(User).filter(User.username == spotify.current_user()["id"]).first()
    refresh_playlist(user, spotify=spotify)
    
    return redirect('/')

@app.route('/timezone')
def currently_playing():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope=scope, cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    timezone = "UTC"
    return "Set Timezone to: " + timezone + "<br> <a href=\"/\">Return</a>" 

    #TODO implemented at a later date current refresh time is UTC: 2

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return redirect('/')

sched.start()
if __name__ == '__main__':
    app.run(threaded=True, host='0.0.0.0', port=80, debug=True)
