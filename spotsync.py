import math
import pickle
import pathlib
import argparse
import logging

import spotipy
from spotipy.oauth2 import SpotifyOAuth

logger = logging.getLogger('freek3.SpotSync')
logging.basicConfig(level='INFO')

playlist = None

# Spotify setup
scope = "user-library-read playlist-read-private playlist-modify-private playlist-modify-public"

def get_args():
    """Sets Arguments 

    Returns:
        Namespace: Arguments and their values
    """
    parser = argparse.ArgumentParser(prog='spotsync',description='Syncs newly added tracks to a selected playlist')
    parser.add_argument('-p', '--playlist', required=False, action='store_true',
                        help='change playlist to sync')
    parser.add_argument('-m', '--max',required=False, type=int,
                        help='maximum of songs in the playlist (default: 100)')
    parser.add_argument('-f','--file', required=False, type=str,
                        help='change playlistfile')
    return parser.parse_args()

def set_playlist(sp, playlist_file = '.playlist', limit=50):
    """Set your playlist to sync and save it in the given file.
    Select from all playlists in your account also nonwritable.

    Args:
        sp (spotipy.Spotify): spotipy instance used
        playlist_file (str, optional): file for the pickle playlist document. Defaults to '.playlist'.
        limit (int, optional): playlists obtained from one request. Defaults to 50. Maximum is 50.
    """
    if limit>50: limit=50 
    
    global playlist
    playlists = sp.current_user_playlists(limit=limit)
    print("Playlists found:",playlists['total'])
    
    # Obtain all playlists if more than limit/50
    if limit<playlists['total']:
        for x in range(1,math.ceil(playlists['total'] / limit)):
            pl = sp.current_user_playlists(limit=limit,offset=limit*x)
            for p in pl['items']:
                playlists['items'].append(p)

    # print Playlists
    for idx, p in enumerate(playlists['items']):
        print(idx,":",p["name"],"-",p["id"])

    # Select a Playlist 
    idp = int(input("Enter number of playlist: "))
    playlist = playlists["items"][idp]

    # Save Playlist to file
    with open(playlist_file, "wb") as f:
        pickle.dump(playlist,f)

def get_playlist(sp, playlist_file = '.playlist'):
    """Obtain your playlist from file, call set_playlist if empty/not exsistend

    Args:
        sp (spotipy.Spotify): spotipy instance used
        playlist_file (str, optional): file for the pickle playlist document. Defaults to '.playlist'.
    """    ""
    global playlist
    
    # check if file exsits
    if pathlib.Path(playlist_file).is_file():
        with open(playlist_file, "rb") as f:
            playlist = pickle.load(f)
    else: # file doesnt exsist
        set_playlist(sp, playlist_file)
    if playlist is None: # file exsists but no playlist set
        set_playlist(sp, playlist_file)
    print("playlist set to:", playlist["name"], "-",playlist["id"])

def get_newest_tracks(sp, max=100,limit=20):
    """Obtain your newly, to your libary, added tracks 

    Args:
        sp (spotipy.Spotify): spotipy instance used
        max (int, optional): Maximum of Tracks obtained and later synced. Defaults to 100. Maximum 100
        limit (int, optional): Tracks per request. Defaults to 20. Maximum 20

    Returns:
        _type_: list of track ids
    """
    if max>100: max=100 # playlists dont allow more than 100 adds/removes at once
    if limit>20: max=20 # maximum of tracks obtainable at once
    
    # get 100 tracks with rate limits in mind
    tracks = []
    for x in range(0,math.ceil(max/limit)):
        r = sp.current_user_saved_tracks(limit=20,offset=limit*x)['items']
        for t in r:
            tracks.append(t["track"]["id"])
    return tracks

def remove_tracks(sp):
    """Remove all tracks from the selected playlist

    Args:
        sp (spotipy.Spotify): spotipy instance used
    """
    global playlist
    # get tracks + owner id from spotify
    r=sp.playlist(playlist['id'],'owner.id,tracks.items')
    # generate list with track ids only
    remove_tracks = []
    for p_track in r['tracks']['items']:
        remove_tracks.append(p_track['track']['id'])
    # remove track ids
    sp.user_playlist_remove_all_occurrences_of_tracks(r['owner']['id'],playlist['id'],remove_tracks)


def spotsync():
    """Main Method calling all other methods

    """
    args = get_args()
    # set playlist file/save
    playlist_file = '.playlist' if args.file is None else args.file #TODO more testing ?
    
    # get Spotify instance
    spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

    if args.playlist:
        set_playlist(spotify,playlist_file)
    
    get_playlist(spotify,playlist_file)
    
    remove_tracks(spotify)
    
    # add tracks to playlist
    if args.max is not None: 
        spotify.playlist_add_items(playlist['id'],get_newest_tracks(spotify,max=args.max,limit=20))
    else:
        spotify.playlist_add_items(playlist['id'],get_newest_tracks(spotify))

if __name__ == '__main__':
    spotsync()