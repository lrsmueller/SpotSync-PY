# SpotSync

Sync your last 100 songs you added to your libary in Spotify to a playlist 

Use case: Download your newest songs not in special playlists so you dont need to download your complete libary

## Setup

### Requirements

- Python3
- spotipy
- [Spotify Web API Application](https://developers.spotify.com/)
  - client secret
  - client id
  - redirect uri: http://127.0.0.1:9090 change port to your likings
- Virtual Enviroment

### Enviroment Variables
add these enviroment variables to your venv/system
```
export SPOTIPY_CLIENT_ID='your_id'
export SPOTIPY_CLIENT_SECRET='your_secret'
export SPOTIPY_REDIRECT_URI='http://127.0.0.1:9090'
```

### Install
install from main branch
``` 
python3 -m pip install https://github.com/freeek3/SpotSync/archive/main.zip
```
### Run
```
spotsync
```
will run you through the login process and lets you choose your playlist.
It also instantly "syncs" your songs to the playlist, by deleting all songs in it.
calling it again will sync the playlist again without the dialog

**Important: it shows every playlist added to your account, also non editable ones**

Now you could setup a cronjob which runs periodically (1 a day) to add your new songs

## Usage
```
spotsync --help
usage: spotsync [-h] [-p] [-m MAX] [-f FILE]

Syncs newly added tracks to a selected playlist

optional arguments:
-h, --help            show this help message and exit
-p, --playlist        change playlist to sync
-m MAX, --max MAX     maximum of songs in the playlist (default: 100)
-f FILE, --file FILE  change playlistfile 
```

## Ideas
- [ ] better sync, not only deleting
- [ ] other savelocation
- [ ] docker setup, but why