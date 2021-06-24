# API dependencies
from ytmusicapi import YTMusic
import requests
import json
import os

# Time dependencies
from datetime import date
import time

# Audio dependencies
import pyaudio
import wave

def get_audio(record_time, output_filename):
    format = pyaudio.paInt16 # 16 bits
    channels = 2 # 2: stereo-channel = better audio quality than 1: mono-channel
    rate = 44100 # number of cycle per second
    chunk = 1024 # length of audio buffer

    audio = pyaudio.PyAudio()

    # open an audio stream as input
    stream = audio.open(format=format, channels=channels, rate=rate, input=True,
                    frames_per_buffer=chunk)

    print('Recording sound...')
    frames = []
    for i in range(0, int(rate / chunk * record_time)):
        data = stream.read(chunk)
        frames.append(data)
    print('Finished recording')

    # close streams
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # save recording
    waveFile = wave.open(output_filename, 'wb')
    waveFile.setnchannels(channels)
    waveFile.setsampwidth(audio.get_sample_size(format))
    waveFile.setframerate(rate)
    waveFile.writeframes(b''.join(frames))
    waveFile.close()

def recognize_song(input_filename):
    # Shazam like API : https://docs.audd.io/
    data = {
        'api_token': 'a92c60b29fb926b74430fdabcba37276',
        'return': 'apple_music'
    }

    file_data = open(input_filename, 'rb')
    files = {
        'file': ('frames.wav', file_data)
    }
    result = requests.post('https://api.audd.io/', data=data, files = files)
    result_json = json.loads(result.text)

    return result_json

def create_new_playlist(playlist_name):
    # API authentification
    api = YTMusic('headers_auth.json')

    # create a new playlist
    current_date = date.today()
    playlist_id = api.create_playlist(playlist_name, 'Party of the {:%d, %b %Y}'.format(current_date))

    return playlist_id

def add_new_song(playlist_id, song_name):
    # API authentification
    api = YTMusic('headers_auth.json')

    # search the song on YoutubeMusic
    search_results = api.search(song_name, limit=3)

    # add the song to the playlist is the song exists
    if search_results is not None:
        api.add_playlist_items(playlist_id, [search_results[0]['videoId']], duplicates=False)
        print(song_name + ' is added to your playlist.\n')


def main():
    frames_file_name = 'frames.wav'

    if os.path.exists(frames_file_name):
        os.remove(frames_file_name)

    ytmusic = YTMusic('headers_auth.json')

    print('Playlist name: ', end='')
    playlist_name = str(input())
    playlist_id = create_new_playlist(playlist_name)

    while (True):
        get_audio(7, frames_file_name)
        result_json = recognize_song(frames_file_name)
        if result_json is not None:
            artist = result_json['result']['artist']
            title = result_json['result']['title']
            if artist is not None and title is not None:
                add_new_song(playlist_id, artist + ' ' + title)
        time.sleep(60)

    if os.path.exists(frames_file_name):
        os.remove(frames_file_name)

if __name__ == "__main__":
    main()
