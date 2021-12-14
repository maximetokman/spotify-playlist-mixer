import json
from os import name
import requests
from math import ceil
from keys import *
from flask import Flask, request

app = Flask(__name__)

inputList = []
newPlaylist = None
allSongs = []
createdPlaylistId = None

# Get updated access token
def getAccessToken():
    """Code for getting a new refresh token with different permissions"""
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
    query = "https://accounts.spotify.com/api/token"
    response = requests.post(
        query,
        {
            "grant_type": "refresh_token",
            "refresh_token": refreshToken,
            "client_id": clientId,
            "client_secret": clientSecret,
        },
    )
    return response.json()["access_token"]

# Retrieve list of user's playlists mapped to id
@app.route("/get-playlists")
def getPlaylists():
    accessToken = getAccessToken()
    query = "https://api.spotify.com/v1/users/{}/playlists".format(userId)
    response = requests.get(
        query,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(accessToken),
        },
    )

    responseJson = response.json()

    playlists = mapPlaylists(responseJson)

    return playlists

def mapPlaylists(response):
    playlists = {}
    for playlist in response["items"]:
        playlists[playlist["id"]] = playlist["name"]
    return playlists

# # Prompt user to enter a list of playlists to mix together
# def getUserInput(self):
#     print("Enter playlists to mix. To stop entering playlists, just press 'enter'.")
#     # enter input until empty return and check if playlist is valid
#     error = False
#     duplicate = False
#     while True:
#         if not error and not duplicate:
#             playlist = input("Enter a playlist: ")
#         elif error:
#             playlist = input(
#                 "You entered an invalid playlist, please enter another one: "
#             )
#         else:
#             playlist = input(
#                 "You have already entered this playlist, please enter another one: "
#             )
#         # check validity
#         validPlaylist = any(item["name"] == playlist for item in self.playlists)
#         # check duplicate
#         duplicatePlaylist = playlist in self.inputList
#         if playlist and validPlaylist and not duplicatePlaylist:
#             self.inputList.append(playlist)
#             print("Playlist added!")
#             error = False
#             duplicate = False
#         elif playlist and not validPlaylist:
#             error = True
#         elif playlist and duplicatePlaylist:
#             duplicate = True
#         else:
#             break

#     # ask for new playlist name
#     # first check that above input is >0
#     if len(self.inputList) == 0:
#         print("You entered 0 playlists, exiting!")
#         return

#     isPlaylist = False
#     while True:
#         if not isPlaylist:
#             self.newPlaylist = input("Enter a new playlist name: ")
#         else:
#             self.newPlaylist = input(
#                 "This playlist already exists, enter a different playlist name: "
#             )
#         # make sure playlist name doesn't already exist
#         if any(item["name"] == self.newPlaylist for item in self.playlists):
#             isPlaylist = True
#         else:
#             break

# create playlist -> /create-playlist?name="playlist_name"
@app.route("/create-playlist")
def createPlaylist():
    accessToken = getAccessToken()
    query = "https://api.spotify.com/v1/users/{}/playlists".format(userId)
    payload = {"name": request.args["name"], "public": "false"}
    # response = requests.post(
    #     query,
    #     headers={
    #         "Authorization": "Bearer {}".format(accessToken),
    #         "Content-Type": "application/json",
    #     },
    #     data=json.dumps(payload),
    # )
    return payload
    # return response.json()["id"]

def getAllSongs():
    # create a list of all songs in the playlists user entered
    playlistIds = [
        item["id"]
        for item in self.playlists
        for playlist in self.inputList
        if item["name"] == playlist
    ]

    for playlistId in playlistIds:
        # get songs while response not empty
        run = True
        offset = 0
        while run:
            query = (
                "https://api.spotify.com/v1/playlists/{}/tracks?offset={}".format(
                    playlistId, offset
                )
            )
            response = requests.get(
                query,
                headers={"Authorization": "Bearer {}".format(self.accessToken)},
            )
            responseJson = response.json()
            items = responseJson["items"]
            for item in items:
                # print(item['track']['name'])
                self.allSongs.append(item["track"]["uri"])
            offset += len(response.json()["items"])
            if len(responseJson["items"]) == 0:
                run = False

# populate new playlist -> 
@app.route("/update-playlist")
def populatePlaylist(self):
    self.getAllSongs()
    self.allSongs = list(set(self.allSongs))
    query = "https://api.spotify.com/v1/playlists/{}/tracks".format(
        self.createdPlaylistId
    )
    numIterations = ceil(len(self.allSongs) / 100)

    for i in range(numIterations):
        start = i * 100
        end = (i + 1) * 100
        payload = self.allSongs[start:end]
        response = requests.post(
            query,
            headers={
                "Authorization": "Bearer {}".format(self.accessToken),
                "Content-Type": "application/json",
            },
            data=json.dumps(payload),
        )

# def run(self):
#     self.getAccessToken()
#     self.mapPlaylists()
#     self.getUserInput()
#     self.createPlaylist()
#     self.populatePlaylist()


if __name__ == "__main__":
    app.run()
    # Mixer = SpotifyMixer()
    # Mixer.run()
