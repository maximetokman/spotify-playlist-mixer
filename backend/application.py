import json
import os
import requests
from math import ceil
from flask import Flask, request, jsonify
from flask_cors import CORS

application = Flask(__name__)

CORS(application)


# Get client id
@application.route("/client")
def getClientId():
    response = jsonify(os.environ.get("CLIENT_ID"))
    return response

# Get access token
@application.route("/callback", methods=["POST"])
def getAccessToken():
    redirect_uri = json.loads(request.get_data())["redirect_uri"]
    code = request.args["code"]
    query = "https://accounts.spotify.com/api/token"
    response = requests.post(
        query,
        {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": os.environ.get("CLIENT_ID"),
            "client_secret": os.environ.get("CLIENT_SECRET")
        }
    )
   
    response = jsonify(response.json()["access_token"])
    return response
    
# Retrieve list of user's playlists mapped to id
@application.route("/get-playlists", methods=["POST"])
def getPlaylists():
    accessToken = json.loads(request.get_data())["access_token"]
    run = True
    offset = 0
    items = []
    while run:
        query = "https://api.spotify.com/v1/me/playlists?offset={}".format(offset)
        response = requests.get(
            query,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(accessToken),
            },
        )
        responseJson = response.json()
        numReturned = len(responseJson["items"])
        if numReturned == 0:
            break
        offset += numReturned
        items += responseJson["items"]
        
    playlists = mapPlaylists(items)
    response = jsonify(playlists)
    return response

def mapPlaylists(items):
    playlists = {}
    for playlist in items:
        playlists[playlist["id"]] = playlist["name"]
    return playlists

# create playlist -> /create-playlist?name="playlist_name"
@application.route("/create-playlist", methods=["POST"])
def createPlaylist():
    request_data = json.loads(request.get_data())
    accessToken = request_data["access_token"]
    # get user id
    query_id = "https://api.spotify.com/v1/me"
    user = requests.get(
        query_id,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(accessToken)
        }
    )
    user_id = user.json()["id"]
    query = "https://api.spotify.com/v1/users/{}/playlists".format(user_id)
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
    playlistData = {k:request_data[k] for k in list(request_data)[:-1]}
    populatePlaylist(playlistId, playlistData, accessToken)
    response = jsonify(playlistId)
    return response

def populatePlaylist(playlistId, playlistData, accessToken):
    playlistIds = [playlistData[f"{i}"] for i in range(len(playlistData))]
    songs = getAllSongs(playlistIds, accessToken)
    unique = []
    remove_dup = [unique.append(s) for s in songs if s not in unique]
    query = "https://api.spotify.com/v1/playlists/{}/tracks".format(
        playlistId
    )
    numIterations = ceil(len(unique) / 100)

    for i in range(numIterations):
        start = i * 100
        end = (i + 1) * 100
        payload = unique[start:end]
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
            numReturned = len(responseJson["items"])
            if numReturned == 0:
                break
            offset += numReturned
            items = responseJson["items"]
            for item in items:
                # print(item['track']['name'])
                allSongs.append(item["track"]["uri"])
    
    return allSongs

if __name__ == "__main__":
    application.run()
