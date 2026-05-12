import requests
import json
import os
from dotenv import load_dotenv

#API_KEY = "AIzaSyD4ZP6t_L95XFh-R6zTWt0CJkyo68nVwYY"
load_dotenv(dotenv_path="./.env")
API_KEY = os.getenv("API_KEY")
CHANNEL_HANDLE ="MrBeast"
maxResults = 50

def get_playlist_id(): #Get the Playlist ID (Channels)

    try:
        url = f"https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={CHANNEL_HANDLE}&key={API_KEY}"

        response = requests.get(url)
        response.raise_for_status()
        #print(response)

        data = response.json()

        #print(json.dumps(data, indent=4))

        # uploads variable is the ID of the playlist
        channel_itmes = data["items"][0] # Gotten using Json Crack Extension

        channel_playlistID = channel_itmes["contentDetails"]["relatedPlaylists"]["uploads"] 

        print(channel_playlistID)

        return channel_playlistID

    except requests.exceptions.RequestException as e:
        raise e

# For second function get Video ID (Playlistitems)
def get_video_ids(playlistId):
    video_ids = []
    pageToken = None
    base_url = f"https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults={maxResults}&playlistId={playlistId}&key={API_KEY}"

    try:
        while True:
            url = base_url
            if pageToken:
                url += f"&pageToken={pageToken}"
            response = requests.get(url)
            response.raise_for_status()
            #print(response)
            data = response.json()

            for item in data.get('items', []):
                video_id = item['contentDetails']['videoId']
                video_ids.append(video_id)

            pageToken = data.get('nextPageToken')

            if not pageToken:
                break

        return video_ids
    except requests.exceptions.RequestException as e:
        raise

if __name__ == "__main__": #__name__ inbuilt python var that is set depending on how the script is run. __main__ is when the script is run directly and no importes as module. If the script is run from another script __name__ is not equal to __main_. __name__ will be set to the script name
    #print("get_playlist_id will be executed")
    playlistId = get_playlist_id()
    get_video_ids(playlistId)
    #print(get_video_ids(playlistId))
else:
    print("get_playlist_id won't be executed")