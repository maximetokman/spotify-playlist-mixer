import React from 'react';
import { 
    Button,
    Modal,
    Spinner,
    Form,
} from 'react-bootstrap';

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
            newPlaylist: null,
            creating: false,
            accessToken: null,
            showModal: false,
            nameValid: true,
            selectionValid: true,
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
            nameValid: e.target.value.length > 0,
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
        if (!this.state.newPlaylist?.length > 0 || !(this.state.selectedPlaylists?.length >= 2)) {
            this.setState({
                nameValid: this.state.newPlaylist?.length > 0,
                selectionValid: this.state.selectedPlaylists?.length >= 2,
            });
        }
        else {
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
    }

    generatePlaylists = () => {
        var queryUrl = this.backendHost + "get-playlists";
        var loadingPlaylists = (
            <Spinner animation='grow'/>
        )
        this.setState({
            playlists: loadingPlaylists,
        });
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
                console.log(json);
                var playlists = Object.keys(json).map(id => 
                    <div>
                        <Form.Check
                        type='checkbox'
                        inline
                        id={id}
                        onClick={() => {
                            var updatedSelection = this.state.selectedPlaylists;
                            updatedSelection = updatedSelection?.includes(id) ?
                                updatedSelection.filter(selected => selected != id) :
                                updatedSelection.concat(id)
                            this.setState({
                                selectedPlaylists: updatedSelection,
                                selectionValid: updatedSelection.length >= 2,
                            });
                        }}
                        label={json[id]}
                        />
                    </div>
                );
                this.setState({
                    playlists: playlists,
                });
            })
            .catch(e => console.log(e));
    }

    toggleModal = (action=null) => {
        const { showModal } = this.state;
        this.setState({
            showModal: action == null ? !showModal : action,
        });
    }

    render() {
        return (
            <div id='container'>
                <h1>
                    Spotify Playlist Mixer
                </h1>
                {this.state.accessToken ?
                <Form id='content-wrap'>
                    {this.state.playlists}
                    <Form.Group id="playlist-input">
                        <Form.Control
                        placeholder='Enter a new playlist name'
                        onChange={this.updatePlaylistName}
                        isInvalid={!this.state.nameValid || !this.state.selectionValid}
                        />
                        <Form.Control.Feedback
                        type='invalid'
                        >
                            {!this.state.nameValid && <p>Please enter a new playlist name.</p>}
                            {!this.state.selectionValid && <p>Please select at least 2 playlists.</p>}
                        </Form.Control.Feedback>
                    </Form.Group>
                    <Button
                    variant='dark'
                    disabled={this.state.creating}
                    onClick={this.createPlaylist}
                    >
                        {this.state.creating ? 
                        <Spinner animation='border' size='sm'/> :
                        'Create Playlist'
                        }
                    </Button>
                </Form> :
                <div id='content-wrap'>
                    <div id="login-button">
                        <Button
                        variant='dark'
                        onClick={this.authenticateUser}
                        >
                            Login with your Spotify credentials
                        </Button>
                    </div>
                    <div id="about-button">
                        <Button variant="outline-dark" onClick={this.toggleModal}>
                            Instructions
                        </Button>
                        <Modal show={this.state.showModal} onHide={() => this.toggleModal(false)}>
                            <Modal.Header closeButton>
                                <Modal.Title>Instructions</Modal.Title>
                            </Modal.Header>
                            <Modal.Body>
                                Log in with your Spotify credentials. Then, pick at least 2 playlists to
                                mix together. Enter a name for your new playlist and wait a few seconds
                                for your new playlist to be visible in your Spotify account.
                            </Modal.Body>
                            <Modal.Footer>
                                <Button variant="secondary" onClick={() => this.toggleModal(false)}>
                                    Close
                                </Button>
                            </Modal.Footer>
                        </Modal>
                    </div>
                </div>
                }
                <div id='footer'>
                    <p>Created by Max Tokman, 2021</p>
                </div>
            </div>
        )
    }
}

export default Mixer