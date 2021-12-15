import React from 'react'
import {  } from 'react-dom'

class Mixer extends React.Component {
    constructor(props) {
        super(props);
        this.backendHost = "http://127.0.0.1:5000/"
        this.state = {
            playlists: [],
            selectedPlaylists: [],
            newPlaylist: "New Playlist",
            creating: false,
        };
    }

    componentDidMount = () => {
        this.generatePlaylists();
    }

    updatePlaylistName = (e) => {
        this.setState({
            newPlaylist: e.target.value,
        });
    }

    createPlaylist = () => {
        this.setState({
            creating: true,
        });
        var queryUrl = this.backendHost + `create-playlist?name=${this.state.newPlaylist}`;
        var selectionData = {}
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
        fetch(queryUrl)
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
        console.log(this.state.newPlaylist);
        return (
            <div>
                <h1>
                    Spotify Playlist Mixer
                </h1>
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
                </div>
            </div>
        )
    }
}

export default Mixer