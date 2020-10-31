import json
import requests
from keys import *


class SpotifyMixer:

    def __init__(self):
        self.accessToken = None
        self.userId = userId
        self.playlists = []
        self.inputList = []
        self.newPlaylist = None
        self.allSongs = []

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
        print(response.json())
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
        
        # ask for new playlist name
        # first check that above input is >0
        if len(self.inputList) == 0:
            print("You entered 0 playlists, exiting!")
            return
        
        isPlaylist = False
        while True:
            if not isPlaylist:
                self.newPlaylist = input("Enter a new playlist name: ")
            else:
                self.newPlaylist = input("This playlist already exists, enter a different playlist name: ")
            # make sure playlist name doesn't already exist
            if any(item['name'] == self.newPlaylist for item in self.playlists):
                isPlaylist = True
            else:
                break

    def createPlaylist(self):
        query = "https://api.spotify.com/v1/users/{}/playlists".format(self.userId)
        payload = {
                "name":self.newPlaylist,
                "public":"false"
            }
        response = requests.post(
            query,
            headers = {
                "Authorization":"Bearer {}".format(self.accessToken),
                "Content-Type":"application/json"
            },
            data = json.dumps(payload)
        )
   
    def populatePlaylist(self):
       # create a list of all songs in the playlists user entered
        for playlist in self.inputList:
            playlistIds = [item['id'] for item in self.playlists if item['name'] == playlist]

        offset = 0
        for playlistId in playlistIds:
            # get songs while response not empty
            while True:
                query = "https://api.spotify.com/v1/playlists/{}/tracks?offset={}".format(playlistId, offset)
                response = requests.get(
                    query,
                    headers = {
                        "Authorization":"Bearer {}".format(self.accessToken)
                    }
                )
                print(response.json()['items'][0])
                offset += len(response.json()['items'])
                print(offset)
                if not response:
                    break
                # self.allSongs.append(response)
            print(response.json())


mixer = SpotifyMixer()
mixer.getAccessToken()
mixer.mapPlaylists()
mixer.getUserInput()
# mixer.createPlaylist()
mixer.populatePlaylist()