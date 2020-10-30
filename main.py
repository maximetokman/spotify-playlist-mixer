import json
import requests
from keys import spotifyToken, userId


class SpotifyMixer:

    def __init__(self):
        self.spotifyToken = spotifyToken
        self.userId = userId
        self.playlists = []
        self.inputList = []

    # Retrieve list of user's playlists
    def getPlaylists(self):
        query = "https://api.spotify.com/v1/users/{}/playlists".format(self.userId)
        response = requests.get(
            query,
            headers = {
                "Accept":"application/json",
                "Content-Type":"application/json",
                "Authorization":"Bearer {}".format(self.spotifyToken)
            }
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
        while True:
            playlist = input("Enter a playlist: ")
            # check validity
            validPlaylist = any(item['id'] == playlist for item in self.playlists)
            if playlist and validPlaylist:
                self.inputList.append(playlist)
            elif not validPlaylist:
                
            else:
                break
            



mixer = SpotifyMixer()
# mixer.mapPlaylists()
mixer.getUserInput()