import math
import logging

import spotipy

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.cacheHandler import DBCacheHandler
from app.db import User, metadata
from app.config import Config

#src:
# https://stackoverflow.com/questions/41004540/using-sqlalchemy-models-in-and-out-of-flask

#TODO worker.py more abstract to use in CLI app
logger = logging.getLogger("app.worker")
logger.info("logging started")

def refresh_playlist(user, spotify=None):
    
    if (spotify is None):
        cache_handler =  DBCacheHandler(db=create_engine(Config.SQLALCHEMY_DATABASE_URI), user=user)
        auth_manager = spotipy.oauth2.SpotifyOAuth(scope=Config.SCOPE,
                                                cache_handler=cache_handler,
                                                show_dialog=False)
        spotify = spotipy.Spotify(auth_manager=auth_manager)

    
    def get_newest_tracks(max=100,limit=20):
        """Obtain your newly, to your libary, added tracks 

        Args:
            max (int, optional): Maximum of Tracks obtained and later synced. Defaults to 100. Maximum 100
            limit (int, optional): Tracks per request. Defaults to 20. Maximum 20

        Returns:
            _type_: list of track ids
        """
        #if max>100: max=100 # playlists dont allow more than 100 adds/removes at once
        #if limit>20: max=20 # maximum of tracks obtainable at once
        
        # get 100 tracks with rate limits in mind
        tracks = []
        for x in range(0,math.ceil(100/limit)):
            r = spotify.current_user_saved_tracks(limit=20,offset=limit*x)['items']
            for t in r:
                tracks.append(t["track"]["id"])
        return tracks

    def remove_tracks():
        """Remove all tracks from the selected playlist
        """
        # get tracks + owner id from spotify
        r=spotify.playlist(user.playlist,'owner.id,tracks.items')
        # generate list with track ids only
        remove_tracks = []
        for p_track in r['tracks']['items']:
            remove_tracks.append(p_track['track']['id'])
        # remove track ids
        spotify.user_playlist_remove_all_occurrences_of_tracks(r['owner']['id'],user.playlist,remove_tracks)

    remove_tracks()
    spotify.playlist_add_items(user.playlist,get_newest_tracks(spotify))
    
    logger.info("refreshed Playlist")
    return None
    
def refresh_all_playlists():
    session = Session(create_engine(Config.SQLALCHEMY_DATABASE_URI))
    users = session.query(User).all()
    session.close()
    
    for u in users:
        refresh_playlist(u)
    
    logger.info("all Playlists refreshed")
    return None
