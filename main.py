import json
import requests
from keys import *


class SpotifyMixer:

    def __init__(self):
        self.accessToken = None
        self.userId = userId
        self.playlists = []
        self.inputList = []

    # Get updated access token
    def getAccessToken(self):
        # query = "https://accounts.spotify.com/api/token"
        # response = requests.post(
        #     query,
        #     {
        #         "grant_type":"authorization_code",
        #         "code":authCode,
        #         "redirect_uri":redirectURI,
        #         "client_id":clientId,
        #         "client_secret":clientSecret
        #     }
        # )

        # print(response.json())
        # self.refreshToken = response.json()['refresh_token']
        query = "https://accounts.spotify.com/api/token"
        response = requests.post(
            query,
            {
                "grant_type":"refresh_token",
                "refresh_token":refreshToken,
                "client_id":clientId,
                "client_secret":clientSecret
            }
        )
        self.accessToken = response.json()['access_token']
        return

    # Retrieve list of user's playlists
    def getPlaylists(self):
        query = "https://api.spotify.com/v1/users/{}/playlists".format(self.userId)
        response = requests.get(
            query,
            headers = {
                "Accept":"application/json",
                "Content-Type":"application/json",
                "Authorization":"Bearer {}".format(self.accessToken)
            },
        )

        responseJson = response.json()

        return responseJson

    # Map retrieved playlists with their ID for searching
    def mapPlaylists(self):
        response = self.getPlaylists()
        for playlist in response["items"]:
            self.playlists.append(
                {
                    "name":playlist['name'],
                    "id":playlist['id']
                }
            )

    # Prompt user to enter a list of playlists to mix together
    def getUserInput(self):
        print("Enter playlists to mix. To stop entering playlists, just press 'enter'.")
        # enter input until empty return and check if playlist is valid
        error = False
        duplicate = False
        while True:
            if not error and not duplicate:
                playlist = input("Enter a playlist: ")
            elif error:
                playlist = input("You entered an invalid playlist, please enter another one: ")
            else:
                playlist = input("You have already entered this playlist, please enter another one: ")
            # check validity
            validPlaylist = any(item['name'] == playlist for item in self.playlists)
            # check duplicate
            duplicatePlaylist = playlist in self.inputList
            if playlist and validPlaylist and not duplicatePlaylist:
                self.inputList.append(playlist)
                print('Playlist added!')
                error = False
                duplicate = False
            elif playlist and not validPlaylist:
                error = True
            elif playlist and duplicatePlaylist:
                duplicate = True
            else:
                break
            



mixer = SpotifyMixer()
mixer.getAccessToken()
mixer.mapPlaylists()
mixer.getUserInput()