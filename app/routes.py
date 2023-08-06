from flask import Flask, session, request, redirect, render_template, Blueprint, current_app
from flask_session import Session

import spotipy

from app.config import Config
from app.db import db, User
from app.worker import refresh_playlist

bp = Blueprint('main', __name__)
@bp.route('/')
def index():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope=Config.SCOPE, cache_handler=cache_handler)

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
        current_app.logger.debug("UPDATE:" + str(current_user))
        db.session.commit()
    else: # User existiert nicht
        current_app.logger.debug(spotify.current_user())
        current_user = User(
            username = spotify.current_user()["id"],
            timezone = "UTC",
            playlist = "Last100",
            token = session["token_info"]
        )
        current_app.logger.debug("NEW: " + str(current_user))

        db.session.add(current_user)
        db.session.commit()
    current_app.logger.debug("AUTH: " + str(auth_manager))
    
    # TODO template
    return f'<h2>Hi {spotify.me()["display_name"]}, ' \
           f'<small><a href="/sign_out">[sign out]<a/></small></h2>' \
           f'<a href="/playlist">change playlist</a> | ' \
           f'<a href="/refresh">Refresh your playlist</a> | ' \
           f'<a href="/refresh_time">Config your daily Refresh Time</a> | ' \

@bp.route("/callback")
def spotify_callback():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope=Config.SCOPE,
                                               cache_handler=cache_handler,
                                               show_dialog=True)
    if request.args.get("code"):
        auth_manager.get_access_token(request.args.get("code"))
        spotify = spotipy.Spotify(auth_manager=auth_manager)
    return redirect('/')

@bp.route('/sign_out')
def sign_out():
    session.pop("token_info", None)
    return redirect('/')

@bp.route('/playlist')
def playlists():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope=Config.SCOPE, cache_handler=cache_handler)
    
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')

    spotify = spotipy.Spotify(auth_manager=auth_manager)
    playlists = spotify.current_user_playlists()
    render_playlist = []
    for playlist in playlists["items"]:
        current_app.logger.debug(playlist["name"])
        render_playlist.append({
                "id": playlist["id"],
                "name": playlist["name"]})
    return render_template('playlists.html', playlists=render_playlist)

@bp.route('/playlist/<string:playlist_id>')
def set_playlist(playlist_id):
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope=Config.SCOPE, cache_handler=cache_handler)
    
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    
    #TODO check if playlist exsits and if its editable
    
    current_user = db.session.query(User).filter_by(username=spotify.current_user()["id"]).first() 
    if current_user is not None: # User existiert
        current_user.playlist = playlist_id
        db.session.commit()
    
    # TODO template
    return "Set Playlist ID: " + playlist_id + "<br> <a href=\"/\">Return</a>"

@bp.route('/refresh')
def refresh():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope=Config.SCOPE, cache_handler=cache_handler)
    
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    
    user = db.session.query(User).filter(User.username == spotify.current_user()["id"]).first()
    refresh_playlist(user, spotify=spotify)
    
    return redirect('/')

@bp.route('/refresh_time')
def currently_playing():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope=Config.SCOPE, cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    timezone = "UTC"
    
    # TODO template
    return "Set Timezone to: " + timezone + "<br> <a href=\"/\">Return</a>" 

# CATCH-ALL and redirect to main
@bp.route('/', defaults={'path': ''})
@bp.route('/<path:path>')
def catch_all(path):
    return redirect('/')
