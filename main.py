import config
import spotipy
import spotipy.util as util

USERNAME = config.USERNAME
CLIENT_ID = config.CLIENT_ID
CLIENT_SECRET = config.CLIENT_SECRET

PLAYLIST_NAME = 'Discover When You Feel Like It'

scope = 'playlist-modify-public playlist-modify-private playlist-read-private playlist-read-collaborative'
token = util.prompt_for_user_token(USERNAME, scope, CLIENT_ID, CLIENT_SECRET, redirect_uri='http://localhost:8888/callback')

spotify = spotipy.Spotify(auth=token)

user_playlists = spotify.user_playlists(USERNAME)
user_playlists_list = [user_playlists['items'][i]['name'] for i in range(len(user_playlists['items']))]

if PLAYLIST_NAME not in user_playlists_list:
    new_playlist = spotify.user_playlist_create(user=USERNAME, name=PLAYLIST_NAME, public=False,
                                                 description="Saved tracks from Discover Weekly and Release Radar")
    user_playlists_list.insert(0,PLAYLIST_NAME)
    user_playlists = spotify.user_playlists(USERNAME)

if PLAYLIST_NAME in user_playlists_list:

    search_dw = spotify.search(q="Discover Weekly", type="playlist")
    search_rr = spotify.search(q="Release Radar", type="playlist")

    dw_playlist_id = search_dw['playlists']['items'][0]['id']
    rr_playlist_id = search_rr['playlists']['items'][0]['id']

    playlist_dw = spotify.user_playlist(USERNAME, dw_playlist_id)
    playlist_rr = spotify.user_playlist(USERNAME, rr_playlist_id)

    dw_song_uri = [playlist_dw["tracks"]["items"][i]['track']['uri'] for i in range(len(playlist_dw["tracks"]["items"]))]
    rr_song_uri = [playlist_rr["tracks"]["items"][i]['track']['uri'] for i in range(len(playlist_dw["tracks"]["items"]))]

    playlist_index = user_playlists_list.index(PLAYLIST_NAME)
    playlist_id = user_playlists['items'][playlist_index]['id']

    playlist = spotify.user_playlist(USERNAME, playlist_id)

    tracks = playlist['tracks']

    # api returns pages of 100 items so 'next' is used to go to the next page of items and get the uris of all songs in the current playlist
    playlist_song_uris = [tracks["items"][i]['track']['uri'] for i in range(len(tracks["items"]))]

    while tracks['next']:
        tracks = spotify.next(tracks)
        playlist_song_uris.extend([tracks["items"][i]['track']['uri'] for i in range(len(tracks["items"]))])

    for i in range(len(dw_song_uri)):
        if dw_song_uri[i] in playlist_song_uris:
            continue
        else:
            spotify.playlist_add_items(playlist_id=playlist_id, items=[dw_song_uri[i]])

    for i in range(len(rr_song_uri)):
        if rr_song_uri[i] in playlist_song_uris:
            continue
        else:
            spotify.playlist_add_items(playlist_id=playlist_id, items=[rr_song_uri[i]])
