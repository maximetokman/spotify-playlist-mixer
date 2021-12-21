import React from 'react'

class Mixer extends React.Component {
    constructor(props) {
        super(props);
        // this.backendHost = "http://127.0.0.1:5000/"
        this.backendHost = "https://api.spotifymix.com/";
        // this.frontendHost = "http://localhost:3000/";
        this.frontendHost = "https://spotifymix.com/";
        this.state = {
            playlists: [],
            selectedPlaylists: [],
            newPlaylist: "New Playlist",

            creating: false,
            accessToken: null,
        };
    }

    componentDidMount = () => {
        var url = new URLSearchParams(window.location.href);
        if (url.has(this.frontendHost + "?code")) {
            var code = url.get(this.frontendHost + "?code");
            var queryUrl = this.backendHost + `callback?code=${code}`;
            fetch(queryUrl, {
                method: "POST",
                body: JSON.stringify({
                    redirect_uri: this.frontendHost,
                }),
            })
                .then(response => response.json())
                .then(json => {
                    this.setState({
                        accessToken: json,
                    });
                })
                .then(() => window.history.pushState({}, '', this.frontendHost))
                .catch(e => console.log(e));
        }
    }

    componentDidUpdate = (prevProps, prevState) => {
        if (prevState.accessToken !== this.state.accessToken) {
            this.generatePlaylists();
        }
    }

    updatePlaylistName = (e) => {
        this.setState({
            newPlaylist: e.target.value,
        });
    }

    authenticateUser = () => {
        var redirect_uri = this.frontendHost;
        var scope = "playlist-modify-private playlist-read-private";
        var client_query = this.backendHost + "client"
        fetch(client_query)
            .then(response => response.json())
            .then(client => {
                window.location = `https://accounts.spotify.com/authorize?` +
                    `client_id=${client}` +
                    `&response_type=code` +
                    `&redirect_uri=${redirect_uri}` +
                    `&scope=${encodeURIComponent(scope)}`;
            })
            .catch(e => console.log(e));
    }

    createPlaylist = () => {
        this.setState({
            creating: true,
        });
        var queryUrl = this.backendHost + `create-playlist?name=${this.state.newPlaylist}`;
        var selectionData = {
            "access_token": this.state.accessToken,
        };
        this.state.selectedPlaylists.forEach((p, i) => {
            selectionData[i] = p;
        });
        fetch(queryUrl, {
            method: "POST",
            headers: {
                "Content-Type": "text/plain",
            },
            body: JSON.stringify(selectionData),
        })
            .then(() => {
                this.setState({
                    creating: false,
                });
            })
            .catch(e => console.log(e));
    }

    generatePlaylists = () => {
        var queryUrl = this.backendHost + "get-playlists";
        fetch(queryUrl, {
            method: "POST",
            headers: {
                "Content-Type": "text/plain",
            },
            body: JSON.stringify({
                "access_token": this.state.accessToken,
            }),
        })
            .then(response => response.json())
            .then(json => {
                var playlists = Object.keys(json).map(id => 
                    <div>
                        <input
                        type="checkbox"
                        id={id}
                        onClick={() => {
                            var updatedSelection = this.state.selectedPlaylists;
                            updatedSelection = updatedSelection?.includes(id) ?
                                updatedSelection.filter(selected => selected != id) :
                                updatedSelection.concat(id)
                            this.setState({
                                selectedPlaylists: updatedSelection,
                            });
                        }}
                        />
                        <label for={id}>{json[id]}</label>
                    </div>
                );
                this.setState({
                    playlists: playlists,
                });
            })
            .catch(e => console.log(e));
    }

    render() {
        return (
            <div>
                <h1>
                    Spotify Playlist Mixer
                </h1>
                {this.state.accessToken ?
                <div>
                    {this.state.playlists}
                    <input
                    id="playlist-input" 
                    type="text" 
                    placeholder='Enter a new playlist name'
                    onChange={this.updatePlaylistName}
                    />
                    <div id='create-button'>
                        <button 
                        disabled={this.state.creating} 
                        onClick={this.createPlaylist}>
                            Create Playlist
                        </button>
                    </div>
                </div> :
                <div id="login-button">
                    <button
                    onClick={this.authenticateUser}
                    >
                        Login
                    </button>
                </div>
                }
            </div>
        )
    }
}

export default Mixer