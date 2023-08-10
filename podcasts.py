import json
import requests
import pprint
import time
from secrets_1 import API_KEY_LISTENNOTES,API_KEY_ASSEMBLYAI,SPOTIFY_CLIENT_ID,SPOTIFY_CLIENT_SECRET
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

def get_episode_info(episode_url):
    """Gets information about a Spotify episode from its URL."""
    spotify = spotipy.Spotify(client_credentials_manager=SPOTIFY_CLIENT_ID&SPOTIFY_CLIENT_SECRET)
    episode = spotify.track(episode_url)
    return episode

listennotes_episode_endpoint = 'https://listen-api.listennotes.com/api/v2/episodes/'
headers_listennotese = {
  'X-ListenAPI-Key': API_KEY_LISTENNOTES,
}
transcript_endpoint = 'https://api.assemblyai.com/v2/transcript'

headers_assemblyai = {
    "authorization": API_KEY_ASSEMBLYAI,
    "content-type": "application/json"
}
def transcribe(audio_url, auto_chapters=False):
    transcript_request = {
        'audio_url': audio_url,
        'auto_chapters': 'True' if auto_chapters else 'False'
    }

    transcript_response = requests.post(transcript_endpoint, json=transcript_request, headers=headers_assemblyai)
    pprint.pprint(transcript_response.json())
    return transcript_response.json()['id']


def poll(transcript_id, **kwargs):
    polling_endpoint = transcript_endpoint + '/' + transcript_id
    polling_response = requests.get(polling_endpoint, headers=headers_assemblyai)

    if polling_response.json()['status'] == 'completed':
        filename = transcript_id + '.txt'
        with open(filename, 'w') as f:
            f.write(polling_response.json()['text'])

        filename = transcript_id + '_chapters.json'
        with open(filename, 'w') as f:
            chapters = polling_response.json()['chapters']

            data = {'chapters': chapters}
            for key, value in kwargs.items():
                data[key] = value

            json.dump(data, f, indent=4)

        print('Transcript saved')
        return True
    return False
def get_episode_audio_url(episode_id):
    url = listennotes_episode_endpoint +'/'+ episode_id
    response = requests.request('GET', url, headers=headers_listennotese)
    #pprint.pprint(json.dumps(response.json()))
    data = response.json()
    # pprint.pprint(data)
    episode_title = data['title']
    thumbnail = data['thumbnail']
    podcast_title = data['podcast']['title']
    audio = data['audio']
    return audio, thumbnail,podcast_title,episode_title
def pipeline(episode_id):
    audio_url, thumbnail, podcast_title, episode_title = get_episode_audio_url(episode_id)
    # print(audio_url, thumbnail, podcast_title, episode_title)
    transcribe_id = transcribe(audio_url, auto_chapters=True)
    while True:
        result = poll(transcribe_id, audio_url=audio_url, thumbnail=thumbnail, podcast_title=podcast_title,
                  episode_title=episode_title)
        if result:
            break
        print("waiting for 60 seconds")
        time.sleep(60)
if __name__ == '__main__':
    pipeline("a73b83041a5f408d9d37adc9bef93dc7")

    