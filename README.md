# SpotSync

Sync the last 100 songs you added to your library in Spotify to a playlist. 

Use Case: Download only your newest liked songs onto your smartphone rather than 2000+ if you have an extensive library like me.

Motivation: I mostly hear my newest liked songs and wanted to download only some of my library.
The Flask App was just thought of as practice and to learn some new technologies.

## Setup
### Prerequisites
- Setup an [Spotify Web API Application](https://developers.spotify.com/) with 
  - client secret
  - client id
  - redirect URIs to your localhost (`http://127.0.0.1:8000/callback`) or an IP/domain like `spotsync.example.org/callback`
  
  **Important is the** `/callback` **path in the redirect URI**
  
  See [Spotify Redirect URI](#spotify-redirect-uri) for more information

- Set the 3 Enviroment Variabels with to the corresponding Settings in your app.
  ```
  SPOTIPY_CLIENT_ID='your_client_id'
  SPOTIPY_CLIENT_SECRET='your_client_secret'
  SPOTIPY_REDIRECT_URI='http://127.0.0.1:8000/callback'
  ```

### Run

#### Docker

```bash
docker run --name spotsync ghcr.io/larsjmueller/SpotSync
--expose 8000:8000 
-e SPOTIPY_CLIENT_ID='your_client_id' \
-e SPOTIPY_CLIENT_SECRET='your_client_secret' \
-e SPOTIPY_REDIRECT_URI='http://127.0.0.1:8000/callback' \
-v ./project.db:/data/project.db
``` 

starts the container and exposes it on port 8000, it is fully functional now if you run it through your local machine.
Datastorage is in a local sqlite database binded as volume into the container.

You can run the container in a `docker-compose` an example can be found at [docker-compose.example.yml](docker-compose.example.yml). This example runs the container behind a reverse proxy with letsencrypt ssl encryption.

#### without docker
- clone this repository and enter the directory
- create a virtual environment with python3 (tested 3.9 and 3.10)
- install requirements `pip install -r requirements.txt`
- set environment variables:
  - `FLASK_APP=app`
  - `SPOTIPY_CLIENT_ID='your_client_id`
  - `SPOTIPY_CLIENT_SECRET='your_client_secret`
  - `SPOTIPY_REDIRECT_URI='http://127.0.0.1:8000/callback`
  - `DATABASE_URI = sqlite:////path/to/database.db`
- `flask run --host 0.0.0.0 --port 8000`
- alternative recomended: run your preferred wsgi server See [Flask deploying]https://flask.palletsprojects.com/en/2.3.x/deploying/) for more information

#### development
- setup like [without docker](#without-docker)
- additional enviroment variables:
  - FLASK_ENV = development
- run `flask run --port 8000`
- `docker-compose.debug.yml` builds the corresponding docker container and allows debugging. 

### Configuration
Configuration of the app happens through environment variables. 
| Variable | Required | Explaination | 
| -- | -- | -- | 
| SPOTIPY_CLIENT_ID | yes |  your spotify cliend id
| SPOTIPY_CLIENT_SECRET | yes |  your spotify client secret
| SPOTIPY_REDIRECT_URI | yes | [Spotify Redirect URI](#spotify-redirect-uri) |
| DATABASE_URI=sqlite:////data/project.db | no docker | Sqlalchemy Database URI DATABASE_URI= |
| FLASK_APP=app | no docker | FLASK_APP=app |
| FLASK_ENV=production | dev | enables development server and debubbing FLASK_ENV=development |
| SECRET_KEY=random | no | random secret used by flask sessions |
| CRON_HOUR=2 | no | hour at which the refresh happens, default=2 |
| CRON_MINUTE=0 | no | minute in which the refresh happens, default=0 |
| MISSFIRE_GRACE_TIME | no | incase of to much load how long can the task be delayed | 
 
 Other Flask specific variables can be set to your likings.

#### **Spotify redirect URI**
Set your `SPOTIPY_REDIRECT_URI` according to your usercase.
Keep in mind that the `SPOTIPY_REDIRECT_URI` needs to be added to the spotify app on the spotify site.

| Location | SPOTIPY_REDIRECT_URI | Example |
| -- | -- | -- |
| on your local machine | http://127.0.0.1:8000/callback | http://127.0.0.1:8000/callback |
| in your home network on a server | http://ipaddress:8000/callback | http://192.168.0.15:8000/callback |
| on a public server | http://ipaddress:8000/callback | http://1.1.1.1:8000/callback |
| on a public server with dns entry | http://domain:8000/callback | http://example.org:8000/callback |
| on a public server behind a reverse proxy with ssl and subdomain | https://sub.domain/callback | https://spotsync.example.org/callback |

Basically set your callback adress to the same adress you use to access the service and add the `callback` path.



## Usage
You can go to your host in your browser and press Login.
After you log in to Spotify and accept the app connection.
Now you need to edit your playlist.
**Important: it currently shows every playlist added to your account, also non-editable ones**
After that, you are finished, and your playlist will be refreshed (everything deleted, and 100 newest songs added) daily.
You can trigger a refresh by clicking on the Refresh button.

