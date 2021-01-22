This is intended to provide an easy command line interface for interacting with the 
VDMS, virtual linear playlist APIs. 

You can set up a python environment and run the playlist api interface (linear_playlist.py) locally
or you can simply build and run the docker container (which will ensure you have the correct python
environment to run the interface).

To get started:

1 - Add your VDMS CMS user id and private key to the api_auth.py (as all interactions with the API require authentication)
2 - Build and run the container
    docker build -t vdmsapigateway .
    docker run --rm -it vdmsapigateway
3 - This will launch you into a bash shell in the container where you can perform api operations.  Get the CLI usage by running:

    python3 linear_playlist.py
    
    EX: reading all the playlists in your account would be:
    python3 linear_playlist.py r
