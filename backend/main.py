import json
from os import name
import flask
import requests
from math import ceil
from keys import *
from flask import Flask, request, jsonify

app = Flask(__name__)

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
    response = jsonify(playlists)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

def mapPlaylists(response):
    playlists = {}
    for playlist in response["items"]:
        playlists[playlist["id"]] = playlist["name"]
    return playlists

# create playlist -> /create-playlist?name="playlist_name"
@app.route("/create-playlist", methods=["POST"])
def createPlaylist():
    accessToken = getAccessToken()
    query = "https://api.spotify.com/v1/users/{}/playlists".format(userId)
    payload = {"name": request.args["name"], "public": "false"}
    response = requests.post(
        query,
        headers={
            "Authorization": "Bearer {}".format(accessToken),
            "Content-Type": "application/json",
        },
        data=json.dumps(payload),
    )
    playlistId = response.json()["id"]
    playlistData = json.loads(request.get_data())
    populatePlaylist(playlistId, playlistData)
    response = jsonify(playlistId)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

def populatePlaylist(playlistId, playlistData):
    accessToken = getAccessToken()
    playlistIds = [playlistData[f"{i}"] for i in range(len(playlistData))]
    songs = getAllSongs(playlistIds, accessToken)
    allSongs = list(set(songs))
    query = "https://api.spotify.com/v1/playlists/{}/tracks".format(
        playlistId
    )
    numIterations = ceil(len(allSongs) / 100)

    for i in range(numIterations):
        start = i * 100
        end = (i + 1) * 100
        payload = allSongs[start:end]
        response = requests.post(
            query,
            headers={
                "Authorization": "Bearer {}".format(accessToken),
                "Content-Type": "application/json",
            },
            data=json.dumps(payload),
        )

def getAllSongs(playlistIds, accessToken):
    allSongs = []
    # create a list of all songs in the playlists user entered
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
                headers={"Authorization": "Bearer {}".format(accessToken)},
            )
            responseJson = response.json()
            items = responseJson["items"]
            for item in items:
                # print(item['track']['name'])
                allSongs.append(item["track"]["uri"])
            offset += len(response.json()["items"])
            if len(responseJson["items"]) == 0:
                run = False
    return allSongs

if __name__ == "__main__":
    app.run()
