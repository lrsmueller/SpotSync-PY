# SpotSync

Sync the last 100 songs you added to your library in Spotify to a playlist. 

Use Case: Download only your newest liked songs onto your smartphone rather than 2000+ if you have an extensive library like me.

Motivation: I mostly hear my newest liked songs and wanted to download only some of my library.
The Flask App was just thought of as practice and to learn some new technologies.

## Setup
### Prerequisites
- [Spotify Web API Application](https://developers.spotify.com/) with 
  - client secret
  - client id
  - redirect URIs to your localhost (`http://127.0.0.1:8000/callback`) or
  
  an IP/domain like `spotsync.example.org/callback`
  
  **Important is the** `/callback` **path**
  
### Enviroment variables
Configuration of the app happens through environment variables. 
create a `.env` file or insert them into your `docker-compose.yaml`
```
SPOTIPY_CLIENT_ID='your_client_id'
SPOTIPY_CLIENT_SECRET='your_client_secret'
SPOTIPY_REDIRECT_URI='http://127.0.0.1:8000'
DATABASE_URI=sqlite:////app/project.db  # can be any sqlalchemy database URI
```

### Run 
##### docker run
```docker run --name spotsync ghcr.io/larsjmueller/SpotSync
--expose 8000:8000 I am running a few minutes late; my previous meeting is running over.

-e SPOTIPY_CLIENT_ID='your_client_id' \
-e SPOTIPY_CLIENT_SECRET='your_client_secret' \
-e SPOTIPY_REDIRECT_URI='http://127.0.0.1:8000' \
-e DATABASE_URI=sqlite:////app/project.db \
-v ./project.db:/app/project.db
``` 
##### docker-compose
see compose.yaml for example

#### without docker
- clone this repository and enter the directory
- create a virtual environment with python3 (tested 3.9 and 3.10)
- install requirements.txt
- set environment variables with the additional `export FLASK_APP=app`
- `flask run --host 0.0.0.0 --port 8000`
- alternative run your preferred wsgi server

#### reverse-proxy
you can run this app behind a reverse proxy with an ssl certificate 

## Usage
You can go to your host in your browser and press Login.
After you log in to Spotify and accept the app connection.
Now you need to edit your playlist.
**Important: it shows every playlist added to your account, also non-editable ones**
After that, you are finished, and your playlist will be refreshed (everything deleted, and 100 newest songs added) daily.
You can trigger a refresh by clicking on the Refresh button.

## Ideas
- [ ] better sync, not only deleting
- [x] other save location
- [x] docker setup
- [ ] command line app 
- [ ] Multi-Page Playlists (more than 50)
- [ ] Enable custom number of songs, maximum 100
- [ ] Customize daily refresh (timezone, or direct over apscheduler)
- [ ] Nicer UI, show current Playlist, show 100 songs

## Development Todos
- [ ] dev compose and production compose
- [ ] tests, docker testing build integration in github 
- [ ] comments, function strings
- [ ] make the auth part its own function
- [ ] specific logging and error throws
- [ ] check playlist writeable/exists
- [ ] smaller docker image (https://cr0hn.medium.com/python-docker-images-in-less-than-50mb-8acc6ed776ec)
- [ ] docstrings
- [ ] automatic new builds with newer packages
