import math

import spotipy

from sqlalchemy import create_engine
from sqlalchemy.orm import Session as SQLSession

from cacheHandler import DBCacheHandler
from db import User, metadata
from config import config

engine = create_engine(config["SQLALCHEMY_DATABASE_URI"])

scope = "user-library-read playlist-read-private playlist-modify-private playlist-modify-public"
#src:
# https://stackoverflow.com/questions/41004540/using-sqlalchemy-models-in-and-out-of-flask

def refresh_playlist(user, spotify=None):
    
    if (spotify is None):
        cache_handler =  DBCacheHandler(db=engine, user=user)
        auth_manager = spotipy.oauth2.SpotifyOAuth(scope=scope,
                                                cache_handler=cache_handler,
                                                show_dialog=False)
        spotify = spotipy.Spotify(auth_manager=auth_manager)
    
    #TODO Playlist aktualsieren
    
    def get_newest_tracks(max=100,limit=20):
        """Obtain your newly, to your libary, added tracks 

        Args:
            sp (spotipy.Spotify): spotipy instance used
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

        Args:
            sp (spotipy.Spotify): spotipy instance used
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
    print("tracks removed")
    spotify.playlist_add_items(user.playlist,get_newest_tracks(spotify))
    print("tracks added")
    
    return None
    
def refresh_all_playlists():
    session = SQLSession(engine)
    users = session.query(User).all()
    print(users)
    session.close()
    
    for u in users:
        print(u.username)
        refresh_playlist(u)
    
    return None

#refresh_all_playlists() 403 insuffiecent client scope at start ? when imported makes sense as there is no api?